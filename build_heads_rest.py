# Remaining head-of-income sheets + main(). Imported by build_tax_workbook.py
# Relies on names already defined in the parent module.

def build_financial(ws, wb):
    r = start_head(
        ws,
        "Income from Financial Assets",
        "ITA 2023  Chapter VII  ss.62–65  |  Interest, profit, discount and dividend  |  Capital gain on transfer of a financial asset is NOT this head (see Capital Gain)  |  TDS is a credit, not a deduction",
    )
    r = year_banner(ws, r)
    r += 1
    r = section(ws, r, "A", "QUICK CONCEPT / DEFINITION")
    for t in [
        "Definition: Income from financial assets covers interest, profit and discount on government / government-approved securities, on debentures and securities issued by a company or local authority, interest or profit on bank deposits and other financial products or schemes, and dividend (s.62). Capital gains from transferring those assets belong under Capital Gains, not here.",
        "What falls here: FDR / SND / savings-account interest; profit on Islamic deposits; discount on treasury bills; interest on Bangladesh Government Treasury Bonds and approved savings instruments; interest on corporate debentures / bonds; dividend (including unit-holder distributions treated as dividend).",
        "Exclusions: capital gain on sale of shares/securities; interest that is really business income of a bank / NBFI (those entities compute it under business); casual interest that the question clearly places elsewhere.",
        "Allowable expenditure (s.64): collection charges / banker commission wholly for earning this income, not capital, not personal. s.65 disallows deductions in specified cases (including, typically, where TDS rules are ignored — VERIFY).",
        "Dividend of an individual is generally charged at a special 15% rate (Seventh Schedule). Do not put it through the regular slab. Interest is normally regular-rate income unless a specific instrument is exempt or final-tax.",
        "ICAB points: (1) Never deduct TDS from the interest line. (2) Do not classify listed-share CG as financial-asset income. (3) Bond-washing / cum-interest vs ex-interest can still be examined conceptually. (4) 'Tax-free' securities are rare — only claim exemption if the question or Sixth Schedule says so. (5) Some savings-certificate interest historically had special treatment — VERIFY the exam-year SRO rather than assuming exemption.",
    ]:
        write_wrapped(ws, r, 1, "•  " + t, "L", 28, font(size=9), LIGHT_NAVY)
        r += 1
    r += 1

    r = section(ws, r, "B", "TYPES OF INCOME  —  TAX TREATMENT")
    header_row(ws, r, ["Particular", "Tax treatment", "Relevant provision", "Example / exam note", "", "", "", "", "", "", "", ""], NAVY)
    r += 1
    types = [
        ("Interest / profit on FDR, SND, savings account", "Taxable at regular slab", "s.62", "TDS by the bank is a credit."),
        ("Interest / profit / discount on government securities", "Usually taxable; some issues may be exempt — VERIFY", "s.62; Sixth Schedule — VERIFY", "Do not assume T-bond interest is tax-free."),
        ("Interest on corporate debenture / bond", "Taxable at regular slab", "s.62", "Distinct from CG on sale of the bond."),
        ("Discount on treasury bill / zero-coupon (if taxable)", "Taxable as this head", "s.62", "Zero-coupon exemption existed historically — VERIFY."),
        ("Dividend from a Bangladeshi company / units treated as dividend", "Special rate (default 15%)", "s.62; Seventh Schedule", "WHT 15% resident individual / 25% non-resident (PwC)."),
        ("Inter-corporate tax-paid dividend", "May be excluded if conditions met", "VERIFY", "More relevant to companies than to individuals."),
        ("Capital gain on sale of shares / securities", "NOT this head", "s.57–61", "Move to the Capital Gain sheet."),
        ("Collection charges / banker commission", "Allowable deduction", "s.64", "Must be wholly for earning this income."),
        ("TDS on interest or dividend", "Credit only", "s.150", "Never reduce the income."),
    ]
    for i, (a, b, c, d) in enumerate(types):
        bg = ALT if i % 2 == 0 else WHITE
        ws.cell(r, 1, a); ws.cell(r, 2, b); ws.cell(r, 3, c)
        ws.merge_cells(f"D{r}:L{r}")
        ws.cell(r, 4, d)
        for col in range(1, 13):
            ws.cell(r, col).font = font(size=8)
            ws.cell(r, col).fill = fill(WARN_FILL if "NOT this head" in b or "Credit" in b else bg)
            ws.cell(r, col).border = thin
            ws.cell(r, col).alignment = WRAP_TL
        ws.row_dimensions[r].height = 18
        r += 1
    r += 1

    r = section(ws, r, "C", "COMPUTATION TEMPLATE")
    write_wrapped(ws, r, 1, "Column C classifies the line as Regular / Dividend (special) / Exempt. TDS is memo only.", "L", 18, font(size=9), LIGHT_GOLD)
    r += 1
    header_row(ws, r, ["Income item", "Gross (BDT)", "Class", "Taxable regular", "Taxable dividend", "Exempt", "Allowable expense", "Net taxable", "Provision / note", "TDS (memo)", "Check", ""], NAVY)
    r += 1
    fin_items = [
        ("FDR interest (scheduled bank)", 180000, "Regular", 0, "s.62 — regular slab; TDS is a credit"),
        ("Savings / SND account interest", 12000, "Regular", 0, "s.62"),
        ("Interest on Bangladesh Govt Treasury Bond", 40000, "Regular", 0, "Not assumed exempt — VERIFY instrument"),
        ("Interest / profit on corporate debenture", 25000, "Regular", 0, "s.62"),
        ("Discount on T-bill / other security", 0, "Regular", 0, "Blank line"),
        ("Other interest / profit / discount", 0, "Regular", 0, "Blank line"),
        ("Cash dividend — listed company (ordinary shareholder)", 80000, "Dividend", 0, "Special 15% rate; not slab"),
        ("Cash dividend — unlisted company", 0, "Dividend", 0, "Still generally 15% for an individual — VERIFY"),
        ("Dividend specifically exempt (if any)", 0, "Exempt", 0, "Only if Sixth Schedule / question says so"),
    ]
    fin_start = r
    for lab, amt, cls, exp, note in fin_items:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        style_input(ws.cell(r, 3), cls, number=False)
        style_calc(ws.cell(r, 4), f'=IF(C{r}="Regular",B{r},0)')
        style_calc(ws.cell(r, 5), f'=IF(C{r}="Dividend",B{r},0)')
        style_calc(ws.cell(r, 6), f'=IF(C{r}="Exempt",B{r},0)')
        style_input(ws.cell(r, 7), exp, number=True)
        style_calc(ws.cell(r, 8), f"=MAX(D{r}+E{r}-G{r},0)")
        style_note(ws.cell(r, 9), note)
        tds_default = 18000 if "FDR" in lab else (12000 if "listed" in lab else 0)
        style_input(ws.cell(r, 10), tds_default, number=True)
        style_calc(ws.cell(r, 11), f'=IF(OR(D{r}+E{r}+F{r}>B{r}+0.001,G{r}>B{r}+0.001),"CHECK REQUIRED","OK")', number=False)
        ws.cell(r, 11).number_format = "@"
        r += 1
    fin_end = r - 1
    add_dv(ws, '"Regular,Dividend,Exempt"', f"C{fin_start}:C{fin_end}")

    style_label(ws.cell(r, 1), "TOTALS", bold=True)
    for col, letter in [(2, "B"), (4, "D"), (5, "E"), (6, "F"), (7, "G"), (8, "H"), (10, "J")]:
        style_calc(ws.cell(r, col), f"=SUM({letter}{fin_start}:{letter}{fin_end})")
        ws.cell(r, col).fill = fill(NAVY)
        ws.cell(r, col).font = font(bold=True, color=WHITE)
    ws.cell(r, 1).fill = fill(NAVY)
    ws.cell(r, 1).font = font(bold=True, color=WHITE)
    C["FIN_GROSS"] = f"$B${r}"
    C["FIN_REG_RAW"] = f"$D${r}"
    C["FIN_DIV_RAW"] = f"$E${r}"
    C["FIN_EXEMPT"] = f"$F${r}"
    C["FIN_EXP"] = f"$G${r}"
    r += 2

    # Allocate collection expenses: user can leave them on specific rows; also a general expense line already in column G.
    style_label(ws.cell(r, 1), "Additional collection charges not allocated above (s.64)", bold=True)
    style_input(ws.cell(r, 2), 0, number=True)
    C["FIN_COLL"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Income from financial assets — REGULAR (interest etc.)", bold=True)
    style_calc(ws.cell(r, 2), f"=MAX({C['FIN_REG_RAW']}-{C['FIN_EXP']}-{C['FIN_COLL']},0)")
    C["FIN_REGULAR"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE); ws.cell(r, 2).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "Income from financial assets — DIVIDEND (special rate)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['FIN_DIV_RAW']}")
    C["FIN_DIVIDEND"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE); ws.cell(r, 2).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "Exempt financial-asset income (not in total income)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['FIN_EXEMPT']}")
    C["FIN_DIV_EXEMPT"] = f"$B${r}"  # used as exempt bucket
    r += 2

    r = section(ws, r, "D", "TAX-TREATMENT TABLE")
    header_row(ws, r, ["Income item", "Gross amount", "Taxable amount", "Exempt amount", "Deduction / adjustment", "Net taxable amount", "Relevant provision", "Explanation", "", "", "", ""], SUBSEC)
    r += 1
    style_label(ws.cell(r, 1), "Interest / profit / discount")
    style_calc(ws.cell(r, 2), f"={C['FIN_REG_RAW']}")
    style_calc(ws.cell(r, 3), f"={C['FIN_REGULAR']}")
    style_calc(ws.cell(r, 4), 0)
    style_calc(ws.cell(r, 5), f"={C['FIN_EXP']}+{C['FIN_COLL']}")
    style_calc(ws.cell(r, 6), f"={C['FIN_REGULAR']}")
    ws.cell(r, 7, "s.62, s.64"); ws.cell(r, 8, "Regular slab on Home sheet")
    r += 1
    style_label(ws.cell(r, 1), "Dividend")
    style_calc(ws.cell(r, 2), f"={C['FIN_DIV_RAW']}")
    style_calc(ws.cell(r, 3), f"={C['FIN_DIVIDEND']}")
    style_calc(ws.cell(r, 4), 0)
    style_calc(ws.cell(r, 5), 0)
    style_calc(ws.cell(r, 6), f"={C['FIN_DIVIDEND']}")
    ws.cell(r, 7, "Seventh Schedule"); ws.cell(r, 8, "Special rate — not slab")
    r += 2

    r = section(ws, r, "E", "WORKED EXAMPLE  —  Mr. Md. Karim Rahman")
    write_wrapped(ws, r, 1,
        "STEP 1 — FACTS. FDR interest 180,000 (TDS 18,000); savings interest 12,000; T-bond interest 40,000; "
        "corporate-debenture interest 25,000; listed-company cash dividend 80,000 (TDS 12,000).",
        "L", 28, font(size=9), LIGHT_GOLD)
    r += 1
    write_wrapped(ws, r, 1,
        "STEP 2–4. Interest 257,000 is regular-rate financial-asset income. Dividend 80,000 is special-rate income. "
        "TDS 30,000 is not deducted from income. TAXABLE FINANCIAL-ASSET INCOME = 257,000 (regular) + 80,000 (dividend).",
        "L", 28, font(size=9), LIGHT_TEAL)
    r += 1
    style_label(ws.cell(r, 1), "Regular (live)", bold=True); style_calc(ws.cell(r, 2), f"={C['FIN_REGULAR']}")
    style_label(ws.cell(r, 3), "Dividend (live)", bold=True); style_calc(ws.cell(r, 4), f"={C['FIN_DIVIDEND']}")
    r += 2
    write_wrapped(ws, r, 1,
        "STEP 5 — WHY. ITA 2023 moved 'interest on securities' into this broader head. "
        "Dividend stays in this head but is taxed at the special rate, so the Home sheet keeps it out of the slab. "
        "A student who nets TDS and shows FDR income of 162,000 loses presentation and technical marks.",
        "L", 32, font(size=9), WHITE)
    r += 2

    r = close_head(ws, r, [
        "Head-identification trap: sale of listed shares is Capital Gain, not financial assets.",
        "Always show Gross interest and Gross dividend, then a separate TDS memo.",
        "If the question says 'interest on tax-free government securities', only then treat as exempt — quote the instrument.",
        "Collection charges are the only routine deduction. Do not invent a 20% standard deduction (that is Indian law on family pension, not BD).",
        "Bond-washing: selling cum-interest just before the coupon to convert interest into CG is a classic theory note.",
        "Dividend of a non-resident individual is often 25% WHT — still this head.",
        "Islamic 'profit' on a deposit is this head, not business (unless the assessee is the bank).",
        "If FDR interest has already been credited in the business P&L, remove it from business (less: income considered separately) and tax it here.",
    ], [
        "Default special dividend rate is P_DivRate on the Home sheet (15%).",
        "No general exemption for bank interest is assumed.",
        "s.64/s.65 detailed disallowance list should be checked in your reprint if the question involves unpaid TDS on a collection fee.",
    ], [
        "ITA 2023 ss.62–65 (Chapter VII).",
        "Seventh Schedule / Part 7 — rate on dividend. VERIFY.",
        "s.27 — dividend paid by a Bangladeshi company is deemed to arise in Bangladesh.",
        "s.150 — credit of tax deducted at source.",
    ])
    define_name(wb, "OUT_FIN_REGULAR", ws.title, C["FIN_REGULAR"])
    define_name(wb, "OUT_FIN_DIVIDEND", ws.title, C["FIN_DIVIDEND"])
    define_name(wb, "OUT_FIN_DIV_EXEMPT", ws.title, C["FIN_DIV_EXEMPT"])
    return r


