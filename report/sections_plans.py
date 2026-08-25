"""Three mini-plans, financial models, KPI, blueprint, sources, QC."""
from __future__ import annotations

from data import USD_BDT
from helpers import bullets, callout, caption, h1, h2, h3, make_table, numbered, p, source_line


def three_plans(doc):
    h1(doc, "21.  Three mini business plans")
    p(
        doc,
        "The three strongest opportunities are not three startups. They are one product studio, one personal "
        "sovereign portfolio, and one optional education asset. Together they are the blueprint.",
        align="justify",
    )

    h2(doc, "Plan A — LedgerCraft BD (primary income engine)")
    h3(doc, "1. Executive summary")
    p(
        doc,
        "LedgerCraft BD is a personal brand that sells original Excel (and later Power BI) tools to Bangladeshi "
        "households, traders, and junior accountants, with a secondary English catalogue for international "
        "marketplaces. It never takes a client, never customises a file for a named company, and never uses the "
        "Deloitte name. It is Category B, permission class 2 (confirm locally).",
        align="justify",
    )
    h3(doc, "2. Market opportunity")
    p(
        doc,
        "Bangladesh has a large informal and SME sector that already lives in Excel and Facebook. Formal VAT and "
        "tax administration is tightening, which increases demand for simple systems. Global marketplaces have "
        "inexhaustible demand for competent financial templates, but also inexhaustible supply of mediocre ones. "
        "The defensible wedge is Bangla-first, VAT-aware, cash-flow-obsessed quality — not another colour-coded dashboard.",
        align="justify",
    )
    h3(doc, "3. Customer persona")
    p(
        doc,
        "‘Rafi’, 34, runs a trading concern in Motijheel with two staff. He has a BIN or is about to. He can use "
        "SUMIFS but his ‘accounts’ are a folder of bank statements. He will pay BDT 1,500 for a sheet that tells "
        "him whether he can take a 60-day LC. Secondary persona: ‘Nusrat’, 26, article student, who will pay BDT "
        "600 for a clean personal net-worth and study-hour tracker and will follow an email list for years.",
        align="justify",
    )
    h3(doc, "4. Value proposition")
    p(doc, "Professional-grade structure, documented assumptions, hostile-input testing, and an honest list of what the file will not do.", align="justify")
    h3(doc, "5. Competitive landscape")
    p(
        doc,
        "Etsy/Gumroad dashboards; local Facebook ‘Excel training’; CA coaching shops; free Google-sheet templates; "
        "AI one-shot workbooks. You win on localisation, trust, and maintenance through Finance Act cycles — not on price.",
        align="justify",
    )
    h3(doc, "6–8. Product, pricing, distribution")
    bullets(
        doc,
        [
            "Core SKUs: 13-week cash-flow; household CFO; VAT information map; management-accounts pack; inventory-light P&L.",
            "Pricing: see Chapter 20. Never discount by offering customisation.",
            "Distribution: own site first, one marketplace second, email third. No agency ads until 50 organic sales.",
        ],
    )
    h3(doc, "9–11. Marketing, technology, automation")
    p(
        doc,
        "Marketing is demonstrated competence: a public sample sheet, short screen recordings, and useful posts that "
        "do not leak client life. Technology is Excel + WordPress + local payments + Payoneer. Automation is "
        "instant fulfilment and a quarterly update ritual.",
        align="justify",
    )
    h3(doc, "12–14. Financials, break-even, risk")
    p(
        doc,
        "See Chapter 22. Break-even is a handful of sales per month because cash costs are tiny. The real break-even "
        "is hours: if you cannot maintain the catalogue in four Saturday hours, the product set is too wide. Risks: "
        "policy, over-claim, custom-work creep, payouts, AI copies. Residual financial risk is low; residual career "
        "risk is low if you obey the constitution.",
        align="justify",
    )
    h3(doc, "15–18. 90 days, 12 months, scale, exit")
    numbered(
        doc,
        [
            "90 days: clearance packet, two SKUs, one checkout, ten conversations, first T-bill bought (wealth engine in parallel).",
            "12 months: 8–12 SKUs, owned list, decision on course filming.",
            "Scale: more SKUs in the same niche, not new niches; annual pass; maybe Power BI.",
            "Exit: a digital catalogue with documented rights can be sold to another educator, or simply kept as a royalty tap. Either is acceptable.",
        ],
    )

    h2(doc, "Plan B — The Sovereign Sleeve (wealth engine)")
    h3(doc, "1. Executive summary")
    p(
        doc,
        "A written, rules-based allocation of salary surplus into Bangladesh government paper and high-quality "
        "deposits. Category A. Permission class 1 for sovereign paper (still confirm bank restricted status). This "
        "is not a ‘business’; it is the reason the rest of the plan cannot ruin you if products fail.",
        align="justify",
    )
    h3(doc, "2–4. Market, persona, proposition")
    p(
        doc,
        "The ‘market’ is the Bangladesh government financing its deficit at auction. You are the customer of the "
        "PD bank. The proposition is a real yield, currently double-digit in the 2026 snapshot, with sovereign "
        "credit and no corporate independence problem. Inflation and rate resets are the enemies, not a competitor startup.",
        align="justify",
    )
    h3(doc, "5–8. Landscape, structure, pricing, distribution")
    p(
        doc,
        "Alternatives: FDR, NSC, listed equity, property, gold. Equity and property fail the year-one test on "
        "independence or capital. Gold pays no coupon. NSC is useful but less flexible than T-bills. Structure: "
        "3 months expenses in breakable deposits; then a ladder of 91/182/364-day bills and one 2–5 year bond "
        "once the emergency fund exists. ‘Pricing’ is the auction yield. Distribution is your payday standing instruction.",
        align="justify",
    )
    h3(doc, "9–12. Process, technology, automation, financial model")
    p(
        doc,
        "IPS v1: no single-name stocks in year one; no product you do not understand; no breaking a deposit to fund "
        "a ‘hot’ idea. Tracking sheet plus calendar. Coupons reinvested. Model: at a 10% average booked yield "
        "(assumption, not a forecast), BDT 400,000 initial + BDT 30,000 monthly is about BDT 1.17m of contributions "
        "over 24 months plus interest — a serious asset. Sensitivity: if yields fall to 7%, you still have the "
        "habit and the principal.",
        align="justify",
    )
    h3(doc, "13–18. Break-even, risk, 90 days, 12 months, scale, exit")
    p(
        doc,
        "Break-even is immediate in the sense that the alternative is cash at ~0% real. Risks: rate reinvestment, "
        "operational error, buying a bank product from a restricted entity, inflation. 90 days: BP ID, first bill, "
        "DPS live. 12 months: three tenors. Scale: raise the surplus rate with each increment. Exit: hold to maturity; "
        "this sleeve is not for trading.",
        align="justify",
    )

    h2(doc, "Plan C — SkillStack Excel (secondary engine, approval-gated)")
    h3(doc, "1. Executive summary")
    p(
        doc,
        "A single evergreen course that teaches professional Excel hygiene and a simple three-statement / cash-flow "
        "build, using LedgerCraft files as the classroom. Category B. Permission class 3. If approval is refused, "
        "this plan is dropped without debate and the files remain downloadable products.",
        align="justify",
    )
    h3(doc, "2–5. Market, persona, proposition, competition")
    p(
        doc,
        "Thousands of Bangladeshi students and juniors will take an Excel course this year. Most courses are either "
        "click-driven or ACCA-syllabus lectures. The proposition is ‘how a working auditor thinks about a clean "
        "workbook’ without claiming to teach audit, without using firm materials, and without putting your face in "
        "front of a sales promise you cannot keep. Competition is Udemy volume; you will not win the algorithm, "
        "you will win the handful of people who find you via LedgerCraft.",
        align="justify",
    )
    h3(doc, "6–11. Product through automation")
    p(
        doc,
        "Ninety to 150 minutes, screen-plus-voice, downloadable files, a 12-question quiz, no live chat promise. "
        "Price: low on Udemy (distribution tax), honest on your site. Film in one quiet month. Host primarily on "
        "your site; Udemy is a billboard. Automation: no cohort, no Slack, FAQ only.",
        align="justify",
    )
    h3(doc, "12–18. Money, risk, roadmap, exit")
    p(
        doc,
        "A successful niche course might sell 10–40 copies a month after a year (estimate; many sell fewer). At "
        "BDT 2,490 that is useful but not life-changing — which is the correct ambition. Risk is mostly time and "
        "brand. 90 days after approval: outline and pilot. 12 months: one course shipped. Scale: a module two only "
        "if module one sells. Exit: the course is part of the catalogue sale.",
        align="justify",
    )


