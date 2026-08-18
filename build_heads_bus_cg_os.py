# Business, Capital Gain, Other Sources + main()

def build_business(ws, wb):
    r = start_head(
        ws,
        "Income from Business",
        "ITA 2023  Chapter V  ss.45–56  |  Start from profit as per accounts  |  Add disallowables (s.55)  |  Substitute tax depreciation (3rd Schedule)  |  Special business income s.56",
    )
    r = year_banner(ws, r)
    r += 1
    r = section(ws, r, "A", "QUICK CONCEPT / DEFINITION")
    for t in [
        "Definition: Profits and gains of a business carried on (or deemed to be carried on) in the income year, plus specified items such as association service-income, FMV of business benefits, management fees, certain lease income, realised exchange gains and income of a discontinued business (s.45). 'Business' includes trade, commerce, manufacture, a venture in that nature, and profession/vocation (s.2).",
        "Computation (s.46): start from the accounting profit for that distinct business, then apply the Chapter V deductions (ss.49–54) and the s.55 disallowances. Speculation is kept separate (s.48).",
        "Allowable in outline (s.49–54): wholly and exclusively revenue expenditure for the business; purchases and inventory; taxes other than income tax; rent; employee costs that are employment income of the staff; repairs, insurance, utilities; realised FX loss; WPPF up to 5% of disclosed NP; tax depreciation (3rd Schedule); bad debts that meet s.51; interest within s.52–53 limits.",
        "Classic s.55 disallowances (exam list): personal; capital; income tax; general provisions / contingent liabilities / impairment (not specific); cash salary; cash rent; other payments ≥ BDT 50,000 otherwise than by bank transfer (VERIFY threshold); perquisite per employee above BDT 1,000,000 (employer's assessment); royalty / technical / intra-group / HO expense above 10% of disclosed net business profit; foreign travel above 0.50% of turnover; promotional expense (ex-advertisement) above 0.50% of turnover; entertainment above 4% of the first BDT 1,000,000 of income (computed before this deduction) plus 2% of the remainder; unpaid TDS cases; partner salary/interest in a firm; unrecognised-fund payments.",
        "s.56 special business income: amounts disallowed under s.55 (other than certain RoU depreciation / finance items) are special business income — taxed at the regular rate with no set-off, no carry-forward and no 3rd Schedule depreciation against them. In a straightforward add-back question the numerical result is the same as adding back to business profit; show a memo if the examiner asks for s.56 separately. Do not double-count.",
        "Unrealised FX and unrealised fair-value gains/losses are not tax items. Only realised FX enters the computation.",
        "ICAB presentation: Profit as per accounts + disallowable expenses − allowable items not charged / income taxed under another head − tax depreciation + accounting depreciation = taxable business income.",
    ]:
        write_wrapped(ws, r, 1, "•  " + t, "L", 32, font(size=9), LIGHT_NAVY)
        r += 1
    r += 1

    r = section(ws, r, "B", "TYPES OF ADJUSTMENT  —  TAX TREATMENT")
    header_row(ws, r, ["Particular", "Tax treatment", "Relevant provision", "Example / exam note", "", "", "", "", "", "", "", ""], NAVY)
    r += 1
    for i, rowt in enumerate([
        ("Net profit as per accounts (PBT)", "Starting point", "s.46", "Use before-tax profit."),
        ("Accounting depreciation", "Add back", "s.55 / 3rd Schedule", "Replace with tax depreciation."),
        ("Tax depreciation (3rd Schedule)", "Deduct", "3rd Schedule", "Normal / initial / accelerated as applicable."),
        ("Personal drawings / household expenses", "Add back", "s.55", "Never allowable."),
        ("Capital expenditure charged to P&L", "Add back", "s.55", "May become a depreciable addition."),
        ("Income tax / tax penalty / fine", "Add back", "s.55", "Income tax is not a business expense."),
        ("General provision for bad debts", "Add back", "s.51 / s.55", "Only a specific write-off that was previously offered is allowable."),
        ("Entertainment — excess over 4% / 2%", "Add back excess", "s.55", "Base = income before this deduction."),
        ("Cash salary / cash rent", "Add back", "s.55", "Must be bank transfer."),
        ("Cash purchase ≥ threshold", "Add back", "s.55", "Default threshold BDT 50,000 — VERIFY."),
        ("Perquisite per employee > BDT 1,000,000", "Add back excess (employer)", "s.55", "Does not reduce the employee's income."),
        ("Royalty / HO / intra-group > 10% of NP", "Add back excess", "s.55", "Net business profit from own operations."),
        ("Foreign travel > 0.50% of turnover", "Add back excess", "s.55", "Govt-service travel may be excepted."),
        ("Promotion (ex-advertisement) > 0.50% of TO", "Add back excess", "s.55", "Advertisement itself is outside this cap."),
        ("Unrealised FX / FV loss", "Add back", "practice / s.55", "Only realised FX is allowed."),
        ("FDR interest / dividend / rent credited in P&L", "Deduct (taxed under other head)", "s.30, s.62, s.36", "Avoid double taxation."),
        ("Donation (unless a business expense)", "Add back; may be rebate", "s.55; Sixth Schedule Part 3", "Rebate is not a P&L deduction."),
        ("WPPF ≤ 5% of disclosed NP", "Allowable", "s.49", "Excess add back."),
    ]):
        bg = ALT if i % 2 == 0 else WHITE
        ws.cell(r, 1, rowt[0]); ws.cell(r, 2, rowt[1]); ws.cell(r, 3, rowt[2])
        ws.merge_cells(f"D{r}:L{r}"); ws.cell(r, 4, rowt[3])
        for col in range(1, 13):
            ws.cell(r, col).font = font(size=8); ws.cell(r, col).fill = fill(bg)
            ws.cell(r, col).border = thin; ws.cell(r, col).alignment = WRAP_TL
        r += 1
    r += 1

    r = section(ws, r, "C", "TAX RECONCILIATION  —  PROFIT AS PER ACCOUNTS → TAXABLE BUSINESS INCOME")
    style_label(ws.cell(r, 1), "Turnover / receipts (for % limits)", bold=True)
    style_input(ws.cell(r, 2), 12000000, number=True)
    C["BUS_TO"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Net profit as per accounts (before income tax)", bold=True)
    style_input(ws.cell(r, 2), 1850000, number=True)
    C["BUS_NP"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Entertainment charged in the accounts")
    style_input(ws.cell(r, 2), 80000, number=True)
    C["BUS_ENT"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Income before entertainment (auto)")
    style_calc(ws.cell(r, 2), f"={C['BUS_NP']}+{C['BUS_ENT']}")
    C["BUS_IBE"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Allowable entertainment (4% of first 10 lakh + 2% of rest)")
    style_calc(ws.cell(r, 2), f"=MIN({C['BUS_IBE']},1000000)*0.04+MAX({C['BUS_IBE']}-1000000,0)*0.02")
    C["BUS_ENT_OK"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Entertainment disallowed")
    style_calc(ws.cell(r, 2), f"=MAX({C['BUS_ENT']}-{C['BUS_ENT_OK']},0)")
    C["BUS_ENT_DIS"] = f"$B${r}"
    r += 2

    r = subsection(ws, r, "ADD: DISALLOWABLE / NON-DEDUCTIBLE ITEMS  (s.55)")
    adds = [
        ("Accounting depreciation", 220000),
        ("Personal expenses charged to P&L", 45000),
        ("Capital expenditure charged to P&L", 80000),
        ("General provision for bad debts / contingent liability", 50000),
        ("Unapproved donation / non-business donation", 30000),
        ("Fine / penalty / income-tax charged (if any)", 10000),
        ("Salary paid otherwise than by bank transfer", 25000),
        ("Rent paid otherwise than by bank transfer", 60000),
        ("Other expense ≥ 50,000 paid otherwise than by bank transfer", 70000),
        ("Unrealised foreign-exchange / fair-value loss", 15000),
        ("Perquisite excess over BDT 1,000,000 per employee (employer)", 0),
        ("Royalty / technical / HO / intra-group excess over 10% of NP", 0),
        ("Foreign travel excess over 0.50% of turnover", 0),
        ("Promotional expense (ex-advertisement) excess over 0.50% of TO", 0),
        ("Other s.55 disallowance (describe in notes)", 0),
    ]
    add_start = r
    for lab, amt in adds:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        style_input(ws.cell(r, 3), "Disallowable", number=False)
        r += 1
    add_end = r - 1
    add_dv(ws, '"Disallowable,Partially Allowable,Allowable"', f"C{add_start}:C{add_end}")
    style_label(ws.cell(r, 1), "Subtotal — itemised add-backs", bold=True)
    style_calc(ws.cell(r, 2), f"=SUM(B{add_start}:B{add_end})")
    C["BUS_ADD_SUB"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Add: entertainment disallowed (from calculator)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['BUS_ENT_DIS']}")
    r += 1
    style_label(ws.cell(r, 1), "TOTAL ADD-BACKS", bold=True)
    style_calc(ws.cell(r, 2), f"={C['BUS_ADD_SUB']}+{C['BUS_ENT_DIS']}")
    C["BUS_ADD"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(WARN_FILL); ws.cell(r, 1).font = font(bold=True, color=WARN_FONT)
    r += 2

    r = subsection(ws, r, "LESS: ALLOWABLE ADJUSTMENTS / INCOME TAXED UNDER ANOTHER HEAD")
    less = [
        ("Tax depreciation (3rd Schedule)", 180000),
        ("Income credited in P&L but taxable under Financial Assets", 0),
        ("Income credited in P&L but taxable under Rent", 0),
        ("Income credited in P&L but taxable as Capital Gain", 0),
        ("Allowable expense not charged in accounts", 0),
        ("Specific bad debt written off (if not already charged, deduct here)", 0),
        ("Other allowable deduction", 0),
    ]
    less_start = r
    for lab, amt in less:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        r += 1
    less_end = r - 1
    style_label(ws.cell(r, 1), "TOTAL DEDUCTIONS FROM ACCOUNTING PROFIT", bold=True)
    style_calc(ws.cell(r, 2), f"=SUM(B{less_start}:B{less_end})")
    C["BUS_LESS"] = f"$B${r}"
    r += 2

    style_label(ws.cell(r, 1), "TAXABLE INCOME FROM BUSINESS", bold=True)
    style_calc(ws.cell(r, 2), f"={C['BUS_NP']}+{C['BUS_ADD']}-{C['BUS_LESS']}")
    C["BUS_TAXABLE"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE, size=12); ws.cell(r, 2).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "Memo: special business income (s.56) = s.55 add-backs other than depreciation substitution")
    # s.56 typically = all s.55 disallowances except depreciation-related. Accounting dep is substituted, not really s.56.
    # We'll treat special = total add-backs minus accounting depreciation (which is a substitution, not a 'disallowance' in the s.56 sense)
    style_calc(ws.cell(r, 2), f"={C['BUS_ADD']}-B{add_start}")
    C["BUS_SPECIAL"] = f"$B${r}"
    style_note(ws.cell(r, 3), "Memo only. Already inside taxable business income via add-backs. Do not add again on the Home sheet.")
    ws.merge_cells(f"C{r}:H{r}")
    r += 2

    r = section(ws, r, "D", "TAX-TREATMENT TABLE")
    header_row(ws, r, ["Income item", "Gross amount", "Taxable amount", "Exempt amount", "Deduction / adjustment", "Net taxable amount", "Relevant provision", "Explanation", "", "", "", ""], SUBSEC)
    r += 1
    style_label(ws.cell(r, 1), "Profit as per accounts ± tax adjustments")
    style_calc(ws.cell(r, 2), f"={C['BUS_NP']}")
    style_calc(ws.cell(r, 3), f"={C['BUS_TAXABLE']}")
    style_calc(ws.cell(r, 4), 0)
    style_calc(ws.cell(r, 5), f"={C['BUS_ADD']}-{C['BUS_LESS']}")
    style_calc(ws.cell(r, 6), f"={C['BUS_TAXABLE']}")
    ws.cell(r, 7, "ss.45–56"); ws.cell(r, 8, "Reconciliation from accounting profit")
    r += 2

    r = section(ws, r, "E", "WORKED EXAMPLE  —  Mr. Md. Karim Rahman (sole-prop trading)")
    write_wrapped(ws, r, 1,
        "STEP 1 — FACTS. Turnover 12,000,000. Net profit (before tax) 1,850,000 after charging: accounting depreciation 220,000; "
        "personal 45,000; capital furniture 80,000; general provision 50,000; entertainment 80,000; unapproved donation 30,000; "
        "penalty 10,000; cash salary 25,000; cash rent 60,000; cash purchases 70,000; unrealised FX loss 15,000. "
        "Tax depreciation (3rd Schedule) is 180,000. Specific bad debt of 20,000 was already charged and is allowable (no add-back). "
        "Realised FX loss 8,000 was charged and is allowable.",
        "L", 56, font(size=9), LIGHT_GOLD)
    r += 1
    write_wrapped(ws, r, 1,
        "STEP 2–4. Entertainment base = 1,850,000 + 80,000 = 1,930,000. Allowable = 4%×1,000,000 + 2%×930,000 = 58,600. Disallow 21,400. "
        "Add-backs = 220,000+45,000+80,000+50,000+30,000+10,000+25,000+60,000+70,000+15,000+21,400 = 626,400. "
        "Less tax depreciation 180,000. TAXABLE BUSINESS INCOME = 1,850,000 + 626,400 − 180,000 = 2,296,400.",
        "L", 44, font(size=9), LIGHT_TEAL)
    r += 1
    style_label(ws.cell(r, 1), "Taxable business income (live)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['BUS_TAXABLE']}")
    r += 2
    write_wrapped(ws, r, 1,
        "STEP 5 — WHY. ICAB wants the reconciliation, not a re-drafted P&L. Personal, capital, provisions, cash payments and excess entertainment "
        "are the marks-rich add-backs. Substituting tax depreciation is compulsory — leaving accounting depreciation in place is a common fail. "
        "s.56 is noted as a memo; because there is no loss to set off, adding back once is enough.",
        "L", 36, font(size=9), WHITE)
    r += 2

    r = close_head(ws, r, [
        "Always start from 'Net profit as per accounts' and reconcile. Do not rebuild the profit from turnover unless accounts are unreliable (s.75).",
        "Entertainment limit is on income BEFORE entertainment, not on turnover (promotion/foreign travel use turnover).",
        "Cash salary and cash rent are 100% disallowed — there is no 'small amount' exception in the usual s.55 wording.",
        "Perquisite cap of BDT 10 lakh is an employer disallowance. The employee is still taxed on the full s.33 value.",
        "If FDR interest sits in 'other income' on the P&L, remove it here and tax it under Financial Assets.",
        "Unrealised losses never reduce taxable business income.",
        "Related-party rent or salary still needs bank transfer and substance; transfer-pricing is a separate discussion if the question is a company.",
        "Show s.56 as a memo if asked; never add it on top of an already-adjusted taxable profit.",
        "Speculation business (s.48) cannot be mixed with regular business — keep a separate working.",
        "Losses: business loss generally cannot be set off against salary (s.70 — VERIFY the current set-off table) and is carried forward 6 years.",
    ], [
        "Cash-payment threshold of BDT 50,000 is the commonly cited figure — VERIFY s.55 of your reprint.",
        "Entertainment 4%/2% follows the long-standing rule restated in ITA 2023 commentaries. If your manual prints a different table, overwrite the formula.",
        "Tax depreciation rates are in the 3rd Schedule (buildings, plant, vehicles, etc.). The example uses a given figure rather than a full asset register.",
        "Default NP is before income tax, so no add-back of current-tax expense is required unless you charge tax in the NP figure.",
    ], [
        "ITA 2023 ss.45–56 (Chapter V).",
        "s.49 general deductions; s.51 bad debts; s.52–53 interest; s.54 conditions; s.55 disallowances; s.56 special business income.",
        "Third Schedule — depreciation.",
        "s.70–71 set-off and carry-forward; s.72 method of accounting.",
    ])
    define_name(wb, "OUT_BUS_TAXABLE", ws.title, C["BUS_TAXABLE"])
    define_name(wb, "OUT_BUS_SPECIAL", ws.title, C["BUS_SPECIAL"])
    return r


def build_cg(ws, wb):
    r = start_head(
        ws,
        "Capital Gain",
        "ITA 2023  Chapter VI  ss.57–61  |  Consideration = higher of actual and FMV  |  Minus cost of acquisition, improvement and transfer expenses  |  Holding period drives the rate",
    )
    r = year_banner(ws, r)
    r += 1
    r = section(ws, r, "A", "QUICK CONCEPT / DEFINITION")
    for t in [
        "Definition: Capital gains are profits and gains from the transfer of a capital asset (s.57). Capital asset includes property of any kind, a business as a unit, and stocks/shares, but excludes stock-in-trade / consumables / raw materials and personal effects held exclusively for personal use (wearing apparel, jewellery, furniture, personal vehicles, etc. — read the exact s.2 definition in your reprint).",
        "Transfer includes sale, exchange, relinquishment, extinguishment of a right. It generally does NOT include gift, bequest, will, or certain liquidations / partitions. A gift received is therefore usually Other Sources (if taxable) rather than CG of the donor.",
        "Computation (s.58): take the HIGHER of full value of consideration and fair market value; deduct cost of acquisition, cost of improvement and expenditure wholly on the transfer. No indexation regime like India's s.48. s.60 limits deductions (including where TDS was required and not deducted).",
        "Rates (individual — VERIFY Seventh Schedule / Finance Act): held for not more than 5 years → generally regular slab (except listed shares, which are typically 15% if taxable at all). Held for more than 5 years → 15%, or tax deducted at registration under s.125 if higher (minimum tax, s.163). Listed-share CG of an ordinary investor is commonly exempt up to BDT 5 million (not sponsor / director / placement shares).",
        "Depreciable business/agri assets: excess of sale proceeds over WDV up to original cost is usually business/agri balancing charge; excess over original cost is capital gain (ss.41 / business equivalent). Do not put the whole surplus here.",
        "ICAB points: always compare consideration with FMV; always state the holding period; never net brokerage after tax; land registration TDS is a minimum tax on that gain, not a deduction from the gain.",
    ]:
        write_wrapped(ws, r, 1, "•  " + t, "L", 32, font(size=9), LIGHT_NAVY)
        r += 1
    r += 1

    r = section(ws, r, "B", "TYPES OF INCOME  —  TAX TREATMENT")
    header_row(ws, r, ["Particular", "Tax treatment", "Relevant provision", "Example / exam note", "", "", "", "", "", "", "", ""], NAVY)
    r += 1
    for i, rowt in enumerate([
        ("Plot of land / building held > 5 years", "CG @ 15% (or s.125 TDS if higher)", "s.58; Seventh Schedule", "Registration TDS is minimum tax."),
        ("Plot of land / building held ≤ 5 years", "CG at regular slab", "Seventh Schedule", "Not 15%."),
        ("Listed shares — ordinary investor, gain ≤ exemption cap", "Exempt", "Sixth Schedule — VERIFY", "Default cap P_ListedCGExempt."),
        ("Listed shares — sponsor / director / placement", "Taxable (special rate — VERIFY)", "SRO / Seventh Schedule", "Do not give the ordinary-investor exemption."),
        ("Unlisted shares", "CG; rate depends on holding period", "s.57–58", "Not the listed exemption."),
        ("Personal jewellery / furniture / private car", "Generally not a capital asset (personal effects)", "s.2 definition — VERIFY", "Do not compute CG unless the definition clearly includes it."),
        ("Stock-in-trade", "Business income, not CG", "s.2 / s.45", "Classification trap."),
        ("Gift / will / bequest (donor)", "Generally not a 'transfer' for CG", "s.57", "Donee may have Other Sources."),
        ("Balancing charge on depreciable asset up to original cost", "Business / agri, not CG", "s.41 / business chapter", "Only the slice above original cost is CG."),
    ]):
        bg = ALT if i % 2 == 0 else WHITE
        ws.cell(r, 1, rowt[0]); ws.cell(r, 2, rowt[1]); ws.cell(r, 3, rowt[2])
        ws.merge_cells(f"D{r}:L{r}"); ws.cell(r, 4, rowt[3])
        for col in range(1, 13):
            ws.cell(r, col).font = font(size=8); ws.cell(r, col).fill = fill(bg)
            ws.cell(r, col).border = thin; ws.cell(r, col).alignment = WRAP_TL
        r += 1
    r += 1

    r = section(ws, r, "C", "COMPUTATION TEMPLATE  (up to 3 assets)")
    header_row(ws, r, [
        "Particulars", "Asset 1 — listed shares", "Asset 2 — plot of land", "Asset 3 (blank)",
        "", "", "", "", "", "", "", "",
    ], NAVY)
    r += 1
    # We'll use columns B, C, D for 3 assets
    labels_in = [
        ("Description", "DSE listed ordinary shares", "Residential plot, Gazipur", ""),
        ("Date of acquisition (text)", "2019-02-10", "2018-04-01", ""),
        ("Date of transfer (text)", "2025-11-20", "2026-01-15", ""),
        ("Held more than 5 years?", "Yes", "Yes", "No"),
        ("Listed share / unit?", "Yes", "No", "No"),
        ("Sponsor / director / placement share?", "No", "No", "No"),
        ("Personal effect / stock-in-trade? (exclude if Yes)", "No", "No", "No"),
    ]
    # text rows
    desc_row = r
    for lab, a, b, c in labels_in:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), a, number=False)
        style_input(ws.cell(r, 3), b, number=False)
        style_input(ws.cell(r, 4), c, number=False)
        r += 1
    add_dv(ws, '"Yes,No"', f"B{desc_row+3}:D{desc_row+6}")

    nums = [
        ("Full value of consideration received", 800000, 4500000, 0),
        ("Fair market value on transfer date", 790000, 4200000, 0),
        ("Cost of acquisition", 550000, 2000000, 0),
        ("Cost of improvement", 0, 150000, 0),
        ("Transfer expenses (brokerage, registration, commission)", 5000, 180000, 0),
        ("TDS / tax at registration (memo)", 0, 180000, 0),
    ]
    num_start = r
    for lab, a, b, c in nums:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), a, number=True)
        style_input(ws.cell(r, 3), b, number=True)
        style_input(ws.cell(r, 4), c, number=True)
        r += 1
    # rows: cons, fmv, cost, impr, exp, tds
    cons_r, fmv_r, cost_r, impr_r, exp_r, tds_r = range(num_start, num_start + 6)
    hold_r = desc_row + 3
    listed_r = desc_row + 4
    sponsor_r = desc_row + 5
    exclude_r = desc_row + 6

    style_label(ws.cell(r, 1), "Deemed consideration (higher of actual and FMV)", bold=True)
    for col in (2, 3, 4):
        style_calc(ws.cell(r, col), f"=MAX({get_column_letter(col)}{cons_r},{get_column_letter(col)}{fmv_r})")
    deem_r = r
    r += 1
    style_label(ws.cell(r, 1), "Capital gain / (loss) before exemption", bold=True)
    for col in (2, 3, 4):
        L = get_column_letter(col)
        style_calc(ws.cell(r, col), f"=IF({L}{exclude_r}=\"Yes\",0,{L}{deem_r}-{L}{cost_r}-{L}{impr_r}-{L}{exp_r})")
    gain_r = r
    r += 1
    style_label(ws.cell(r, 1), "Exempt listed-share CG (ordinary investor, gain ≤ cap, not sponsor)")
    for col in (2, 3, 4):
        L = get_column_letter(col)
        style_calc(
            ws.cell(r, col),
            f'=IF(AND({L}{listed_r}="Yes",{L}{sponsor_r}="No",{L}{gain_r}>0,{L}{gain_r}<=P_ListedCGExempt),{L}{gain_r},0)',
        )
    ex_r = r
    r += 1
    style_label(ws.cell(r, 1), "Taxable CG — regular slab (held ≤ 5 years, not listed-exempt)")
    for col in (2, 3, 4):
        L = get_column_letter(col)
        style_calc(
            ws.cell(r, col),
            f'=IF(AND({L}{hold_r}="No",{L}{ex_r}=0),MAX({L}{gain_r},0),0)',
        )
    reg_r = r
    r += 1
    style_label(ws.cell(r, 1), "Taxable CG — special 15% (held > 5 years or listed taxable)")
    for col in (2, 3, 4):
        L = get_column_letter(col)
        style_calc(
            ws.cell(r, col),
            f'=IF({L}{ex_r}>0,0,IF(OR({L}{hold_r}="Yes",{L}{listed_r}="Yes"),MAX({L}{gain_r},0),0))',
        )
    sp_r = r
    r += 2

    style_label(ws.cell(r, 1), "TOTAL EXEMPT CAPITAL GAIN", bold=True)
    style_calc(ws.cell(r, 2), f"=B{ex_r}+C{ex_r}+D{ex_r}")
    C["CG_EXEMPT"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "TOTAL CG CHARGED AT REGULAR SLAB", bold=True)
    style_calc(ws.cell(r, 2), f"=B{reg_r}+C{reg_r}+D{reg_r}")
    C["CG_REGULAR"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE); ws.cell(r, 2).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "TOTAL CG CHARGED AT 15%", bold=True)
    style_calc(ws.cell(r, 2), f"=B{sp_r}+C{sp_r}+D{sp_r}")
    C["CG_SPECIAL15"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE, size=12); ws.cell(r, 2).number_format = NUM
    r += 2

    r = section(ws, r, "D", "TAX-TREATMENT TABLE")
    header_row(ws, r, ["Income item", "Gross amount", "Taxable amount", "Exempt amount", "Deduction / adjustment", "Net taxable amount", "Relevant provision", "Explanation", "", "", "", ""], SUBSEC)
    r += 1
    style_label(ws.cell(r, 1), "Capital gains (all assets)")
    style_calc(ws.cell(r, 2), f"=B{gain_r}+C{gain_r}+D{gain_r}")
    style_calc(ws.cell(r, 3), f"={C['CG_REGULAR']}+{C['CG_SPECIAL15']}")
    style_calc(ws.cell(r, 4), f"={C['CG_EXEMPT']}")
    style_calc(ws.cell(r, 5), f"=B{cost_r}+C{cost_r}+D{cost_r}+B{impr_r}+C{impr_r}+D{impr_r}+B{exp_r}+C{exp_r}+D{exp_r}")
    style_calc(ws.cell(r, 6), f"={C['CG_REGULAR']}+{C['CG_SPECIAL15']}")
    ws.cell(r, 7, "s.58"); ws.cell(r, 8, "Split by rate on Home sheet")
    r += 2

    r = section(ws, r, "E", "WORKED EXAMPLE  —  Mr. Md. Karim Rahman")
    write_wrapped(ws, r, 1,
        "STEP 1 — FACTS. (i) Ordinary listed shares sold for 800,000 (FMV 790,000); cost 550,000; brokerage 5,000; held since 2019. "
        "(ii) Gazipur plot bought 2018 for 2,000,000; boundary wall 150,000; sold 15 Jan 2026 for 4,500,000 (FMV 4,200,000); "
        "transfer expenses 180,000; registration tax collected 180,000.",
        "L", 40, font(size=9), LIGHT_GOLD)
    r += 1
    write_wrapped(ws, r, 1,
        "STEP 2–4. Listed shares: deemed consideration 800,000 − 550,000 − 5,000 = 245,000, exempt (ordinary investor, well below 5 million). "
        "Land: deemed consideration 4,500,000 − 2,000,000 − 150,000 − 180,000 = 2,170,000, held > 5 years → special 15%. "
        "TAXABLE CAPITAL GAIN = 0 (regular) + 2,170,000 (15%).",
        "L", 36, font(size=9), LIGHT_TEAL)
    r += 1
    style_label(ws.cell(r, 1), "Regular CG (live)", bold=True); style_calc(ws.cell(r, 2), f"={C['CG_REGULAR']}")
    style_label(ws.cell(r, 3), "15% CG (live)", bold=True); style_calc(ws.cell(r, 4), f"={C['CG_SPECIAL15']}")
    style_label(ws.cell(r, 5), "Exempt (live)", bold=True); style_calc(ws.cell(r, 6), f"={C['CG_EXEMPT']}")
    r += 2
    write_wrapped(ws, r, 1,
        "STEP 5 — WHY. Consideration is the higher of actual and FMV — for the land, actual 4.5m beats FMV 4.2m. "
        "There is no indexation. The listed-share exemption is not available to a sponsor/director. "
        "s.125 tax of 180,000 is compared with 15% of 2,170,000 (= 325,500) on the Home sheet; tax on the gain is the higher figure.",
        "L", 36, font(size=9), WHITE)
    r += 2

    r = close_head(ws, r, [
        "Write: Deemed consideration (higher of actual & FMV) − cost − improvement − transfer expenses = CG.",
        "State the holding period in the first line of the working. Rate depends on it.",
        "Do not apply Indian indexation or Indian LTCG 12.5%/10% with 1.25 lakh exemption.",
        "Personal effects are outside the capital-asset definition — do not compute CG on a private car unless the question takes it out of 'personal effects'.",
        "Gift is usually not a transfer. The donee's tax, if any, is Other Sources.",
        "Listed-share exemption is lost for sponsor / director / placement shares — a favourite twist.",
        "Balancing charge on a depreciable asset is mostly business income.",
        "Loss under this head can generally be set off only against capital gains and carried forward 6 years (s.70 — VERIFY).",
    ], [
        "Exemption cap and 15% rate are Home-sheet parameters (P_ListedCGExempt, P_CGLongRate).",
        "If the exam year has withdrawn the 5-million listed-share exemption, set the cap to 0 on the Home sheet.",
        "s.61 other factors (e.g. FMV determination by the Board) are fact-specific — do not invent a valuation.",
    ], [
        "ITA 2023 ss.57–61.",
        "Seventh Schedule — rates on capital gains. VERIFY.",
        "s.125 tax at registration; s.163 minimum tax.",
        "Sixth Schedule — listed-share exemption (paragraph: VERIFY).",
    ])
    define_name(wb, "OUT_CG_REGULAR", ws.title, C["CG_REGULAR"])
    define_name(wb, "OUT_CG_SPECIAL15", ws.title, C["CG_SPECIAL15"])
    define_name(wb, "OUT_CG_EXEMPT", ws.title, C["CG_EXEMPT"])
    return r


