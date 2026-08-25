"""Opportunity universe and scoring matrix."""
from __future__ import annotations

from data import BURDEN, CRITERIA_LABELS, OPPS, POSITIVE, WEIGHTS, ranked
from helpers import TEAL, add_image, bullets, callout, caption, h1, h2, h3, make_table, p, source_line


def universe(doc):
    h1(doc, "4.  Opportunity universe")
    p(
        doc,
        "Forty-five realistic options were evaluated. The list is intentionally broader than the final plan so that "
        "rejected ideas are rejected on the record, not forgotten and later revived in a weak moment. Each item is "
        "tagged with category (A/B/C) and permission class (1–5).",
        align="justify",
    )
    h2(doc, "4.1  Investment-based (mostly Category A)")
    p(
        doc,
        "Bangladesh still offers a usable, if imperfect, set of capital-market and deposit products for a salaried "
        "professional. Sovereign paper is the cleanest independence profile because the issuer is the government, "
        "not an audit client. Bank deposits are clean if the bank itself is not a restricted entity for you personally "
        "(confirm). Listed equities and many mutual funds are economically attractive and independence-dangerous: "
        "one holding in a restricted entity can become a reportable incident. REITs exist in rule form (BSEC Real "
        "Estate Investment Trust Fund Rules, 2024) but a liquid, high-quality listed REIT market for retail investors "
        "is not yet a core building block — treat as watch-list, not year-one allocation (inference from public BSEC "
        "coverage; verify current listings before buying).",
        align="justify",
    )
    h2(doc, "4.2  Knowledge and digital products (mostly Category B)")
    p(
        doc,
        "This is where an auditor’s comparative advantage is real: structuring numbers, designing controls, and "
        "explaining financial statements. The products that survive independence review are impersonal, original, "
        "and sold to a crowd (students, household CFOs, small traders), not to named companies. Anything that "
        "repackages firm methodology, ISA application guides used internally, or anonymised-but-recognisable client "
        "patterns is prohibited. ‘Audit workpaper templates’ are listed in the universe only to be scored poorly "
        "on confidentiality and reputation and then excluded from the recommended set.",
        align="justify",
    )
    h2(doc, "4.3  Content, education, technology, and leveraged services")
    p(
        doc,
        "Content is a distribution system for products, not a strategy by itself. YouTube and LinkedIn can work, "
        "but they are slow, public, and brand-sensitive — Class 3. Micro-SaaS can be a year-2 or year-3 project "
        "if the first products validate demand. Freelance marketplaces are scored because people in your position "
        "always ask; they fail the permission test.",
        align="justify",
    )
    rows = []
    for o in OPPS:
        rows.append(
            [
                o["id"],
                o["name"],
                o["family"],
                o["cat"],
                o["permission"],
                o["score"],
            ]
        )
    make_table(
        doc,
        ["#", "Opportunity", "Family", "Cat.", "Perm.", "Score"],
        rows,
        col_widths=[1.2, 8.2, 3.2, 1.4, 1.4, 1.6],
        font_size=8,
    )
    caption(doc, "Table 4.1  Full universe ranked later in Chapter 5. Cat. A/B/C = passivity class. Perm. 1–5 = permission class.")
    h2(doc, "4.4  Notes on a few frequently misunderstood items")
    h3(doc, "Cryptocurrency, forex, and CFDs")
    p(
        doc,
        "These are not in the investable universe. They fail financial-risk, reputation, and usually policy tests. "
        "Deloitte public independence materials in other member firms expressly treat digital assets as reportable "
        "financial relationships. Even if a local policy were silent, the reputational optics of an audit Senior "
        "Executive running a crypto or FX channel are unacceptable (opinion, informed by public Deloitte independence pages).",
        align="justify",
    )
    h3(doc, "International brokerage / US ETFs")
    p(
        doc,
        "Bangladesh remains a regulated foreign-exchange jurisdiction. Resident individuals cannot treat overseas "
        "brokerage as a casual click-and-buy activity. Some channels exist under specific Bangladesh Bank permissions "
        "(for example historically limited opportunities, RFCD/ERQ uses, or authorised outward remittance). This "
        "report does not assume you can lawfully fund a foreign brokerage. If a lawful channel opens, the economic "
        "case for a global equity index sleeve is strong — but only after FX legality and independence pre-clearance. "
        "Until then, international diversification is not part of the core plan (inference; confirm with your bank’s "
        "authorised dealer and current FE circulars).",
        align="justify",
    )
    h3(doc, "Teaching, ICAB tuition, and ‘CA coaching’")
    p(
        doc,
        "Intellectually adjacent and emotionally tempting. It is also outside employment, often evening-heavy, and "
        "sometimes involves firms’ clients’ staff as students. Class 3 at best. If approved, prefer recorded, "
        "impersonal courses over live coaching of people who work at audited entities.",
        align="justify",
    )


