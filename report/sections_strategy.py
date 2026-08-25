"""Top 10, tiers, scenarios, portfolios, roadmap, weekly system."""
from __future__ import annotations

from data import PORTFOLIOS, SCENARIOS, USD_BDT
from helpers import add_image, bullets, callout, caption, h1, h2, h3, make_table, numbered, p


def top10(doc):
    h1(doc, "9.  Top 10 opportunities for this profile")
    p(
        doc,
        "The Top 10 is not ‘the ten highest raw scores’. It is the ten ideas that survive the cut-off rule, fit a "
        "6–10 hour week, and form a coherent portfolio. Class 4–5 service work is excluded even where income potential is high.",
        align="justify",
    )
    make_table(
        doc,
        ["#", "Opportunity", "Cat", "Why it survives"],
        [
            ["1", "Bangladesh Government T-bills & T-bonds", "A", "Sovereign, liquid enough, clean independence, current yields historically attractive vs cash"],
            ["2", "Bank DPS + selected FDR", "A", "Automation, tiny admin, builds the surplus habit"],
            ["3", "National Savings Certificates (right product, right limit)", "A", "Still useful after rate reform if the tenor matches your liquidity needs"],
            ["4", "Original Excel finance template studio", "B", "Best skill-to-asset conversion; impersonal sales"],
            ["5", "BD SME cash-flow & VAT workbooks (info, not advice)", "B", "Local differentiation AI cannot easily copy"],
            ["6", "Power BI / dashboard packs", "B", "Adjacent SKU once Excel catalogue sells"],
            ["7", "Household CFO kits (Bangla + English)", "B", "Lowest conflict digital product; volume play"],
            ["8", "Evergreen Excel course (after written approval)", "B", "Turns the same IP into a higher-ticket asset"],
            ["9", "Screened open-end mutual fund sleeve", "A", "Diversification after restricted-list process exists"],
            ["10", "AI / public-data calculator microsite (capped experiment)", "B", "Optional upside; hard capital and time cap"],
        ],
        font_size=8,
    )
    caption(doc, "Table 9.1  Recommended set. Items 8–10 are sequenced after 1–7, not parallel in month one.")

    details = [
        (
            "1. Treasury bills and bonds",
            "Fits because the issuer is the sovereign, not a corporate audit client. Better than a random FDR ladder "
            "because you can build a maturity schedule and, for bonds, collect coupons. Skills: you already understand "
            "accrual, dirty/clean price, and interest-rate risk — use them. Capital: from BDT 100,000 per ticket as "
            "commonly described. Tools: PD bank, BP ID. Timeline: account opening 1–3 weeks; first bill in month one "
            "after that. Income: yield snapshot ~10–11% in April 2026 (fact then; not a forecast). Risks: rate moves "
            "if you sell early; operational friction; withholding. Exit: hold to maturity or sell via PD. Automation: "
            "standing instructions and a calendar. First steps: pick one PD bank you do not audit; open BP ID; buy a "
            "364-day bill rather than stretching to 20 years.",
        ),
        (
            "2. DPS and selected FDR",
            "Fits as the plumbing of surplus capture. Better than ‘I’ll invest what’s left’ because it removes "
            "discretion. Capital: DPS can start very small. Time: one afternoon to open, then zero. Do not open "
            "seven bank relationships. Screen the bank against the restricted list if your policy requires it.",
        ),
        (
            "3. National Savings Certificates",
            "Still a legitimate sovereign product after the 2025 rate reset. Better than stretching into equities "
            "for money you cannot watch. Worse than T-bills if you need secondary-market flexibility. Read current "
            "limits so you do not over-concentrate or buy a product you are not eligible for.",
        ),
        (
            "4. Excel finance template studio",
            "This is the primary engine. Why it beats freelancing: no client, declining marginal time, exportable, "
            "and it uses the exact muscle you already train (structure, controls, documentation). Capital: BDT "
            "25,000–80,000 for domain, software, design, and payment setup. Time: 6–10 hours/week for 16 weeks to "
            "reach a five-SKU catalogue. First income: often month 4–8 if you actually ship and distribute; can be "
            "longer. Risks: marketplace noise, AI copycats, payout friction, the temptation to offer customisation "
            "(do not). Exit: the catalogue is a sellable digital asset. Automation: checkout, email delivery, help "
            "docs, once-a-quarter update cycle.",
        ),
        (
            "5. BD SME cash-flow and VAT workbooks",
            "Same studio, localised SKUs. The problem you solve is not ‘Excel looks pretty’; it is ‘a trader cannot "
            "see cash next month and is frightened of Mushak’. Position as an information tool with a thick disclaimer. "
            "Never complete a return for a customer.",
        ),
        (
            "6. Power BI / dashboard packs",
            "A second catalogue once Excel SKUs sell. Higher technical difficulty, smaller but higher-paying audience. "
            "Do not start here — start where you can finish a product in two weekends.",
        ),
        (
            "7. Household CFO kits",
            "Bangla-first household budgets, debt snowballs, and wedding/hajj sinking funds. Low independence risk, "
            "high competition, useful as a volume and brand-safe line. Good experimental SKU.",
        ),
        (
            "8. Evergreen Excel course",
            "Only after written approval. Why it is better than live workshops: it is an asset. Why it is later: "
            "filming is a time sink and the brand is public. Use the templates as the course files so you do not "
            "build twice.",
        ),
        (
            "9. Screened open-end mutual funds",
            "Useful once you have a restricted-entity process and an emergency fund. Not a year-one core if you "
            "cannot see the fund’s underlying names. Prefer income/balanced funds with transparent portfolios over "
            "opaque thematic products.",
        ),
        (
            "10. Calculator / public-data microsite",
            "A capped experiment (money cap BDT 40,000, time cap 40 hours) to test whether Bangladesh-specific "
            "calculators attract organic traffic. If it does not move by hour 40, archive it. If it does, it can "
            "become a lead engine for the template studio.",
        ),
    ]
    for title, body in details:
        h3(doc, title)
        p(doc, body, align="justify")


