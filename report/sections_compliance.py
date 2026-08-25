"""Deloitte/independence, BD tax/legal, international platforms."""
from __future__ import annotations

from helpers import bullets, callout, caption, h1, h2, h3, make_table, numbered, p, source_line


def deloitte(doc):
    h1(doc, "6.  Deloitte, independence, and professional-conduct analysis")
    p(
        doc,
        "This chapter is the most important in the report. A well-designed template shop that creates an independence "
        "exception is a negative-NPV project once you price career risk correctly.",
        align="justify",
    )
    h2(doc, "6.1  What can be verified publicly — and what cannot")
    p(
        doc,
        "Deloitte member firms publish personal-independence explainers for candidates and spouses. Those pages "
        "(Deloitte US and other member firms) consistently state that: independence applies to professionals and "
        "their immediate family; financial relationships may need to be reported and monitored; outside employment "
        "and outside business activities — paid or unpaid, including teaching, self-employment, and independent "
        "professional services — require disclosure and approval; investments in restricted entities (attest clients "
        "and specified affiliates) can be prohibited; and digital assets are treated as financial relationships in "
        "at least some member-firm policies. ICAB, via IFAC’s membership profile, has adopted the IESBA International "
        "Code of Ethics; Bangladesh’s Financial Reporting Council has statutory authority over ethical requirements "
        "for professional accountants.",
        align="justify",
    )
    source_line(
        doc,
        "Verified fact: Deloitte public independence pages (deloitte.com ‘Personal independence’ / common independence topics); "
        "IFAC country profile for Bangladesh (IESBA Code adopted). Not verified from public sources: the text of "
        "Deloitte Bangladesh’s local independence manual, restricted-entity list, personal trading system, or employment contract.",
    )
    callout(
        doc,
        "Hard stop",
        "Do not treat this chapter as a substitute for the local Independence & Conflicts process. Before any outside "
        "activity other than ordinary personal bank deposits and government savings products, read the current local "
        "policy and, where the policy is unclear, obtain written guidance. If the policy requires pre-clearance, "
        "the absence of a ‘no’ is not a ‘yes’.",
    )
    h2(doc, "6.2  Independence in mind and in appearance")
    p(
        doc,
        "IESBA defines independence as both of mind and of appearance. The second limb is what catches content "
        "creators and side consultants. A reasonable and informed third party who sees a Deloitte auditor selling "
        "‘audit workpaper packs’, offering cheap tax filings, or holding shares in an audit client does not need "
        "a secret kickback to lose confidence. Appearance failures are still failures.",
        align="justify",
    )
    h2(doc, "6.3  Topic-by-topic implications")
    h3(doc, "Outside employment and self-employment")
    p(
        doc,
        "Public Deloitte materials tell candidates to disclose any non-Deloitte employment, self-employment, family "
        "business, professor/instructor roles, advisory boards, and professional services provided independently. "
        "Inference for you: a template shop that is clearly a product business with no clients may be easier to "
        "clear than ‘I do bookkeeping on weekends’, but it is still an outside business activity. A course, a "
        "workshop, Upwork, Fiverr, and any retainer are outside employment. Default action: written approval.",
        align="justify",
    )
    h3(doc, "Directorships, partnerships, and business ownership")
    p(
        doc,
        "Owning a private limited company, being a partner, or sitting on a board is a Class 3–5 event. Even a "
        "dormant company can require reporting. If you later incorporate the digital studio, do it after clearance, "
        "and never take a corporate customer that is, or is likely to become, a restricted entity.",
        align="justify",
    )
    h3(doc, "Personal investments and securities trading")
    p(
        doc,
        "Government securities and ordinary bank deposits are the lowest-friction instruments. Listed shares, "
        "corporate bonds, and many mutual funds require a restricted-entity screen. Do not trade on the basis of "
        "anything you learn on an engagement. Do not ‘help family’ pick stocks in sectors you audit. If the firm "
        "operates a pre-clear / tracking system, use it. If it does not, keep a personal register of holdings and "
        "compare it to the restricted list you are given.",
        align="justify",
    )
    h3(doc, "Confidential information and firm IP")
    p(
        doc,
        "You may not use client information, non-public information, internal manuals, workpaper structures that "
        "are firm proprietary, training decks, or even distinctive phrasing from firm documents. ‘I anonymised it’ "
        "is not a defence if the pattern is recognisable or the document was never yours to reuse. Build templates "
        "from public standards (IAS/IFRS as published, VAT Act language, textbooks you have a right to use) and "
        "from blank-sheet design.",
        align="justify",
    )
    h3(doc, "Use of the Deloitte name, logo, and ‘I work in Big Four audit’")
    p(
        doc,
        "Using the firm name or logo to sell a side product is almost certainly prohibited. Describing yourself as "
        "a Deloitte auditor on a sales page to imply quality or access is a reputation and possibly a trademark / "
        "policy problem. Safer pattern: ‘Chartered-accountancy track professional / financial reporting specialist’ "
        "without naming the firm on commercial pages. LinkedIn employment history is a fact; a Gumroad banner that "
        "says ‘Templates by a Deloitte Auditor’ is marketing use. When in doubt, omit.",
        align="justify",
    )
    h3(doc, "Content creation and monetisation")
    p(
        doc,
        "Educational content about public rules (how a cash-flow statement hangs together; how a T-bill works) is "
        "the cleanest content. Content that discusses named clients, deal rumours, or ‘what we see in audits’ is "
        "unsafe. Monetisation (ads, affiliates, sponsorships) adds a commercial relationship that may itself need "
        "approval. Affiliate relationships with software vendors used by audit clients deserve extra caution.",
        align="justify",
    )
    h3(doc, "Teaching and corporate training")
    p(
        doc,
        "Live teaching of corporate finance teams is high risk because the audience may be restricted. Recorded "
        "public courses with anonymous students are lower risk but still usually Class 3. ICAB/ICMAB lecturing "
        "should be pre-cleared.",
        align="justify",
    )
    h3(doc, "Freelancing and remote consulting")
    p(
        doc,
        "Upwork ‘financial modelling for a US startup’ still looks like outside professional services. You will not "
        "know whether the counterparty is affiliated with a restricted entity. You cannot run firm-grade conflict "
        "checks as a night-time freelancer. This is why marketplace accounting is Class 4–5 in this report.",
        align="justify",
    )
    h3(doc, "Cryptocurrency, forex, CFDs, copy trading")
    p(
        doc,
        "Public Deloitte materials in some member firms list digital assets as reportable. High-leverage retail FX "
        "and signal communities are incompatible with the professional brand of an auditor, regardless of local "
        "legality. They are on the avoid list.",
        align="justify",
    )
    h2(doc, "6.4  Activities that should not be pursued without written approval")
    bullets(
        doc,
        [
            "Any paid professional service (accounting, tax, modelling, CFO-as-a-service, bookkeeping).",
            "Any teaching, tutoring, corporate training, or paid webinar.",
            "Incorporation, partnership, or directorship.",
            "A public brand that references Deloitte or audit-client work.",
            "A securities account used for single-name equities or corporate bonds.",
            "Affiliate or sponsorship deals with companies in the financial-reporting supply chain.",
            "Holding or advising on crypto, FX, or unregulated investments.",
            "Joining another firm’s panel, expert network, or paid survey that discusses clients or sectors you audit.",
        ],
    )
    h2(doc, "6.5  A practical clearance packet")
    p(doc, "If you seek approval for the recommended digital studio, take a one-page note covering:", align="justify")
    numbered(
        doc,
        [
            "Nature: sale of original, generic Excel/educational products to the public; no client service.",
            "Time: outside working hours; estimated weekly hours; busy-season pause rule.",
            "Customers: individuals and anonymous online buyers; no outreach to restricted entities.",
            "IP: created on personal devices; no firm content.",
            "Brand: no Deloitte name or logo.",
            "Money: expected revenue band; personal bank account / later a disclosed proprietorship.",
            "Conflicts: you will not accept custom work; you will not use non-public information.",
            "Ask: written confirmation that the activity is permitted subject to those conditions.",
        ],
    )


