"""Tech stack, AI, avoid list, risk, decision framework, 10 concepts."""
from __future__ import annotations

from helpers import add_image, bullets, callout, caption, h1, h2, h3, make_table, numbered, p


def tech(doc):
    h1(doc, "15.  Technology stack")
    p(
        doc,
        "Buy as little as possible. Prefer tools you already know. Do not build a ‘startup stack’ for a catalogue "
        "that does not yet have ten customers.",
        align="justify",
    )
    make_table(
        doc,
        ["Tool", "Purpose", "Indicative cost", "Free alternative", "Essential?", "Automation"],
        [
            ["Microsoft Excel / 365 personal", "Product factory", "Existing / modest personal sub", "LibreOffice (weaker)", "Yes", "Templates themselves automate users"],
            ["Power BI Desktop", "Dashboard SKUs", "Desktop free; Pro if sharing", "Google Looker Studio", "Later", "High once models exist"],
            ["ChatGPT / Claude / Gemini", "Drafting, formula help, QA scripts", "USD 0–20/mo personal", "Free tiers", "Yes, personal licence", "Draft → you review"],
            ["Notion or Google Docs", "SOP, changelog, content calendar", "Free", "—", "Yes", "Medium"],
            ["Canva", "Covers, marketplace thumbnails", "Free–Pro", "Photopea / Figma free", "Nice", "Medium"],
            ["WordPress + minimal theme", "Owned storefront", "BDT 3–8k/yr hosting+domain", "Carrd / Gumroad page", "Yes by month 3", "Woo + email"],
            ["SSLCOMMERZ / bKash", "BDT checkout", "Transaction %", "Manual bKash with honour system (poor)", "Yes for BD sales", "High"],
            ["Payoneer", "FX collection", "FX + withdrawal fees", "Bank wire (clunky)", "Yes for export", "Medium"],
            ["Payhip or similar", "Global digital delivery", "Platform %", "Own site only", "Test", "High"],
            ["Google Workspace personal", "Email on your domain", "Low", "Gmail", "Nice", "Low"],
            ["GitHub (private)", "Version control for workbooks / site", "Free", "Local zip versions", "Yes if you build a site", "High"],
            ["Google Analytics 4 + Search Console", "Traffic truth", "Free", "—", "Once you have a site", "High"],
            ["Bitwarden / similar", "Password hygiene", "Free", "—", "Yes", "—"],
            ["Zapier / Make", "Connect forms to sheets", "Free tier first", "Native integrations", "No until volume", "High"],
            ["Cursor / VS Code + AI", "Microsite only", "Free–low", "—", "Only for experiment", "High"],
            ["SEMrush / Ahrefs", "SEO", "Expensive", "Search Console + Keywords Everywhere", "No", "Medium"],
        ],
        font_size=7.5,
    )
    caption(doc, "Table 15.1  Stack. Costs are indicative (estimate) and change. Use personal subscriptions, never firm licences, for side work.")
    p(
        doc,
        "Stripe is not assumed. Firm Microsoft 365, firm GitHub, firm ChatGPT Enterprise, and firm data are out of "
        "bounds. If a tool would require uploading anything that even resembles client information, it is the wrong tool.",
        align="justify",
    )