def build_os(ws, wb):
    r = start_head(
        ws,
        "Income from Other Sources",
        "ITA 2023  Chapter VIII  ss.66–69  |  Residual head + listed items (royalty, subsidy, gifts, lottery)  |  s.67 special / deemed items  |  Lottery at 25% with no deduction",
    )
    r = year_banner(ws, r)
    r += 1
    r = section(ws, r, "A", "QUICK CONCEPT / DEFINITION")
    for t in [
        "Definition: Residual head — income that does not fall under the other six heads — plus specifically listed items (s.66): royalty, licence fees, technical-know-how fees, consideration for the right to use an intangible; government cash subsidy / incentive; transfer of certain naturally created property / goodwill (not mineral/hydrocarbon); gifts, donations and presentations; lottery / crossword / card / online-game winnings; and any other income not classified elsewhere.",
        "s.67 adds special / deemed areas (exam favourites for companies, but individuals can meet some of them): asset bought below FMV (difference); waiver of a loan; cash share-capital of an unlisted company; borrowings otherwise than through banking channel; motor-car / jeep cost above 10% of capital & reserves (50% of excess); unexplained cash credits, investments, expenditures (the old s.19 family, now recast — VERIFY the exact s.67 list in your reprint).",
        "Deductions (s.68): expenditure wholly and exclusively for earning this income, not capital, not personal, and reasonable. s.69 disallows specified items. No deduction against lottery / game winnings.",
        "Gifts: money received as a gift from a spouse, parent or child is exempt if shown in both the donor's and the recipient's returns. A gift from a friend, cousin or employer (if not employment) is taxable here. Do not confuse a gift with capital gain.",
        "Why an item is here rather than elsewhere: royalty for an intangible is OS unless it is business of licensing; a one-off examiner honorarium with no employment relationship is OS; cash incentive from the government is OS (not business, unless the question treats it as part of business receipts); lottery is always OS.",
        "ICAB points: residual does not mean 'miscellaneous dump'. First decide that it is not employment, rent, agri, business, CG or financial assets. Then apply s.66/s.67. Lottery is 25% standalone.",
    ]:
        write_wrapped(ws, r, 1, "•  " + t, "L", 30, font(size=9), LIGHT_NAVY)
        r += 1
    r += 1

    r = section(ws, r, "B", "TYPES OF INCOME  —  TAX TREATMENT")
    header_row(ws, r, ["Particular", "Tax treatment", "Relevant provision", "Why this head (not another)", "", "", "", "", "", "", "", ""], NAVY)
    r += 1
    for i, rowt in enumerate([
        ("Royalty / licence / technical-know-how / intangible use", "Taxable here (regular)", "s.66", "Not employment (no office); not business unless licensing is the business."),
        ("Government cash subsidy / cash incentive", "Taxable here (regular)", "s.66", "Not automatically agri or business."),
        ("Gift from spouse / parent / child (disclosed both sides)", "Exempt", "Sixth Schedule — VERIFY", "Not CG (no transfer computation)."),
        ("Gift from friend / other person", "Taxable here (regular)", "s.66", "Not employment unless it is a reward from the employer."),
        ("Lottery / crossword / card / online game", "Special 25%; no deduction", "s.66; Seventh Schedule", "Never slab, never net of expenses."),
        ("Examiner / guest-lecture honorarium (no employment)", "Taxable here", "s.66 residual", "If paid by the employer as salary, it is employment."),
        ("Family pension (if not employment)", "Usually this head — VERIFY", "s.66", "Government pension may be exempt — VERIFY."),
        ("Waiver of loan / unexplained credit / asset below FMV", "Deemed OS (s.67)", "s.67", "Anti-avoidance / deemed income."),
        ("Director sitting fee (if not treated as employment)", "Often OS — VERIFY facts", "s.32 vs s.66", "A company director can be an 'employee' under s.2 — check the question."),
        ("Interest already classified as financial assets", "NOT this head", "s.62", "Do not double-count bank interest here."),
    ]):
        bg = ALT if i % 2 == 0 else WHITE
        ws.cell(r, 1, rowt[0]); ws.cell(r, 2, rowt[1]); ws.cell(r, 3, rowt[2])
        ws.merge_cells(f"D{r}:L{r}"); ws.cell(r, 4, rowt[3])
        for col in range(1, 13):
            ws.cell(r, col).font = font(size=8); ws.cell(r, col).fill = fill(bg)
            ws.cell(r, col).border = thin; ws.cell(r, col).alignment = WRAP_TL
        r += 1
    r += 1

    r = section(ws, r, "C", "COMPUTATION TEMPLATE")
    header_row(ws, r, ["Income item", "Gross (BDT)", "Class", "Allowable expense", "Taxable regular", "Lottery 25%", "Exempt", "Net taxable", "Why this head / provision", "TDS (memo)", "Check", ""], NAVY)
    r += 1
    os_items = [
        ("Royalty / licence / technical fee", 100000, "Regular", 5000, "s.66 — not a business of licensing"),
        ("Government cash incentive / subsidy", 50000, "Regular", 0, "s.66 — specifically listed"),
        ("Gift from friend / unrelated person", 80000, "Regular", 0, "s.66 — not a specified relative"),
        ("Gift from spouse / parent / child (both returns)", 200000, "Exempt", 0, "Exempt if disclosed both sides — VERIFY"),
        ("Examiner / miscellaneous honorarium", 15000, "Regular", 0, "Residual — no employment relationship"),
        ("Deemed income (s.67) — describe", 0, "Regular", 0, "Use when the question has a deemed item"),
        ("Other residual income", 0, "Regular", 0, "Only after eliminating the other six heads"),
        ("Lottery / crossword / card / online-game winnings", 40000, "Lottery", 0, "25%; no deduction even if you enter an expense"),
    ]
    os_start = r
    for lab, amt, cls, exp, note in os_items:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        style_input(ws.cell(r, 3), cls, number=False)
        style_input(ws.cell(r, 4), exp, number=True)
        style_calc(ws.cell(r, 5), f'=IF(C{r}="Regular",MAX(B{r}-D{r},0),0)')
        style_calc(ws.cell(r, 6), f'=IF(C{r}="Lottery",B{r},0)')
        style_calc(ws.cell(r, 7), f'=IF(C{r}="Exempt",B{r},0)')
        style_calc(ws.cell(r, 8), f"=E{r}+F{r}")
        style_note(ws.cell(r, 9), note)
        style_input(ws.cell(r, 10), 10000 if "Lottery" in lab else 0, number=True)
        style_calc(ws.cell(r, 11), f'=IF(OR(E{r}+F{r}+G{r}>B{r}+0.001,AND(C{r}="Lottery",D{r}<>0)),"CHECK REQUIRED","OK")', number=False)
        ws.cell(r, 11).number_format = "@"
        r += 1
    os_end = r - 1
    add_dv(ws, '"Regular,Lottery,Exempt"', f"C{os_start}:C{os_end}")

    style_label(ws.cell(r, 1), "TOTALS", bold=True)
    for col, letter in [(2, "B"), (4, "D"), (5, "E"), (6, "F"), (7, "G"), (8, "H"), (10, "J")]:
        style_calc(ws.cell(r, col), f"=SUM({letter}{os_start}:{letter}{os_end})")
        ws.cell(r, col).fill = fill(NAVY); ws.cell(r, col).font = font(bold=True, color=WHITE)
    ws.cell(r, 1).fill = fill(NAVY); ws.cell(r, 1).font = font(bold=True, color=WHITE)
    C["OS_GROSS"] = f"$B${r}"
    C["OS_REGULAR"] = f"$E${r}"
    C["OS_LOTTERY"] = f"$F${r}"
    C["OS_EXEMPT"] = f"$G${r}"
    r += 2
    style_label(ws.cell(r, 1), "TAXABLE INCOME FROM OTHER SOURCES — regular", bold=True)
    style_calc(ws.cell(r, 2), f"={C['OS_REGULAR']}")
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE); ws.cell(r, 2).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "LOTTERY / GAME WINNINGS (special 25%, no deduction)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['OS_LOTTERY']}")
    ws.cell(r, 1).fill = fill(TEAL); ws.cell(r, 1).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).fill = fill(TEAL); ws.cell(r, 2).font = font(bold=True, color=WHITE, size=12); ws.cell(r, 2).number_format = NUM
    r += 2

    r = section(ws, r, "D", "TAX-TREATMENT TABLE")
    header_row(ws, r, ["Income item", "Gross amount", "Taxable amount", "Exempt amount", "Deduction / adjustment", "Net taxable amount", "Relevant provision", "Explanation", "", "", "", ""], SUBSEC)
    r += 1
    style_label(ws.cell(r, 1), "Regular other sources")
    style_calc(ws.cell(r, 2), f"={C['OS_REGULAR']}+{C['OS_EXEMPT']}")
    style_calc(ws.cell(r, 3), f"={C['OS_REGULAR']}")
    style_calc(ws.cell(r, 4), f"={C['OS_EXEMPT']}")
    style_calc(ws.cell(r, 5), f"=D{os_end+1}")  # this might be wrong - D totals are on totals row
    # fix: use SUM of expenses on regular rows via the totals row column D
    style_calc(ws.cell(r, 5), f"=SUM(D{os_start}:D{os_end})")
    style_calc(ws.cell(r, 6), f"={C['OS_REGULAR']}")
    ws.cell(r, 7, "s.66, s.68")
    r += 1
    style_label(ws.cell(r, 1), "Lottery / games")
    style_calc(ws.cell(r, 2), f"={C['OS_LOTTERY']}")
    style_calc(ws.cell(r, 3), f"={C['OS_LOTTERY']}")
    style_calc(ws.cell(r, 4), 0)
    style_calc(ws.cell(r, 5), 0)
    style_calc(ws.cell(r, 6), f"={C['OS_LOTTERY']}")
    ws.cell(r, 7, "Seventh Schedule"); ws.cell(r, 8, "25%; no deduction")
    r += 2

    r = section(ws, r, "E", "WORKED EXAMPLE  —  Mr. Md. Karim Rahman")
    write_wrapped(ws, r, 1,
        "STEP 1 — FACTS. Royalty 100,000 (collection cost 5,000); government cash incentive 50,000; gift from a college friend 80,000; "
        "gift from father 200,000 (shown in both returns); examiner honorarium 15,000; lottery prize 40,000 (TDS 10,000).",
        "L", 32, font(size=9), LIGHT_GOLD)
    r += 1
    write_wrapped(ws, r, 1,
        "STEP 2–4. Regular OS = (100,000 − 5,000) + 50,000 + 80,000 + 15,000 = 240,000. Father's gift exempt. "
        "Lottery 40,000 at 25% with no deduction. TAXABLE OS = 240,000 (regular) + 40,000 (lottery).",
        "L", 28, font(size=9), LIGHT_TEAL)
    r += 1
    style_label(ws.cell(r, 1), "Regular OS (live)", bold=True); style_calc(ws.cell(r, 2), f"={C['OS_REGULAR']}")
    style_label(ws.cell(r, 3), "Lottery (live)", bold=True); style_calc(ws.cell(r, 4), f"={C['OS_LOTTERY']}")
    r += 2
    write_wrapped(ws, r, 1,
        "STEP 5 — WHY. Royalty is listed in s.66 and he is not in the business of licensing. The friend's gift is not from a specified relative. "
        "The father's gift is exempt only because both returns disclose it — if the question is silent on disclosure, state the assumption. "
        "Lottery cannot be reduced by ticket cost. Bank interest is not on this sheet (Financial Assets).",
        "L", 36, font(size=9), WHITE)
    r += 2

    r = close_head(ws, r, [
        "Ask 'could this be one of the other six heads?' before you put it here.",
        "Relative-gift exemption needs disclosure in both returns — write that condition.",
        "Lottery: quote the 25% rate and write 'no deduction' in the working.",
        "Do not put FDR interest or dividend here. That is Chapter VII.",
        "A director may be an employee under s.2 — sitting fee can be employment. Read the facts.",
        "s.67 deemed items are easy marks if you identify them (cash loan, asset below FMV, unexplained credit).",
        "Collection expenses are allowed only against the income they earn, and never against lottery.",
        "Cash incentive is often forgotten or dumped into business — s.66 lists it here unless the question clearly treats it as business receipts.",
    ], [
        "Lottery rate is P_LotteryRate on the Home sheet.",
        "s.67 list is summarised from practitioner sources (PwC). Tick 'VERIFY' against your reprint before quoting a specific clause number in the exam.",
        "Sibling gifts: FO 2025 materials mention gifts from spouse, parents, children and (in some summaries) siblings. Default example treats only spouse/parent/child as exempt. Sibling: VERIFY.",
    ], [
        "ITA 2023 ss.66–69.",
        "Seventh Schedule — lottery 25%. VERIFY.",
        "Sixth Schedule — gift from specified relatives. VERIFY paragraph.",
        "s.150 — credit of TDS on winnings.",
    ])
    define_name(wb, "OUT_OS_REGULAR", ws.title, C["OS_REGULAR"])
    define_name(wb, "OUT_OS_LOTTERY", ws.title, C["OS_LOTTERY"])
    define_name(wb, "OUT_OS_EXEMPT", ws.title, C["OS_EXEMPT"])
    return r


