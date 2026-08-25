"""Cover through passive-income framework."""
from __future__ import annotations

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

from helpers import (
    GOLD,
    NAVY,
    SLATE,
    TEAL,
    add_image,
    bullets,
    callout,
    caption,
    h1,
    h2,
    h3,
    numbered,
    p,
    page_break,
    set_run_font,
    source_line,
)


def cover(doc, assets):
    # Hide header content feel on cover by extra space
    if assets.get("cover_bar"):
        add_image(doc, assets["cover_bar"], 17.4)
    p(doc, "DELOITTE BANGLADESH  ·  AUDIT & ASSURANCE  ·  SENIOR EXECUTIVE", size=10, color=TEAL, bold=True, space_after=14, space_before=18)
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(6)
    r = para.add_run("Strategic Passive Income &\nWealth-Building Blueprint")
    set_run_font(r, name="Calibri", size=28, bold=True, color=NAVY)
    p(doc, "for a Deloitte Bangladesh Audit Professional", size=16, color=TEAL, bold=True, space_after=8)
    p(doc, "2026–2029  ·  Version 1.0  ·  August 2026", size=13, color=NAVY, space_after=16)
    p(
        doc,
        "A professionally constrained, legally grounded, and execution-ready roadmap for building "
        "legitimate recurring income and long-term capital — without compromising independence, "
        "confidentiality, employment obligations, or audit quality.",
        size=12,
        italic=True,
        align="justify",
        space_after=18,
    )
    bullets(
        doc,
        [
            "Prepared as personal strategic advisory — not a solicitation, not a product offering, and not client advice.",
            "Primary currency: Bangladeshi Taka (BDT). USD conversions use an estimated mid-market rate of ~BDT 122 per USD (August 2026) and are labelled as estimates.",
            "Where Deloitte Bangladesh internal policy cannot be verified from public sources, this report requires you to confirm the applicable Independence / Outside Business Activity process before acting.",
        ],
    )
    p(doc, "Classification", size=10, bold=True, color=NAVY, space_before=16, space_after=2)
    p(doc, "Confidential — intended solely for the named professional’s personal planning.", size=11)
    p(doc, "Evidence standard", size=10, bold=True, color=NAVY, space_before=8, space_after=2)
    p(
        doc,
        "Every material legal, tax, or market claim is tagged as verified fact, reasonable inference, estimate, or strategic opinion. Sources are listed in the final chapter.",
        size=11,
        align="justify",
    )
    page_break(doc)


def disclaimers(doc):
    h1(doc, "Important disclaimers")
    p(
        doc,
        "This document is a personal research and planning memorandum. It is not legal advice, tax advice, "
        "investment advice, an offer to sell securities, or a substitute for Deloitte’s internal independence, "
        "ethics, or employment-policy processes. Nothing in this report authorises outside employment, client "
        "service, or the use of firm intellectual property.",
        align="justify",
    )
    h3(doc, "What this report will not do")
    bullets(
        doc,
        [
            "It will not promise returns, ‘passive income in 30 days’, or a replacement for your salary.",
            "It will not treat a technically possible idea as professionally permissible.",
            "It will not invent Deloitte Bangladesh handbook clauses that cannot be verified publicly.",
            "It will not recommend leveraged FX, binary options, unregulated platforms, MLM, or signal-selling.",
            "It will not provide a filing-ready tax computation or a formal independence clearance.",
        ],
    )
    h3(doc, "What you must do before implementing anything beyond personal bank deposits")
    numbered(
        doc,
        [
            "Read the current Deloitte Bangladesh / member-firm independence, conflicts, outside-business-activity, personal-trading, social-media, and confidentiality policies (intranet / Independence & Conflicts Network).",
            "Pre-clear or report financial interests, outside activities, teaching, content monetisation, and any business ownership as required by those policies.",
            "Confirm restricted-entity status before buying any security, fund, or corporate bond, and before providing any service or training to an organisation.",
            "Take Bangladesh tax and, if relevant, foreign-exchange advice from an independent practitioner who is not in a conflict with your employment (or use the firm’s designated personal-tax channel if one exists).",
            "Keep all side activity off firm devices, off client data, and outside working hours, unless a written policy says otherwise.",
        ],
    )
    callout(
        doc,
        "Non-negotiable objective function",
        "Maximise long-term, professionally defensible wealth subject to: (1) zero independence breaches, "
        "(2) zero confidentiality breaches, (3) no degradation of audit quality, and (4) sustainable weekly hours. "
        "Income maximisation is subordinate to career preservation.",
    )
    page_break(doc)