def ai_strategy(doc):
    h1(doc, "16.  AI-leveraged passive-income strategy")
    p(
        doc,
        "AI should shorten the distance between your professional knowledge and a finished asset. It should not "
        "become the product, and it should not become a freelance service you sell by the hour.",
        align="justify",
    )
    h2(doc, "16.1  Where AI is allowed to work hard")
    bullets(
        doc,
        [
            "First drafts of help files, listings, and lesson scripts — which you then rewrite in your voice and check for legal over-claim.",
            "Formula construction and test-case generation for workbooks. You still design the control logic.",
            "Regression testing: ‘break this cash-flow sheet with messy inputs’.",
            "Bangla/English localisation of consumer products (then native review).",
            "Code scaffolding for a calculator microsite.",
            "Summarising public NBR/BB circulars into an internal research note (not into ‘tax advice’ for sale).",
        ],
    )
    h2(doc, "16.2  Where AI is a trap")
    bullets(
        doc,
        [
            "Auto-generated e-books and prompt packs with no proprietary knowledge — already a commodity, high AI-disruption score.",
            "Chatbots that answer Bangladesh tax questions as if they were a practitioner — liability and reputation risk.",
            "Uploading any workbook that ever touched client data, even ‘for cleaning’.",
            "Selling ‘AI audit opinions’ or anything that sounds like assurance.",
            "Using firm-licensed AI tools for the side business.",
        ],
    )
    h2(doc, "16.3  Asset ideas that remain yours after the model changes")
    numbered(
        doc,
        [
            "A tested Excel engine with Bangladesh-specific tax/VAT flags and a changelog tied to Finance Acts.",
            "A distribution list of people who already trust your household or SME tools.",
            "A calculator whose traffic comes from Bangla search terms you actually rank for.",
            "A recorded course whose value is your walkthrough of messy, real-world spreadsheet hygiene — not the slides.",
            "The sovereign ladder, which AI cannot disintermediate.",
        ],
    )
    h2(doc, "16.4  Operating pattern")
    p(
        doc,
        "Saturday: you specify the workbook like an audit programme (objective, inputs, checks, outputs, what it "
        "will not do). AI drafts. You test with hostile data. You write the disclaimer. You ship. Weekly: AI may "
        "draft listing variants; you pick one. Quarterly: you feed the latest Finance Act into a personal research "
        "chat and update the two SKUs that actually depend on law. That is an AI-leveraged studio. It is not an "
        "‘AI business’.",
        align="justify",
    )
    callout(
        doc,
        "Ownership test",
        "If OpenAI shut down tomorrow, would you still own something that produces cash? If the answer is only "
        "‘I would lose my prompt pack store’, the strategy was wrong. If the answer is ‘I still own tested workbooks, "
        "an email list, and a T-bond ladder’, the strategy is right.",
    )


def avoid(doc):
    h1(doc, "17.  Avoid at all costs")
    p(
        doc,
        "An auditor’s downside is not a lost Saturday. It is a professional-conduct file, a visa or partnership-track "
        "problem, or a newspaper paragraph. The following fail that asymmetric test.",
        align="justify",
    )
    make_table(
        doc,
        ["Pattern", "Why it is toxic for this career", "What people say instead"],
        [
            ["Ponzi / ‘guaranteed 15% a month’ clubs", "Fraud-adjacent; reporting duties; ruin", "‘Private investment circle’"],
            ["MLM / net-work marketing", "Reputation; possible staff/client entanglement", "‘Membership business’"],
            ["High-leverage retail FX / binaries / CFDs", "Losses + gambling optics + policy risk", "‘Currency investing’"],
            ["Unregulated offshore ‘prop firms’ / signal rooms", "Same as above plus often a scam", "‘Funded account’"],
            ["Copy trading / PAMM for others", "You become an unlicensed advisor", "‘I just share my trades’"],
            ["Crypto speculation & coin-calling", "Reportable in many firm policies; optics", "‘Digital assets allocation’"],
            ["Selling trading signals or ‘VIP’ groups", "Advice + gambling + conflicts", "‘Education community’"],
            ["Gambling / betting tips", "Conduct and reputation", "‘Sports analytics’"],
            ["Fake passive-income courses (guru model)", "You become the thing this report is written against", "‘I’ll teach you my method’"],
            ["Grey affiliate (loan sharks, betting, fake degrees)", "Brand damage, possible legal exposure", "‘High converting offers’"],
            ["Selling ‘Deloitte audit workpapers’ or ISA packs copied from the firm", "IP theft + confidentiality + possible crime", "‘Shared for education’"],
            ["Undisclosed paid opinions on companies", "Independence destruction", "‘Thought leadership’"],
            ["Hundi / unofficial FX", "Criminal and career-ending", "‘My cousin will settle’"],
            ["Tax evasion structures for yourself or others", "Disqualifying", "‘Everyone does it’"],
        ],
        font_size=8,
    )
    caption(doc, "Table 17.1  Red-flag catalogue. If a WhatsApp message created urgency and a referral bonus, it is already wrong.")
    p(
        doc,
        "If a friend invites you into any of the above, the professional response is a short no. You do not need "
        "to write them a memo. You do need to keep the chat in case it ever becomes relevant — and you must not "
        "introduce colleagues or clients.",
        align="justify",
    )


