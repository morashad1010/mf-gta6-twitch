#!/usr/bin/env python3
"""
Improved Twitch CCU Forecast for GTA VI launch day
Uses comparable launches, diurnal patterns, and quantile regression
"""

import json, math, os, sys, statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]

def round2(x):
    scaled = x * 100
    whole = math.floor(scaled)
    if scaled - whole >= 0.5:
        whole += 1
    v = whole / 100
    return int(v) if v.is_integer() else v

def quantile(data, q):
    """Linear interpolation quantile"""
    if not data:
        return 0
    data = sorted(data)
    idx = q * (len(data) - 1)
    lo, hi = int(math.floor(idx)), int(math.ceil(idx))
    if lo == hi:
        return data[lo]
    return data[lo] + (data[hi] - data[lo]) * (idx - lo)

def extract_comparable_curves(comparables):
    """Extract normalized decay curves from comparable launches"""
    curves = []
    for c in comparables:
        hourly = c.get("hourly", [])
        if len(hourly) < 24:
            continue
        # Normalize by hour 1
        h1 = hourly[0].get("viewers", 1)
        if h1 <= 0:
            h1 = 1
        norm = [max(0.01, h.get("viewers", 0) / h1) for h in hourly[:24]]
        curves.append(norm)
    return curves

def median_curve(curves):
    """Median decay curve across comparables"""
    if not curves:
        return [1.0] * 24
    n = min(len(c) for c in curves)
    med = []
    for i in range(n):
        vals = [c[i] for c in curves if i < len(c)]
        med.append(statistics.median(vals) if vals else 1.0)
    return med

def quantile_curves(curves, qs):
    """Quantile curves for each hour"""
    if not curves:
        return [[1.0]*5]*24
    n = min(len(c) for c in curves)
    result = []
    for i in range(n):
        vals = [c[i] for c in curves if i < len(c)]
        if not vals:
            result.append([1.0]*5)
            continue
        result.append([quantile(vals, q) for q in qs])
    return result

def diurnal_factors(history_hourly):
    """Extract hour-of-day factors from pre-launch history"""
    if not history_hourly:
        return [1.0]*24
    factors = {}
    for h in history_hourly:
        hr = h.get("hour", 0)
        if 1 <= hr <= 24:
            v = h.get("viewers", 0)
            if v > 0:
                factors.setdefault(hr, []).append(v)
    # Normalize to median
    med = statistics.median([statistics.median(v) for v in factors.values()]) if factors else 1
    return [statistics.median(factors.get(h, [med])) / med for h in range(1, 25)]

def forecast_case(case):
    if case["levels"] != LEVELS:
        raise ValueError(f"levels mismatch: {case['levels']} != {LEVELS}")
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError("no hour-1 print")
    p1 = max(1, first["viewers"])
    
    # Get comparable curves
    curves = extract_comparable_curves(case.get("comparables", []))
    med_curve = median_curve(curves)
    q_curves = quantile_curves(curves, LEVELS)
    
    # Diurnal adjustment from history
    diurnal = diurnal_factors(case.get("history_hourly", []))
    
    # Hour 1 stream concentration factor
    streams = case.get("streams", [])
    if streams:
        top_share = sum(s.get("viewers", 0) for s in streams[:5]) / max(1, sum(s.get("viewers", 0) for s in streams))
        conc_factor = 1 + (top_share - 0.3) * 0.5  # higher concentration = more volatile
    else:
        conc_factor = 1.0
    
    # GTA VI category history (pre-launch trend)
    gta_hist = [h for h in case.get("comparables", []) if h.get("name") == "Grand Theft Auto VI"]
    gta_trend = 1.0
    if gta_hist and gta_hist[0].get("hourly"):
        recent = gta_hist[0]["hourly"][-7:]  # last 7 hours
        if len(recent) >= 2:
            gta_trend = recent[-1].get("viewers", p1) / max(1, recent[0].get("viewers", p1))
    
    hours = []
    for row in case["forecast"]:
        h = row["hour"]
        idx = h - 1  # 0-indexed
        
        # Base prediction from median comparable curve
        base = med_curve[idx] if idx < len(med_curve) else med_curve[-1]
        
        # Quantile spread from comparable quantiles
        if idx < len(q_curves):
            qs = q_curves[idx]
        else:
            # Fallback: log-normal spread widening with sqrt(hour)
            sigma = 0.15 * conc_factor
            qs = [base * math.exp(z * sigma * math.sqrt(h - 1)) for z in Z]
        
        # Apply diurnal and GTA trend
        d = diurnal[idx] if idx < len(diurnal) else 1.0
        qs = [round2(q * d * gta_trend) for q in qs]
        
        # Ensure non-decreasing
        for i in range(1, 5):
            if qs[i] < qs[i-1]:
                qs[i] = qs[i-1]
        
        hours.append({"hour": h, "q": qs})
    
    return {"hours": hours}

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        fc = forecast_case(case)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(json.dumps(fc, separators=(",", ":")) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()