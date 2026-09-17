"""Analytic convolution/dense MAC counts. No model weights or ML runtime needed.

Inception executes only the retained original architecture function against shape
operators. The other models follow the retained source block specifications.
Two FLOPs per MAC; normalizations, nonlinearities, interpolation and pooling
arithmetic are omitted. Counts describe recipes, not measured device operations.
"""
import ast
import json
import math
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import argparse
cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument('source_dir', type=Path)
cli.add_argument('output_dir', type=Path)
args = cli.parse_args()
SOURCE_DIR = args.source_dir
OUTPUT_DIR = args.output_dir
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class Counter:
    def __init__(self):
        self.rows = []

    def conv(self, x, c, k=1, s=1, padding="SAME", groups=1, name="conv"):
        h, w, ci = x
        kh, kw = (k, k) if isinstance(k, int) else k
        oh, ow = ((math.ceil(h/s), math.ceil(w/s)) if padding == "SAME"
                  else ((h-kh)//s+1, (w-kw)//s+1))
        macs = oh * ow * ci * c * kh * kw // groups
        self.rows.append(dict(name=name, input=list(x), output=[oh, ow, c],
                              kernel=[kh, kw], stride=s, groups=groups, macs=macs))
        return oh, ow, c

    def dense(self, ni, no, name="dense"):
        self.rows.append(dict(name=name, input_features=ni, output_features=no,
                              macs=ni*no))

    @property
    def macs(self):
        return sum(row["macs"] for row in self.rows)


def inception(classes):
    count = Counter()
    defaults = [dict(stride=1, padding="SAME")]

    @contextmanager
    def scope(*args, **kwargs):
        yield None

    @contextmanager
    def arg_scope(ops, **kwargs):
        defaults.append(defaults[-1] | kwargs)
        yield None
        defaults.pop()

    def conv2d(x, c, k, **kw):
        opts = defaults[-1] | kw
        return count.conv(x, c, k, opts["stride"], opts["padding"],
                          name=opts.get("scope", "conv"))

    def pool(x, k, **kw):
        opts = defaults[-1] | kw
        h, w, c = x
        s = opts["stride"]
        return ((math.ceil(h/s), math.ceil(w/s), c) if opts["padding"] == "SAME"
                else ((h-k[0])//s+1, (w-k[1])//s+1, c))

    def concat(axis, values):
        assert axis == 3 and len({v[:2] for v in values}) == 1
        return values[0][0], values[0][1], sum(v[2] for v in values)

    tree = ast.parse((SOURCE_DIR / "skin/inception_v3.py").read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "inception_v3_base")
    namespace = dict(tf=SimpleNamespace(variable_scope=scope, concat=concat),
                     slim=SimpleNamespace(arg_scope=arg_scope, conv2d=conv2d,
                                          max_pool2d=pool, avg_pool2d=pool))
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "original_inception", "exec"), namespace)
    x, endpoints = namespace["inception_v3_base"]((299, 299, 3))
    assert x == (8, 8, 2048)
    count.dense(x[2], classes, "pooled_logits")
    return count


def arcface():
    count = Counter()
    x = count.conv((112,112,3), 64, 3, name="stem")
    for stage, (c, n) in enumerate(zip([64,128,256,512],[3,13,30,3]), 1):
        for unit in range(n):
            previous = x
            x = count.conv(x,c,3,name=f"stage{stage}.{unit}.conv1")
            x = count.conv(x,c,3,s=2 if unit == 0 else 1,
                           name=f"stage{stage}.{unit}.conv2")
            if unit == 0:
                shortcut = count.conv(previous,c,1,s=2,name=f"stage{stage}.shortcut")
                assert shortcut == x
    assert x == (7,7,512)
    count.dense(math.prod(x), 512, "embedding")
    return count


def resnet(h, w, channels=3, stride_at="block_end"):
    """TF-Slim end-of-block stride, or original first 1x1 stride sensitivity."""
    count = Counter()
    x = count.conv((h,w,channels),64,7,s=2,name="stem")
    x = (math.ceil(x[0]/2), math.ceil(x[1]/2), x[2])
    for i,(b,n) in enumerate(zip([64,128,256,512],[3,4,6,3])):
        for j in range(n):
            previous = x
            s = (2 if i<3 and j==n-1 else 1) if stride_at=="block_end" else (2 if i>0 and j==0 else 1)
            if previous[2] != 4*b:
                count.conv(previous,4*b,1,s=s,name=f"block{i}.{j}.shortcut")
            x = count.conv(x,b,1,s=s if stride_at=="original" else 1,name=f"block{i}.{j}.conv1")
            x = count.conv(x,b,3,s=s if stride_at=="block_end" else 1,name=f"block{i}.{j}.conv2")
            x = count.conv(x,4*b,1,name=f"block{i}.{j}.conv3")
    assert x == (math.ceil(h/32),math.ceil(w/32),2048)
    return count


def mobilenet(size=409, width=1):
    count = Counter()
    def channels(c):
        return max(8, int(c*width+4)//8*8)
    x = count.conv((size,size,3), channels(32),3,s=2,name="stem")
    for i,(t,c,n,s) in enumerate([(1,16,1,1),(6,24,2,2),(6,32,3,2),
                                 (6,64,4,2),(6,96,3,1),(6,160,3,2),(6,320,1,1)]):
        for j in range(n):
            expanded = x[2]*t
            if t != 1:
                x = count.conv(x,expanded,1,name=f"block{i}.{j}.expand")
            x = count.conv(x,expanded,3,s=s if j==0 else 1,groups=expanded,
                           name=f"block{i}.{j}.depthwise")
            x = count.conv(x,channels(c),1,name=f"block{i}.{j}.project")
    count.conv(x,max(1280,channels(1280)),1,name="features")
    return count


def detector():
    """Assumed standard R50/FPN RetinaNet: 256-wide pyramid, 9 anchors, 1 class."""
    count = resnet(2048,2048)
    for level,c in [(3,512),(4,1024),(5,2048)]:
        n = 2048//(2**level)
        count.conv((n,n,c),256,1,name=f"fpn{level}.lateral")
        count.conv((n,n,256),256,3,name=f"fpn{level}.output")
    count.conv((64,64,2048),256,3,s=2,name="fpn6")
    count.conv((32,32,256),256,3,s=2,name="fpn7")
    for level in range(3,8):
        n = 2048//(2**level)
        for head,out in [("class",9),("box",36)]:
            x = (n,n,256)
            for j in range(4):
                x = count.conv(x,256,3,name=f"p{level}.{head}{j}")
            count.conv(x,out,3,name=f"p{level}.{head}.out")
    return count


def breast_head(width=2048):
    """Unreported head widths: constant output width, quarter-width bottlenecks."""
    count = Counter()
    x = (128,104,4096)  # two spatial ResNet feature maps concatenated
    for group,stride in enumerate([4,2,2]):
        for j in range(4):
            s = stride if j==0 else 1
            old = x
            x = count.conv(x,width//4,1,name=f"head{group}.{j}.conv1")
            x = count.conv(x,width//4,3,s=s,name=f"head{group}.{j}.conv2")
            x = count.conv(x,width,1,name=f"head{group}.{j}.conv3")
            if old[2] != width:
                count.conv(old,width,1,s=s,name=f"head{group}.{j}.shortcut")
    count.conv(x,1,1,name="breast_logit")
    return count


def main():
    models = {"inception_skin": inception(757), "inception_retina": inception(4),
              "arcface_r100": arcface(), "resnet50_case": resnet(2048,2048),
              "resnet50_case_original_stride": resnet(2048,2048,stride_at="original"),
              "resnet50_breast":resnet(4096,3328), "mobilenet_patch":mobilenet(),
              "retinanet_detector":detector(), "breast_head_assumed":breast_head()}
    macs = {name:c.macs for name,c in models.items()}
    # Standard pooled features assumed; a spatially flattened case head is a sensitivity.
    case_head = 4*2048*512 + 512
    lesion_head = (2*1280+8)*1  # assumed one linear binary logit per candidate
    case = 3*500*(4*macs["resnet50_case"] + case_head)
    lesion = 3*(4*macs["retinanet_detector"] + 500*(20*macs["mobilenet_patch"] + 10*lesion_head))
    breast = 3*(4*macs["resnet50_breast"] + 2*macs["breast_head_assumed"])
    mammo = 2*(case+lesion+breast)
    report = dict(convention="2 FLOPs per convolution/dense MAC; excludes pooling, normalization, activation and image transformations",
                  per_forward_macs=macs,
                  points=dict(arcface_flops=4*macs["arcface_r100"],
                              skin_flops=2*macs["inception_skin"],
                              retina_flops=20*macs["inception_retina"],
                              mammography_flops=mammo),
                  mammography_branch_flops=dict(case=2*case,lesion=2*lesion,breast=2*breast),
                  sensitivities=dict(mammography_500_breast_views=2*(case+lesion+500*breast),
                                     mammography_original_resnet_stride=mammo+2*3*500*4*(macs["resnet50_case_original_stride"]-macs["resnet50_case"]),
                                     mammography_spatial_case_head=mammo+2*3*500*(4*64*64*2048*512-4*2048*512),
                                     arcface_flip_pair_flops=8*macs["arcface_r100"]),
                  human_seconds=dict(arcface=30,skin=3.2,retina=50,mammography=150),
                  human_sensitivity_seconds=dict(arcface=[20,60],skin=[2,10],retina=[25,100],mammography=[75,300]))
    (OUTPUT_DIR / "calculations.json").write_text(json.dumps(report,indent=2)+"\n")
    (OUTPUT_DIR / "operation-ledger.json").write_text(json.dumps({k:v.rows for k,v in models.items()},indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