def financials(doc):
    h1(doc, "22.  Financial models and sensitivity")
    p(
        doc,
        "All figures are assumptions for planning. They are internally consistent. They are not forecasts, and they "
        "are not advice to spend money you need for living costs or your emergency fund.",
        align="justify",
    )
    h2(doc, "22.1  LedgerCraft BD — conservative studio model (BDT)")
    make_table(
        doc,
        ["Line", "Year 1", "Year 2", "Year 3"],
        [
            ["SKUs at year end", "6", "10", "12"],
            ["Orders (assumption)", "40–120", "120–320", "200–500"],
            ["Average net ticket after fees", "1,100", "1,200", "1,300"],
            ["Revenue (range)", "44,000–132,000", "144,000–384,000", "260,000–650,000"],
            ["Variable fees (15% blended)", "7,000–20,000", "22,000–58,000", "39,000–98,000"],
            ["Fixed cash cost (hosting, software, design)", "40,000", "30,000", "30,000"],
            ["Independent disclaimer review (once / refresh)", "10,000", "5,000", "5,000"],
            ["Gross margin (approx.)", "High on each sale; fixed costs dominate Y1", "60–80%+", "70–85%"],
            ["Indicative net (range)", "(20,000)–60,000", "80,000–290,000", "180,000–520,000"],
            ["Hours (year)", "280–380", "180–260", "140–200"],
        ],
        font_size=8,
    )
    caption(doc, "Table 22.1  Studio model (estimate). Parentheses = loss. A year-one accounting loss with a working catalogue is acceptable.")
    p(
        doc,
        "Break-even cash (year 1): with BDT 50,000 cash costs and BDT 1,100 net ticket, about 46 paid orders. That "
        "is one modest sale a week after launch — achievable or not depending on distribution, not on Excel skill. "
        "Payback on cash cost: under 12 months if validation succeeds; never if you never distribute. ROI on cash is "
        "the wrong primary metric in year one; ROI on hours versus learning and option value is the right one. "
        "Do not include your salary opportunity cost of Saturday mornings unless you would otherwise work paid overtime — you would not.",
        align="justify",
    )
    h2(doc, "22.2  Sovereign sleeve — contribution model (assumption 10% booked yield)")
    make_table(
        doc,
        ["Item", "Conservative", "Balanced", "Aggressive-but-reasonable"],
        [
            ["Initial (BDT)", "150,000", "400,000", "1,000,000"],
            ["Monthly (BDT)", "15,000", "30,000", "50,000"],
            ["Contributions over 36 months", "690,000", "1,480,000", "2,800,000"],
            ["Illustrative value @10% (approx.)", "~800k", "~1.72m", "~3.26m"],
            ["Illustrative value @7%", "~760k", "~1.62m", "~3.07m"],
            ["Illustrative value @12%", "~830k", "~1.80m", "~3.40m"],
            ["Year-3 coupon run-rate @10% (rough)", "~6–7k/mo", "~14k/mo", "~27k/mo"],
        ],
        font_size=8,
    )
    caption(
        doc,
        "Table 22.2  Simple future-value illustration (estimate). Not a promise. Ignores tax, WHT timing, and yield-curve shape. "
        f"USD translation at ~BDT {USD_BDT:.0f}: balanced 36-month contributions ≈ USD 12,100.",
    )
    h2(doc, "22.3  Combined year-3 picture (balanced path)")
    make_table(
        doc,
        ["Engine", "Year-3 cash (indicative range)", "Passivity"],
        [
            ["Sovereign / DPS coupons & interest", "BDT 120,000–200,000", "A"],
            ["LedgerCraft net", "BDT 180,000–520,000", "B"],
            ["Course (if approved and mediocre-to-good)", "BDT 30,000–150,000", "B"],
            ["Calculator / other", "BDT 0–80,000", "B"],
            ["Combined", "BDT 330,000–950,000  (table 11.1 uses a wider band to include weaker product years)", "Mix"],
        ],
        font_size=8,
    )
    p(
        doc,
        "Table 11.1’s balanced year-3 band (BDT 0.65–1.7m) is wider because it also allows a stronger product year "
        "and counts grosser cash flows. Use the lower half of every range for personal budgeting. Never pre-spend expected digital income.",
        align="justify",
    )
    h2(doc, "22.4  Sensitivity narrative")
    bullets(
        doc,
        [
            "If yields fall 300 bps: the sleeve still beats idle cash; increase surplus rate rather than ‘reaching’ for equity.",
            "If products sell at half the conservative order count: you lose a few Saturday hours and a small cash outlay; the sleeve is intact.",
            "If approval for the course is refused: Plan C dies; Plans A and B are unchanged.",
            "If busy season eats six months: freeze SKUs; coupons continue.",
            "If a policy problem appears: shut public brand within 48 hours; keep the sovereign sleeve.",
        ],
    )