def tiers(doc):
    h1(doc, "10.  Tiered recommendation")
    h2(doc, "Tier 1 — Start in the next 90 days (low/moderate capital, manageable time, low risk)")
    bullets(
        doc,
        [
            "Policy read + clearance packet for the digital studio.",
            "Emergency cash (3 months of essential personal expenses) in a deposit you can break.",
            "First sovereign purchase (T-bill or eligible NSC) and one DPS mandate.",
            "Two original templates shipped (one household, one SME cash-flow).",
            "Payment rail tested with a real BDT sale and, if possible, one foreign test purchase.",
        ],
    )
    h2(doc, "Tier 2 — Strategic medium-term (months 3–12)")
    bullets(
        doc,
        [
            "Catalogue of 8–12 SKUs including one VAT information workbook and one dashboard.",
            "Own-site checkout plus one marketplace experiment.",
            "If approved: film a short Excel course from the same files.",
            "T-bill/T-bond ladder with at least three maturities.",
            "Documented restricted-entity process before any mutual fund or equity.",
        ],
    )
    h2(doc, "Tier 3 — Long-term wealth (years 2–3)")
    bullets(
        doc,
        [
            "Automatic surplus: 15–25% of take-home into the sovereign/DPS sleeve every payday.",
            "Digital assets on a quarterly update cadence, not a weekly content treadmill.",
            "Only then consider: a larger screened fund sleeve, a lawful foreign diversification channel if one exists, or a professionally managed rental if capital and approval allow.",
            "Explicit non-goals for year 1–3: agency, staff, office, SME retainers, leveraged property.",
        ],
    )
    callout(
        doc,
        "Why this beats ‘just invest more’ and ‘just freelance’",
        "Invest-more is correct for the wealth engine and insufficient as a skill-monetisation plan. Freelance is "
        "correct for cash speed and incorrect for a Big Four auditor. The tiering keeps both truths.",
    )