def risk(doc, assets):
    h1(doc, "18.  Risk-management framework")
    p(
        doc,
        "Risk score below is Probability (1–10) × Impact (1–10). Mitigation is a control, not a slogan. Residual "
        "risk remains; the point is to keep residual career risk near zero.",
        align="justify",
    )
    if assets.get("risk"):
        add_image(doc, assets["risk"], 16.4)
        caption(doc, "Figure 18.1  Risk map.")
    make_table(
        doc,
        ["Risk", "P", "I", "P×I", "Primary mitigation"],
        [
            ["Independence / outside-activity breach", "2", "10", "20", "Written policy + pre-clearance + no client service + restricted-list discipline"],
            ["Confidentiality / IP leakage", "2", "10", "20", "Personal devices only; original work; no client anecdotes; legal review of anything that feels close"],
            ["Audit-quality slip / burnout", "4", "9", "36", "Hour caps; busy-season freeze; sleep rule; pause-the-studio trigger"],
            ["Tax or forex non-compliance", "3", "8", "24", "Authorised rails; simple books; disclose; professional review before year 2"],
            ["Public-brand incident", "3", "7", "21", "No firm name in commerce; no political/client content; cooling-off on posts"],
            ["Digital products do not sell", "6", "3", "18", "Tiny cash at risk; validation gate at month 6; sovereign sleeve still compounds"],
            ["Platform deplatforming / payout failure", "4", "5", "20", "Owned site + owned list + tested Payoneer/bank path; two-channel max, not one"],
            ["Investment drawdown (if you stray into equities)", "5", "5", "25", "Core in sovereign paper; equity only after process; no leverage"],
            ["AI commoditises generic templates", "6", "4", "24", "Localise to BD rules; quality-control reputation; own distribution"],
            ["Payment fraud / chargebacks / cyber", "3", "5", "15", "Reputable checkout; 2FA; no stored card data; backups"],
            ["Income volatility", "7", "3", "21", "Do not budget living costs against digital revenue; salary + coupons are the base"],
            ["Regulatory change (VAT, FE, savings rates)", "5", "4", "20", "Quarterly law scan; product changelog; no strategy that needs a loophole"],
        ],
        font_size=7.5,
    )
    caption(doc, "Table 18.1  Risk register. P and I are structured estimates (estimate).")
    h2(doc, "18.1  Control environment (yes, you already know this language)")
    bullets(
        doc,
        [
            "Preventive: policy clearance, device separation, no custom work, no restricted names, hour caps.",
            "Detective: monthly 30-minute self-audit (holdings vs restricted list; hours vs cap; revenue vs books).",
            "Corrective: freeze rule, takedown rule, voluntary disclosure to Independence if something went wrong.",
            "Directive: this document, an IPS, and a one-page studio constitution pinned in Notion.",
        ],
    )