def toc(doc):
    h1(doc, "Contents")
    items = [
        "1.  Executive summary",
        "2.  Professional-context assumptions",
        "3.  Passive-income framework and classification rules",
        "4.  Opportunity universe (45 options)",
        "5.  Scoring methodology and quantitative matrix",
        "6.  Deloitte, independence, and professional-conduct analysis",
        "7.  Bangladesh legal, tax, and foreign-exchange considerations",
        "8.  International platforms and payment rails",
        "9.  Top 10 opportunities for this profile",
        "10. Tiered recommendation (immediate / medium-term / wealth)",
        "11. Three financial scenarios (conservative / balanced / aggressive-but-reasonable)",
        "12. Passive-income portfolio models",
        "13. Three-year roadmap (2026–2029)",
        "14. Weekly execution system and burnout controls",
        "15. Technology stack",
        "16. AI-leveraged asset strategy",
        "17. Opportunities to avoid at all costs",
        "18. Risk-management framework",
        "19. Reusable decision formula",
        "20. Ten concrete business concepts",
        "21. Three mini business plans",
        "22. Financial models and sensitivity",
        "23. KPI dashboard",
        "24. My recommended passive income blueprint",
        "25. Sources and references",
        "26. Quality-control checklist and document control",
    ]
    for it in items:
        p(doc, it, size=11, space_after=3, color=NAVY)
    p(
        doc,
        "Word/LibreOffice users: heading styles are applied throughout so an automatic table of contents can be refreshed if desired.",
        size=9,
        italic=True,
        space_before=10,
    )
    page_break(doc)


def executive_summary(doc, assets):
    h1(doc, "1.  Executive summary")
    p(
        doc,
        "You are a Senior Executive in Audit & Assurance at Deloitte Bangladesh. That fact is not background colour — "
        "it is the binding constraint. The highest-value ‘passive income’ programme for you is the one that can run "
        "for a decade without creating an independence incident, a confidentiality issue, a moonlighting breach, or "
        "a tired auditor in peak season. Everything in this blueprint is filtered through that constraint first, and "
        "through return potential second.",
        align="justify",
    )
    h2(doc, "The short answer")
    p(
        doc,
        "Build a four-engine system. Do not chase a single viral idea. Do not freelance accounting. Do not sell "
        "anything that looks like audit methodology, client workpapers, or ‘Deloitte-quality’ advice.",
        align="justify",
    )
    bullets(
        doc,
        [
            "Primary engine (semi-passive): an original digital-product studio — Excel / Power BI / SME finance templates and calculators sold impersonally under your own brand. Highest skill fit, modest capital, scalable, and controllable conflict if you stay generic.",
            "Secondary engine (semi-passive after a library exists): an evergreen Excel / financial-literacy course and a tightly scoped public-education channel. Teaching and public branding should be pre-cleared in writing.",
            "Wealth engine (truly passive): a Bangladesh sovereign-and-deposit ladder — Treasury bills and bonds, National Savings Certificates where still suitable, DPS, and high-quality bank deposits — funded by salary surplus. This is the compounding core.",
            "Experimental engine (small, capped capital): one AI-assisted Bangladesh calculator or public-data microsite. Treat it as a product experiment, not a second job.",
        ],
    )
    h2(doc, "What not to do")
    p(
        doc,
        "Do not open an SME accounting practice, take Upwork audit/tax gigs, sell firm-derived workpapers, trade "
        "restricted entities, run a signal or forex Telegram, or become a director of a client or prospective client. "
        "Those paths fail the career-preservation test even if they can pay faster in year one.",
        align="justify",
    )
    h2(doc, "Capital, time, and honest income ranges")
    p(
        doc,
        "All figures below are modelling ranges (estimate), not forecasts. They assume you keep a demanding full-time "
        "audit role, protect busy season, and do not use leverage.",
        align="justify",
    )
    from helpers import make_table

    make_table(
        doc,
        ["Horizon", "Conservative", "Balanced", "Aggressive-but-reasonable"],
        [
            ["Starting capital", "BDT 150,000", "BDT 400,000", "BDT 1,000,000"],
            ["Monthly surplus deployed", "BDT 15,000", "BDT 30,000", "BDT 50,000"],
            ["Weekly hours (off-peak)", "5–7", "7–10", "10–14"],
            ["Side income, month 12", "8–18k BDT/mo", "18–45k BDT/mo", "30–80k BDT/mo"],
            ["Side income, month 36", "22–50k BDT/mo", "50–130k BDT/mo", "100–280k BDT/mo"],
            ["Year-3 total (invest + side)", "0.28–0.65m BDT", "0.65–1.7m BDT", "1.3–3.4m BDT"],
        ],
    )
    caption(doc, "Table 1.1  Scenario ranges. Mid-points are not targets. Downside can be near-zero digital revenue in year one.")
    if assets.get("scenarios"):
        add_image(doc, assets["scenarios"], 16.8)
        caption(doc, "Figure 1.1  Scenario bands for estimated monthly side income (BDT thousands).")
    h2(doc, "Why this mix beats the obvious alternatives")
    p(
        doc,
        "A pure investment programme is truly passive and independence-clean if you stay in government paper and "
        "screened deposits — but it will not, by itself, create a scalable asset. A pure freelance programme can "
        "earn faster and will almost certainly violate outside-employment and independence rules. Digital products "
        "sit in the narrow band where your Excel, reporting, and control-design skill is scarce, the product can "
        "sell while you sleep, and you never have to take a client. That is the only combination that is both "
        "scalable and professionally defensible for a Big Four auditor.",
        align="justify",
    )
    callout(
        doc,
        "Decision already made by this report",
        "Start this month with (1) a written policy check, (2) an emergency-fund + sovereign investment sleeve, "
        "and (3) the first two original templates. Do not start a YouTube channel, an agency, or a brokerage account "
        "in individual stocks until the first two items are done.",
    )


