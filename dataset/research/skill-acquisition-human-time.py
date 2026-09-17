import math, json

def sig2(x):
    if x == 0: return 0
    e = math.floor(math.log10(abs(x))) - 1
    return round(x, -e) if e > 0 else round(x, -e)

# ---- Ladder L: adult second language ----
LAD = [(0.0,0.0),(0.10,95.0),(0.25,190.0),(0.45,375.0),(0.65,550.0),(0.85,750.0),(1.00,1100.0)]
def HL(c):
    c = max(0.0, min(1.0, c))
    for i in range(1, len(LAD)):
        c0,h0 = LAD[i-1]; c1,h1 = LAD[i]
        if c <= c1: return h0 + (c-c0)/(c1-c0)*(h1-h0)
    return LAD[-1][1]
def cfrac(s, ch): return max(0.0, (s-ch)/(1.0-ch))
KL = {'Japanese':2200/750.0, 'Arabic':2200/750.0, 'Estonian':1100/750.0, 'Basque':2250/750.0}

# ---- Ladder P: programming ----
# Fully-correct rates on the Rainfall Problem, one entry per reported cohort,
# from Table 2 of Seppala et al. (2015). Twenty cohorts at the end of a first
# programming course, three after a second. Fisler's seven-student high-school
# cohort is left out as too small to carry a quartile.
RAINFALL_CS1 = [45, 53, 72,          # Seppala contexts 1-3
                54, 39, 11, 2,       # Fisler T1, T1Acc, T2, T3Non
                0,                   # Simon
                19,                  # Venables et al.
                31, 2,               # de Raadt 2007, 2003
                12,                  # Guzdial et al.
                5, 20, 20, 15,       # Ebrahimi, Pascal / C / Fortran / Lisp
                11,                  # Johnson et al.
                14, 24,              # Soloway et al. 1983, CS1 Pascal / Pascal-L
                39]                  # Soloway et al. 1982, novices
RAINFALL_CS2 = [36, 61,              # Soloway et al. 1983, CS2 Pascal / Pascal-L
                42]                  # Soloway et al. 1982, intermediates
# A first programming course is 135 student-hours: three credits at the Carnegie
# credit hour's three student-hours a week over a fifteen-week semester. A second
# course doubles it.
PH1, PH2 = 135.0, 270.0

def _quartiles(xs):
    xs = sorted(xs); n = len(xs)
    def q(f):
        pos = f * (n - 1); lo = math.floor(pos); hi = math.ceil(pos)
        return xs[lo] + (pos - lo) * (xs[hi] - xs[lo])
    return q(0.25), q(0.50), q(0.75)