def decision(doc):
    h1(doc, "19.  Reusable decision framework")
    p(
        doc,
        "Future-you will be offered a ‘can’t-miss’ idea. Use the same scoring machine, not adrenaline.",
        align="justify",
    )
    h2(doc, "19.1  Stage 0 screens (any ‘no’ kills the idea)")
    numbered(
        doc,
        [
            "Is it lawful in Bangladesh (including FE rules) as you would actually operate it?",
            "Can you describe it in an independence confirmation without wincing?",
            "Does it require client data, firm IP, or the Deloitte name? If yes, kill.",
            "Does it create a professional relationship with an identifiable company? If yes, kill unless written approval and a conflict check exist — which, in practice, means kill.",
            "Can you pause it for eight weeks? If no, it is a second job; kill or redesign.",
            "Would a reasonable partner at the firm be embarrassed if The Business Standard wrote about it? If yes, kill.",
        ],
    )
    h2(doc, "19.2  Scored formula")
    p(
        doc,
        "Opportunity Score = 100 × [ 0.10·Inc + 0.09·Scale + 0.09·Pas + 0.08·Fit + 0.06·BD + 0.04·Intl + 0.06·Sust "
        "+ 0.04·Auto + 0.03·Exit + 0.04·(11−Cap)/10 + 0.03·(11−Setup)/10 + 0.05·(11−Hours)/10 + 0.03·(11−TTI)/10 "
        "+ 0.02·(11−Tech)/10 + 0.03·(11−Comp)/10 + 0.03·(11−Reg)/10 + 0.02·(11−Tax)/10 + 0.08·(11−Emp)/10 "
        "+ 0.08·(11−Ind)/10 + 0.05·(11−Confid)/10 + 0.05·(11−Rep)/10 + 0.03·(11−FinRisk)/10 + 0.03·(11−Fail)/10 "
        "+ 0.02·(11−AI)/10 ]",
        size=10,
        align="justify",
    )
    p(
        doc,
        "All inputs are 1–10. This is the same formula as Chapter 5. Decision rule: pursue only if Score ≥ 70 and "
        "Stage 0 is clean and independence risk ≤ 4 unless written approval already exists. If two ideas pass, pick "
        "the one that adds a new sleeve (money, product, or distribution) rather than a clone of what you already do.",
        align="justify",
    )
    h2(doc, "19.3  Expected-value overlay for money-at-risk")
    p(
        doc,
        "For any idea that needs more than BDT 50,000 of cash at risk: EV = p_success · upside − p_fail · cash_at_risk "
        "− p_career · C_career. Set C_career at a minimum of five years of incremental career value (a deliberately "
        "large number). Any non-trivial p_career makes EV negative. That is the mathematics of not freelancing for "
        "audit clients.",
        align="justify",
    )