def tax_legal(doc):
    h1(doc, "7.  Bangladesh legal, tax, and foreign-exchange considerations")
    p(
        doc,
        "This chapter separates legal requirement, tax treatment, and practical recommendation. Bangladesh tax law "
        "moved from the Income Tax Ordinance, 1984 to the Income Tax Act, 2023, with rates and administrative rules "
        "updated by successive Finance Ordinances/Acts. Always confirm the assessment year that applies to the "
        "income year in which you earn the money.",
        align="justify",
    )
    h2(doc, "7.1  Individual income-tax architecture (current through 2026)")
    p(
        doc,
        "Resident individuals are taxed on a progressive slab system administered by the National Board of Revenue. "
        "Professional summaries of the Finance Ordinance 2025 (Rahman Rahman Huq / KPMG Bangladesh, June 2025) state "
        "that for assessment year 2025–26 the general exemption was BDT 350,000, followed by a 5% band and then "
        "10–30%. The same source set out proposed slabs for assessment years 2026–27 and 2027–28 with a general "
        "exemption of BDT 375,000, removal of the 5% band, and a first positive rate of 10%, topping out at 30%. "
        "Later 2026 practitioner commentary on the Finance Act 2026 reports a further increase in the general "
        "exemption toward BDT 400,000. Because Finance Act numbers can differ from earlier ordinance proposals, "
        "treat the exact threshold as a confirm-with-NBR item before you file.",
        align="justify",
    )
    source_line(
        doc,
        "Verified fact (professional secondary source): KPMG/RRH ‘Salient features of Finance Ordinance 2025’ (June 2025) "
        "for AY 2025–26 effective slabs and proposed AY 2026–27/2027–28 slabs. Later 2026 threshold of BDT 400,000: "
        "practitioner commentary — confirm against the gazetted Finance Act 2026 and NBR circulars.",
    )
    make_table(
        doc,
        ["Item", "AY 2025–26 (RRH/KPMG)", "AY 2026–27 as proposed by RRH/KPMG", "Status"],
        [
            ["General tax-free threshold", "BDT 350,000", "BDT 375,000", "Confirm latest gazetted figure"],
            ["First positive rate", "5% on next 100,000", "10% on next 300,000", "5% band widely reported as removed later"],
            ["Top marginal rate", "30%", "30%", "Stable across sources"],
            ["Women / seniors 65+", "Higher threshold (400k)", "Higher threshold (425k)", "Confirm"],
            ["Minimum tax", "Location-based historically", "Policy has been moving toward simplification", "Confirm current NBR table"],
        ],
    )
    caption(doc, "Table 7.1  Individual tax architecture — do not file from this table; verify on nbr.gov.bd / e-TIN portal.")
    h2(doc, "7.2  How different income types are likely to be characterised")
    p(
        doc,
        "Characterisation drives both rate and withholding. The following is a practical map (inference from the "
        "Income Tax Act framework and standard NBR practice), not a ruling.",
        align="justify",
    )
    make_table(
        doc,
        ["Source", "Likely head / character", "Typical friction", "Practical note"],
        [
            ["Salary from Deloitte", "Employment income", "Employer withholding", "Keep this clean; do not mix side money here"],
            ["FDR / bank interest", "Interest", "WHT often 10% with TIN", "Credit against final tax; retain certificates"],
            ["NSC profit", "Interest / profit on securities", "Product-specific WHT and investment limits", "Track purchase limits and reinvestment rules"],
            ["T-bill / T-bond", "Interest on securities", "WHT on securities reported at 10% in 2025 professional summaries", "Keep auction / PD documents"],
            ["Mutual-fund dividend / gain", "Dividend / capital gains", "Fund-level and investor-level rules", "Screen holdings; keep statements"],
            ["Listed-share gains", "Capital gains", "Sources conflict on individual exemption vs 15%", "Do not assume exemption; confirm before trading"],
            ["Template / course sales (BD)", "Business income", "May need trade licence if regular", "Books of account; possible VAT/turnover tax later"],
            ["Foreign platform payouts", "Foreign-source business / residual", "Repatriation + disclosure", "Bring money through authorised channels"],
            ["YouTube / ads / affiliate", "Business / residual", "Platform 1099-style docs rare", "Self-assess; keep payout statements"],
            ["Rental", "House property / business", "WHT on rent often 10% (2025 summaries)", "Separate from digital activity"],
        ],
        font_size=8,
    )
    caption(doc, "Table 7.2  Characterisation map — inference. Obtain advice for material amounts.")
    p(
        doc,
        "On listed-share capital gains, published secondary sources disagree: some practitioner notes still describe "
        "an exemption for individuals on listed shares, while PwC’s Bangladesh summary discusses a 15% concept for "
        "certain listed-share gains and a holding-period rule (average rate if disposed within five years; 15% or "
        "average, whichever is lower, after five years for many other capital assets). That conflict is exactly why "
        "this report does not build a strategy that depends on a presumed CGT exemption.",
        align="justify",
    )
    source_line(
        doc,
        "Sources in tension: Moore Global Bangladesh notes (individual listed-share profits described as exempt in one table) "
        "versus PwC Worldwide Tax Summaries (Bangladesh overview, 2026 update) on CGT. Treat as unresolved without primary-law check.",
    )
    h2(doc, "7.3  Withholding, VAT, and ‘do I need a business?’")
    p(
        doc,
        "KPMG/RRH’s 2025 ordinance note describes higher withholding on resident advisory, consultancy and "
        "professional services (illustratively 15% for natural persons in one table). If you ever invoice a "
        "Bangladeshi company for training or advice, expect withholding. Product sales to consumers are different: "
        "there is usually no customer WHT, but you have a self-assessment obligation.",
        align="justify",
    )
    p(
        doc,
        "VAT (Value Added Tax and Supplementary Duty Act, 2012) is generally 15% once you are in the standard "
        "regime. Smaller businesses may fall under a turnover-tax / enlistment regime (commonly described in 2025–26 "
        "practitioner guides as around 3–4% on turnover between a lower threshold and BDT 3 crore). Thresholds and "
        "mandatory-registration categories change and some entity types must register regardless of turnover. "
        "Exported services are typically zero-rated, which is relevant if you sell digital products to non-residents "
        "and can evidence the export. Locally developed software / ITES has historically enjoyed time-limited VAT "
        "benefits — do not assume they still apply after their sunset date without checking the current statutory "
        "list.",
        align="justify",
    )
    p(
        doc,
        "Practical recommendation: in year one, while revenue is experimental, operate as an individual, keep "
        "invoices and payout statements, and disclose the income on your return. When run-rate revenue is clearly "
        "a business (a common-sense test: regular sales, a brand, and more than incidental amounts), obtain a trade "
        "licence if required by your city corporation, consider a proprietorship, and take VAT advice before you "
        "cross enlistment thresholds. Do not ignore BIN/VAT merely because the money arrives from Payoneer.",
        align="justify",
    )
    h2(doc, "7.4  Foreign exchange and platform income")
    p(
        doc,
        "Bangladesh Bank remains the foreign-exchange regulator. Freelancing and digital-service exports are lawful "
        "and, as of 22 July 2026, subject to a more practical documentation regime. Multiple reputable news reports "
        "of a Foreign Exchange Policy Department circular that day state that: platform statements, emails, invoices "
        "and contracts can evidence foreign income; inward remittances up to USD 20,000 may be accepted without "
        "formal declaration; OPGSP receipts may be allowed up to USD 10,000 per transaction if repatriated in time; "
        "a dual-currency ‘Freelancer Card’ is contemplated; and IT freelancers may retain up to 50% of export "
        "earnings in an Exporters’ Retention Quota account (30% for other service exporters). These are verified "
        "as reported by The Daily Star, Dhaka Tribune and others; retrieve the circular itself from your bank "
        "before relying on a specific limit.",
        align="justify",
    )
    source_line(
        doc,
        "Verified fact (news of official circular, 22 July 2026): The Daily Star; Dhaka Tribune; Times of Bangladesh. "
        "Primary text: Bangladesh Bank FEPD circular — obtain via authorised dealer bank.",
    )
    p(
        doc,
        "Wage-earner remittance incentives (the widely discussed 2.5% incentive) are not designed for freelance or "
        "digital-export proceeds; commentary in 2026 has emphasised misclassification risk. Do not claim an incentive "
        "you are not entitled to. Bring funds through authorised dealers or recognised OPGSPs (Payoneer is the "
        "practical rail for many Bangladeshi earners). Avoid hundi. Keep a simple forex file: platform statement, "
        "invoice, bank credit advice, conversion rate.",
        align="justify",
    )
    h2(doc, "7.5  Investment products — what is actually available")
    p(
        doc,
        "Prothom Alo’s 5 May 2026 explainer, citing Bangladesh Bank data as of 29 April 2026, reported T-bill cut-off "
        "yields of about 10.17% (91-day), 10.49% (182-day) and 10.64% (364-day), and T-bond yields roughly 10.2–11.23% "
        "across 2- to 20-year tenors. Minimum investment was described as BDT 100,000, with a Business Partner ID "
        "at Bangladesh Bank and purchase via primary-dealer banks; securities are tradable in the secondary market. "
        "These yields move every auction — use them as a 2026 snapshot, not a locked-in forecast.",
        align="justify",
    )
    source_line(doc, "Verified fact (secondary journalism citing BB): Prothom Alo English, 5 May 2026. Confirm live yields with your PD bank.")
    p(
        doc,
        "National Savings Certificates remain a household staple but are no longer a static 12% product. The Daily "
        "Star (1–2 July 2025) reported a 47–57 basis-point cut and a six-monthly review mechanism tied to treasury "
        "yields plus a small premium. Purchase limits, tax treatment, and eligibility (including the 5-year Bangladesh "
        "Sanchayapatra versus family/pensioner variants) must be read from the Department of National Savings before "
        "you concentrate capital there. Bank FDR rates will generally sit near, and often slightly below, T-bill "
        "yields in a functioning market; shop, but do not jump banks solely for 20 basis points if the bank is a "
        "restricted entity or operationally inconvenient.",
        align="justify",
    )
    h2(doc, "7.6  Return filing and records")
    p(
        doc,
        "You already file as a salaried professional. Side income does not get to live in a separate moral universe. "
        "Keep: product sales ledgers, platform CSV files, withholding certificates, NSC/T-bill advices, and a note "
        "of expenses that are wholly and exclusively for the side activity (software, domain, payment fees). Do not "
        "claim personal living costs. Proof of Submission of Return remains socially and financially important in "
        "Bangladesh (bank, land, and some professional contexts). File on time.",
        align="justify",
    )
    callout(
        doc,
        "Legal requirement vs tax treatment vs recommendation — example",
        "Legal: if you are resident, foreign platform income is generally within the tax net. Tax treatment: it is "
        "usually business income, possibly with export-related nuances. Recommendation: repatriate through a bank, "
        "keep evidence, disclose, and do not spend energy on grey structures. The expected-value of non-disclosure "
        "is negative once you price career risk.",
    )


