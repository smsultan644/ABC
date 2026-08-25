"""Generate charts used in the DOCX."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

from data import OPPS, PORTFOLIOS, SCENARIOS, ranked

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

NAVY = "#0B1F3A"
GOLD = "#C4A35A"
TEAL = "#1F6F6A"
SLATE = "#4A5568"
CREAM = "#F7F4EC"
RED = "#9B2C2C"
GREEN = "#276749"


def _style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": CREAM,
            "figure.facecolor": "white",
            "axes.edgecolor": NAVY,
            "axes.labelcolor": NAVY,
            "xtick.color": NAVY,
            "ytick.color": NAVY,
            "text.color": NAVY,
            "axes.titleweight": "bold",
        }
    )


def chart_top_scores():
    _style()
    top = ranked()[:12]
    labels = [o["name"][:38] for o in top][::-1]
    scores = [o["score"] for o in top][::-1]
    colors = [TEAL if o["cat"] == "A" else (GOLD if o["cat"] == "B" else SLATE) for o in top][::-1]
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.barh(labels, scores, color=colors, height=0.62)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Composite opportunity score (0–100)")
    ax.set_title("Highest-scoring opportunities under career-safe weights")
    ax.axvline(70, color=NAVY, ls="--", lw=0.8, alpha=0.5)
    for i, s in enumerate(scores):
        ax.text(s + 0.8, i, f"{s:.1f}", va="center", fontsize=8)
    from matplotlib.patches import Patch

    ax.legend(
        handles=[
            Patch(color=TEAL, label="A · Truly / near-passive"),
            Patch(color=GOLD, label="B · Semi-passive"),
            Patch(color=SLATE, label="C · Leveraged active"),
        ],
        loc="lower right",
        frameon=False,
        fontsize=8,
    )
    fig.tight_layout()
    p = OUT / "top_scores.png"
    fig.savefig(p, dpi=160)
    plt.close()
    return p


def chart_scenarios():
    _style()
    months = [6, 12, 24, 36]
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    specs = [
        ("conservative", TEAL, "Conservative (mid)"),
        ("balanced", GOLD, "Balanced (mid)"),
        ("aggressive", NAVY, "Aggressive-but-reasonable (mid)"),
    ]
    for key, color, lab in specs:
        s = SCENARIOS[key]
        mids = []
        lows, highs = [], []
        for k in ("income_m6", "income_m12", "income_m24", "income_m36"):
            a, b = s[k]
            lows.append(a / 1000)
            highs.append(b / 1000)
            mids.append(((a + b) / 2) / 1000)
        ax.plot(months, mids, marker="o", color=color, lw=2.2, label=lab)
        ax.fill_between(months, lows, highs, color=color, alpha=0.12)
    ax.set_xticks(months)
    ax.set_xticklabels(["6 mo", "12 mo", "24 mo", "36 mo"])
    ax.set_ylabel("Estimated monthly side income (BDT '000)")
    ax.set_title("Three scenarios — ranges, not promises")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    p = OUT / "scenarios.png"
    fig.savefig(p, dpi=160)
    plt.close()
    return p


def chart_portfolios():
    _style()
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.4))
    palettes = [
        ["#0B1F3A", "#1F6F6A", "#C4A35A", "#8AA6A3"],
        ["#0B1F3A", "#345B8C", "#C4A35A", "#1F6F6A"],
        ["#0B1F3A", "#1F6F6A", "#C4A35A", "#6B4F2A"],
    ]
    for ax, (key, pal) in zip(axes, zip(PORTFOLIOS.keys(), palettes)):
        pf = PORTFOLIOS[key]
        vals = [a[1] for a in pf["alloc"]]
        labels = [f"{a[1]}%" for a in pf["alloc"]]
        ax.pie(
            vals,
            colors=pal,
            startangle=90,
            wedgeprops=dict(width=0.48, edgecolor="white"),
            labels=labels,
        )
        ax.set_title(pf["name"], fontsize=8.5, pad=8)
    fig.tight_layout()
    p = OUT / "portfolios.png"
    fig.savefig(p, dpi=160)
    plt.close()
    return p


def chart_risk_heat():
    _style()
    items = [
        ("Career / independence breach", 2, 10),
        ("Confidentiality incident", 2, 10),
        ("Tax / forex non-compliance", 3, 8),
        ("Reputation event (public content)", 3, 7),
        ("Digital product failure to sell", 6, 3),
        ("Platform deplatforming", 4, 5),
        ("Investment market drawdown", 5, 5),
        ("Burnout / audit-quality slip", 4, 9),
        ("AI commoditises templates", 6, 4),
        ("Payment / payout friction", 5, 4),
    ]
    fig, ax = plt.subplots(figsize=(10.2, 6.0))
    for name, p, i in items:
        ax.scatter(p, i, s=220, c=GOLD if i < 7 else RED, zorder=3, edgecolors=NAVY)
        ax.text(p + 0.12, i + 0.12, name, fontsize=7.5)
    ax.set_xlim(0.5, 8)
    ax.set_ylim(1, 11)
    ax.set_xlabel("Probability (1–10)")
    ax.set_ylabel("Impact (1–10)")
    ax.set_title("Risk map — mitigate top-right first")
    ax.axhspan(7, 11, xmin=0.35, alpha=0.06, color=RED)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    p = OUT / "risk_heat.png"
    fig.savefig(p, dpi=160)
    plt.close()
    return p


def chart_week():
    _style()
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    hours = [0.75, 0.5, 0.5, 0.5, 0.5, 3.0, 5.5]
    fig, ax = plt.subplots(figsize=(10.2, 4.2))
    ax.bar(days, hours, color=[TEAL if h < 2 else GOLD if h < 4 else NAVY for h in hours])
    ax.set_ylabel("Hours")
    ax.set_title("Illustrative weekly execution load (busy-season cap: 4h)")
    for i, h in enumerate(hours):
        ax.text(i, h + 0.12, f"{h}h", ha="center", fontsize=8)
    ax.set_ylim(0, 7)
    fig.tight_layout()
    p = OUT / "weekly.png"
    fig.savefig(p, dpi=160)
    plt.close()
    return p


def chart_cover_bar():
    """Simple branded banner used on the cover."""
    fig, ax = plt.subplots(figsize=(11.2, 1.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(NAVY)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=NAVY))
    ax.add_patch(plt.Rectangle((0, 0), 0.018, 1, color=GOLD))
    ax.text(0.04, 0.55, "CONFIDENTIAL  ·  PERSONAL STRATEGIC ADVISORY  ·  NOT LEGAL, TAX OR INVESTMENT ADVICE",
            color="white", fontsize=9, va="center")
    p = OUT / "cover_bar.png"
    fig.savefig(p, dpi=160, facecolor=NAVY, bbox_inches="tight", pad_inches=0)
    plt.close()
    return p


def all_charts():
    return {
        "top": chart_top_scores(),
        "scenarios": chart_scenarios(),
        "portfolios": chart_portfolios(),
        "risk": chart_risk_heat(),
        "weekly": chart_week(),
        "cover_bar": chart_cover_bar(),
    }


if __name__ == "__main__":
    print(all_charts())