def scenarios(doc, assets):
    h1(doc, "11.  Three financial scenarios")
    p(
        doc,
        "These are planning ranges (estimate). They assume you keep your job, do not use leverage, and accept that "
        "digital revenue can be zero for long stretches. They are not promises. USD figures use ~BDT 122 / USD.",
        align="justify",
    )
    rows = []
    order = ["conservative", "balanced", "aggressive"]
    labels = [SCENARIOS[k]["label"] for k in order]
    headers = ["Item"] + labels
    keys = [
        ("Initial capital (BDT)", "initial_capital_bdt"),
        ("Monthly contribution (BDT)", "monthly_contrib_bdt"),
        ("Weekly time", "hours_week"),
        ("Income after 6 months (BDT/mo)", "income_m6"),
        ("Income after 12 months (BDT/mo)", "income_m12"),
        ("Income after 24 months (BDT/mo)", "income_m24"),
        ("Income after 36 months (BDT/mo)", "income_m36"),
        ("Potential year-3 total (BDT)", "annual_y3"),
        ("Invested-sleeve note", "blend_yield"),
    ]
    for label, key in keys:
        row = [label]
        for k in order:
            val = SCENARIOS[k][key]
            if isinstance(val, tuple):
                row.append(f"{val[0]:,} – {val[1]:,}")
            elif isinstance(val, int):
                row.append(f"{val:,}")
            else:
                row.append(str(val))
        rows.append(row)
    make_table(doc, headers, rows, font_size=8)
    caption(doc, "Table 11.1  Scenario dashboard. ‘Income’ means combined side-activity cash flow plus investment coupons/interest received, not mark-to-market.")
    if assets.get("scenarios"):
        add_image(doc, assets["scenarios"], 16.8)
        caption(doc, "Figure 11.1  Scenario bands.")

    h2(doc, "11.1  Conservative — low regret")
    p(
        doc,
        "You treat the side activity as a Saturday craft and the investment sleeve as the real story. Digital "
        "products may earn little in year one; you still win if the DPS/T-bill machine is on. Major risks: boredom "
        "and abandoning the surplus habit. Key assumption: you actually buy the first T-bill and do not leave the "
        "BDT 150,000 in a current account.",
        align="justify",
    )
    h2(doc, "11.2  Balanced — the intended path")
    p(
        doc,
        "Enough capital to ladder government paper and enough time to ship a real catalogue. Year-two income is "
        "still modest by Big Four salary standards; that is acceptable. Major risks: scope creep into custom work; "
        "busy-season collapse; spending too long on branding. Key assumption: two shipped products by month 4 and "
        "no Class 4 activity.",
        align="justify",
    )
    h2(doc, "11.3  Aggressive-but-reasonable — still legitimate")
    p(
        doc,
        "More capital in the sovereign ladder and a faster catalogue/course build. It is not ‘aggressive’ in the "
        "sense of options, margin, or crypto. It is aggressive only relative to time and savings rate. Major risks: "
        "burnout and a public-brand mis-step if you rush YouTube/courses without approval. Hard cap: if audit "
        "reviews slip, this scenario is automatically downgraded.",
        align="justify",
    )
    p(
        doc,
        f"Illustrative USD translation of year-3 annual ranges at BDT {USD_BDT:.0f}/USD (estimate): "
        f"conservative ~USD 2.3k–5.3k; balanced ~USD 5.3k–13.9k; aggressive-but-reasonable ~USD 10.7k–27.9k. "
        f"These are small relative to a Senior Executive career path — and that is the point. The job remains the "
        f"main engine. The side system is optional convexity plus a compounding stack of government paper.",
        align="justify",
    )


