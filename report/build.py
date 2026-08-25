#!/usr/bin/env python3
"""Assemble the professional DOCX report."""
from __future__ import annotations

from pathlib import Path

from charts import all_charts
from helpers import setup_document
from sections_compliance import deloitte, platforms, tax_legal
from sections_front import context, cover, disclaimers, executive_summary, framework, toc
from sections_opps import scoring, universe
from sections_ops import ai_strategy, avoid, decision, risk, tech, ten_ideas
from sections_plans import blueprint, financials, kpi, qc, sources, three_plans
from sections_strategy import portfolios, roadmap, scenarios, tiers, top10, weekly

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Strategic-Passive-Income-Wealth-Building-Blueprint-2026-2029.docx"


def main():
    assets = all_charts()
    doc = setup_document()
    cover(doc, assets)
    disclaimers(doc)
    toc(doc)
    executive_summary(doc, assets)
    context(doc)
    framework(doc)
    universe(doc)
    scoring(doc, assets)
    deloitte(doc)
    tax_legal(doc)
    platforms(doc)
    top10(doc)
    tiers(doc)
    scenarios(doc, assets)
    portfolios(doc, assets)
    roadmap(doc)
    weekly(doc, assets)
    tech(doc)
    ai_strategy(doc)
    avoid(doc)
    risk(doc, assets)
    decision(doc)
    ten_ideas(doc)
    three_plans(doc)
    financials(doc)
    kpi(doc)
    blueprint(doc)
    sources(doc)
    qc(doc)
    doc.save(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