def apply_sheet_tab_colors(wb):
    colors = {
        "Income from Employment": "1B365D",
        "Income from Financial Assets": "1F6F6A",
        "Income from Rent": "4A6FA5",
        "Income from Agriculture": "2E7D32",
        "Income from Business": "E65100",
        "Capital Gain": "6A1B9A",
        "Income from Other Sources": "37474F",
        "Comprehensive Tax Computation": "0D1B2A",
    }
    for name, col in colors.items():
        if name in wb.sheetnames:
            wb[name].sheet_properties.tabColor = col


def build_workbook(path):
    wb = Workbook()
    # create sheets in required order
    first = True
    sheets = {}
    for name in SHEETS:
        if first:
            ws = wb.active
            ws.title = name
            first = False
        else:
            ws = wb.create_sheet(name)
        sheets[name] = ws

    # Print titles / calc mode
    wb.calculation.calcMode = "auto"
    wb.calculation.fullCalcOnLoad = True

    s8 = sheets["Comprehensive Tax Computation"]
    after = build_sheet8_parameters(s8, wb)

    build_employment(sheets["Income from Employment"], wb)
    build_financial(sheets["Income from Financial Assets"], wb)
    build_rent(sheets["Income from Rent"], wb)
    build_agriculture(sheets["Income from Agriculture"], wb)
    build_business(sheets["Income from Business"], wb)
    build_cg(sheets["Capital Gain"], wb)
    build_os(sheets["Income from Other Sources"], wb)

    finish_sheet8(s8, wb, after)
    apply_sheet_tab_colors(wb)

    # reorder just in case
    for i, name in enumerate(SHEETS):
        wb.move_sheet(name, offset=i - wb.sheetnames.index(name))

    wb.properties.title = "ICAB Professional Taxation – 7 Heads of Income"
    wb.properties.creator = "ICAB exam-oriented study workbook"
    wb.properties.subject = "Bangladesh Income Tax Act, 2023 — seven heads of income"
    wb.properties.description = (
        "Study + practice + computation template for ICAB Professional Level "
        "Business Planning: Taxation & Compliance. Default IY 2025-26 / AY 2026-27."
    )

    wb.save(path)
    return path