def kpi(doc):
    h1(doc, "23.  KPI dashboard")
    p(doc, "Review on the first Saturday of each month. Red / amber / green. No vanity metrics.", align="justify")
    make_table(
        doc,
        ["KPI", "Green", "Amber", "Red", "Response"],
        [
            ["Independence / policy items open", "0", "1 (in process)", ">1 or any breach", "Stop commercial work"],
            ["Busy-season freeze obeyed", "Yes", "One slip", "Quality comment at work", "Two-week studio halt"],
            ["Hours / week (off-peak)", "6–10", "11–14", ">14 or <2 for a month without a freeze reason", "Cut scope or restart ritual"],
            ["Emergency fund", "≥3 months", "2–3", "<2", "All surplus to cash"],
            ["Sovereign surplus actually invested", "Payday + 5 days", "Same month", "Skipped month", "Automate DPS"],
            ["SKUs live / promised", "Shipped ≥ promised", "One slip", "Ghost roadmap", "Halve the roadmap"],
            ["Paid orders (trailing 90 days)", "Rising or ≥15", "5–14", "0 after month 6 with real distribution", "Niche or pause paid tools"],
            ["Support time / week", "<40 min", "40–90", ">90", "Kill custom work; improve docs"],
            ["Books vs bank / Payoneer", "Reconciled", "1 month lag", ">1 month or mixed funds", "Rebuild ledger"],
            ["Sleep <6h nights / month", "0–2", "3–5", ">5", "Cancel Saturday block"],
        ],
        font_size=8,
    )
    caption(doc, "Table 23.1  Operating dashboard.")