def context(doc):
    h1(doc, "2.  Professional-context assumptions")
    p(
        doc,
        "The recommendations are calibrated to the following working assumptions. If any assumption is wrong, "
        "re-run the decision framework in Chapter 19 rather than forcing the same plan.",
        align="justify",
    )
    h2(doc, "2.1  Role and constraints")
    bullets(
        doc,
        [
            "Employer: Deloitte Bangladesh (Deloitte Touche Tohmatsu member-firm network). Public independence materials of Deloitte member firms are used as a guide only; local policy governs.",
            "Function: Audit & Assurance, Senior Executive — a client-facing, independence-sensitive grade.",
            "Skills that transfer legally: financial reporting, audit logic, internal control design, Excel/modelling, taxation literacy, documentation discipline, professional writing.",
            "Skills that do not transfer: client facts, firm methodology, workpapers, proprietary checklists, non-public information, the Deloitte brand.",
            "Time: limited weekday capacity; Friday afternoon and Saturday are the only realistic deep-work blocks. Busy-season weeks may offer zero surplus hours.",
            "Capital: limited to moderate. The plan must work at BDT 150,000 and still make sense at BDT 1,000,000.",
            "Preference: scalable assets over selling hours. Long-term compounding over speculative spikes.",
            "Geography: resident of Bangladesh for tax and foreign-exchange purposes (assumed). Worldwide income is therefore generally taxable in Bangladesh (verified principle of residence taxation; confirm status each year).",
        ],
    )
    h2(doc, "2.2  What ‘success’ means in this context")
    p(
        doc,
        "Success is not a particular monthly number. Success is: (a) your Deloitte performance and licence-track "
        "remain unimpaired; (b) you hold a growing stock of lawful financial assets; (c) you own at least one "
        "digital asset that can produce royalties with declining marginal time; and (d) you could pause the side "
        "activity for eight weeks in audit peak season without the system collapsing.",
        align="justify",
    )
    h2(doc, "2.3  Five permission classes used throughout")
    from helpers import make_table

    make_table(
        doc,
        ["Class", "Meaning", "Examples", "Action rule"],
        [
            ["1", "Generally permissible personal activity", "FDR, T-bills, household budget templates", "Proceed; still disclose income on tax return"],
            ["2", "Usually acceptable if generic and original", "Excel template shop, public-data site", "Document originality; no client material; monitor policy"],
            ["3", "Potentially restricted — written approval", "Teaching, YouTube brand, mutual funds, listed stocks", "Do not start until cleared / reported"],
            ["4", "High conflict", "Freelance modelling, corporate training to companies", "Default is no; only with formal written approval and restricted-entity screen"],
            ["5", "Avoid", "SME retainers, audit-client work, selling workpapers, FX signals", "Do not pursue while at the firm"],
        ],
    )
    caption(doc, "Table 2.1  Permission classes. Classes are a strategic framework (opinion), not a legal opinion on your contract.")
    h2(doc, "2.4  Time budget that the rest of the plan respects")
    p(
        doc,
        "A Senior Executive who tries to run a 20-hour side hustle will fail twice: the side hustle will be mediocre "
        "and the audit work will eventually show it. The operating budget used in this report is 6–10 hours in a "
        "normal week, 0–4 hours in a busy-season week, and one Saturday deep-work block. If that budget is "
        "violated for more than three consecutive weeks, the plan requires you to pause product work, not audit work.",
        align="justify",
    )