P_Q1, P_MED, P_Q3 = [x / 100.0 for x in _quartiles(RAINFALL_CS1)]
P_CS2 = sorted(RAINFALL_CS2)[len(RAINFALL_CS2) // 2] / 100.0
P_GAIN = P_CS2 / P_MED                      # second course multiplies the rate

def _fit(p1):
    """pass rate = C * hours**beta through (135 h, p1) and (270 h, p1*P_GAIN)."""
    beta = math.log(P_GAIN) / math.log(PH2 / PH1)
    return beta, p1 / PH1 ** beta

BETA, CC = _fit(P_MED)
BETA_LO, CC_LO = _fit(P_Q3)                 # fast cohorts: fewer hours
BETA_HI, CC_HI = _fit(P_Q1)                 # slow cohorts: more hours

def HP(p, C=None):
    C = CC if C is None else C
    return 0.0 if p <= 0 else (p / C) ** (1.0 / BETA)

# ---- Ladder C: child ----
# Active language-interaction hours per day, from Gilkerson et al. (2017):
# 12,700 adult words per day at 150 words/minute = 1.41 h of speech, plus 1,817
# child vocalizations at 1 s = 0.51 h. Held constant across childhood.
CHILD_HOURS_PER_DAY = 1.9
def child_age(score): return 12.0 ** ((score-0.50)/(0.886-0.50))
def child_hours(A): return CHILD_HOURS_PER_DAY * 365 * A

LANG = [
 ('lang-xfer-ja-swallow7b','Japanese',0.20,0.385,0.481),
 ('lang-xfer-ja-swallow70b','Japanese',0.20,0.869,0.935),
 ('lang-xfer-ar-acegpt7b-base','Arabic',0.25,0.2947,0.3214),
 ('lang-xfer-ar-acegpt13b-base','Arabic',0.25,0.3376,0.4045),
 ('lang-xfer-et-llammas-base','Estonian',0.25,0.2295,0.3934),
 ('lang-xfer-eu-latxa13b','Basque',0.25,0.259044,0.450184),
 ('lang-xfer-eu-latxa70b','Basque',0.25,0.241633,0.606113),
]
CODE = [
 ('agen-codexfer-codex300m',0.0,0.1317,1.0),
 ('agen-codexfer-codex2p5b',0.0,0.2136,1.0),
 ('agen-codexfer-codex12b',0.0,0.2881,1.0),
 ('agen-codexfer-codellama7b',0.122,0.335,1.0),
 ('agen-codexfer-codellama34b',0.226,0.488,1.0),
 ('agen-codexfer-kotlin7b',0.2609,0.4224,0.2),
 ('agen-codexfer-mplt-ocaml1b',0.015,0.097,0.2),
 ('agen-codexfer-mplt-ocaml15b',0.069,0.199,0.2),
 ('agen-codexfer-mplt-racket15b',0.118,0.210,0.2),
]
CHILD = [
 ('lang-lacq-blimp-lstm',0.698),
 ('lang-lacq-zorro-babyberta',0.805),
 ('lang-lacq-blimp-gptbert10m',0.812),
 ('lang-lacq-blimp-elcbert100m',0.853),
 ('lang-lacq-blimp-gptbert100m',0.861),
]

res = {}
for pid,lg,ch,b,t in LANG:
    cb,ct = cfrac(b,ch), cfrac(t,ch); k = KL[lg]
    h = sig2(k*(HL(ct)-HL(cb)))
    res[pid] = dict(kind='lang', lang=lg, chance=ch, base=b, target=t, c_base=cb, c_tgt=ct,
                    h_base=k*HL(cb), h_tgt=k*HL(ct), hours=h, seconds=int(round(h*3600)))
for pid,b,t,tau in CODE:
    h  = sig2(tau*(HP(t)-HP(b)))
    lo = sig2(tau*(HP(t,CC_LO)-HP(b,CC_LO)))   # fast-cohort curve: fewer hours
    hi = sig2(tau*(HP(t,CC_HI)-HP(b,CC_HI)))   # slow-cohort curve: more hours
    res[pid] = dict(kind='code', base=b, target=t, tau=tau, h_base=HP(b), h_tgt=HP(t),
                    hours=h, seconds=int(round(h*3600)),
                    hours_low=lo, seconds_low=int(round(lo*3600)),
                    hours_high=hi, seconds_high=int(round(hi*3600)))
for pid,s in CHILD:
    A = child_age(s); h = sig2(child_hours(A))
    res[pid] = dict(kind='child', score=s, a=(s-0.50)/(0.886-0.50), age=A,
                    hours=h, seconds=int(round(h*3600)))
if __name__ == '__main__':
    print(f"Table P: CS1 quartiles {P_Q1:.3f}/{P_MED:.3f}/{P_Q3:.3f} at {PH1:g} h, "
          f"CS2 median {P_CS2:.3f} at {PH2:g} h, gain {P_GAIN:.3f}")
    print(f"beta={BETA:.4f} C={CC:.6g}  C_fast={CC_LO:.6g} C_slow={CC_HI:.6g}")
    for k,v in res.items():
        print(k, v.get('hours'), v.get('seconds'), {kk:round(vv,3) for kk,vv in v.items() if isinstance(vv,float)})