def platforms(doc):
    h1(doc, "8.  International platforms and payment rails")
    p(
        doc,
        "A platform is useful only if a Bangladeshi resident can get paid, stay compliant, and avoid turning a "
        "product business back into a client-service business. Popularity is not a criterion.",
        align="justify",
    )
    make_table(
        doc,
        ["Platform", "Use for you", "BD payout reality", "Conflict", "Verdict"],
        [
            ["Payoneer", "Master collection account", "Widely used; bank withdrawal; OPGSP pathway", "Low (rail only)", "Essential rail"],
            ["Local bank AD + Freelancer a/c", "Repatriation, ERQ if eligible", "EBL and peers offer freelancer USD accounts", "Low", "Essential rail"],
            ["bKash / Nagad / SSLCOMMERZ", "Domestic digital sales", "Native, instant, high trust", "Low", "Essential for BD customers"],
            ["Payhip / Lemonsqueezy-class", "Digital products to foreign buyers", "Often friendlier than Gumroad on payouts", "Low if products generic", "Preferred storefront"],
            ["Gumroad", "Digital products", "Direct deposit country list may exclude BD; PayPal weak in BD", "Low", "Only if payout actually works"],
            ["Etsy", "Template listings", "Possible; fees + policy risk on ‘financial/legal’ items", "Low–med", "Secondary channel"],
            ["Teachable / own WordPress", "Courses", "Collect via Payoneer-friendly processor or local gateway", "Class 3 teaching", "After approval"],
            ["Udemy", "Evergreen Excel course", "Instructor payouts exist; revenue share is steep", "Class 3", "Distribution, not home"],
            ["YouTube / AdSense", "Education library", "YPP available in Bangladesh; AdSense thresholds apply", "Class 3 brand", "Distribution after approval"],
            ["Substack / Beehiiv", "Paid newsletter", "Payouts can be awkward from BD", "Class 2–3", "Optional; start free"],
            ["Amazon KDP", "E-books", "Payouts historically awkward for BD; confirm current methods", "Class 2", "Later, not year one"],
            ["Upwork / Fiverr", "Services", "Payouts work; that is not the problem", "Class 4–5", "Do not use for accounting/audit/tax"],
            ["Patreon", "Fan funding", "Possible; weak fit for this brand", "Class 3", "Skip"],
            ["Stripe (direct)", "Global cards", "Bangladesh is generally not a Stripe merchant country", "n/a", "Do not plan on it"],
            ["PayPal", "Global casual payments", "Limited / unreliable as a BD home currency account", "n/a", "Do not depend on it"],
        ],
        font_size=7.5,
    )
    caption(doc, "Table 8.1  Platform verdicts as of 2026 research. Re-test payouts before building a catalogue around one storefront.")
    h2(doc, "8.1  Recommended commercial architecture")
    numbered(
        doc,
        [
            "Domestic storefront: a simple WordPress or Carrd site + SSLCOMMERZ or bKash for BDT buyers.",
            "International storefront: Payhip or equivalent that can pay a US/EU-style account you control via Payoneer or a bank-sponsored virtual account, if lawfully available.",
            "Collection: Payoneer → authorised dealer bank / freelancer account. Repatriate on a monthly cadence, not when you need cash.",
            "Books: one spreadsheet that reconciles storefront, Payoneer, and bank. You already know how to do this.",
            "Do not open five marketplaces in month one. Two storefronts is the maximum until a product has sold 50 times.",
        ],
    )
    h2(doc, "8.2  Fees, competition, and time")
    p(
        doc,
        "Udemy and Etsy buy distribution and sell your margin. That can be rational for a first course or a first "
        "template if you treat them as paid acquisition, not as your business. Your own site plus a Payoneer rail "
        "is the long-term home. Competition in generic ‘Excel dashboard’ listings is severe; competition in "
        "Bangla-first VAT and cash-flow tools for Bangladeshi traders is not. That is the positioning.",
        align="justify",
    )
    callout(
        doc,
        "Gumroad caution",
        "Gumroad’s own help centre has stated that if a country is not on the direct-deposit list and PayPal is not "
        "usable, they have no way to pay the creator. Test a $10 product and a live payout before investing a catalogue.",
    )