def ten_ideas(doc):
    h1(doc, "20.  Ten concrete business concepts")
    p(
        doc,
        "These are specified products, not genres. Pricing is an opening hypothesis (estimate). None requires you "
        "to leave Deloitte. Concepts 8–10 are sequenced later or capped.",
        align="justify",
    )

    ideas = [
        {
            "n": "1. LedgerCraft BD",
            "who": "Bangladeshi SME owners, accountants in industry, and finance students who live in Excel.",
            "problem": "Spreadsheets that do not forecast cash and do not match how VAT/books actually feel on the ground.",
            "offer": "A branded catalogue of original workbooks: 13-week cash-flow, management accounts, inventory-light trading P&L, payroll register, and a VAT information workbook.",
            "rev": "One-time digital downloads; later a ‘catalogue pass’ subscription.",
            "price": "BDT 790–2,490 per SKU locally; USD 12–39 internationally; pass BDT 4,900/year.",
            "acq": "Bangla SEO, Facebook groups (value posts, not spam), marketplace listings, later email.",
            "tools": "Excel, Canva, WordPress, bKash/SSLCOMMERZ, Payhip, Payoneer.",
            "cost": "BDT 25,000–70,000 year one.",
            "time": "6–9 h/week for 16 weeks, then 2–4.",
            "auto": "Instant delivery, FAQ, quarterly update batch.",
            "d90": "Name, disclaimer, 2 SKUs, live checkout, 10 conversations.",
            "y12": "10 SKUs, 50–200 customers, first repeat buyers.",
            "risk": "Custom-work requests; legal over-claim on VAT; marketplace copycats.",
        },
        {
            "n": "2. Ghorer CFO (Household CFO Kit)",
            "who": "Salaried couples in Dhaka/Chattogram who want a shared number system.",
            "problem": "Households run on bKash history and anxiety, not a plan.",
            "offer": "Bangla+English budget, sinking funds (school, hajj, wedding), debt payoff, net-worth.",
            "rev": "Low-ticket downloads; optional printed planner later.",
            "price": "BDT 390–990.",
            "acq": "Reels that show the sheet, not your face if you prefer privacy; HR/welfare groups.",
            "tools": "Excel/Google Sheets, Canva, bKash.",
            "cost": "BDT 10,000–25,000.",
            "time": "4–6 h/week for 8 weeks.",
            "auto": "Sheets copy-on-purchase; annual inflation update.",
            "d90": "One kit, 30 testers, iterate.",
            "y12": "A recognisable consumer SKU that feeds LedgerCraft traffic.",
            "risk": "High competition; low willingness to pay — mitigate with volume and an email list.",
        },
        {
            "n": "3. Mushak Map (information workbook + explainer)",
            "who": "Small traders and first-time BIN holders.",
            "problem": "VAT paperwork feels like a locked room.",
            "offer": "A map of forms, calendars, and checklists plus a calculator that does arithmetic — explicitly not a filing service.",
            "rev": "Download + paid annual update after each Finance Act.",
            "price": "BDT 1,490; update BDT 490.",
            "acq": "Search for ‘Mushak’ + ‘Excel’; YouTube explainers if approved.",
            "tools": "Excel, WordPress, disclaimer reviewed by an independent tax practitioner (paid once).",
            "cost": "BDT 20,000–40,000 including a legal/tax read of the disclaimer.",
            "time": "5–8 h/week for 10 weeks.",
            "auto": "Annual versioning.",
            "d90": "Scope freeze; disclaimer; prototype; 5 accountant reviews.",
            "y12": "Flagship local SKU.",
            "risk": "Being seen as giving tax advice; law changes. Mitigation: disclaimer + ‘information only’ + no numbers that pretend to be a ruling.",
        },
        {
            "n": "4. The Friday Spreadsheet",
            "who": "Junior accountants and SME bookkeepers.",
            "problem": "Scattered Excel tricks; no weekly cadence of professional hygiene.",
            "offer": "Free fortnightly note; paid annual pack of the year’s workbooks.",
            "rev": "List → product. No paid Substack until payouts are easy.",
            "price": "Free / BDT 1,900 year-pack.",
            "acq": "LinkedIn (careful, no firm IP) and email.",
            "tools": "Beehiiv or Buttondown if payout-friendly; otherwise MailerLite + own site.",
            "cost": "BDT 5,000–15,000.",
            "time": "2 hours a fortnight plus product time.",
            "auto": "Queue 4 issues; templates do the monetising.",
            "d90": "6 issues, 200 subscribers, no growth hacks.",
            "y12": "Owned audience of 1,000+ or kill.",
            "risk": "Becomes a content treadmill. Hard cap: 12 issues/year.",
        },
        {
            "n": "5. SkillStack Excel (evergreen course)",
            "who": "ACC A/CA students and industry juniors who can already open Excel but cannot model a clean three-statement flow.",
            "problem": "Courses are either too Western or too click-bait.",
            "offer": "A 90–150 minute recorded course using LedgerCraft files. No live cohort in year one.",
            "rev": "Udemy (distribution) + own-site (margin).",
            "price": "USD 19.99 list on Udemy / BDT 2,490 own site.",
            "acq": "Udemy search; your list; university clubs.",
            "tools": "OBS, a decent microphone, Teachable or own site, Udemy.",
            "cost": "BDT 20,000–50,000 (mic, lights, editing).",
            "time": "A 30-hour filming block after approval — schedule in a quiet month, not March.",
            "auto": "Recorded; Q&A via FAQ only.",
            "d90": "Approval first; outline; 20-minute pilot.",
            "y12": "One course, not a ‘university’.",
            "risk": "Class 3 activity; time sink; face-on-camera brand risk. Audio-plus-screen is enough.",
        },
        {
            "n": "6. Indicator Desk BD",
            "who": "Students, journalists, and curious professionals who want clean charts of BB/NBR/BBS releases.",
            "problem": "Public data is scattered and ugly.",
            "offer": "A static-first site that updates key series; affiliate or donation optional; mainly a traffic engine.",
            "rev": "Indirect (leads to LedgerCraft) plus optional ads later.",
            "price": "Free public good.",
            "acq": "SEO on ‘Bangladesh inflation’, ‘T-bill yield’, etc.",
            "tools": "Python or even Excel→CSV→static site; GitHub Pages.",
            "cost": "BDT 5,000–20,000.",
            "time": "Weekend build + 1 hour per release.",
            "auto": "Scripts where possible; otherwise a manual ritual after BB releases.",
            "d90": "Five series, cited, dated.",
            "y12": "Keep only if organic traffic appears.",
            "risk": "Scraping TOS; becoming a newsroom. Cite and link official sources.",
        },
        {
            "n": "7. Close-the-Books Checklist (generic)",
            "who": "New industry accountants.",
            "problem": "Month-end is tribal knowledge.",
            "offer": "A public-domain-knowledge checklist and recon pack. No firm methodology.",
            "rev": "BDT 590–1,290 download.",
            "price": "Low ticket.",
            "acq": "LinkedIn and student groups.",
            "tools": "Excel/Notion.",
            "cost": "BDT 5,000.",
            "time": "Two Saturdays if you are disciplined about originality.",
            "auto": "Download.",
            "d90": "Legal self-check: would a partner say this looks like ours? If yes, rewrite from blank.",
            "y12": "A catalogue add-on, not a standalone company.",
            "risk": "IP resemblance. When in doubt, thin it out.",
        },
        {
            "n": "8. Compounder Notes (KDP / PDF essays)",
            "who": "English-reading BD professionals who want a sober personal-finance book that is not American FIRE cosplay.",
            "problem": "Local personal-finance content is either folk wisdom or stock-tip culture.",
            "offer": "A short book: emergency fund, sovereign ladder, independence-aware investing, anti-guru.",
            "rev": "Royalty; also a brand magnet.",
            "price": "USD 4.99 / BDT 450 equivalent PDF.",
            "acq": "Your list; later KDP if payouts work.",
            "tools": "Google Docs, Vellum-class or Word, own site first.",
            "cost": "BDT 10,000–30,000 (edit/cover).",
            "time": "A 6-week Saturday project in year 2.",
            "auto": "Once published, near-passive.",
            "d90": "Do not start in month 1.",
            "y12": "Outline only, unless the list is already hungry.",
            "risk": "AI-slush pile. Only write if the voice is clearly yours.",
        },
        {
            "n": "9. Shonchoy Lab calculators",
            "who": "Anyone Googling ‘Bangladesh income tax calculator 2026’.",
            "problem": "Calculators go stale every Finance Act and often hide their assumptions.",
            "offer": "Transparent, versioned calculators with sources cited. Donations or template upsell.",
            "rev": "Lead gen + optional ‘pro workbook’.",
            "price": "Free web; pro BDT 990.",
            "acq": "SEO.",
            "tools": "Simple web app; your personal AI coding tool; hosting.",
            "cost": "BDT 15,000–40,000. Hard cap.",
            "time": "40-hour experiment.",
            "auto": "High if you resist feature creep.",
            "d90": "One calculator, one source table, one disclaimer.",
            "y12": "Keep iff search traffic exists.",
            "risk": "People treat it as advice; you must design the UI to prevent that.",
        },
        {
            "n": "10. The Sovereign Sleeve (not a product — a personal utility)",
            "who": "You.",
            "problem": "Salary surplus decays in a current account.",
            "offer": "A written IPS, a PD-bank relationship, a T-bill/T-bond/NSC/DPS ladder, and an annual rebalance.",
            "rev": "Interest and coupons. This is the wealth engine.",
            "price": "n/a",
            "acq": "n/a",
            "tools": "Bank, BB BP ID, a tracking sheet.",
            "cost": "Your investable surplus.",
            "time": "3 hours to set up; 30 minutes a month.",
            "auto": "DPS + maturity calendar.",
            "d90": "Emergency fund + first bill + IPS v1.",
            "y12": "A visible ladder, not a single deposit.",
            "risk": "Rate cuts; breaking deposits early; mission creep into hot stocks.",
        },
    ]
    for idea in ideas:
        h3(doc, idea["n"])
        make_table(
            doc,
            ["Element", "Specification"],
            [
                ["Target customer", idea["who"]],
                ["Problem", idea["problem"]],
                ["Product / service", idea["offer"]],
                ["Revenue model", idea["rev"]],
                ["Pricing (hypothesis)", idea["price"]],
                ["Acquisition", idea["acq"]],
                ["Tools", idea["tools"]],
                ["Startup cost (est.)", idea["cost"]],
                ["Time", idea["time"]],
                ["Automation", idea["auto"]],
                ["90-day launch", idea["d90"]],
                ["12-month growth", idea["y12"]],
                ["Main risks", idea["risk"]],
            ],
            col_widths=[4.2, 12.8],
            font_size=8,
        )