def framework(doc):
    h1(doc, "3.  Passive-income framework")
    p(
        doc,
        "‘Passive income’ is one of the most abused phrases in retail finance. For this report it has a precise "
        "meaning: income that continues, within a defined band, after the originating labour has largely stopped. "
        "Interest on a Treasury bill is passive. A Saturday bookkeeping client is not. A recorded Excel course that "
        "still needs weekly community management is semi-passive. Honesty about category prevents you from building "
        "a second job and calling it an asset.",
        align="justify",
    )
    h2(doc, "3.1  Category A — Truly passive")
    p(
        doc,
        "Cash flows arrive because capital, not ongoing labour, is at work. Ongoing effort is limited to occasional "
        "rebalancing, tax reporting, and policy/independence checks. Examples that actually exist for a Bangladeshi "
        "resident: bank interest, National Savings profit, T-bill accretion, T-bond coupons, screened mutual-fund "
        "distributions, and (later) rental yield if the property is professionally managed. Royalties from a finished "
        "book or template can become Category A only after the catalogue is large and marketing is automated; until "
        "then they are Category B.",
        align="justify",
    )
    h2(doc, "3.2  Category B — Semi-passive")
    p(
        doc,
        "A front-loaded build (typically 80–250 hours) creates an asset that then requires light maintenance "
        "(1–5 hours a week): updates for a Finance Act change, customer support, and occasional new SKUs. This is "
        "the correct home for digital products, evergreen courses, calculator sites, and most content libraries. "
        "Semi-passive is the highest-quality category available to a skilled professional who does not yet have "
        "investable capital in the millions of taka.",
        align="justify",
    )
    h2(doc, "3.3  Category C — Leveraged active")
    p(
        doc,
        "You still trade time for money, but with leverage: productised services, workshops, a personal brand that "
        "feeds products, or a small team. These can be useful as a temporary bootstrap (for example, one paid "
        "workshop that funds photography and a course). They are dangerous as a steady state because they collide "
        "with Deloitte hours and with independence rules the moment the buyer is a company.",
        align="justify",
    )
    h2(doc, "3.4  The ‘asset test’")
    p(doc, "Before treating an idea as passive, it must pass all five tests:", align="justify")
    numbered(
        doc,
        [
            "Separability: the income can continue if you take eight weeks of audit leave.",
            "Non-client: no ongoing professional relationship with an identified company that could be a restricted entity.",
            "Originality: the IP is yours, not the firm’s, not a publisher’s, and not a client’s.",
            "Disclosability: you would be comfortable describing the activity in an independence confirmation and on your tax return.",
            "Reputational symmetry: a reasonable and informed third party, reading your LinkedIn and your audit opinion, would not see a conflict or a circus.",
        ],
    )
    h2(doc, "3.5  How AI changes the framework")
    p(
        doc,
        "AI compresses the build time of Category B assets and simultaneously raises the failure rate of low-differentiation "
        "products (prompt packs, generic e-books, undifferentiated Excel dashboards). The correct response is not to "
        "avoid AI; it is to use AI as labour and to compete on Bangladesh-specific domain knowledge, professional "
        "quality control, and distribution — things a generic model does not possess. Owning the asset (templates, "
        "audience, calculator, sovereign ladder) remains the point. Selling AI-generated labour on a marketplace is "
        "still Category C, and usually Class 4 or 5.",
        align="justify",
    )
    callout(
        doc,
        "Working rule",
        "If an opportunity cannot be placed cleanly in A or B within 12 months, it is not part of the core plan. "
        "It may be a short experiment with a hard time-box. It may not become your identity.",
    )