def build_rent(ws, wb):
    r = start_head(
        ws,
        "Income from Rent",
        "ITA 2023  Chapter III  ss.35–39  |  Gross rental value s.37  |  Deductions s.38  |  Special income from rent s.39  |  Hotels/motels/resorts are business, not this head",
    )
    r = year_banner(ws, r)
    r += 1
    r = section(ws, r, "A", "QUICK CONCEPT / DEFINITION")
    for t in [
        "Definition: Income from rent is the amount remaining after allowable expenses (this Chapter) from the gross rental value of a property (s.36(1)). Property includes house property, land, furniture, fixtures, factory buildings, business premises, machinery, personal vehicles and other rentable physical capital assets (s.35).",
        "House property used in the owner's own business is not computed here (s.36(2)). Hostel, hotel, motel or resort rent is business income, not this head (s.36(3)). Letting a shop or office is still this head even if the owner is 'in the business of letting', except those lodging cases.",
        "Gross rental value of house property (s.37): A = (B + C + D + E) − F, where B = higher of rent accrued and annual value; C = adjustable advance relating to the year; D/E = other benefits / service charges etc.; F = vacancy allowance supported by electricity bill. Unadjustable security deposit is not income.",
        "Deductions for house property (s.38(1)): insurance; interest/profit on bank/NBFI loan for acquisition/construction/renovation (not post-period pre-rental interest after that period); municipal/local tax/annual charge (not capital); statutory collection/repair/utilities — 30% if commercial, 25% if non-commercial — of total rental value. Partial letting / part-year letting is proportional.",
        "You cannot claim actual repair instead of the statutory percentage. If the tenant pays a service charge that already covers those services, a restriction may apply — VERIFY / flag in the answer.",
        "s.39 special income from rent: unspent statutory deduction claimed, and certain disallowed expenses on non-house property, are special income — regular rate, no set-off, no 3rd Schedule. Interpretation of 'unspent' is flagged VERIFY. This sheet has a Yes/No toggle (default No) so you can apply it if the examiner clearly wants it.",
        "ICAB points: start from higher of actual rent and annual value; vacancy needs evidence; statutory % is on gross rental value after vacancy; interest is extra, not inside the 25%/30%; TDS on rent is a credit.",
    ]:
        write_wrapped(ws, r, 1, "•  " + t, "L", 30, font(size=9), LIGHT_NAVY)
        r += 1
    r += 1

    r = section(ws, r, "B", "TYPES OF INCOME  —  TAX TREATMENT")
    header_row(ws, r, ["Particular", "Tax treatment", "Relevant provision", "Example / exam note", "", "", "", "", "", "", "", ""], NAVY)
    r += 1
    for i, rowt in enumerate([
        ("Rent of residential house / flat", "This head; 25% statutory deduction", "s.36, s.38(1)(e)", "Non-commercial."),
        ("Rent of shop / office / commercial floor", "This head; 30% statutory deduction", "s.38(1)(e)", "Commercial."),
        ("Rent of land / machinery / furniture (not house)", "This head; business-style deductions", "s.38(2)", "ss.49–55 limits; bank transfer."),
        ("Hotel / motel / resort / hostel", "NOT this head — business", "s.36(3)", "Common classification trap."),
        ("Portion used in owner's own business", "NOT this head", "s.36(2)", "That portion is business."),
        ("Adjustable advance rent relating to the year", "Included in GRV", "s.37", "Unadjustable security deposit is not income."),
        ("Service charge / other benefit from tenant", "Included in GRV", "s.37", "May restrict the statutory repair claim — VERIFY."),
        ("Vacancy", "Deducted if electricity bill produced", "s.37", "Personal occupation is not vacancy."),
        ("Municipal / local tax, insurance, loan interest", "Allowable (actual)", "s.38(1)(a)–(d)", "Interest is in addition to the 25%/30%."),
        ("Actual repair / collection / utility spend", "Absorbed in the 25%/30% — not extra", "s.38(1)(e)", "Claiming both is a common mistake."),
        ("s.39 unspent statutory deduction", "Special income from rent — VERIFY", "s.39", "Toggle below."),
    ]):
        bg = ALT if i % 2 == 0 else WHITE
        ws.cell(r, 1, rowt[0]); ws.cell(r, 2, rowt[1]); ws.cell(r, 3, rowt[2])
        ws.merge_cells(f"D{r}:L{r}"); ws.cell(r, 4, rowt[3])
        for col in range(1, 13):
            ws.cell(r, col).font = font(size=8); ws.cell(r, col).fill = fill(bg); ws.cell(r, col).border = thin; ws.cell(r, col).alignment = WRAP_TL
        ws.row_dimensions[r].height = 18
        r += 1
    r += 1

    r = section(ws, r, "C", "COMPUTATION  —  HOUSE PROPERTY  (s.37–s.38)")
    style_label(ws.cell(r, 1), "Description of property", bold=True)
    style_input(ws.cell(r, 2), "3-bed residential flat, Dhanmondi, Dhaka (let out)", number=False)
    ws.merge_cells(f"B{r}:F{r}")
    r += 1
    style_label(ws.cell(r, 1), "Use", bold=True)
    style_input(ws.cell(r, 2), "Non-commercial", number=False)
    C["RENT_USE"] = f"$B${r}"
    add_dv(ws, '"Commercial,Non-commercial"', f"B{r}")
    r += 1
    style_label(ws.cell(r, 1), "Statutory repair % (auto)")
    style_calc(ws.cell(r, 2), f'=IF({C["RENT_USE"]}="Commercial",0.3,0.25)', number=False)
    ws.cell(r, 2).number_format = "0%"
    C["RENT_PCT"] = f"$B${r}"
    r += 1

    # GRV components
    items = [
        ("Actual rent accrued / received for the year", 480000, "RENT_ACT"),
        ("Annual value (reasonable letting value)", 450000, "RENT_AV"),
        ("Adjustable advance relating to this year (C)", 40000, "RENT_ADV"),
        ("Service charge / other benefit from tenant (D/E)", 24000, "RENT_BEN"),
        ("Vacancy allowance (supported by electricity bill) (F)", 80000, "RENT_VAC"),
    ]
    for lab, amt, key in items:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        C[key] = f"$B${r}"
        r += 1
    style_label(ws.cell(r, 1), "B = higher of actual rent and annual value", bold=True)
    style_calc(ws.cell(r, 2), f"=MAX({C['RENT_ACT']},{C['RENT_AV']})")
    C["RENT_B"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "GROSS RENTAL VALUE  A = (B + C + D/E) − F", bold=True)
    style_calc(ws.cell(r, 2), f"={C['RENT_B']}+{C['RENT_ADV']}+{C['RENT_BEN']}-{C['RENT_VAC']}")
    C["RENT_GRV"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(NAVY); ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(NAVY); ws.cell(r, 2).font = font(bold=True, color=WHITE); ws.cell(r, 2).number_format = NUM
    r += 2

    r = subsection(ws, r, "ALLOWABLE DEDUCTIONS  (s.38)")
    deds = [
        ("Insurance premium against damage / destruction", 8000, "RENT_INS"),
        ("Interest / profit on bank or NBFI housing loan (post-completion)", 95000, "RENT_INT"),
        ("Municipal / local tax / annual charge (not capital)", 18000, "RENT_MUN"),
        ("Pre-rental interest still deductible this year (if any)", 0, "RENT_PRE"),
        ("Other allowable actual deduction (not repair)", 0, "RENT_OTH"),
        ("Actual repair / collection / utility spent (memo — not added again)", 50000, "RENT_ACTREP"),
    ]
    for lab, amt, key in deds:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        C[key] = f"$B${r}"
        r += 1
    style_label(ws.cell(r, 1), "Statutory collection / repair / utility allowance", bold=True)
    style_calc(ws.cell(r, 2), f"={C['RENT_GRV']}*{C['RENT_PCT']}")
    C["RENT_STAT"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Total allowable deductions", bold=True)
    style_calc(ws.cell(r, 2), f"={C['RENT_INS']}+{C['RENT_INT']}+{C['RENT_MUN']}+{C['RENT_PRE']}+{C['RENT_OTH']}+{C['RENT_STAT']}")
    C["RENT_DED"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "INCOME FROM RENT (ordinary)", bold=True)
    style_calc(ws.cell(r, 2), f"=MAX({C['RENT_GRV']}-{C['RENT_DED']},0)")
    C["RENT_TAXABLE"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE, size=12); ws.cell(r, 2).number_format = NUM
    r += 2

    r = subsection(ws, r, "s.39 SPECIAL INCOME FROM RENT  (optional — default OFF)")
    style_label(ws.cell(r, 1), "Apply s.39 unspent statutory deduction as special income?", bold=True)
    style_input(ws.cell(r, 2), "No", number=False)
    C["RENT_S39"] = f"$B${r}"
    add_dv(ws, '"Yes,No"', f"B{r}")
    style_note(ws.cell(r, 3), "VERIFY. Default No preserves the traditional statutory-% computation used in most ICAB answers. Switch to Yes only if the question clearly requires s.39.")
    ws.merge_cells(f"C{r}:H{r}")
    r += 1
    style_label(ws.cell(r, 1), "Unspent statutory deduction (statutory − actual repair, not below 0)")
    style_calc(ws.cell(r, 2), f"=MAX({C['RENT_STAT']}-{C['RENT_ACTREP']},0)")
    C["RENT_UNSPENT"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "SPECIAL INCOME FROM RENT (s.39)", bold=True)
    style_calc(ws.cell(r, 2), f'=IF({C["RENT_S39"]}="Yes",{C["RENT_UNSPENT"]},0)')
    C["RENT_SPECIAL"] = f"$B${r}"
    r += 1
    style_calc(ws.cell(r, 2), f'=IF({C["RENT_DED"]}>{C["RENT_GRV"]}, "CHECK REQUIRED — deductions exceed GRV","OK")', number=False)
    style_label(ws.cell(r, 1), "Error check")
    ws.cell(r, 2).number_format = "@"
    r += 2

    r = section(ws, r, "D", "TAX-TREATMENT TABLE")
    header_row(ws, r, ["Income item", "Gross amount", "Taxable amount", "Exempt amount", "Deduction / adjustment", "Net taxable amount", "Relevant provision", "Explanation", "", "", "", ""], SUBSEC)
    r += 1
    style_label(ws.cell(r, 1), "Gross rental value")
    style_calc(ws.cell(r, 2), f"={C['RENT_GRV']}")
    style_calc(ws.cell(r, 3), f"={C['RENT_GRV']}")
    style_calc(ws.cell(r, 4), 0)
    style_calc(ws.cell(r, 5), f"={C['RENT_DED']}")
    style_calc(ws.cell(r, 6), f"={C['RENT_TAXABLE']}")
    ws.cell(r, 7, "s.37–38"); ws.cell(r, 8, "Ordinary income from rent")
    r += 2

    r = section(ws, r, "E", "WORKED EXAMPLE  —  Mr. Md. Karim Rahman")
    write_wrapped(ws, r, 1,
        "STEP 1 — FACTS. Residential flat: actual rent 480,000; annual value 450,000; adjustable advance relating to the year 40,000; "
        "service charge 24,000; vacant 2 months (electricity bills available) 80,000; municipal tax 18,000; insurance 8,000; "
        "housing-loan interest 95,000; actual repairs 50,000.",
        "L", 36, font(size=9), LIGHT_GOLD)
    r += 1
    write_wrapped(ws, r, 1,
        "STEP 2–4. B = max(480,000, 450,000) = 480,000. GRV = 480,000 + 40,000 + 24,000 − 80,000 = 464,000. "
        "Statutory 25% = 116,000. Deductions = 8,000 + 95,000 + 18,000 + 116,000 = 237,000. "
        "TAXABLE INCOME FROM RENT = 227,000. Actual repair is not claimed extra. s.39 toggle is No.",
        "L", 36, font(size=9), LIGHT_TEAL)
    r += 1
    style_label(ws.cell(r, 1), "Taxable rent (live)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['RENT_TAXABLE']}")
    r += 2
    write_wrapped(ws, r, 1,
        "STEP 5 — WHY. Annual value is a floor, not a ceiling — when actual rent is higher, use actual. "
        "Vacancy is allowed only with electricity-bill evidence. The 25% already covers repair, so adding 50,000 again would be a classic wrong answer. "
        "Interest is a separate actual deduction.",
        "L", 32, font(size=9), WHITE)
    r += 2

    r = close_head(ws, r, [
        "Write the s.37 formula in the answer: A = (B+C+D+E)−F. Examiners look for it.",
        "25% vs 30% depends on commercial vs non-commercial use, not on whether the owner is a company.",
        "Self-occupied house: ITA 2023 does not give a notional-rent charge in the same way as some other systems. If the property is not let, do not invent annual-value income unless the question requires it. VERIFY.",
        "Unadjustable security deposit / salami: historically could be deemed income; under s.37 unadjustable advance is not in GRV. If the question uses the word 'salami', discuss deemed-income provisions separately (often other sources / special). VERIFY.",
        "Hotel is business. A row of let-out shops is rent. Classification is a free mark.",
        "Part-year or part-property letting: prorate the statutory %.",
        "TDS on rent is a credit on the Home sheet.",
        "Do not deduct vacancy and also use a reduced 'actual rent for occupied months' as B — that double-counts vacancy.",
    ], [
        "Default example is a non-commercial let-out flat. Change Use to Commercial to switch the statutory % to 30%.",
        "s.39 default is off. Turn it on only with a stated assumption.",
        "Non-house-property letting (machinery, bare land) uses s.38(2), not the 25%/30%. Use the notes if the question is of that type.",
    ], [
        "ITA 2023 ss.35–39.",
        "Form IT-11GA rental schedule (useful presentation).",
        "Finance Act 2024 clarifications on advance, service charge, vacancy evidence.",
    ])
    define_name(wb, "OUT_RENT_TAXABLE", ws.title, C["RENT_TAXABLE"])
    define_name(wb, "OUT_RENT_SPECIAL", ws.title, C["RENT_SPECIAL"])
    return r


def build_agriculture(ws, wb):
    r = start_head(
        ws,
        "Income from Agriculture",
        "ITA 2023  Chapter IV  ss.40–44  |  Tea/rubber 60% agri + 40% business  |  No books → 60% of market value deemed expense (s.43)  |  Exemption only if almost exclusive agri income",
    )
    r = year_banner(ws, r)
    r += 1
    r = section(ws, r, "A", "QUICK CONCEPT / DEFINITION")
    for t in [
        "Definition: Income from activities related to agriculture is classified as income from agriculture (s.40(1)). Agriculture includes horticulture, animal husbandry and allied activities as defined in the section — read the question's activity against s.40 rather than against Indian s.2(1A).",
        "Tea and rubber produced and processed by the assessee: 40% of sale proceeds is business income and 60% is agricultural income (s.40(2)). Split them; do not leave 100% here.",
        "Allowable deductions (s.42): land development tax / rent; cultivation, development and maintenance; interest on agricultural loans; repair of agricultural machinery and cattle-rearing / processing / transport costs; insurance; depreciation (3rd Schedule); other expenditure wholly and exclusively for agriculture that is not capital and not personal. Only the agri portion of a mixed expense is allowed.",
        "No proper books (s.43): 60% of the market value of agricultural produce is deemed allowable expenditure (not applicable to adhi / barga / bhaga / share-cropping received by a landowner).",
        "s.44: no deduction if applicable TDS provisions were ignored.",
        "Exemption (FO 2025, commonly tested): agricultural income up to BDT 500,000 is exempt if the assessee has no income other than agriculture and financial assets. The moment there is employment, rent, business, CG or other sources, the exemption falls away. Separate (and year-sensitive) reliefs exist for poultry / hatchery / dairy etc. — VERIFY amount and conditions.",
        "ICAB points: show gross receipts, then expenses, then exemption test. Do not call all rural income 'agricultural'. Sale of agricultural land is generally capital gain, not this head (unless it is produce). Livestock sold as a farm activity is usually this head.",
    ]:
        write_wrapped(ws, r, 1, "•  " + t, "L", 30, font(size=9), LIGHT_NAVY)
        r += 1
    r += 1

    r = section(ws, r, "B", "TYPES OF INCOME  —  TAX TREATMENT")
    header_row(ws, r, ["Particular", "Tax treatment", "Relevant provision", "Example / exam note", "", "", "", "", "", "", "", ""], NAVY)
    r += 1
    for i, rowt in enumerate([
        ("Sale of paddy, jute, vegetables, fruit", "This head", "s.40", "Core agri receipts."),
        ("Livestock / poultry / fishery carried on as agriculture", "This head (unless a separate SRO applies)", "s.40; SRO — VERIFY", "Industrial-scale poultry may have a special SRO."),
        ("Tea / rubber proceeds", "60% here, 40% business", "s.40(2)", "Always split."),
        ("Adhi / barga / bhaga share of produce", "This head; s.43 deemed 60% expense does not apply", "s.43(2)", "Landowner's share."),
        ("Sale of agricultural land / orchard as capital asset", "Capital gain, not this head", "s.57", "Classification trap."),
        ("Land development tax, seed, fertiliser, labour, irrigation, interest", "Allowable", "s.42", "Wholly and exclusively; not capital."),
        ("Personal drawings / household consumption of produce", "Not an expense; may need a receipt adjustment", "s.42", "If consumed, either add to receipts or disallow the cost."),
        ("No books of account", "Deemed expense = 60% of market value of produce", "s.43", "Overrides itemised expenses."),
    ]):
        bg = ALT if i % 2 == 0 else WHITE
        ws.cell(r, 1, rowt[0]); ws.cell(r, 2, rowt[1]); ws.cell(r, 3, rowt[2])
        ws.merge_cells(f"D{r}:L{r}"); ws.cell(r, 4, rowt[3])
        for col in range(1, 13):
            ws.cell(r, col).font = font(size=8); ws.cell(r, col).fill = fill(bg); ws.cell(r, col).border = thin; ws.cell(r, col).alignment = WRAP_TL
        r += 1
    r += 1

    r = section(ws, r, "C", "COMPUTATION TEMPLATE")
    style_label(ws.cell(r, 1), "Proper books of account maintained?", bold=True)
    style_input(ws.cell(r, 2), "Yes", number=False)
    C["AG_BOOKS"] = f"$B${r}"
    add_dv(ws, '"Yes,No"', f"B{r}")
    r += 1

    header_row(ws, r, ["Agricultural receipt", "Gross (BDT)", "Of which tea/rubber (40% to business)", "Agri portion", "Note", "", "", "", "", "", "", ""], NAVY)
    r += 1
    recs = [
        ("Sale of paddy / rice / other crops", 850000, 0),
        ("Sale of vegetables / fruit / horticulture", 120000, 0),
        ("Livestock / poultry / dairy / fishery receipts", 80000, 0),
        ("Tea / rubber sale proceeds (if any)", 0, 0),
        ("Share of produce (adhi/barga/bhaga)", 0, 0),
        ("Other agricultural receipts", 0, 0),
        ("Produce consumed by household (add to receipts)", 0, 0),
    ]
    rec_start = r
    for lab, amt, tea in recs:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        # tea/rubber column: only the tea row should have the full amount copied by user into col C
        style_input(ws.cell(r, 3), amt if "Tea / rubber" in lab else 0, number=True)
        style_calc(ws.cell(r, 4), f"=B{r}-C{r}*0.4")
        style_note(ws.cell(r, 5), "Col C = tea/rubber proceeds on that row; 40% of Col C leaves this head.")
        ws.merge_cells(f"E{r}:H{r}")
        r += 1
    rec_end = r - 1
    style_label(ws.cell(r, 1), "GROSS AGRICULTURAL RECEIPTS (after 40% tea/rubber split)", bold=True)
    style_calc(ws.cell(r, 2), f"=SUM(B{rec_start}:B{rec_end})")
    style_calc(ws.cell(r, 4), f"=SUM(D{rec_start}:D{rec_end})")
    C["AG_GROSS_ALL"] = f"$B${r}"
    C["AG_GROSS"] = f"$D${r}"
    ws.cell(r, 1).fill = fill(NAVY); ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 4).fill = fill(NAVY); ws.cell(r, 4).font = font(bold=True, color=WHITE); ws.cell(r, 4).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "40% of tea/rubber transferred to business (memo)")
    style_calc(ws.cell(r, 2), f"=SUM(C{rec_start}:C{rec_end})*0.4")
    C["AG_TO_BUS"] = f"$B${r}"
    r += 2

    r = subsection(ws, r, "ALLOWABLE AGRICULTURAL EXPENSES  (s.42)  —  ignored if books = No")
    exps = [
        ("Land development tax / rent of agricultural land", 12000),
        ("Seeds / seedlings / plants", 40000),
        ("Fertiliser / pesticide / manure", 55000),
        ("Labour / wages (cultivation)", 180000),
        ("Irrigation / fuel / electricity for agriculture", 35000),
        ("Interest on agricultural loan", 20000),
        ("Transport / processing of produce", 18000),
        ("Cattle feed / livestock rearing cost", 25000),
        ("Repair of agricultural machinery / implements", 0),
        ("Insurance of land / crop / cattle", 0),
        ("Tax depreciation (3rd Schedule) on agri assets", 0),
        ("Other wholly agri revenue expenses", 0),
    ]
    exp_start = r
    for lab, amt in exps:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        r += 1
    exp_end = r - 1
    style_label(ws.cell(r, 1), "Total itemised expenses")
    style_calc(ws.cell(r, 2), f"=SUM(B{exp_start}:B{exp_end})")
    C["AG_EXP_ITEM"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "s.43 deemed expense (60% of agri receipts) if no books")
    style_calc(ws.cell(r, 2), f"=0.6*{C['AG_GROSS']}")
    C["AG_EXP_43"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Expense allowed", bold=True)
    style_calc(ws.cell(r, 2), f'=IF({C["AG_BOOKS"]}="Yes",{C["AG_EXP_ITEM"]},{C["AG_EXP_43"]})')
    C["AG_EXP"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "NET AGRICULTURAL INCOME before exemption", bold=True)
    style_calc(ws.cell(r, 2), f"=MAX({C['AG_GROSS']}-{C['AG_EXP']},0)")
    C["AG_NET"] = f"$B${r}"
    r += 2

    r = subsection(ws, r, "EXEMPTION TEST  (FO 2025 — VERIFY)")
    style_label(ws.cell(r, 1), "Has the assessee any income other than agriculture and financial assets?", bold=True)
    style_input(ws.cell(r, 2), "Yes", number=False)
    C["AG_OTHER"] = f"$B${r}"
    add_dv(ws, '"Yes,No"', f"B{r}")
    style_note(ws.cell(r, 3), "Pre-filled Yes because Mr. Rahman has employment, rent, business, CG and other sources. Change to No only for a pure farmer (+ bank interest).")
    ws.merge_cells(f"C{r}:H{r}")
    r += 1
    style_label(ws.cell(r, 1), "Exemption allowed")
    style_calc(ws.cell(r, 2), f'=IF({C["AG_OTHER"]}="No",MIN({C["AG_NET"]},P_AgriExempt),0)')
    C["AG_EXEMPT"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "TAXABLE INCOME FROM AGRICULTURE", bold=True)
    style_calc(ws.cell(r, 2), f"={C['AG_NET']}-{C['AG_EXEMPT']}")
    C["AG_TAXABLE"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE, size=12); ws.cell(r, 2).number_format = NUM
    r += 2

    r = section(ws, r, "D", "TAX-TREATMENT TABLE")
    header_row(ws, r, ["Income item", "Gross amount", "Taxable amount", "Exempt amount", "Deduction / adjustment", "Net taxable amount", "Relevant provision", "Explanation", "", "", "", ""], SUBSEC)
    r += 1
    style_label(ws.cell(r, 1), "Agricultural receipts (agri portion)")
    style_calc(ws.cell(r, 2), f"={C['AG_GROSS']}")
    style_calc(ws.cell(r, 3), f"={C['AG_TAXABLE']}")
    style_calc(ws.cell(r, 4), f"={C['AG_EXEMPT']}")
    style_calc(ws.cell(r, 5), f"={C['AG_EXP']}")
    style_calc(ws.cell(r, 6), f"={C['AG_TAXABLE']}")
    ws.cell(r, 7, "s.40–44"); ws.cell(r, 8, "After expenses and exclusive-income exemption test")
    r += 2

    r = section(ws, r, "E", "WORKED EXAMPLE  —  Mr. Md. Karim Rahman")
    write_wrapped(ws, r, 1,
        "STEP 1 — FACTS. Crop sales 850,000; vegetables 120,000; livestock 80,000. Expenses: land tax 12,000; seed 40,000; "
        "fertiliser 55,000; labour 180,000; irrigation 35,000; agri-loan interest 20,000; transport 18,000; cattle feed 25,000. "
        "Books are maintained. He also has employment and other heads.",
        "L", 36, font(size=9), LIGHT_GOLD)
    r += 1
    write_wrapped(ws, r, 1,
        "STEP 2–4. Gross 1,050,000 − expenses 385,000 = 665,000. Exemption = 0 because he has other heads. "
        "TAXABLE INCOME FROM AGRICULTURE = 665,000.",
        "L", 24, font(size=9), LIGHT_TEAL)
    r += 1
    style_label(ws.cell(r, 1), "Taxable agriculture (live)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['AG_TAXABLE']}")
    r += 2
    write_wrapped(ws, r, 1,
        "STEP 5 — WHY. Students often deduct the BDT 5 lakh agri exemption even when the assessee is a salaried person. "
        "The exemption is a small-farmer relief, not a standard deduction. Because books exist, s.43 is not used.",
        "L", 28, font(size=9), WHITE)
    r += 2

    r = close_head(ws, r, [
        "Always run the exclusive-income test before claiming the 5-lakh exemption.",
        "Tea/rubber: 60/40 split is statutory — even if the question does not remind you.",
        "No books → ignore the itemised list and take 60% of market value. Do not take both.",
        "Sale of agri land ≠ agri income.",
        "Household consumption: add to receipts or disallow cost — do not ignore it if the question gives a figure.",
        "Interest on a loan used to buy a city apartment is not an agri deduction even if the assessee is a farmer.",
        "If TDS on a contract labour payment was not deducted, s.44 can kill that deduction.",
        "Poultry / dairy special SROs change almost every budget — if the question is a poultry farm, look up the exam-year SRO rather than using this general head blindly.",
    ], [
        "Default exemption amount is P_AgriExempt on the Home sheet.",
        "s.41 special agri income (disposal of agri assets vs WDV) is not in the default example — compute it on the Capital Gain / special working if the question has a tractor sale.",
        "40% tea/rubber memo is not automatically added on the Business sheet; if you use tea/rubber, copy that memo into a business add-line.",
    ], [
        "ITA 2023 ss.40–44.",
        "Third Schedule — depreciation on agri assets.",
        "Finance Ordinance 2025 — BDT 500,000 exclusive-agri exemption. VERIFY.",
        "Relevant poultry / dairy / fishery SRO of the exam year — VERIFY.",
    ])
    define_name(wb, "OUT_AGRI_TAXABLE", ws.title, C["AG_TAXABLE"])
    define_name(wb, "OUT_AGRI_EXEMPT", ws.title, C["AG_EXEMPT"])
    define_name(wb, "OUT_AGRI_GROSS", ws.title, C["AG_GROSS"])
    return r