def scoring(doc, assets):
    h1(doc, "5.  Scoring methodology and quantitative matrix")
    p(
        doc,
        "Each opportunity is scored 1–10 on 24 criteria. Positive criteria (income, scalability, passivity, skill fit, "
        "feasibility, sustainability, automation, exit) are better when high. Burden and risk criteria are worse when "
        "high. The composite converts both types onto a 0–100 scale using explicit weights that privilege career safety.",
        align="justify",
    )
    h2(doc, "5.1  Formula")
    p(
        doc,
        "Let P be the set of positive criteria and B the set of burden/risk criteria. For criterion k with weight w_k "
        "and raw score r_k ∈ [1,10]:",
        align="justify",
    )
    p(
        doc,
        "S = Σ_{k∈P} w_k · (r_k / 10) · 100   +   Σ_{k∈B} w_k · ((11 − r_k) / 10) · 100",
        size=11,
        bold=True,
        color=TEAL,
        align="center",
    )
    p(
        doc,
        "Weights sum to 1.00. Employer-conflict and independence risk together carry 16% of the weight — more than "
        "income potential (10%). That is intentional. An 8/10 income idea with a 9/10 independence risk cannot outrank "
        "a 4/10 income idea with a 1/10 independence risk.",
        align="justify",
    )
    weight_rows = []
    for k, w in sorted(WEIGHTS.items(), key=lambda x: -x[1]):
        typ = "Positive" if k in POSITIVE else "Burden / risk"
        weight_rows.append([CRITERIA_LABELS[k], typ, f"{w:.2f}"])
    make_table(doc, ["Criterion", "Type", "Weight"], weight_rows, col_widths=[11.5, 3.2, 2.2], font_size=8)
    caption(doc, "Table 5.1  Scoring weights. Strategic opinion on relative importance, not a scientific law.")
    h2(doc, "5.2  How scores were set")
    bullets(
        doc,
        [
            "Capital: 1 = under ~BDT 10k to start; 10 = requires property-scale capital.",
            "Weekly time: 1 = under 30 minutes in steady state; 10 = a second job.",
            "Passivity: 10 = coupon/interest with annual admin; 1 = every hour billed.",
            "Skill fit: 10 = uses audit/reporting/Excel at a high level without using firm IP.",
            "BD / international feasibility: practical ability to operate and get paid from Bangladesh in 2026.",
            "Independence / employer / confidentiality / reputation: scored as an audit Senior Executive, not as a generic freelancer.",
            "Income potential: 10-year ceiling under competent execution, not a first-month fantasy.",
            "AI disruption: how easily a generic model plus a cheaper creator can erase the edge.",
        ],
    )
    p(
        doc,
        "Scores are structured estimates (estimate), internally consistent across the universe, and deliberately "
        "conservative on income and harsh on conflict. They are not market measurements.",
        align="justify",
    )
    h2(doc, "5.3  Ranked results")
    top = ranked()
    rows = []
    for i, o in enumerate(top, 1):
        rows.append(
            [
                i,
                o["name"],
                o["cat"],
                o["permission"],
                o["score"],
                o["income_potential"],
                o["passivity"],
                o["employer_conflict"],
                o["independence_risk"],
            ]
        )
    make_table(
        doc,
        ["Rank", "Opportunity", "Cat", "Perm", "Score", "Inc", "Pas", "Conf", "Ind"],
        rows,
        col_widths=[1.3, 7.4, 1.2, 1.3, 1.5, 1.2, 1.2, 1.2, 1.2],
        font_size=8,
    )
    caption(
        doc,
        "Table 5.2  Ranked universe. Inc = income potential; Pas = passivity; Conf = employer-conflict; Ind = independence risk (higher = worse).",
    )
    if assets.get("top"):
        add_image(doc, assets["top"], 16.8)
        caption(doc, "Figure 5.1  Top twelve composite scores.")

    h2(doc, "5.4  Split matrices (selected criteria)")
    p(doc, "Time, capital and income (higher capital/time/time-to-income = more demanding):", align="justify")
    rows = []
    for o in OPPS:
        rows.append([o["id"], o["name"][:32], o["capital"], o["setup_time"], o["weekly_time"], o["time_to_income"], o["income_potential"]])
    make_table(
        doc,
        ["#", "Opportunity", "Cap", "Setup", "Wk", "TTI", "Inc"],
        rows,
        col_widths=[1.1, 8.6, 1.5, 1.6, 1.4, 1.4, 1.4],
        font_size=7.5,
    )
    caption(doc, "Table 5.3  Capital and time burden versus income potential.")

    p(doc, "Professional-risk cluster (higher = worse):", align="justify")
    rows = []
    for o in OPPS:
        rows.append(
            [
                o["id"],
                o["name"][:30],
                o["employer_conflict"],
                o["independence_risk"],
                o["confidentiality_risk"],
                o["reputation_risk"],
                o["reg_complexity"],
            ]
        )
    make_table(
        doc,
        ["#", "Opportunity", "Emp", "Ind", "Confid", "Rep", "Reg"],
        rows,
        col_widths=[1.1, 8.2, 1.6, 1.6, 1.8, 1.5, 1.5],
        font_size=7.5,
    )
    caption(doc, "Table 5.4  Professional-risk scores.")

    p(doc, "Feasibility, durability and optionality (higher = better, except AI disruption):", align="justify")
    rows = []
    for o in OPPS:
        rows.append(
            [
                o["id"],
                o["name"][:28],
                o["bd_feasibility"],
                o["intl_feasibility"],
                o["sustainability"],
                o["automation"],
                o["exit_potential"],
                o["ai_disruption"],
            ]
        )
    make_table(
        doc,
        ["#", "Opportunity", "BD", "Intl", "Sust", "Auto", "Exit", "AI↓"],
        rows,
        col_widths=[1.1, 7.4, 1.4, 1.4, 1.5, 1.5, 1.4, 1.4],
        font_size=7.5,
    )
    caption(doc, "Table 5.5  Feasibility and durability. AI↓ = disruption risk (higher = more exposed).")

    h2(doc, "5.5  Reading the scores like an auditor")
    p(
        doc,
        "The top of the table is dominated by sovereign and deposit products — not because they will make you rich "
        "quickly, but because they are the only ideas that are simultaneously passive, lawful, and almost free of "
        "independence friction. Immediately below them sit original digital products with high skill fit and moderate "
        "conflict. The bottom of the table is not ‘bad businesses’; it is bad businesses for you. Direct SME retainers "
        "and Fiverr bookkeeping score poorly because they fail the constraint that matters most.",
        align="justify",
    )
    callout(
        doc,
        "Cut-off rule used later",
        "An idea cannot enter the recommended Top 10 if permission class is 5, or if independence risk ≥ 8 and "
        "employer-conflict ≥ 8. Class 4 ideas may appear only as explicit ‘do not start without written approval’ items.",
    )