def blueprint(doc):
    h1(doc, "24.  My recommended passive income blueprint")
    p(
        doc,
        "This is the decision. It privileges career preservation, capital protection, scalability, sustainability, "
        "and compounding over short-term speculative returns.",
        align="justify",
    )
    h2(doc, "Primary income engine")
    p(
        doc,
        "LedgerCraft BD — original Excel (then Power BI) digital products for Bangladeshi households and SMEs, "
        "sold impersonally, never customised for a company, never using firm IP or the firm name.",
        align="justify",
    )
    h2(doc, "Secondary income engine")
    p(
        doc,
        "SkillStack Excel — one evergreen course, filmed only after written approval, using the same files. If "
        "approval is not granted, the secondary engine is simply a larger LedgerCraft catalogue plus a small owned email list.",
        align="justify",
    )
    h2(doc, "Wealth engine")
    p(
        doc,
        "The Sovereign Sleeve — emergency cash, DPS, Treasury bills and bonds, and National Savings Certificates "
        "where they still fit. Screened mutual funds only after a restricted-entity process. No year-one single-name equity programme.",
        align="justify",
    )
    h2(doc, "Experimental engine")
    p(
        doc,
        "Shonchoy Lab — one transparent Bangladesh calculator or public-data page. Hard cap: BDT 40,000 and 40 hours. "
        "Promote LedgerCraft or die quietly.",
        align="justify",
    )
    make_table(
        doc,
        ["Item", "Blueprint default"],
        [
            ["Total starting capital", "BDT 400,000 balanced default (BDT 150,000 still works). Of which ≤ BDT 70,000 is operating risk capital."],
            ["Expected weekly time", "7–9 hours off-peak; 0–4 in busy season."],
            ["First 30 days", "Policy read; clearance note; personal-device hygiene; DPS; emergency fund; brand skeleton; Template 1 in build."],
            ["First 90 days", "Approval submitted/received; Template 1–2 live; checkout tested; BP ID; first T-bill or NSC; 10 conversations."],
            ["First 12 months", "8–12 SKUs; ladder with three tenors; tax file ready; course only if approved; no staff; no custom work."],
            ["3-year target", "A sovereign stack funded by a durable surplus habit, plus a catalogue that can pause for a busy season and still sell. Year-3 combined cash in the lower half of the balanced range is a win."],
            ["Key KPIs", "Zero policy incidents; emergency fund intact; surplus automated; SKUs shipped; hours capped; books reconciled."],
            ["Major risks", "Independence/OBA miss; burnout; product non-sale; payout friction; over-claiming on tax/VAT tools."],
            ["Compliance checkpoints", "Before start; before any public brand; before first security that is not sovereign; before filming; before incorporating; every confirmation cycle; every Finance Act; every tax filing."],
        ],
        col_widths=[4.4, 12.6],
        font_size=8.5,
    )
    callout(
        doc,
        "If you only do four things this quarter",
        "1) Read and follow local independence rules. 2) Automate a DPS. 3) Buy the first government security. "
        "4) Ship one original template to a real checkout. Everything else is optional.",
    )


