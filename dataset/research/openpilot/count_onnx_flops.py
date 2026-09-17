#!/usr/bin/env python3
"""Count multiply-accumulate operations per forward pass of an ONNX graph.

Reads the deployed comma.ai openpilot driving models and reports, per model:
  - parameter count (initializer elements)
  - MACs per inference, by operator type
  - FLOPs per inference at 2 FLOPs per MAC

Usage: count_onnx_flops.py <model.onnx> [<model.onnx> ...]
Writes a JSON summary to stdout.
"""
import json
import sys

import numpy as np
import onnx
from onnx import shape_inference


def dims(vi):
    t = vi.type.tensor_type
    out = []
    for d in t.shape.dim:
        out.append(d.dim_value if d.HasField("dim_value") else None)
    return out


def numel(shape):
    n = 1
    for d in shape:
        if d in (None, 0):
            return None
        n *= d
    return n


def count(path):
    m = onnx.load(path)
    m = shape_inference.infer_shapes(m, strict_mode=False, data_prop=True)
    g = m.graph

    shapes = {}
    for coll in (g.input, g.output, g.value_info):
        for vi in coll:
            shapes[vi.name] = dims(vi)
    init = {}
    for t in g.initializer:
        init[t.name] = list(t.dims)
        shapes[t.name] = list(t.dims)

    params = sum(int(np.prod(s)) if s else 1 for s in init.values())

    macs_by_op = {}
    unknown = []

    def add(op, n):
        macs_by_op[op] = macs_by_op.get(op, 0) + n

    for node in g.node:
        op = node.op_type
        ins = [shapes.get(i) for i in node.input]
        outs = [shapes.get(o) for o in node.output]
        if op == "Conv":
            o = outs[0]
            w = ins[1]
            if o is None or w is None or numel(o) is None:
                unknown.append((op, node.name))
                continue
            # out elements * (kernel elements * in_channels_per_group)
            kern = int(np.prod(w[1:]))
            add(op, numel(o) * kern)
        elif op == "ConvTranspose":
            i = ins[0]
            w = ins[1]
            if i is None or w is None or numel(i) is None:
                unknown.append((op, node.name))
                continue
            kern = int(np.prod(w[1:]))
            add(op, numel(i) * kern)
        elif op in ("Gemm", "MatMul"):
            a, b = ins[0], ins[1]
            o = outs[0]
            if op == "Gemm":
                if a is None or b is None:
                    unknown.append((op, node.name))
                    continue
                transB = 0
                for at in node.attribute:
                    if at.name == "transB":
                        transB = at.i
                M = a[0]
                K = a[1]
                N = b[0] if transB else b[1]
                if None in (M, K, N):
                    unknown.append((op, node.name))
                    continue
                add(op, M * K * N)
            else:
                if a is None or b is None or o is None or numel(o) is None:
                    unknown.append((op, node.name))
                    continue
                K = a[-1]
                if K is None:
                    unknown.append((op, node.name))
                    continue
                add(op, numel(o) * K)
        elif op == "Einsum":
            eq = ""
            for at in node.attribute:
                if at.name == "equation":
                    eq = at.s.decode()
            o = outs[0]
            if o is None or numel(o) is None or "->" not in eq:
                unknown.append((op, node.name + " " + eq))
                continue
            lhs, rhs = eq.split("->")
            terms = lhs.split(",")
            sizes = {}
            for term, shp in zip(terms, ins):
                if shp is None:
                    continue
                for lab, d in zip(term.strip(), shp):
                    if d:
                        sizes[lab] = d
            total = 1
            ok = True
            for lab in set(lhs.replace(",", "").strip()):
                if lab not in sizes:
                    ok = False
                    break
                total *= sizes[lab]
            if not ok:
                unknown.append((op, node.name + " " + eq))
                continue
            add(op, total)
    macs = sum(macs_by_op.values())
    return {
        "model": path.split("/")[-1],
        "parameters": params,
        "macs_per_inference": macs,
        "flops_per_inference": 2 * macs,
        "macs_by_op": macs_by_op,
        "unknown_nodes": unknown,
        "inputs": {vi.name: dims(vi) for vi in g.input if vi.name not in init},
        "outputs": {vi.name: dims(vi) for vi in g.output},
        "op_histogram": {},
    }


if __name__ == "__main__":
    res = [count(p) for p in sys.argv[1:]]
    print(json.dumps(res, indent=2))