def portfolios(doc, assets):
    h1(doc, "12.  Passive-income portfolio models")
    p(
        doc,
        "Allocation here means allocation of new surplus (money and, separately, hours), not a mark-to-market "
        "portfolio weight you must rebalance weekly. Hours cannot be 70% T-bills — T-bills take almost no hours. "
        "Money should not be 70% experimental SaaS.",
        align="justify",
    )
    if assets.get("portfolios"):
        add_image(doc, assets["portfolios"], 17.0)
        caption(doc, "Figure 12.1  Three money-allocation models.")
    for key, blurb in [
        (
            "career_first",
            "Default for the first 12 months and for any period when independence clearance is still pending. "
            "Almost all money goes to sovereign and deposit products. A thin slice funds the studio so the skill "
            "asset still gets built. Hours, by contrast, are 70% studio and 30% admin/learning — the opposite of the money split.",
        ),
        (
            "builder",
            "Use once the first products have sold and written approval (if required) is in hand. More hours go to "
            "a course and a calculator experiment. A small screened-fund sleeve is allowed only after a restricted-list process.",
        ),
        (
            "asset",
            "A year-2/3 tilt if the digital assets are producing recurring sales. Still no leverage. The 10% ‘rental "
            "reserve’ is a sinking fund, not a mandate to buy a flat. If Dhaka property does not clear a conservative "
            "yield-and-liquidity test, that 10% stays in T-bonds.",
        ),
    ]:
        pf = PORTFOLIOS[key]
        h2(doc, pf["name"])
        p(doc, blurb, align="justify")
        make_table(
            doc,
            ["Sleeve", "Share of new money"],
            [[a, f"{b}%"] for a, b in pf["alloc"]],
            col_widths=[13.5, 3.5],
        )
    h3(doc, "Hour allocation (all models, off-peak week of ~8 hours)")
    make_table(
        doc,
        ["Activity", "Hours", "Notes"],
        [
            ["Deep product build / update", "4.0", "Saturday block; non-negotiable if shipping"],
            ["Distribution (SEO, marketplace, email)", "1.5", "Not scrolling; scheduled posts and listings"],
            ["Investment admin / learning FE & tax changes", "0.5", "Monthly in practice, shown as weekly average"],
            ["Support / storefront hygiene", "0.5", "Canned responses; FAQ first"],
            ["Buffer / rest", "1.5", "If unused, do not fill with new projects"],
        ],
    )
    caption(doc, "Table 12.2  Hours are the scarce resource. Protect the buffer.")


def roadmap(doc):
    h1(doc, "13.  Three-year roadmap (2026–2029)")
    h2(doc, "Month 0–3  ·  Foundation")
    p(doc, "Hours/week: 6–8. Capital: BDT 25,000 operating + first sovereign ticket (from the 150–400k pool).", align="justify")
    bullets(
        doc,
        [
            "Read local independence / OBA / social-media / personal-trading policies. Write the one-page clearance packet.",
            "Open PD-bank pathway and BP ID; start DPS; park emergency fund.",
            "Personal tech hygiene: personal laptop, personal cloud, password manager, no firm files.",
            "Brand skeleton: name, domain, simple landing page, disclaimer, privacy note.",
            "Ship Template 1 (Household CFO) and Template 2 (13-week cash-flow).",
            "Test one live checkout path.",
        ],
    )
    p(doc, "KPIs: policies read (Y/N); approval submitted (Y/N); 2 SKUs live; 1 successful payout test; first T-bill/NSC bought.", align="justify")
    p(doc, "Revenue target: BDT 0–15,000 (nice if it happens; not the point). Stop doing: channel research beyond two storefronts; logo obsession; YouTube.", align="justify")
    h2(doc, "Month 4–6  ·  Validation")
    p(doc, "Hours/week: 7–9. Capital: another BDT 15–40,000 if listings need design/ads tests (capped).", align="justify")
    bullets(
        doc,
        [
            "Ship Templates 3–5 (VAT information workbook, personal net-worth, simple management-accounts pack).",
            "Ten customer conversations (even if they do not buy). Record objections.",
            "One distribution experiment with a hard stop: e.g., 20 targeted Facebook/Instagram posts or 15 marketplace listings — not both plus YouTube.",
            "Extend the sovereign ladder to a second tenor.",
        ],
    )
    p(doc, "KPIs: ≥5 SKUs; ≥10 genuine conversations; ≥5 paid orders or a documented reason why not; support tickets <30 minutes/week.", align="justify")
    p(doc, "Decision gate: if zero sales and zero wait-list after 5 SKUs and real distribution, narrow the niche or pause paid tools. Do not ‘add a SaaS’.", align="justify")
    h2(doc, "Month 7–12  ·  Scale (still small)")
    p(doc, "Hours/week: 7–10 off-peak; 0–4 in busy season. Capital: operating costs only plus regular surplus into paper.", align="justify")
    bullets(
        doc,
        [
            "Catalogue 8–12 SKUs. Quarterly update calendar aligned to the Finance Act cycle.",
            "If approval received: outline and film a 90-minute Excel course — no more.",
            "Introduce a simple email list (owned audience).",
            "Write an Investment Policy Statement for yourself (see Chapter 21, plan 2).",
            "First-year tax file: separate folder, complete by August/September so November filing is boring.",
        ],
    )
    p(doc, "Revenue target (estimate): conservative 8–18k BDT/month by month 12; balanced 18–45k. Scale what converted; kill SKUs with no sales and no learning.", align="justify")
    h2(doc, "Year 2  ·  Automation and diversification")
    bullets(
        doc,
        [
            "Move from ‘making products’ to ‘maintaining a catalogue’: help docs, versioning, changelog.",
            "One calculator or public-data experiment, time-boxed.",
            "Screened mutual-fund sleeve only if the process is clean.",
            "No staff. Contract a designer for 10 hours if needed, not a co-founder.",
            "Busy-season protocol written and actually used.",
        ],
    )
    p(doc, "Milestone: a month where sales occur while you do almost no new creation.", align="justify")
    h2(doc, "Year 3  ·  Asset-building and optimisation")
    bullets(
        doc,
        [
            "Sovereign ladder is the largest financial asset you have built outside CPF/provident/employer savings.",
            "Digital assets either throw off royalties worth keeping (keep) or they do not (sunset politely).",
            "Revisit lawful international diversification only if FX rules and independence allow.",
            "Revisit property only with a written yield model and a property manager — not as a side-hustle landlord.",
            "Decision: double down, maintain, or sell the digital catalogue. Do not drift.",
        ],
    )
    make_table(
        doc,
        ["Phase", "Hours/wk", "Capital focus", "Kill if…", "Scale if…"],
        [
            ["0–3 mo", "6–8", "Rails + first paper + 2 SKUs", "You skip policy work", "Checkout works"],
            ["4–6 mo", "7–9", "SKU depth", "No conversations", "Repeat buyers or clear demand signal"],
            ["7–12 mo", "7–10", "Course (if approved) + ladder", "Custom-work creep", "Email list + repeatable sales"],
            ["Year 2", "5–8", "Automation + screened funds", "It becomes a second job", "Sales without weekly creation"],
            ["Year 3", "4–7", "Compound + optional real asset", "Career friction appears", "Royalties + coupons cover a meaningful bill"],
        ],
        font_size=8,
    )
    caption(doc, "Table 13.1  Phase gates.")