def sources(doc):
    h1(doc, "25.  Sources and references")
    p(
        doc,
        "Accessed during research in August 2026. URLs decay; keep a PDF copy of anything you rely on for a filing "
        "or a policy decision. Primary law always beats this list.",
        align="justify",
    )
    h2(doc, "Official and professional tax / finance")
    bullets(
        doc,
        [
            "Income Tax Act, 2023 (Bangladesh) — primary statute. Confirm consolidated text via NBR / Ministry of Law.",
            "Value Added Tax and Supplementary Duty Act, 2012 — primary VAT statute.",
            "National Board of Revenue — nbr.gov.bd (rates, e-TIN, circulars). Confirm any slab before filing.",
            "KPMG / Rahman Rahman Huq, ‘Salient features of Finance Ordinance 2025’ (June 2025), PDF on assets.kpmg.com — professional secondary source for AY 2025–26 and proposed AY 2026–27/27–28 individual slabs and selected WHT notes.",
            "PwC Worldwide Tax Summaries, Bangladesh overview (updated 2026) — https://taxsummaries.pwc.com/bangladesh — CGT and headline rates; use as secondary.",
            "Bloomberg Tax, ‘Bangladesh Gazettes 2026 Finance Act’ (21 July 2026) — existence of Finance Act 2026 measures (VAT on imported services, WHT notes, threshold increase). Read the gazette for operative text.",
            "ICAB technical upload: Finance Ordinance 2025 / Income Tax presentation (Sept 2025) — member professional education material.",
        ],
    )
    h2(doc, "Bangladesh Bank, savings, and markets")
    bullets(
        doc,
        [
            "Bangladesh Bank — Foreign Exchange Policy Department circular reported 22 July 2026 (freelancer documentation, USD 20,000 undeclared inward threshold as reported, OPGSP USD 10,000, Freelancer Card, ERQ 50%/30%). Retrieve the circular via your authorised dealer. News corroboration: The Daily Star; Dhaka Tribune; Times of Bangladesh (22 July 2026).",
            "Prothom Alo English, ‘Govt treasury bills-bonds can be alternatives…’ (5 May 2026) — T-bill/T-bond yields as of 29 April 2026 and retail access mechanics (BP ID, BDT 100,000 minimum as reported).",
            "The Daily Star, ‘Govt slashes interest rates on savings certificates’ (1–2 July 2025) — NSC rate reset and six-monthly review vs treasury yields.",
            "Eastern Bank Ltd. public page, EBL Freelancer Suite — example of a bank freelancer USD account (50% retention feature as marketed). Product terms change; read the current term sheet.",
            "BSEC Real Estate Investment Trust Fund Rules, 2024 — as reported by The Business Standard (31 March 2024). Watch-list, not a year-one allocation.",
        ],
    )
    h2(doc, "Professional ethics and independence")
    bullets(
        doc,
        [
            "IESBA International Code of Ethics for Professional Accountants (including International Independence Standards) — latest handbook. ICAB/IFAC: Bangladesh has adopted the IESBA Code (IFAC country profile: ifac.org membership profile for Bangladesh).",
            "Financial Reporting Act, 2015 and Financial Reporting Council — statutory ethics overlay for professional accountants in Bangladesh.",
            "Deloitte public independence explainers: ‘Personal independence at Deloitte’ / ‘Common independence topics’ on deloitte.com / www2.deloitte.com — member-firm educational pages on outside employment, restricted entities, family holdings, digital assets. Not a substitute for Deloitte Bangladesh internal policy.",
        ],
    )
    h2(doc, "Platforms")
    bullets(
        doc,
        [
            "Gumroad Help Centre, ‘Getting paid by Gumroad’ — payout country constraints; no Payoneer/Wise native payout as stated by Gumroad.",
            "YouTube Help, YouTube Partner Program eligibility — Bangladesh is an eligible country in public 2026 country lists; thresholds (subscribers / watch hours or Shorts views) apply.",
            "Payoneer and individual AD-bank pages — operational payout practice for Bangladeshi freelancers (practical, not legal authority).",
        ],
    )
    h2(doc, "FX working assumption")
    bullets(
        doc,
        [
            "USD/BDT mid-market near 122–123 on 25 August 2026 (xe.com and other market pages). This report uses 122 as a modelling estimate, not Bangladesh Bank’s official rate.",
        ],
    )
    h2(doc, "Evidence labels used in the text")
    bullets(
        doc,
        [
            "Verified fact — stated in an official text or independently corroborated high-quality secondary source, as cited.",
            "Reasonable inference — application of a verified rule to this profile (e.g., ‘outside teaching is likely Class 3’).",
            "Estimate — numbers in models, scores, and timelines.",
            "Strategic opinion — weights, cut-offs, and the final blueprint mix.",
        ],
    )