def weekly(doc, assets):
    h1(doc, "14.  Weekly execution system")
    p(
        doc,
        "The system is designed around a Dhaka audit week: unpredictable weekday evenings, a slightly lighter Friday, "
        "and a Saturday that must also contain rest and a life. Sunday–Thursday are maintenance only.",
        align="justify",
    )
    if assets.get("weekly"):
        add_image(doc, assets["weekly"], 16.4)
        caption(doc, "Figure 14.1  Illustrative off-peak week (~11 hours shown; target 7–9 by cutting Friday if needed).")
    make_table(
        doc,
        ["Day", "Window", "Work", "Hard stop"],
        [
            ["Sun–Thu", "30–45 min, after dinner", "Inbox, one listing tweak, flash-card learning, or nothing", "No new product features on weeknights"],
            ["Friday", "2–3 hours", "Admin: payouts, books, policy notes, light editing", "Stop if a client deadline slipped"],
            ["Saturday", "4–6 hours, morning", "The only deep-work block: build or update one asset", "End by mid-afternoon; rest is a control"],
            ["Busy season", "0–4 hours/week", "Only storefront fire-fighting and coupon collection", "Products freeze; auto-responders on"],
        ],
        font_size=8,
    )
    h2(doc, "14.1  Burnout and audit-quality controls")
    numbered(
        doc,
        [
            "A red-flag rule: if you work past midnight twice in a week on side activity, Saturday is cancelled.",
            "A second red-flag rule: any review note that mentions inattention or a restatement risk pauses the studio for two weeks.",
            "Sleep is a professional control, not a lifestyle accessory.",
            "One hobby that is not monetised must remain on the calendar.",
            "Quarterly ‘stop-doing’ review: list projects and kill one.",
        ],
    )
    h2(doc, "14.2  A standing Saturday agenda")
    bullets(
        doc,
        [
            "30 min: last week’s numbers (sales, hours, errors, mood).",
            "3–4 hours: single WIP item from a written list of three. No new ideas allowed into the list until one leaves.",
            "30 min: ship or schedule (listing, changelog, email).",
            "10 min: write Monday’s 30-minute task so weeknights do not require willpower.",
        ],
    )
    callout(
        doc,
        "The real weekly KPI",
        "Shipped increments and protected sleep beat ‘hours worked on the side hustle’. If you remember one operating "
        "rule, remember that.",
    )