def qc(doc):
    h1(doc, "26.  Quality-control checklist and document control")
    make_table(
        doc,
        ["Check", "Result"],
        [
            ["Feasible for a full-time Deloitte audit Senior Executive?", "Yes — hour-capped, busy-season freeze, no client service."],
            ["Employer / conflict / independence risks addressed?", "Yes — Chapter 6; Class 4–5 excluded from the blueprint; written approval gates."],
            ["Bangladesh tax/FE current as of 2026 research?", "Yes, with explicit uncertainty on exact 2026–27 threshold and listed-share CGT; primary-law confirm required."],
            ["Financial assumptions realistic / not promised?", "Yes — ranges, downside of zero product sales, small USD equivalents."],
            ["Passive vs semi-passive distinguished?", "Yes — A/B/C throughout."],
            ["High-risk schemes excluded?", "Yes — Chapter 17."],
            ["Scalable elements present?", "Yes — catalogue + course option + compounding sleeve."],
            ["Executable beside a demanding audit job?", "Yes — Saturday deep work; weeknight cap."],
            ["Sources authoritative where claims are material?", "Yes — NBR/BB/BSEC/ICAB/IFAC/Deloitte public/KPMG/PwC/major newspapers; gaps labelled."],
            ["Calculations internally consistent?", "Yes — scenario table, Chapter 22 models, and USD conversions share the same rate and contribution maths (illustrative FV)."],
            ["Three-year projections mathematically reasonable?", "Yes — contribution totals plus modest product nets; no hockey sticks."],
            ["Actionable rather than theoretical?", "Yes — 30/90/365 actions, weekly system, KPI dashboard, four-thing quarter."],
        ],
        font_size=8,
    )
    h2(doc, "Document control")
    make_table(
        doc,
        ["Field", "Value"],
        [
            ["Title", "Strategic Passive Income & Wealth-Building Blueprint for a Deloitte Bangladesh Audit Professional — 2026–2029"],
            ["Version", "1.0"],
            ["Date", "25 August 2026"],
            ["Classification", "Confidential — personal strategic advisory"],
            ["Next review", "After the next Finance Act / any change in local independence policy / 30 November tax cycle"],
        ],
        col_widths=[4.5, 12.5],
    )
    p(
        doc,
        "End of report. If a paragraph in this document ever conflicts with Deloitte policy, Bangladesh law, or "
        "the IESBA Code as it applies to you, those authorities win and this document yields.",
        align="justify",
        space_before=12,
    )
