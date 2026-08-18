#!/usr/bin/env python3
"""
ICAB Professional Level — Business Planning: Taxation & Compliance
Workbook generator: 7 heads of income under the Bangladesh Income Tax Act, 2023.

Default working year: Income Year 2025-26 / Assessment Year 2026-27.
Rate and threshold cells are user-editable so the file can be updated for a later Finance Act.
"""

from copy import copy
from openpyxl import Workbook
from openpyxl.chart.series import SeriesLabel
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    NamedStyle,
    PatternFill,
    Protection,
    Side,
)
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.page import PageMargins
from openpyxl.workbook.properties import CalcProperties
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.utils.cell import quote_sheetname

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
NAVY = "1B365D"
NAVY2 = "243E73"
SECTION = "2E5090"
SUBSEC = "4A6FA5"
GREY = "D9D9D9"
GREY_DK = "7F7F7F"
INPUT_FILL = "DCE6F1"
INPUT_FONT = "1F4E79"
CALC_FILL = "C6EFCE"
CALC_FONT = "006100"
NOTE_FILL = "FFF2CC"
NOTE_FONT = "7F6000"
WARN_FILL = "F8CBAD"
WARN_FONT = "C00000"
WHITE = "FFFFFF"
ALT = "F4F7FB"
GOLD = "F4B183"
TEAL = "1F6F6A"
LINK = "0563C1"
OK_FILL = "E2EFDA"
BAND = "0D1B2A"
LIGHT_NAVY = "E8EEF7"
LIGHT_TEAL = "E6F3F2"
LIGHT_GOLD = "FDF3E7"
LIGHT_RED = "FDECEA"

thin = Border(
    left=Side(style="thin", color="B0B0B0"),
    right=Side(style="thin", color="B0B0B0"),
    top=Side(style="thin", color="B0B0B0"),
    bottom=Side(style="thin", color="B0B0B0"),
)
med_navy = Border(
    left=Side(style="medium", color=NAVY),
    right=Side(style="medium", color=NAVY),
    top=Side(style="medium", color=NAVY),
    bottom=Side(style="medium", color=NAVY),
)

NUM = '#,##0;(#,##0);"—"'
PCT = "0.00%"
WRAP = Alignment(wrap_text=True, vertical="center")
WRAP_TL = Alignment(wrap_text=True, vertical="top", horizontal="left")
LEFT = Alignment(vertical="center", horizontal="left", wrap_text=True)
CENTER = Alignment(vertical="center", horizontal="center", wrap_text=True)
RIGHT = Alignment(vertical="center", horizontal="right")

SHEETS = [
    "Income from Employment",
    "Income from Financial Assets",
    "Income from Rent",
    "Income from Agriculture",
    "Income from Business",
    "Capital Gain",
    "Income from Other Sources",
    "Comprehensive Tax Computation",
]

# Cell map populated while building
C = {}


def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)


def font(name="Calibri", size=10, bold=False, italic=False, color="000000"):
    return Font(name=name, size=size, bold=bold, italic=italic, color=color)


def apply_border_range(ws, start_row, end_row, start_col, end_col):
    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            ws.cell(r, c).border = thin


def set_col_widths(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def page_setup(ws, title, landscape=False):
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_setup.horizontalCentered = True
    ws.page_margins = PageMargins(left=0.45, right=0.45, top=0.6, bottom=0.55, header=0.25, footer=0.25)
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:4"
    ws.oddHeader.left.text = f"&8ICAB Professional Taxation  |  {title}"
    ws.oddFooter.left.text = "&8Bangladesh Income Tax Act, 2023  |  For study / exam practice — verify Finance Act of the exam year"
    ws.oddFooter.right.text = "&8Page &P of &N"
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 100
    ws.freeze_panes = "A5"
    ws.page_setup.scale = None


def style_input(cell, value=None, number=False):
    if value is not None:
        cell.value = value
    cell.fill = fill(INPUT_FILL)
    cell.font = font(color=INPUT_FONT, size=10)
    cell.border = thin
    cell.alignment = RIGHT if number else LEFT
    if number:
        cell.number_format = NUM


def style_calc(cell, value=None, number=True):
    if value is not None:
        cell.value = value
    cell.fill = fill(CALC_FILL)
    cell.font = font(color=CALC_FONT, size=10, bold=True)
    cell.border = thin
    cell.alignment = RIGHT if number else LEFT
    if number:
        cell.number_format = NUM


def style_note(cell, value=None):
    if value is not None:
        cell.value = value
    cell.fill = fill(NOTE_FILL)
    cell.font = font(color=NOTE_FONT, size=9, italic=True)
    cell.border = thin
    cell.alignment = WRAP_TL


def style_warn(cell, value=None):
    if value is not None:
        cell.value = value
    cell.fill = fill(WARN_FILL)
    cell.font = font(color=WARN_FONT, size=9, bold=True)
    cell.border = thin
    cell.alignment = LEFT


def style_grey(cell, value=None, center=False):
    if value is not None:
        cell.value = value
    cell.fill = fill(GREY)
    cell.font = font(size=9, bold=True, color="333333")
    cell.border = thin
    cell.alignment = CENTER if center else LEFT


def style_label(cell, value=None, bold=False):
    if value is not None:
        cell.value = value
    cell.font = font(size=10, bold=bold)
    cell.alignment = LEFT
    cell.border = thin


def banner(ws, row, text, merge="A1:L1", fill_color=NAVY, size=16):
    ws.merge_cells(merge)
    cell = ws.cell(row, 1, text)
    cell.font = font(size=size, bold=True, color=WHITE)
    cell.fill = fill(fill_color)
    cell.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    end_col = ws[merge.split(":")[1]].column
    for c in range(1, end_col + 1):
        ws.cell(row, c).fill = fill(fill_color)
        ws.cell(row, c).font = font(size=size, bold=True, color=WHITE)
    ws.row_dimensions[row].height = 26
    return cell


def section(ws, row, code, title, merge="A:L"):
    start, end = merge.split(":")
    ws.merge_cells(f"{start}{row}:{end}{row}")
    cell = ws.cell(row, 1, f"  {code}   {title}")
    cell.font = font(size=12, bold=True, color=WHITE)
    cell.fill = fill(SECTION)
    cell.alignment = Alignment(vertical="center", horizontal="left")
    last = ws[f"{end}{row}"].column
    for c in range(1, last + 1):
        ws.cell(row, c).fill = fill(SECTION)
        ws.cell(row, c).font = font(size=12, bold=True, color=WHITE)
        ws.cell(row, c).alignment = Alignment(vertical="center")
    ws.row_dimensions[row].height = 20
    return row + 1


def subsection(ws, row, title, merge_end="L"):
    ws.merge_cells(f"A{row}:{merge_end}{row}")
    cell = ws.cell(row, 1, f"  {title}")
    cell.font = font(size=10, bold=True, color=WHITE)
    cell.fill = fill(SUBSEC)
    last = ws[f"{merge_end}{row}"].column
    for c in range(1, last + 1):
        ws.cell(row, c).fill = fill(SUBSEC)
        ws.cell(row, c).font = font(size=10, bold=True, color=WHITE)
    ws.row_dimensions[row].height = 16
    return row + 1


def write_wrapped(ws, row, col, text, merge_end=None, height=None, fnt=None, fl=None):
    if merge_end:
        ws.merge_cells(f"{get_column_letter(col)}{row}:{merge_end}{row}")
    cell = ws.cell(row, col, text)
    cell.alignment = WRAP_TL
    cell.font = fnt or font(size=9)
    if fl:
        cell.fill = fill(fl)
        if merge_end:
            last = ws[f"{merge_end}{row}"].column
            for c in range(col, last + 1):
                ws.cell(row, c).fill = fill(fl)
    if height:
        ws.row_dimensions[row].height = height
    return cell


def nav_row(ws, row, current):
    """Navigation hyperlinks across columns A–H."""
    labels = [
        ("HOME / Summary", "Comprehensive Tax Computation"),
        ("Employment", "Income from Employment"),
        ("Financial Assets", "Income from Financial Assets"),
        ("Rent", "Income from Rent"),
        ("Agriculture", "Income from Agriculture"),
        ("Business", "Income from Business"),
        ("Capital Gain", "Capital Gain"),
        ("Other Sources", "Income from Other Sources"),
    ]
    for i, (lab, target) in enumerate(labels, start=1):
        cell = ws.cell(row, i, lab)
        cell.hyperlink = f"#{quote_sheetname(target)}!A1"
        cell.font = font(size=8, bold=True, color=WHITE if target == current else "D6E3F8")
        cell.fill = fill(TEAL if target == current else NAVY2)
        cell.alignment = CENTER
        cell.border = thin
    for c in range(9, 13):
        ws.cell(row, c).fill = fill(NAVY2)
    ws.row_dimensions[row].height = 18


def legend_row(ws, row):
    items = [
        (1, "Blue = User input", INPUT_FILL, INPUT_FONT),
        (3, "Green = Formula / calculated", CALC_FILL, CALC_FONT),
        (5, "Yellow = Assumption / note", NOTE_FILL, NOTE_FONT),
        (7, "Grey = Heading / reference", GREY, "333333"),
        (9, "Red = Warning / disallowable / special", WARN_FILL, WARN_FONT),
    ]
    for c in range(1, 13):
        ws.cell(row, c).fill = fill("F0F0F0")
        ws.cell(row, c).border = thin
    for start, text, bg, fg in items:
        cell = ws.cell(row, start, f"  {text}")
        cell.fill = fill(bg)
        cell.font = font(size=8, bold=True, color=fg)
        cell.alignment = LEFT
        if start + 1 <= 12:
            ws.cell(row, start + 1).fill = fill(bg)
    ws.row_dimensions[row].height = 16


def header_row(ws, row, headers, fills=None):
    for i, h in enumerate(headers, start=1):
        cell = ws.cell(row, i, h)
        style_grey(cell, center=True)
        cell.alignment = CENTER
        cell.font = font(size=8, bold=True, color="222222")
        if fills:
            cell.fill = fill(fills)
            cell.font = font(size=8, bold=True, color=WHITE)
    ws.row_dimensions[row].height = 28


def define_name(wb, name, sheet, cell_ref):
    # remove if exists
    existing = [dn for dn in wb.defined_names.values() if dn.name == name]
    for dn in existing:
        wb.defined_names.delete(name)
    wb.defined_names.add(DefinedName(name=name, attr_text=f"{quote_sheetname(sheet)}!{cell_ref}"))


def comment(cell, text):
    cell.comment = Comment(text, "ICAB Tax Workbook")
    cell.comment.width = 280
    cell.comment.height = 80


def add_dv(ws, formula, cells, allow="list"):
    dv = DataValidation(type=allow, formula1=formula, allow_blank=True)
    dv.error = "Select a value from the list"
    dv.errorTitle = "Invalid entry"
    dv.prompt = "Select from the list"
    dv.promptTitle = "Input"
    ws.add_data_validation(dv)
    dv.add(cells)
    return dv


# ===========================================================================
# SHEET 8 — parameters first (so other sheets can reference named ranges)
# ===========================================================================
def build_sheet8_parameters(ws, wb):
    """Top control panel + identity. Returns the next free row after the panel."""
    page_setup(ws, "Comprehensive Tax Computation", landscape=True)
    set_col_widths(
        ws,
        {
            "A": 46,
            "B": 18,
            "C": 18,
            "D": 18,
            "E": 18,
            "F": 18,
            "G": 20,
            "H": 16,
            "I": 16,
            "J": 16,
            "K": 16,
            "L": 28,
        },
    )

    banner(
        ws,
        1,
        "ICAB PROFESSIONAL LEVEL  ·  BUSINESS PLANNING: TAXATION & COMPLIANCE  ·  7 HEADS OF INCOME",
        "A1:L1",
        BAND,
        14,
    )
    ws.merge_cells("A2:L2")
    ws["A2"] = (
        "Comprehensive Income Tax Computation  |  Bangladesh Income Tax Act, 2023  |  "
        "Default: Income Year 2025-26  /  Assessment Year 2026-27  |  All amounts in BDT (৳)"
    )
    ws["A2"].font = font(size=9, italic=True, color=WHITE)
    ws["A2"].fill = fill(NAVY)
    ws["A2"].alignment = Alignment(vertical="center", indent=1)
    for c in range(1, 13):
        ws.cell(2, c).fill = fill(NAVY)
        ws.cell(2, c).font = font(size=9, italic=True, color=WHITE)
    ws.row_dimensions[2].height = 16

    nav_row(ws, 3, "Comprehensive Tax Computation")
    legend_row(ws, 4)

    r = 6
    r = section(ws, r, "0", "HOW TO USE THIS WORKBOOK  ·  CONTROL PANEL  ·  TAX YEAR ASSUMPTIONS")

    ws.merge_cells(f"A{r}:L{r}")
    write_wrapped(
        ws,
        r,
        1,
        "This workbook is a study + practice + computation template for ICAB Professional Level. "
        "BLUE cells are inputs (overwrite them to solve any exam question). GREEN cells are formulas — do not type over them. "
        "Sheets 1–7 compute each head. This sheet pulls those outputs automatically and computes total income and tax liability. "
        "Yellow cells flag assumptions that depend on the Finance Act / SRO of the exam year — always verify those before an exam. "
        "Withholding tax (TDS/VDS) is a TAX CREDIT / payment, not a deduction from income.",
        "L",
        36,
        font(size=9),
        LIGHT_NAVY,
    )
    r += 2

    # ---- Taxpayer identity ----
    r = subsection(ws, r, "TAXPAYER IDENTITY  (user input — pre-filled with the integrated example)")
    id_start = r
    labels = [
        ("Assessee name", "Mr. Md. Karim Rahman"),
        ("TIN (optional)", "123-456-789-012"),
        ("Residential status", "Resident"),
        ("Taxpayer category", "General (male, under 65)"),
        ("Parent / guardian of a person with disability?", "No"),
        ("New taxpayer this year?", "No"),
        ("Location (for information)", "Dhaka South City Corporation"),
        ("Shareholder-director of a company?", "No"),
        ("Government employee?", "No"),
    ]
    keys = [
        "P_Name",
        "P_TIN",
        "P_Status",
        "P_Category",
        "P_DisabledChild",
        "P_NewTaxpayer",
        "P_Location",
        "P_ShareholderDir",
        "P_GovtEmp",
    ]
    for i, ((lab, val), key) in enumerate(zip(labels, keys)):
        style_label(ws.cell(r, 1), lab, bold=True)
        style_input(ws.cell(r, 2), val, number=False)
        ws.merge_cells(f"B{r}:C{r}")
        C[key] = f"$B${r}"
        r += 1

    # year
    style_label(ws.cell(r, 1), "Income year (IY)", bold=True)
    style_input(ws.cell(r, 2), "2025-26", number=False)
    C["P_IY"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Assessment year (AY)", bold=True)
    style_input(ws.cell(r, 2), "2026-27", number=False)
    C["P_AY"] = f"$B${r}"
    r += 1

    add_dv(ws, '"Resident,Non-resident Bangladeshi (NRB),Non-resident (foreigner)"', f"B{id_start+2}")
    add_dv(
        ws,
        '"General (male, under 65),Woman / Senior citizen (65+),Third gender,Person with disability,Gazetted freedom fighter / July Warrior"',
        f"B{id_start+3}",
    )
    add_dv(ws, '"Yes,No"', f"B{id_start+4}")
    add_dv(ws, '"Yes,No"', f"B{id_start+5}")
    add_dv(ws, '"Yes,No"', f"B{id_start+7}")
    add_dv(ws, '"Yes,No"', f"B{id_start+8}")

    # ---- Parameter table on the right of identity (columns E–L) ----
    # Rebuild beside identity for compact layout — put parameters below instead for clarity.

    r += 1
    r = subsection(ws, r, "STATUTORY PARAMETERS  (edit these when the Finance Act of your exam year differs)")

    # Threshold lookup table (hidden-ish to the right, columns I–J)
    # We'll put the lookup table in columns I-J starting this row, and the live parameters in A-C.

    # Live parameters
    param_rows = {}

    def param(label, value, key, note, number=True, pct=False):
        nonlocal r
        style_label(ws.cell(r, 1), label, bold=True)
        style_input(ws.cell(r, 2), value, number=number)
        if pct:
            ws.cell(r, 2).number_format = "0.00%"
        elif number:
            ws.cell(r, 2).number_format = NUM
        style_note(ws.cell(r, 3), note)
        ws.merge_cells(f"C{r}:H{r}")
        C[key] = f"$B${r}"
        param_rows[key] = r
        r += 1
        return r

    # Threshold is a FORMULA from category + disabled child
    style_label(ws.cell(r, 1), "Tax-free threshold (first slab, BDT)", bold=True)
    # lookup table will be placed at I/J of this block — we'll set formula after creating lookup
    thresh_row = r
    style_calc(ws.cell(r, 2), number=True)
    style_note(
        ws.cell(r, 3),
        "Formula: category table + BDT 50,000 if parent/guardian of a person with disability (one parent only). "
        "Default AY 2026-27 (Finance Ordinance 2025). Finance Act 2026 sources also mention BDT 400,000 for general taxpayers — VERIFY.",
    )
    ws.merge_cells(f"C{r}:H{r}")
    C["P_Threshold"] = f"$B${r}"
    r += 1

    param(
        "Employment exemption cap (BDT)",
        500000,
        "P_EmpCap",
        "Lower of 1/3 of income from employment or this cap. FO 2025 raised the cap from 450,000 to 500,000. VERIFY for exam year. Sixth Schedule, Part A.",
    )
    param(
        "Agricultural exemption (sole agri + financial assets) (BDT)",
        500000,
        "P_AgriExempt",
        "FO 2025: agri income up to this amount is exempt IF the assessee has no income other than agriculture and financial assets. VERIFY conditions and amount.",
    )
    param(
        "Listed-share capital-gain exemption (BDT)",
        5000000,
        "P_ListedCGExempt",
        "PwC / ITA 2023 practice: CG on listed shares/units exempt if gain does not exceed this amount, except sponsor / director / placement shares. VERIFY.",
    )
    param(
        "Dividend special rate",
        0.15,
        "P_DivRate",
        "Individual: dividend generally taxed at 15% (special rate). Do not put dividend into the regular slab. VERIFY Seventh Schedule / Finance Act.",
        pct=True,
    )
    param(
        "Lottery / game-winning special rate",
        0.25,
        "P_LotteryRate",
        "Winnings from lottery, crossword, card/online games: 25% on the receipt; no deduction. VERIFY Seventh Schedule.",
        pct=True,
    )
    param(
        "Long-term capital gain rate (held > 5 years)",
        0.15,
        "P_CGLongRate",
        "Transfer after more than 5 years: 15%, or tax deducted at registration (s.125) if higher (treated as minimum tax s.163). VERIFY.",
        pct=True,
    )
    param(
        "Listed-share CG rate (if exemption not available)",
        0.15,
        "P_CGListedRate",
        "Listed-share CG that is not exempt is generally 15% (not the regular slab). Sponsor/director/placement: different treatment — VERIFY.",
        pct=True,
    )
    param(
        "Investment rebate — % of eligible total income",
        0.03,
        "P_RebateIncPct",
        "Lowest of (a) this % of eligible total income, (b) % of eligible investment, (c) absolute cap. Eligible income excludes exempt, reduced/final-rate income and (typically) firm/AOP share. VERIFY.",
        pct=True,
    )
    param(
        "Investment rebate — % of eligible investment",
        0.10,
        "P_RebateInvPct",
        "FO 2025 (KPMG): 15% / cap BDT 1,000,000. Later 2026 practitioner sources (PwC Jul 2026): 10% / cap BDT 750,000. DEFAULT uses the later figures. VERIFY for your exam Finance Act.",
        pct=True,
    )
    param(
        "Investment rebate — absolute cap (BDT)",
        750000,
        "P_RebateCap",
        "See note above. Change this cell if your exam year still uses BDT 1,000,000.",
    )
    param(
        "Minimum tax — existing taxpayer (BDT)",
        5000,
        "P_MinTax",
        "AY 2026-27: flat BDT 5,000 if total income exceeds the tax-free threshold, regardless of location (FO 2025). New taxpayer: see next row.",
    )
    param(
        "Minimum tax — new taxpayer (BDT)",
        1000,
        "P_MinTaxNew",
        "AY 2026-27 / 2027-28: BDT 1,000 for a person who has not previously been assessed. VERIFY.",
    )
    param(
        "Non-resident (foreigner) flat rate",
        0.30,
        "P_NRRate",
        "Non-residents other than Bangladeshi non-residents: flat 30% on total income (no slabs). NRB uses the resident slab. VERIFY.",
        pct=True,
    )

    # Slab table
    r += 1
    r = subsection(ws, r, "INDIVIDUAL SLAB TABLE  (edit widths / rates for another assessment year)")
    header_row(
        ws,
        r,
        ["Slab", "Width (BDT)", "Rate", "Income in this slab", "Tax on this slab", "Running total of income used", "", "", "", "", "", ""],
        NAVY,
    )
    slab_header = r
    r += 1
    # Slab 1 width = threshold (formula)
    slab_start = r
    # 6 slabs
    # We'll fill widths: s1 = threshold; s2-s6 user input with defaults for AY 2026-27
    default_widths = [None, 300000, 400000, 500000, 2000000, None]  # last is balance
    default_rates = [0.00, 0.10, 0.15, 0.20, 0.25, 0.30]
    slab_names = [
        "Slab 1 — tax-free threshold",
        "Slab 2",
        "Slab 3",
        "Slab 4",
        "Slab 5",
        "Slab 6 — balance",
    ]
    C["SLAB_START"] = slab_start
    for i in range(6):
        style_label(ws.cell(r, 1), slab_names[i], bold=True)
        if i == 0:
            style_calc(ws.cell(r, 2), f"={C['P_Threshold']}")
        elif i == 5:
            style_note(ws.cell(r, 2), "Balance (no width limit)")
            ws.cell(r, 2).number_format = "@"
        else:
            style_input(ws.cell(r, 2), default_widths[i], number=True)
        style_input(ws.cell(r, 3), default_rates[i], number=False)
        ws.cell(r, 3).number_format = "0%"
        ws.cell(r, 3).fill = fill(INPUT_FILL)
        ws.cell(r, 3).font = font(color=INPUT_FONT)
        ws.cell(r, 3).border = thin
        # D, E, F filled later when regular taxable income cell is known
        style_calc(ws.cell(r, 4), 0)
        style_calc(ws.cell(r, 5), 0)
        style_calc(ws.cell(r, 6), 0)
        C[f"SLAB_{i+1}_W"] = f"$B${r}"
        C[f"SLAB_{i+1}_R"] = f"$C${r}"
        C[f"SLAB_{i+1}_INC"] = f"$D${r}"
        C[f"SLAB_{i+1}_TAX"] = f"$E${r}"
        r += 1
    C["SLAB_END"] = r - 1

    # Category lookup table in columns J–K on identity rows (those rows only merge B:C)
    ws["J10"] = "CATEGORY LOOKUP (do not delete)"
    ws["J10"].font = font(size=8, bold=True, color=GREY_DK)
    ws["J10"].fill = fill(GREY)
    ws["K10"] = "Threshold"
    ws["K10"].font = font(size=8, bold=True)
    ws["K10"].fill = fill(GREY)
    cats = [
        ("General (male, under 65)", 375000),
        ("Woman / Senior citizen (65+)", 425000),
        ("Third gender", 500000),
        ("Person with disability", 500000),
        ("Gazetted freedom fighter / July Warrior", 525000),
    ]
    for i, (name, amt) in enumerate(cats):
        ws.cell(11 + i, 10, name).font = font(size=8)
        ws.cell(11 + i, 10).fill = fill(GREY)
        ws.cell(11 + i, 10).border = thin
        ws.cell(11 + i, 11, amt).number_format = NUM
        ws.cell(11 + i, 11).font = font(size=8)
        ws.cell(11 + i, 11).fill = fill(GREY)
        ws.cell(11 + i, 11).border = thin
    C["CAT_TABLE"] = "$J$11:$K$15"

    # Threshold formula
    ws[C["P_Threshold"]].value = (
        f'=IFERROR(VLOOKUP({C["P_Category"]},{C["CAT_TABLE"]},2,FALSE),375000)'
        f'+IF({C["P_DisabledChild"]}="Yes",50000,0)'
    )

    # Eligible investment inputs (for rebate)
    r += 1
    r = subsection(ws, r, "ELIGIBLE INVESTMENT / EXPENDITURE FOR REBATE  (Sixth Schedule, Part 3 — user input)")
    inv_items = [
        ("Employee's contribution to recognised provident fund", 120000),
        ("Employer's contribution to recognised provident fund (if eligible)", 120000),
        ("Life insurance premium (self / spouse / minor child) — limited to 10% of sum assured", 80000),
        ("Deposit pension scheme (DPS) in scheduled bank / financial institution", 60000),
        ("Investment in listed shares / mutual fund / unit / ETF / government securities", 200000),
        ("Contribution to approved superannuation / pension / gratuity fund", 0),
        ("Zakat paid to Zakat Fund / approved zakat institution", 0),
        ("Donation to NBR-approved charitable hospital / specified institution", 0),
        ("Other eligible investment / expenditure (describe in notes)", 0),
    ]
    header_row(
        ws,
        r,
        ["Eligible item (Part 3, Sixth Schedule)", "Amount invested (BDT)", "Included in rebate base?", "Note / limitation", "", "", "", "", "", "", "", ""],
        SUBSEC,
    )
    r += 1
    inv_start = r
    for lab, amt in inv_items:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        style_input(ws.cell(r, 3), "Yes", number=False)
        style_note(
            ws.cell(r, 4),
            "Confirm the item is still listed in Part 3 of the Sixth Schedule for the exam year. Life premium: max 10% of sum assured.",
        )
        ws.merge_cells(f"D{r}:H{r}")
        r += 1
    inv_end = r - 1
    add_dv(ws, '"Yes,No"', f"C{inv_start}:C{inv_end}")
    style_label(ws.cell(r, 1), "TOTAL ELIGIBLE INVESTMENT", bold=True)
    style_calc(ws.cell(r, 2), f'=SUMIFS(B{inv_start}:B{inv_end},C{inv_start}:C{inv_end},"Yes")')
    C["P_EligInv"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(NAVY)
    ws.cell(r, 1).font = font(bold=True, color=WHITE, size=10)
    r += 2

    # Payments on account of tax
    r = subsection(ws, r, "TAX ALREADY PAID  (credits against liability — do NOT deduct these from income)")
    pay_items = [
        ("TDS on employment income (s.86) — from Form 16 / employer certificate", 280000, "P_TDS_Emp"),
        ("TDS on interest / profit from bank, FDR, securities", 18000, "P_TDS_Int"),
        ("TDS on dividend", 12000, "P_TDS_Div"),
        ("TDS / tax collected at registration of land or other capital asset (s.125)", 180000, "P_TDS_CG"),
        ("TDS on lottery / game winnings", 10000, "P_TDS_Lot"),
        ("TDS on rent / other heads (if any)", 0, "P_TDS_Oth"),
        ("Advance income tax paid (AIT)", 50000, "P_AIT"),
        ("Tax paid on regular assessment / other credit", 0, "P_OthCredit"),
    ]
    header_row(
        ws,
        r,
        ["Payment / credit", "Amount (BDT)", "Treatment", "", "", "", "", "", "", "", "", ""],
        SUBSEC,
    )
    r += 1
    for lab, amt, key in pay_items:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        style_note(
            ws.cell(r, 3),
            "Tax credit / payment on account. Some credits (e.g. certain minimum-tax TDS) may be non-refundable — VERIFY s.150 / s.163.",
        )
        ws.merge_cells(f"C{r}:H{r}")
        C[key] = f"$B${r}"
        r += 1
    style_label(ws.cell(r, 1), "TOTAL TAX PAID / CREDITS", bold=True)
    style_calc(
        ws.cell(r, 2),
        f"={C['P_TDS_Emp']}+{C['P_TDS_Int']}+{C['P_TDS_Div']}+{C['P_TDS_CG']}+{C['P_TDS_Lot']}+{C['P_TDS_Oth']}+{C['P_AIT']}+{C['P_OthCredit']}",
    )
    C["P_TaxPaid"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(NAVY)
    ws.cell(r, 1).font = font(bold=True, color=WHITE)
    r += 2

    # Optional surcharge inputs
    r = subsection(ws, r, "SURCHARGE ON NET WEALTH  (optional — leave wealth at 0 to ignore)")
    style_label(ws.cell(r, 1), "Net wealth / net worth (BDT)", bold=True)
    style_input(ws.cell(r, 2), 25000000, number=True)
    C["P_Wealth"] = f"$B${r}"
    style_note(
        ws.cell(r, 3),
        "Surcharge if net worth exceeds BDT 4 crore, OR owner of more than 1 motor car, OR house property > 8,000 sft. Rates 10%/20%/30%/35%. VERIFY.",
    )
    ws.merge_cells(f"C{r}:H{r}")
    r += 1
    style_label(ws.cell(r, 1), "Owns more than one motor car?", bold=True)
    style_input(ws.cell(r, 2), "No", number=False)
    C["P_MultiCar"] = f"$B${r}"
    add_dv(ws, '"Yes,No"', f"B{r}")
    r += 1
    style_label(ws.cell(r, 1), "Owns house property exceeding 8,000 sft?", bold=True)
    style_input(ws.cell(r, 2), "No", number=False)
    C["P_BigHouse"] = f"$B${r}"
    add_dv(ws, '"Yes,No"', f"B{r}")
    r += 1
    style_label(ws.cell(r, 1), "Surcharge rate (auto)", bold=True)
    style_calc(ws.cell(r, 2), number=False)
    ws.cell(r, 2).number_format = "0%"
    # 4cr=40m, 10cr=100m, 20cr=200m, 50cr=500m
    ws.cell(r, 2).value = (
        f'=IF(OR({C["P_Wealth"]}>500000000),"",'
        f'IF({C["P_Wealth"]}>200000000,0.3,'
        f'IF({C["P_Wealth"]}>100000000,0.2,'
        f'IF(OR({C["P_Wealth"]}>40000000,{C["P_MultiCar"]}="Yes",{C["P_BigHouse"]}="Yes"),0.1,0))))'
    )
    # fix: over 50cr is 35%
    ws.cell(r, 2).value = (
        f'=IF({C["P_Wealth"]}>500000000,0.35,'
        f'IF({C["P_Wealth"]}>200000000,0.3,'
        f'IF({C["P_Wealth"]}>100000000,0.2,'
        f'IF(OR({C["P_Wealth"]}>40000000,{C["P_MultiCar"]}="Yes",{C["P_BigHouse"]}="Yes"),0.1,0))))'
    )
    C["P_SurRate"] = f"$B${r}"
    r += 2

    C["S8_AFTER_PARAMS"] = r

    # Define names now so other sheets can use them
    define_name(wb, "P_Threshold", ws.title, C["P_Threshold"])
    define_name(wb, "P_EmpCap", ws.title, C["P_EmpCap"])
    define_name(wb, "P_AgriExempt", ws.title, C["P_AgriExempt"])
    define_name(wb, "P_ListedCGExempt", ws.title, C["P_ListedCGExempt"])
    define_name(wb, "P_DivRate", ws.title, C["P_DivRate"])
    define_name(wb, "P_LotteryRate", ws.title, C["P_LotteryRate"])
    define_name(wb, "P_CGLongRate", ws.title, C["P_CGLongRate"])
    define_name(wb, "P_CGListedRate", ws.title, C["P_CGListedRate"])
    define_name(wb, "P_AY", ws.title, C["P_AY"])
    define_name(wb, "P_IY", ws.title, C["P_IY"])
    define_name(wb, "P_Name", ws.title, C["P_Name"])
    define_name(wb, "P_Status", ws.title, C["P_Status"])
    define_name(wb, "P_Category", ws.title, C["P_Category"])
    define_name(wb, "P_GovtEmp", ws.title, C["P_GovtEmp"])
    define_name(wb, "P_ShareholderDir", ws.title, C["P_ShareholderDir"])

    return r


def finish_sheet8(ws, wb, start_row):
    """Consolidation, tax liability, exam tips, references — after sheets 1–7 exist."""
    r = start_row
    r = section(ws, r, "1", "CONSOLIDATION OF THE SEVEN HEADS  (linked to Sheets 1–7 — do not type amounts here)")

    ws.merge_cells(f"A{r}:L{r}")
    write_wrapped(
        ws,
        r,
        1,
        "Section 29 ITA 2023: total income is computed by aggregating income from all heads. "
        "Section 30 classifies income under the seven heads below. "
        "Special-rate income is included in total income but is taxed separately (do not run it through the regular slab). "
        "Figures in column B are live links to the output boxes on Sheets 1–7.",
        "L",
        28,
        font(size=9),
        LIGHT_NAVY,
    )
    r += 1

    header_row(
        ws,
        r,
        [
            "Particulars",
            "Amount (BDT)",
            "Of which: regular-rate",
            "Of which: special-rate",
            "Of which: exempt / excluded",
            "Source sheet",
            "Check",
            "",
            "",
            "",
            "",
            "",
        ],
        NAVY,
    )
    r += 1
    cons_start = r

    rows_def = [
        (
            "Income from employment (taxable)",
            "='Income from Employment'!OUT_EMP_TAXABLE",
            "='Income from Employment'!OUT_EMP_TAXABLE",
            0,
            "='Income from Employment'!OUT_EMP_EXEMPT",
            "Sheet 1",
        ),
        (
            "Income from financial assets — interest / profit / discount (regular)",
            "='Income from Financial Assets'!OUT_FIN_REGULAR",
            "='Income from Financial Assets'!OUT_FIN_REGULAR",
            0,
            0,
            "Sheet 2",
        ),
        (
            "Income from financial assets — dividend (special rate)",
            "='Income from Financial Assets'!OUT_FIN_DIVIDEND",
            0,
            "='Income from Financial Assets'!OUT_FIN_DIVIDEND",
            "='Income from Financial Assets'!OUT_FIN_DIV_EXEMPT",
            "Sheet 2",
        ),
        (
            "Income from rent",
            "='Income from Rent'!OUT_RENT_TAXABLE",
            "='Income from Rent'!OUT_RENT_TAXABLE",
            "='Income from Rent'!OUT_RENT_SPECIAL",
            0,
            "Sheet 3",
        ),
        (
            "Income from agriculture",
            "='Income from Agriculture'!OUT_AGRI_TAXABLE",
            "='Income from Agriculture'!OUT_AGRI_TAXABLE",
            0,
            "='Income from Agriculture'!OUT_AGRI_EXEMPT",
            "Sheet 4",
        ),
        (
            "Income from business",
            "='Income from Business'!OUT_BUS_TAXABLE",
            "='Income from Business'!OUT_BUS_TAXABLE",
            "='Income from Business'!OUT_BUS_SPECIAL",
            0,
            "Sheet 5",
        ),
        (
            "Capital gains — regular slab (asset held ≤ 5 years, not listed-exempt)",
            "='Capital Gain'!OUT_CG_REGULAR",
            "='Capital Gain'!OUT_CG_REGULAR",
            0,
            "='Capital Gain'!OUT_CG_EXEMPT",
            "Sheet 6",
        ),
        (
            "Capital gains — special 15% (held > 5 years / listed taxable)",
            "='Capital Gain'!OUT_CG_SPECIAL15",
            0,
            "='Capital Gain'!OUT_CG_SPECIAL15",
            0,
            "Sheet 6",
        ),
        (
            "Income from other sources — regular",
            "='Income from Other Sources'!OUT_OS_REGULAR",
            "='Income from Other Sources'!OUT_OS_REGULAR",
            0,
            "='Income from Other Sources'!OUT_OS_EXEMPT",
            "Sheet 7",
        ),
        (
            "Income from other sources — lottery / game winnings (special 25%)",
            "='Income from Other Sources'!OUT_OS_LOTTERY",
            0,
            "='Income from Other Sources'!OUT_OS_LOTTERY",
            0,
            "Sheet 7",
        ),
    ]

    # Use named ranges (workbook-level) instead of sheet!OUT_ refs — more reliable
    # After defining names OUT_* we will set formulas to =OUT_EMP_TAXABLE etc.
    named_map = [
        ("Income from employment (taxable after 1/3 exemption)", "OUT_EMP_TAXABLE", "OUT_EMP_TAXABLE", "0", "OUT_EMP_EXEMPT", "Income from Employment"),
        ("Income from financial assets — interest / profit / discount", "OUT_FIN_REGULAR", "OUT_FIN_REGULAR", "0", "0", "Income from Financial Assets"),
        ("Income from financial assets — dividend (special rate)", "OUT_FIN_DIVIDEND", "0", "OUT_FIN_DIVIDEND", "OUT_FIN_DIV_EXEMPT", "Income from Financial Assets"),
        ("Income from rent (ordinary)", "OUT_RENT_TAXABLE", "OUT_RENT_TAXABLE", "0", "0", "Income from Rent"),
        ("Special income from rent (if any, s.39)", "OUT_RENT_SPECIAL", "OUT_RENT_SPECIAL", "0", "0", "Income from Rent"),
        ("Income from agriculture", "OUT_AGRI_TAXABLE", "OUT_AGRI_TAXABLE", "0", "OUT_AGRI_EXEMPT", "Income from Agriculture"),
        ("Income from business (including add-backs)", "OUT_BUS_TAXABLE", "OUT_BUS_TAXABLE", "0", "0", "Income from Business"),
        ("Special business income (s.56 memo — already in business figure if added back)", "OUT_BUS_SPECIAL", "0", "0", "0", "Income from Business"),
        ("Capital gains — charged at regular slab (held ≤ 5 years)", "OUT_CG_REGULAR", "OUT_CG_REGULAR", "0", "OUT_CG_EXEMPT", "Capital Gain"),
        ("Capital gains — charged at 15% (held > 5 years / listed taxable)", "OUT_CG_SPECIAL15", "0", "OUT_CG_SPECIAL15", "0", "Capital Gain"),
        ("Income from other sources — regular", "OUT_OS_REGULAR", "OUT_OS_REGULAR", "0", "OUT_OS_EXEMPT", "Income from Other Sources"),
        ("Income from other sources — lottery / games (25%)", "OUT_OS_LOTTERY", "0", "OUT_OS_LOTTERY", "0", "Income from Other Sources"),
    ]

    cons_cells = []
    for lab, total, regular, special, exempt, src in named_map:
        style_label(ws.cell(r, 1), lab)
        if total == "0":
            style_calc(ws.cell(r, 2), 0)
        else:
            style_calc(ws.cell(r, 2), f"={total}")
        if regular == "0":
            style_calc(ws.cell(r, 3), 0)
        else:
            style_calc(ws.cell(r, 3), f"={regular}")
        if special == "0":
            style_calc(ws.cell(r, 4), 0)
        else:
            style_calc(ws.cell(r, 4), f"={special}")
        if exempt == "0":
            style_calc(ws.cell(r, 5), 0)
        else:
            style_calc(ws.cell(r, 5), f"={exempt}")
        cell = ws.cell(r, 6, src)
        cell.font = font(size=8, color=LINK, italic=True)
        cell.hyperlink = f"#{quote_sheetname(src)}!A1"
        cell.alignment = CENTER
        # check: B should equal C+D (special business memo row is an exception)
        if "Special business income" in lab:
            style_note(ws.cell(r, 7), "Memo only — do not double count")
        else:
            style_calc(ws.cell(r, 7), f'=IF(ABS(B{r}-C{r}-D{r})>1,"CHECK REQUIRED","OK")', number=False)
            ws.cell(r, 7).number_format = "@"
        cons_cells.append(r)
        if "Special business" in lab:
            C["ROW_BUS_SPECIAL_MEMO"] = r
        r += 1
    cons_end = r - 1
    C["CONS_START"] = cons_start
    C["CONS_END"] = cons_end

    # Totals — exclude the special business memo row from the sum of column B
    style_label(ws.cell(r, 1), "TOTAL INCOME (sum of seven heads, excluding memo row)", bold=True)
    # Sum B but subtract memo if it was included — we put 0 in B for memo? Wait I put OUT_BUS_SPECIAL in B.
    # Better: B of memo should be 0 to avoid double count. Fix: set memo B = 0.
    ws.cell(C["ROW_BUS_SPECIAL_MEMO"], 2).value = 0
    ws.cell(C["ROW_BUS_SPECIAL_MEMO"], 3).value = 0
    ws.cell(C["ROW_BUS_SPECIAL_MEMO"], 4).value = 0
    ws.cell(C["ROW_BUS_SPECIAL_MEMO"], 5).value = 0
    style_calc(ws.cell(C["ROW_BUS_SPECIAL_MEMO"], 7), "=OUT_BUS_SPECIAL")
    ws.cell(C["ROW_BUS_SPECIAL_MEMO"], 7).number_format = NUM
    style_note(ws.cell(C["ROW_BUS_SPECIAL_MEMO"], 8), "Memo amount (s.56). Already inside business income. Not added again.")
    style_calc(ws.cell(r, 2), f"=SUM(B{cons_start}:B{cons_end})")
    style_calc(ws.cell(r, 3), f"=SUM(C{cons_start}:C{cons_end})")
    style_calc(ws.cell(r, 4), f"=SUM(D{cons_start}:D{cons_end})")
    style_calc(ws.cell(r, 5), f"=SUM(E{cons_start}:E{cons_end})")
    for c in range(1, 6):
        ws.cell(r, c).fill = fill(NAVY)
        ws.cell(r, c).font = font(bold=True, color=WHITE, size=10)
        if c > 1:
            ws.cell(r, c).number_format = NUM
    C["S8_TotalIncome"] = f"$B${r}"
    C["S8_Regular"] = f"$C${r}"
    C["S8_Special"] = f"$D${r}"
    C["S8_Exempt"] = f"$E${r}"
    define_name(wb, "S8_TotalIncome", ws.title, C["S8_TotalIncome"])
    define_name(wb, "S8_Regular", ws.title, C["S8_Regular"])
    r += 1

    style_label(ws.cell(r, 1), "Less: further exempt income / statutory exclusion not already stripped on head sheets", bold=True)
    style_input(ws.cell(r, 2), 0, number=True)
    style_note(ws.cell(r, 3), "Use only if an exemption applies at total-income level and was not already removed on a head sheet.")
    ws.merge_cells(f"C{r}:H{r}")
    C["S8_FurtherExempt"] = f"$B${r}"
    r += 1

    style_label(ws.cell(r, 1), "TOTAL TAXABLE INCOME", bold=True)
    style_calc(ws.cell(r, 2), f"={C['S8_TotalIncome']}-{C['S8_FurtherExempt']}")
    for c in range(1, 3):
        ws.cell(r, c).fill = fill(TEAL)
        ws.cell(r, c).font = font(bold=True, color=WHITE, size=11)
    ws.cell(r, 2).number_format = NUM
    C["S8_TTI"] = f"$B${r}"
    define_name(wb, "S8_TTI", ws.title, C["S8_TTI"])
    r += 2

    # Integrity check
    style_label(ws.cell(r, 1), "INTEGRITY CHECK — sum of head outputs vs this sheet", bold=True)
    style_calc(
        ws.cell(r, 2),
        '=IF(ABS(S8_TotalIncome-(OUT_EMP_TAXABLE+OUT_FIN_REGULAR+OUT_FIN_DIVIDEND+OUT_RENT_TAXABLE+OUT_RENT_SPECIAL'
        '+OUT_AGRI_TAXABLE+OUT_BUS_TAXABLE+OUT_CG_REGULAR+OUT_CG_SPECIAL15+OUT_OS_REGULAR+OUT_OS_LOTTERY))>1,'
        '"CHECK REQUIRED","OK — Sheet 8 equals Sheets 1–7")',
        number=False,
    )
    ws.merge_cells(f"B{r}:F{r}")
    ws.cell(r, 2).number_format = "@"
    C["S8_Integrity"] = f"$B${r}"
    r += 2

    # ---- Tax liability ----
    r = section(ws, r, "2", "COMPUTATION OF TAX LIABILITY")

    write_wrapped(
        ws,
        r,
        1,
        "Regular-rate income is taxed under the slab in the Control Panel (or at 30% flat if the assessee is a non-resident foreigner). "
        "Dividend, long-term / listed capital gains and lottery winnings are taxed at their own rates and are NOT passed through the slab. "
        "Investment rebate is then applied to the regular tax (not to special-rate tax). "
        "Minimum tax is compared with tax after rebate. Surcharge (if any) is added. "
        "TDS / AIT is credited last.",
        "L",
        32,
        font(size=9),
        LIGHT_NAVY,
    )
    r += 1

    # Regular income for slab = S8_Regular (already excludes special)
    style_label(ws.cell(r, 1), "A. Income charged at regular / slab rate", bold=True)
    style_calc(ws.cell(r, 2), f"={C['S8_Regular']}")
    C["TAX_REG_BASE"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "B. Income charged at special rates (dividend + LTCG/listed CG + lottery)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['S8_Special']}")
    r += 1

    # Now fill slab income/tax formulas using TAX_REG_BASE
    # Remaining income cascading
    s1 = C["SLAB_START"]
    # D = income in slab, E = tax, F = cumulative income allocated
    # Slab 1
    ws[f"D{s1}"].value = f'=MIN({C["TAX_REG_BASE"]},{C["SLAB_1_W"]})'
    ws[f"E{s1}"].value = f"=D{s1}*C{s1}"
    ws[f"F{s1}"].value = f"=D{s1}"
    for i in range(1, 5):
        rr = s1 + i
        prev = rr - 1
        ws[f"D{rr}"].value = f'=MIN(MAX({C["TAX_REG_BASE"]}-F{prev},0),B{rr})'
        ws[f"E{rr}"].value = f"=D{rr}*C{rr}"
        ws[f"F{rr}"].value = f"=F{prev}+D{rr}"
    # last slab — balance
    last = s1 + 5
    ws[f"D{last}"].value = f'=MAX({C["TAX_REG_BASE"]}-F{last-1},0)'
    ws[f"E{last}"].value = f"=D{last}*C{last}"
    ws[f"F{last}"].value = f"=F{last-1}+D{last}"

    style_label(ws.cell(r, 1), "C. Tax on regular income as per slab (or 30% if non-resident foreigner)", bold=True)
    style_calc(
        ws.cell(r, 2),
        f'=IF({C["P_Status"]}="Non-resident (foreigner)",{C["TAX_REG_BASE"]}*{C.get("P_NRRate","0.3")},SUM(E{s1}:E{last}))',
    )
    # P_NRRate is a cell
    ws.cell(r, 2).value = (
        f'=IF(\'Comprehensive Tax Computation\'!{C["P_Status"]}="Non-resident (foreigner)",'
        f'{C["TAX_REG_BASE"]}*\'Comprehensive Tax Computation\'!{C["P_NRRate"]},'
        f"SUM(E{s1}:E{last}))"
    )
    C["TAX_SLAB"] = f"$B${r}"
    r += 1

    style_label(ws.cell(r, 1), "D. Tax on dividend @ special rate", bold=True)
    style_calc(ws.cell(r, 2), "=OUT_FIN_DIVIDEND*P_DivRate")
    C["TAX_DIV"] = f"$B${r}"
    r += 1

    style_label(ws.cell(r, 1), "E. Tax on special-rate capital gains @ 15% (or s.125 TDS if you treat it as minimum — see note)", bold=True)
    style_calc(ws.cell(r, 2), "=OUT_CG_SPECIAL15*P_CGLongRate")
    C["TAX_CG"] = f"$B${r}"
    style_note(ws.cell(r, 3), "Compare with TDS at registration (s.125). Tax payable on this gain is the higher of 15% and s.125 TDS (minimum tax). The higher-of logic is applied in row G below.")
    ws.merge_cells(f"C{r}:H{r}")
    r += 1

    style_label(ws.cell(r, 1), "F. Tax on lottery / game winnings @ special rate (no deduction)", bold=True)
    style_calc(ws.cell(r, 2), "=OUT_OS_LOTTERY*P_LotteryRate")
    C["TAX_LOT"] = f"$B${r}"
    r += 1

    style_label(ws.cell(r, 1), "G. Extra tax if s.125 TDS on long-term CG exceeds 15% (minimum tax on that gain)", bold=True)
    style_calc(ws.cell(r, 2), f"=MAX(0,{C['P_TDS_CG']}-{C['TAX_CG']})")
    C["TAX_CG_MIN_EXTRA"] = f"$B${r}"
    style_note(ws.cell(r, 3), "If registration TDS > 15% of the gain, the excess is still payable as minimum tax on that transfer. VERIFY s.163 / s.125.")
    ws.merge_cells(f"C{r}:H{r}")
    r += 1

    style_label(ws.cell(r, 1), "H. GROSS TAX (C + D + E + F + G) before rebate", bold=True)
    style_calc(ws.cell(r, 2), f"={C['TAX_SLAB']}+{C['TAX_DIV']}+{C['TAX_CG']}+{C['TAX_LOT']}+{C['TAX_CG_MIN_EXTRA']}")
    C["TAX_GROSS"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(NAVY)
    ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(NAVY)
    ws.cell(r, 2).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).number_format = NUM
    r += 2

    # Rebate
    r = subsection(ws, r, "INVESTMENT TAX REBATE  (s.78 / Sixth Schedule, Part 3)")
    style_label(ws.cell(r, 1), "Eligible total income for 3% base (regular-rate income only)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['TAX_REG_BASE']}")
    style_note(ws.cell(r, 3), "Default excludes special-rate income (dividend, 15% CG, lottery) and exempt income. FO 2025: includes income subject to minimum tax; excludes firm/AOP share and final-tax income. VERIFY.")
    ws.merge_cells(f"C{r}:H{r}")
    C["REB_BASE"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "(a)  % of eligible total income")
    style_calc(ws.cell(r, 2), f"={C['REB_BASE']}*{C['P_RebateIncPct']}")
    C["REB_A"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "(b)  % of eligible investment")
    style_calc(ws.cell(r, 2), f"={C['P_EligInv']}*{C['P_RebateInvPct']}")
    C["REB_B"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "(c)  Absolute statutory cap")
    style_calc(ws.cell(r, 2), f"={C['P_RebateCap']}")
    C["REB_C"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Rebate allowed = LOWEST of (a), (b), (c)  — cannot exceed regular slab tax", bold=True)
    style_calc(ws.cell(r, 2), f"=MIN({C['REB_A']},{C['REB_B']},{C['REB_C']},{C['TAX_SLAB']})")
    C["REBATE"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL)
    ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(TEAL)
    ws.cell(r, 2).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "I. Tax after investment rebate", bold=True)
    style_calc(ws.cell(r, 2), f"={C['TAX_GROSS']}-{C['REBATE']}")
    C["TAX_AFTER_REB"] = f"$B${r}"
    r += 2

    # Minimum tax
    r = subsection(ws, r, "MINIMUM TAX")
    style_label(ws.cell(r, 1), "Applicable minimum tax (existing vs new taxpayer)", bold=True)
    style_calc(
        ws.cell(r, 2),
        f'=IF({C["S8_TTI"]}>{C["P_Threshold"]},IF({C["P_NewTaxpayer"]}="Yes",{C["P_MinTaxNew"]},{C["P_MinTax"]}),0)',
    )
    C["TAX_MIN"] = f"$B${r}"
    style_note(ws.cell(r, 3), "Charged only if total income exceeds the tax-free threshold. AY 2026-27: BDT 5,000 (BDT 1,000 if new). VERIFY.")
    ws.merge_cells(f"C{r}:H{r}")
    r += 1
    style_label(ws.cell(r, 1), "J. Tax after minimum-tax comparison  (higher of tax after rebate and minimum tax)", bold=True)
    style_calc(ws.cell(r, 2), f"=MAX({C['TAX_AFTER_REB']},{C['TAX_MIN']})")
    C["TAX_AFTER_MIN"] = f"$B${r}"
    r += 2

    # Surcharge
    r = subsection(ws, r, "SURCHARGE")
    style_label(ws.cell(r, 1), "K. Surcharge on income tax (rate × tax after minimum tax)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['TAX_AFTER_MIN']}*{C['P_SurRate']}")
    C["TAX_SUR"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "L. TOTAL TAX + SURCHARGE", bold=True)
    style_calc(ws.cell(r, 2), f"={C['TAX_AFTER_MIN']}+{C['TAX_SUR']}")
    C["TAX_LIAB"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(NAVY)
    ws.cell(r, 1).font = font(bold=True, color=WHITE, size=11)
    ws.cell(r, 2).fill = fill(NAVY)
    ws.cell(r, 2).font = font(bold=True, color=WHITE, size=11)
    ws.cell(r, 2).number_format = NUM
    r += 2

    # Net payable
    r = subsection(ws, r, "TAX PAID AND NET PAYABLE / REFUNDABLE")
    style_label(ws.cell(r, 1), "M. Total TDS + AIT + other credits (from Control Panel)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['P_TaxPaid']}")
    r += 1
    style_label(ws.cell(r, 1), "N. NET TAX PAYABLE / (REFUNDABLE)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['TAX_LIAB']}-{C['P_TaxPaid']}")
    C["TAX_NET"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL)
    ws.cell(r, 1).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).fill = fill(TEAL)
    ws.cell(r, 2).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).number_format = NUM
    r += 1
    style_calc(
        ws.cell(r, 2),
        f'=IF({C["TAX_NET"]}>0,"PAYABLE","REFUNDABLE / NIL")',
        number=False,
    )
    ws.cell(r, 2).number_format = "@"
    style_label(ws.cell(r, 1), "Status")
    r += 2

    # Warning on refundability
    write_wrapped(
        ws,
        r,
        1,
        "EXAM WARNING: Do not automatically treat every TDS as refundable. Dividend TDS and certain collected taxes can operate as minimum tax "
        "and may not generate a cash refund. Land-registration tax (s.125) is a minimum tax on that capital gain. "
        "If the exam is silent, show TDS as a credit and add a one-line note that refundability of minimum-tax TDS should be confirmed.",
        "L",
        32,
        font(size=9, italic=True, color=WARN_FONT),
        WARN_FILL,
    )
    r += 2

    # ---- Integrated example narrative ----
    r = section(ws, r, "3", "INTEGRATED ICAB-STYLE EXAMPLE  (the same taxpayer is pre-filled on Sheets 1–7)")
    write_wrapped(
        ws,
        r,
        1,
        "QUESTION / FACTS  —  Mr. Md. Karim Rahman is a resident individual (male, age 42) living in Dhaka. "
        "He is not a government employee and not a shareholder-director. "
        "During income year 2025-26 he had: (i) employment with a private company; (ii) FDR, savings-bank and treasury-bond interest and a listed-company dividend; "
        "(iii) a let-out residential flat; (iv) agricultural operations on ancestral land; (v) a sole-proprietorship trading business; "
        "(vi) sale of listed shares and a plot of land held for 7 years; and (vii) royalty, a gift from a friend, a gift from his father, a government cash incentive and a lottery prize. "
        "He contributed to a recognised provident fund, paid a life-insurance premium and invested in a DPS and listed shares. "
        "TDS was deducted from salary, interest, dividend, land registration and lottery, and he paid advance tax. "
        "REQUIRED: Compute income under each of the 7 heads, total income, tax liability and net tax payable for AY 2026-27.",
        "L",
        72,
        font(size=9),
        LIGHT_GOLD,
    )
    r += 1
    write_wrapped(
        ws,
        r,
        1,
        "APPROACH (what ICAB expects): Compute each head on its own legal basis (do not start from a single 'net profit' and dump everything there). "
        "Apply head-specific exemptions (employment 1/3, agri 5-lakh only if exclusive, listed-share CG exemption, relative-gift exemption) on the correct sheet. "
        "Keep special-rate income (dividend 15%, long-term CG 15%, lottery 25%) out of the slab. "
        "TDS is never a deduction from income. Then aggregate under s.29, compute slab tax + special-rate tax − rebate, compare with minimum tax, add surcharge, subtract credits.",
        "L",
        48,
        font(size=9),
        LIGHT_TEAL,
    )
    r += 2

    # ---- Exam tips ----
    r = section(ws, r, "4", "ICAB EXAM TIPS  —  TOTAL INCOME AND TAX LIABILITY")
    tips = [
        "Always start the answer with Income Year and Assessment Year, residential status and the seven-head heading. Presentation marks are real marks.",
        "Identify the head BEFORE you discuss exemption. Festival bonus is employment; FDR interest is financial assets; rent of a shop (not a hotel) is rent, not business; lottery is other sources.",
        "Never net TDS against the income line. Show gross income, then show TDS only in the tax-payment section.",
        "Employment: from AY under ITA 2023 there are no separate HRA / medical / conveyance exemptions. One composite exemption — lower of 1/3 of employment income or the statutory cap.",
        "Duty TA/DA and specified major-surgery medical reimbursement (non-shareholder-director) are EXCLUDED from employment income under s.32(2) — they never enter the 1/3 calculation.",
        "Rent: statutory repair is 30% commercial / 25% non-commercial of gross rental value. You cannot claim actual repair instead. Vacancy needs electricity-bill evidence (s.37).",
        "Business: start from profit as per accounts and reconcile. Personal, capital, provisions, cash-salary, cash-rent, excess entertainment, income-tax and accounting depreciation are the classic add-backs.",
        "Special business income (s.56) is taxed at the regular rate with no set-off / no 3rd Schedule depreciation against it. If the exam asks for it separately, show a memo. Do not double-count.",
        "Capital gain on listed shares of an ordinary investor up to the exemption threshold is often exempt — do not automatically put it in the 15% pot. Land held > 5 years is 15% (or s.125 TDS if higher).",
        "Gift from spouse / parent / child is exempt if disclosed in both returns. Gift from a friend is other sources. Do not confuse with capital gain (a gift is not a 'transfer' for CG in the usual sense).",
        "Agricultural exemption of BDT 5 lakh is NOT available once the assessee has employment, rent, business, CG or other-source income. Financial-asset income alone does not destroy it (FO 2025 — VERIFY).",
        "If the question is silent on the Finance Act year, state your assumed AY and rates at the top. Examiners reward a clear assumption more than a silent (and possibly wrong) rate.",
    ]
    for i, t in enumerate(tips, 1):
        write_wrapped(ws, r, 1, f"{i}.  {t}", "L", 28, font(size=9), ALT if i % 2 == 0 else WHITE)
        r += 1
    r += 1

    # ---- Assumptions ----
    r = section(ws, r, "5", "ASSUMPTIONS / NOTES  (read before using numbers in an answer script)")
    notes = [
        "Default year: Income Year 2025-26 / Assessment Year 2026-27. Slabs, thresholds, rebate percentages and the employment-exemption cap are taken from Finance Ordinance 2025 as commonly summarised by KPMG / ACNABIN / PwC, with later-2026 practitioner updates on rebate (10% / BDT 750,000) adopted as the default. VERIFY against the Finance Act printed in your ICAB study pack.",
        "Some 2026 commentaries mention a general threshold of BDT 400,000 rather than BDT 375,000. The Control Panel is formula-driven — change the category-lookup amounts in J11:K15 if your examiner uses a different figure.",
        "Section numbers cited are those of the Income Tax Act, 2023 (as commonly numbered: s.29–s.31 heads; s.32–34 employment; s.35–39 rent; s.40–44 agriculture; s.45–56 business; s.57–61 capital gains; s.62–65 financial assets; s.66–69 other sources). Where a paragraph of the Sixth / Seventh Schedule is year-sensitive it is marked VERIFY.",
        "Government-employee special exemptions (NBR notification after ITA 2023) are NOT built into the default example. If the question is a government servant, tick 'Government employee?' and adjust the employment sheet notes; do not rely on the private-sector 1/3 alone without reading the notification.",
        "This file is an educational template. It is not a substitute for the Act, the Rules, the Finance Act of the exam year, or an NBR circular. If a treatment is uncertain it is flagged in yellow rather than silently assumed.",
    ]
    for i, t in enumerate(notes, 1):
        write_wrapped(ws, r, 1, f"{i}.  {t}", "L", 40, font(size=9), NOTE_FILL)
        r += 1
    r += 1

    # ---- Legal references ----
    r = section(ws, r, "6", "LEGAL REFERENCES")
    refs = [
        "Income Tax Act, 2023 (ITA 2023) — principal statute replacing the Income-tax Ordinance, 1984.",
        "s.18 charge of tax; s.26 scope of total income; s.27 income deemed to accrue or arise in Bangladesh; s.29 computation of total income; s.30 heads of income; s.31 consolidation.",
        "s.76–s.79 exemptions, exclusions and general tax relief on investments (Sixth Schedule).",
        "s.86 onwards — deduction / collection of tax at source; s.150 credit of tax deducted; s.163 minimum tax (VERIFY current numbering if your reprint differs).",
        "Seventh Schedule / Part 7 — special rates (capital gains, dividend, lottery). VERIFY the reprint you are using.",
        "Third Schedule — depreciation allowance.",
        "Finance Ordinance, 2025 and subsequent Finance Act(s) — rates, thresholds, rebate formula, agricultural exemption, employment-exemption cap.",
        "Relevant SROs / NBR circulars / Paripatra of the exam year (especially government-employee salary exemption and listed-share CG).",
        "Form of Return (IT-11GA) — presentation of rental computation and head-wise totals; useful as a presentation template in the exam.",
    ]
    for t in refs:
        write_wrapped(ws, r, 1, "•  " + t, "L", 18, font(size=9))
        r += 1
    r += 1

    # Error-check dashboard
    r = section(ws, r, "7", "WORKBOOK ERROR-CHECK DASHBOARD")
    checks = [
        ("Sheet 8 equals sum of Sheets 1–7", f"={C['S8_Integrity']}"),
        ("Regular + special = total income", f'=IF(ABS({C["S8_TotalIncome"]}-{C["S8_Regular"]}-{C["S8_Special"]})>1,"CHECK REQUIRED","OK")'),
        ("Rebate does not exceed slab tax", f'=IF({C["REBATE"]}>{C["TAX_SLAB"]}+0.001,"CHECK REQUIRED","OK")'),
        ("Net payable = liability − credits", f'=IF(ABS({C["TAX_NET"]}-({C["TAX_LIAB"]}-{C["P_TaxPaid"]}))>1,"CHECK REQUIRED","OK")'),
        ("Employment taxable ≤ gross (from Sheet 1)", '=IF(OUT_EMP_TAXABLE>OUT_EMP_GROSS+0.001,"CHECK REQUIRED","OK")'),
        ("Exempt employment ≤ gross", '=IF(OUT_EMP_EXEMPT>OUT_EMP_GROSS+0.001,"CHECK REQUIRED","OK")'),
    ]
    # fix the rebate check formula properly
    checks[2] = ("Rebate does not exceed slab tax", f'=IF({C["REBATE"]}>{C["TAX_SLAB"]}+0.001,"CHECK REQUIRED","OK")')
    header_row(ws, r, ["Check", "Result", "", "", "", "", "", "", "", "", "", ""], SUBSEC)
    r += 1
    for lab, formula in checks:
        style_label(ws.cell(r, 1), lab)
        style_calc(ws.cell(r, 2), formula, number=False)
        ws.cell(r, 2).number_format = "@"
        r += 1

    # Conditional formatting for CHECK REQUIRED
    red_font = Font(color="9C0006", bold=True, name="Calibri", size=10)
    red_fill = PatternFill("solid", fgColor="FFC7CE")
    ws.conditional_formatting.add(
        "B1:G400",
        FormulaRule(formula=['ISNUMBER(SEARCH("CHECK REQUIRED",B1))'], fill=red_fill, font=red_font),
    )

    ws.auto_filter.ref = None
    return r


def start_head(ws, title, legal_line):
    page_setup(ws, title, landscape=True)
    set_col_widths(
        ws,
        {
            "A": 44,
            "B": 15,
            "C": 15,
            "D": 15,
            "E": 15,
            "F": 15,
            "G": 20,
            "H": 38,
            "I": 14,
            "J": 14,
            "K": 14,
            "L": 18,
        },
    )
    banner(ws, 1, f"HEAD OF INCOME  ·  {title.upper()}  ·  ALL AMOUNTS IN BDT (৳)", "A1:L1", BAND, 14)
    ws.merge_cells("A2:L2")
    ws["A2"] = legal_line
    ws["A2"].font = font(size=9, italic=True, color=WHITE)
    ws["A2"].fill = fill(NAVY)
    ws["A2"].alignment = Alignment(vertical="center", indent=1)
    for c in range(1, 13):
        ws.cell(2, c).fill = fill(NAVY)
        ws.cell(2, c).font = font(size=9, italic=True, color=WHITE)
    ws.row_dimensions[2].height = 16
    nav_row(ws, 3, title)
    legend_row(ws, 4)
    return 6


def year_banner(ws, r):
    style_label(ws.cell(r, 1), "Assessee / IY / AY (linked to Home sheet)", bold=True)
    style_calc(ws.cell(r, 2), '=P_Name', number=False)
    style_calc(ws.cell(r, 3), '="IY "&P_IY&"  |  AY "&P_AY', number=False)
    ws.merge_cells(f"C{r}:E{r}")
    style_calc(ws.cell(r, 6), '=P_Status', number=False)
    style_calc(ws.cell(r, 7), '=P_Category', number=False)
    ws.merge_cells(f"G{r}:I{r}")
    return r + 1


def close_head(ws, r, tips, notes, refs):
    r = section(ws, r, "F", "ICAB EXAM TIPS")
    for i, t in enumerate(tips, 1):
        write_wrapped(ws, r, 1, f"{i}.  {t}", "L", 26, font(size=9), ALT if i % 2 == 0 else WHITE)
        r += 1
    r += 1
    r = section(ws, r, "G", "ASSUMPTIONS / NOTES")
    for i, t in enumerate(notes, 1):
        write_wrapped(ws, r, 1, f"{i}.  {t}", "L", 32, font(size=9), NOTE_FILL)
        r += 1
    r += 1
    r = section(ws, r, "H", "LEGAL REFERENCES")
    for t in refs:
        write_wrapped(ws, r, 1, "•  " + t, "L", 16, font(size=9))
        r += 1
    return r


def output_box(ws, r, title, rows):
    """rows = list of (label, formula_or_value, key_or_None, is_input). Last key rows become named later by caller."""
    r = subsection(ws, r, title)
    start = r
    keys = {}
    for lab, val, key, is_in in rows:
        style_label(ws.cell(r, 1), lab, bold=True)
        if is_in:
            style_input(ws.cell(r, 2), val, number=True)
        else:
            style_calc(ws.cell(r, 2), val)
        if key:
            keys[key] = r
        r += 1
    for c in range(1, 3):
        ws.cell(r - 1, c).fill = fill(TEAL)
        ws.cell(r - 1, c).font = font(bold=True, color=WHITE, size=11)
        if c == 2:
            ws.cell(r - 1, c).number_format = NUM
    return r + 1, keys


# ===========================================================================
# SHEET 1 — EMPLOYMENT
# ===========================================================================
def build_employment(ws, wb):
    r = start_head(
        ws,
        "Income from Employment",
        "ITA 2023  Chapter II  ss.32–34  |  Exemption: Sixth Schedule Part A (lower of 1/3 of employment income or the cap on the Home sheet)  |  Valuation of perquisites: s.33",
    )
    r = year_banner(ws, r)
    r += 1

    r = section(ws, r, "A", "QUICK CONCEPT / DEFINITION")
    bullets = [
        "Definition: Income from employment is the residual of monetary receipts, salaries and benefits from an office or employment, including employee-share-scheme income, untaxed arrear salary, and amounts received from a past or future employer (s.32(1)).",
        "What falls here: basic salary, wages, allowances, festival and incentive bonus, overtime, leave encashment, commission, advance and arrear salary, perquisites (including incentive bonus), profit in lieu of salary (e.g. termination compensation), and the value of accommodation / vehicle / other benefits.",
        "Important exclusions (s.32(2) — these never enter gross employment income): (a) medical expenses for heart, kidney, eye, liver or cancer operations of an employee who is NOT a shareholder-director; (b) conveyance, travelling and daily allowance received wholly and exclusively for the performance of duties.",
        "Employer reimbursements incurred wholly and necessarily for duties, and group-insurance receipts, are also commonly excluded / exempt — confirm the Sixth Schedule paragraph in your reprint.",
        "ITA 2023 change (exam favourite): the old separate exemptions for house-rent allowance, medical allowance and conveyance allowance have been REPLACED by a single exemption — lower of one-third of income from employment or the statutory cap (BDT 500,000 under FO 2025). Do not apply the old ITO 1984 HRA/medical/conveyance limits unless the question is set under the old Ordinance.",
        "Perquisite (s.32): any payment or benefit including incentive bonus, but NOT basic, arrear, advance, festival allowance, leave encashment, overtime, or contributions to recognised PF / approved pension / gratuity / superannuation funds.",
        "Valuation (s.33): rent-free accommodation = annual cost / rent paid by employer; concessional accommodation = that amount minus rent paid by employee. Vehicle (personal use) is a monthly statutory amount by engine capacity (see calculator below).",
        "ICAB points: (1) 1/3 is of employment income AFTER s.32(2) exclusions, not of CTC. (2) Employee PF is part of salary already; it is not a second deduction here — it may be an investment rebate on the Home sheet. (3) Employer's contribution to a recognised fund is generally not taxed as employment income — VERIFY. (4) TDS u/s 86 is a credit, not a deduction. (5) Government-employee notifications can be more generous — do not apply them to a private employee.",
    ]
    for t in bullets:
        write_wrapped(ws, r, 1, "•  " + t, "L", 28, font(size=9), LIGHT_NAVY)
        r += 1
    r += 1

    r = section(ws, r, "B", "TYPES OF INCOME  —  TAX TREATMENT")
    header_row(
        ws,
        r,
        ["Particular", "Tax treatment", "Relevant provision", "Example / exam note", "", "", "", "", "", "", "", ""],
        NAVY,
    )
    r += 1
    types = [
        ("Basic salary / wages", "Fully included", "s.32(1) / definition of salary", "Starting point of every employment computation."),
        ("House rent allowance (cash)", "Included; no separate HRA exemption", "s.32; Sixth Schedule Part A", "Covered only by the composite 1/3 exemption."),
        ("Medical allowance (ordinary)", "Included; no separate exemption", "s.32; Sixth Schedule Part A", "Do not apply the old 10% / BDT 120,000 rule."),
        ("Conveyance allowance (cash, not duty)", "Included", "s.32", "Duty TA/DA is excluded under s.32(2)(b) — different item."),
        ("Festival bonus", "Included (not a 'perquisite')", "s.32 definition", "Festival allowance is excluded from the definition of perquisite, but it is still salary."),
        ("Incentive / performance bonus", "Included (is a perquisite)", "s.32 perquisite", "Incentive bonus is specifically a perquisite. Still fully in the employee's income."),
        ("Overtime / leave encashment / arrear / advance", "Included", "s.32", "Arrear is taxable in the year of receipt if not previously taxed."),
        ("Commission, fees, honorarium from employer", "Included", "s.32", "If paid by a third party for a non-employment activity, consider Other Sources."),
        ("Rent-free / concessional accommodation", "Included at s.33 value", "s.33 table", "Annual cost or (annual cost − concessional rent)."),
        ("Employer-provided car (personal / mixed use)", "Included at monthly statutory value × months", "s.33", "By cc band: 15k / 20k / 30k / 50k per month (PwC 2025). VERIFY."),
        ("Other benefits in kind", "Included at monetary / FMV", "s.33", "Utilities paid by employer, domestic help, club, etc."),
        ("Employee share scheme", "FMV − cost, in the year of receipt", "s.34", "Sale of the right is also employment income."),
        ("Employer contribution to recognised PF / approved funds", "Generally not included (assumption)", "s.32 perquisite exclusion; Sixth Schedule — VERIFY", "Unrecognised-fund credits are usually taxable."),
        ("Employee contribution to PF", "Already inside salary; no extra deduction here", "s.78 / Sixth Schedule Part 3", "May qualify for investment rebate on the Home sheet."),
        ("Termination compensation / profit in lieu of salary", "Included", "s.32(1)(b)", "Label does not matter — look at the substance."),
        ("Duty TA/DA / conveyance wholly for duties", "EXCLUDED from this head", "s.32(2)(b)", "Do not put it in gross and then exempt it."),
        ("Specified major-surgery medical (non-shareholder-director)", "EXCLUDED from this head", "s.32(2)(a)", "Heart, kidney, eye, liver, cancer. Shareholder-director does not get this exclusion."),
        ("Group insurance receipt / employer group-insurance cost", "Generally exempt / excluded — VERIFY", "Sixth Schedule — VERIFY", "Do not invent a number; follow the question."),
        ("TDS on salary", "NOT a deduction from income", "s.86, s.150", "Credit in the tax-payment section on the Home sheet."),
    ]
    for i, (a, b, c, d) in enumerate(types):
        bg = ALT if i % 2 == 0 else WHITE
        ws.cell(r, 1, a).alignment = WRAP_TL
        ws.cell(r, 2, b).alignment = WRAP_TL
        ws.cell(r, 3, c).alignment = WRAP_TL
        ws.merge_cells(f"D{r}:L{r}")
        ws.cell(r, 4, d).alignment = WRAP_TL
        for col in range(1, 13):
            ws.cell(r, col).font = font(size=8)
            ws.cell(r, col).fill = fill(bg)
            ws.cell(r, col).border = thin
        if "EXCLUDED" in b or "NOT a deduction" in b:
            ws.cell(r, 2).fill = fill(WARN_FILL)
            ws.cell(r, 2).font = font(size=8, color=WARN_FONT, bold=True)
        ws.row_dimensions[r].height = 18
        r += 1
    r += 1

    # ---- Computation ----
    r = section(ws, r, "C", "COMPUTATION TEMPLATE  (blue = input; overwrite to solve any question)")
    write_wrapped(
        ws,
        r,
        1,
        "Pre-filled figures are those of Mr. Md. Karim Rahman (the integrated example). "
        "Column C 'Include in gross?' drives the formula. Duty TA/DA and specified surgery start as Exclude. "
        "TDS is recorded only as a memo.",
        "L",
        22,
        font(size=9),
        LIGHT_GOLD,
    )
    r += 1

    header_row(
        ws,
        r,
        [
            "Income item",
            "Gross amount (BDT)",
            "Include in gross?",
            "Amount included",
            "Exempt / excluded amount",
            "Net for 1/3 base",
            "Tax treatment",
            "Explanation / provision",
            "TDS (memo)",
            "Check",
            "",
            "",
        ],
        NAVY,
    )
    r += 1
    emp_items = [
        ("Basic salary", 1200000, "Include", "Taxable", "s.32 — core salary"),
        ("House rent allowance (cash)", 600000, "Include", "Taxable", "No separate HRA exemption under ITA 2023"),
        ("Medical allowance (ordinary)", 60000, "Include", "Taxable", "Covered only by composite 1/3 exemption"),
        ("Conveyance allowance (cash, not duty)", 36000, "Include", "Taxable", "Not s.32(2)(b) — that needs 'wholly for duties'"),
        ("Festival bonus", 200000, "Include", "Taxable", "Salary; not a perquisite, but fully included"),
        ("Incentive / performance bonus", 150000, "Include", "Taxable", "Perquisite, still fully in employee's income"),
        ("Overtime", 40000, "Include", "Taxable", "s.32"),
        ("Leave encashment", 0, "Include", "Taxable", "Blank line for other questions"),
        ("Arrear salary (previously untaxed)", 80000, "Include", "Taxable", "Taxable in year of receipt if not earlier taxed"),
        ("Commission / fees from employer", 0, "Include", "Taxable", "Blank line"),
        ("Other cash allowances", 0, "Include", "Taxable", "Blank line"),
        ("Rent-free / concessional accommodation (s.33)", 0, "Include", "Taxable", "Use the perquisite calculator below and copy the value"),
        ("Employer-provided vehicle (s.33)", 240000, "Include", "Taxable", "Pre-filled from 1,800 cc × 12 × 20,000 — see calculator"),
        ("Other benefits in kind (FMV)", 0, "Include", "Taxable", "Utilities, servant, club, etc."),
        ("Employee share scheme (FMV − cost)", 0, "Include", "Taxable", "s.34"),
        ("Employer contribution to recognised PF", 120000, "Exclude", "Exempt", "Assumption: recognised fund — VERIFY; unrecognised = Include"),
        ("Duty TA/DA / conveyance wholly for duties", 45000, "Exclude", "Not Applicable", "s.32(2)(b) — never in gross"),
        ("Specified surgery medical (heart/kidney/eye/liver/cancer)", 200000, "Exclude", "Not Applicable", "s.32(2)(a) — not a shareholder-director"),
        ("Group insurance / other excluded receipt", 0, "Exclude", "Exempt", "VERIFY Sixth Schedule"),
    ]
    emp_start = r
    for lab, amt, inc, treat, expl in emp_items:
        style_label(ws.cell(r, 1), lab)
        style_input(ws.cell(r, 2), amt, number=True)
        style_input(ws.cell(r, 3), inc, number=False)
        style_calc(ws.cell(r, 4), f'=IF(C{r}="Include",B{r},0)')
        style_calc(ws.cell(r, 5), f'=IF(C{r}="Include",0,B{r})')
        style_calc(ws.cell(r, 6), f"=D{r}")
        style_input(ws.cell(r, 7), treat, number=False)
        style_note(ws.cell(r, 8), expl)
        style_input(ws.cell(r, 9), 0, number=True)
        style_calc(ws.cell(r, 10), f'=IF(OR(D{r}>B{r}+0.001,E{r}>B{r}+0.001),"CHECK REQUIRED","OK")', number=False)
        ws.cell(r, 10).number_format = "@"
        r += 1
    emp_end = r - 1
    add_dv(ws, '"Include,Exclude"', f"C{emp_start}:C{emp_end}")
    add_dv(ws, '"Taxable,Exempt,Partially Taxable,Special Rate,Not Applicable"', f"G{emp_start}:G{emp_end}")

    # totals
    style_label(ws.cell(r, 1), "GROSS EMPLOYMENT INCOME (included items only)", bold=True)
    style_calc(ws.cell(r, 2), f"=SUM(B{emp_start}:B{emp_end})")
    style_calc(ws.cell(r, 4), f"=SUM(D{emp_start}:D{emp_end})")
    style_calc(ws.cell(r, 5), f"=SUM(E{emp_start}:E{emp_end})")
    style_calc(ws.cell(r, 6), f"=SUM(F{emp_start}:F{emp_end})")
    style_calc(ws.cell(r, 9), f"=SUM(I{emp_start}:I{emp_end})")
    C["EMP_GROSS"] = f"$D${r}"
    C["EMP_EXCL"] = f"$E${r}"
    ws.cell(r, 1).fill = fill(NAVY)
    ws.cell(r, 1).font = font(bold=True, color=WHITE)
    for col in (2, 4, 5, 6, 9):
        ws.cell(r, col).fill = fill(NAVY)
        ws.cell(r, col).font = font(bold=True, color=WHITE)
        ws.cell(r, col).number_format = NUM
    r += 2

    # Exemption
    r = subsection(ws, r, "COMPOSITE EMPLOYMENT EXEMPTION  (Sixth Schedule, Part A)")
    style_label(ws.cell(r, 1), "One-third of gross employment income", bold=True)
    style_calc(ws.cell(r, 2), f"={C['EMP_GROSS']}/3")
    C["EMP_THIRD"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Statutory cap (linked to Home sheet)", bold=True)
    style_calc(ws.cell(r, 2), "=P_EmpCap")
    r += 1
    style_label(ws.cell(r, 1), "Exemption allowed = LOWER of the two", bold=True)
    style_calc(ws.cell(r, 2), f"=MIN({C['EMP_THIRD']},P_EmpCap)")
    C["EMP_EXEMPT"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL)
    ws.cell(r, 1).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).fill = fill(TEAL)
    ws.cell(r, 2).font = font(bold=True, color=WHITE)
    ws.cell(r, 2).number_format = NUM
    r += 1
    style_label(ws.cell(r, 1), "TAXABLE INCOME FROM EMPLOYMENT", bold=True)
    style_calc(ws.cell(r, 2), f"={C['EMP_GROSS']}-{C['EMP_EXEMPT']}")
    C["EMP_TAXABLE"] = f"$B${r}"
    ws.cell(r, 1).fill = fill(TEAL)
    ws.cell(r, 1).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).fill = fill(TEAL)
    ws.cell(r, 2).font = font(bold=True, color=WHITE, size=12)
    ws.cell(r, 2).number_format = NUM
    r += 1
    style_calc(
        ws.cell(r, 2),
        f'=IF(OR({C["EMP_TAXABLE"]}>{C["EMP_GROSS"]}+0.001,{C["EMP_EXEMPT"]}>{C["EMP_GROSS"]}+0.001),"CHECK REQUIRED","OK")',
        number=False,
    )
    style_label(ws.cell(r, 1), "Error check")
    ws.cell(r, 2).number_format = "@"
    r += 2

    # Perquisite calculator
    r = subsection(ws, r, "PERQUISITE CALCULATORS  (s.33)  —  copy the result into the table above if needed")
    style_label(ws.cell(r, 1), "Vehicle — engine capacity (cc)", bold=True)
    style_input(ws.cell(r, 2), 1800, number=True)
    C["VEH_CC"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Months the vehicle was available")
    style_input(ws.cell(r, 2), 12, number=True)
    C["VEH_M"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Monthly statutory value (auto)", bold=True)
    style_calc(
        ws.cell(r, 2),
        f'=IF({C["VEH_CC"]}<=1500,15000,IF({C["VEH_CC"]}<=2000,20000,IF({C["VEH_CC"]}<=2500,30000,50000)))',
    )
    C["VEH_MTH"] = f"$B${r}"
    style_note(ws.cell(r, 3), "PwC 2025 bands: ≤1,500 cc = 15,000; 1,501–2,000 = 20,000; 2,001–2,500 = 30,000; >2,500 = 50,000 per month. VERIFY s.33 table in your reprint.")
    ws.merge_cells(f"C{r}:H{r}")
    r += 1
    style_label(ws.cell(r, 1), "Vehicle perquisite for the year", bold=True)
    style_calc(ws.cell(r, 2), f"={C['VEH_MTH']}*{C['VEH_M']}")
    r += 1
    style_label(ws.cell(r, 1), "Accommodation — annual cost / rent paid by employer")
    style_input(ws.cell(r, 2), 0, number=True)
    C["ACC_COST"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Rent paid by employee (concessional)")
    style_input(ws.cell(r, 2), 0, number=True)
    C["ACC_PAID"] = f"$B${r}"
    r += 1
    style_label(ws.cell(r, 1), "Accommodation perquisite (s.33)", bold=True)
    style_calc(ws.cell(r, 2), f"=MAX({C['ACC_COST']}-{C['ACC_PAID']},0)")
    r += 2

    # Tax treatment summary table (formulas)
    r = section(ws, r, "D", "TAX-TREATMENT TABLE  (formula-driven from Section C)")
    header_row(
        ws,
        r,
        ["Income item", "Gross amount", "Taxable amount", "Exempt amount", "Deduction / adjustment", "Net taxable amount", "Relevant provision", "Explanation", "", "", "", ""],
        SUBSEC,
    )
    r += 1
    style_label(ws.cell(r, 1), "All included employment receipts")
    style_calc(ws.cell(r, 2), f"={C['EMP_GROSS']}")
    style_calc(ws.cell(r, 3), f"={C['EMP_GROSS']}")
    style_calc(ws.cell(r, 4), 0)
    style_calc(ws.cell(r, 5), 0)
    style_calc(ws.cell(r, 6), f"={C['EMP_GROSS']}")
    ws.cell(r, 7, "s.32(1)")
    ws.cell(r, 8, "Gross after s.32(2) exclusions")
    r += 1
    style_label(ws.cell(r, 1), "s.32(2) and other excluded receipts")
    style_calc(ws.cell(r, 2), f"={C['EMP_EXCL']}")
    style_calc(ws.cell(r, 3), 0)
    style_calc(ws.cell(r, 4), f"={C['EMP_EXCL']}")
    style_calc(ws.cell(r, 5), 0)
    style_calc(ws.cell(r, 6), 0)
    ws.cell(r, 7, "s.32(2)")
    ws.cell(r, 8, "Never part of this head")
    r += 1
    style_label(ws.cell(r, 1), "Composite 1/3 exemption")
    style_calc(ws.cell(r, 2), 0)
    style_calc(ws.cell(r, 3), 0)
    style_calc(ws.cell(r, 4), f"={C['EMP_EXEMPT']}")
    style_calc(ws.cell(r, 5), f"={C['EMP_EXEMPT']}")
    style_calc(ws.cell(r, 6), f"=-{C['EMP_EXEMPT']}")
    ws.cell(r, 7, "Sixth Schedule Part A")
    ws.cell(r, 8, "Lower of 1/3 and cap")
    r += 1
    style_label(ws.cell(r, 1), "TAXABLE INCOME UNDER THIS HEAD", bold=True)
    style_calc(ws.cell(r, 6), f"={C['EMP_TAXABLE']}")
    for c in (1, 6):
        ws.cell(r, c).fill = fill(NAVY)
        ws.cell(r, c).font = font(bold=True, color=WHITE)
    ws.cell(r, 6).number_format = NUM
    r += 2

    # Worked example narrative
    r = section(ws, r, "E", "WORKED EXAMPLE  —  Mr. Md. Karim Rahman (same figures as the template)")
    write_wrapped(
        ws,
        r,
        1,
        "STEP 1 — FACTS. During IY 2025-26 Mr. Rahman received: basic BDT 1,200,000; HRA 600,000; medical allowance 60,000; "
        "cash conveyance 36,000; festival bonus 200,000; incentive bonus 150,000; overtime 40,000; arrear salary 80,000. "
        "The company provided a 1,800 cc car for mixed official/personal use all year. Employer contributed BDT 120,000 to a recognised PF. "
        "He received duty TA/DA of 45,000 (spent on official tours) and a reimbursement of 200,000 for a kidney operation (he is not a shareholder-director). "
        "TDS of 280,000 was deducted from salary.",
        "L",
        56,
        font(size=9),
        LIGHT_GOLD,
    )
    r += 1
    write_wrapped(
        ws,
        r,
        1,
        "STEP 2 — TAX TREATMENT. All cash salary items and the vehicle perquisite (20,000 × 12 = 240,000) are included. "
        "Duty TA/DA is excluded under s.32(2)(b). Kidney-operation reimbursement is excluded under s.32(2)(a). "
        "Employer RPF contribution is treated as excluded (recognised fund — flagged as an assumption). "
        "TDS is ignored in the income computation.",
        "L",
        40,
        font(size=9),
        LIGHT_TEAL,
    )
    r += 1
    write_wrapped(
        ws,
        r,
        1,
        "STEP 3 — COMPUTATION (all live formulas). Gross included = SUM of 'Include' rows. "
        "Exemption = MIN(Gross/3, P_EmpCap). Taxable = Gross − Exemption. "
        "With the pre-filled figures: Gross 2,606,000; 1/3 = 868,667; cap = 500,000; exemption = 500,000; "
        "TAXABLE INCOME FROM EMPLOYMENT = 2,106,000.",
        "L",
        40,
        font(size=9),
        LIGHT_NAVY,
    )
    r += 1
    style_label(ws.cell(r, 1), "Taxable income under this head (live)", bold=True)
    style_calc(ws.cell(r, 2), f"={C['EMP_TAXABLE']}")
    ws.cell(r, 1).fill = fill(TEAL)
    ws.cell(r, 1).font = font(bold=True, color=WHITE, size=11)
    ws.cell(r, 2).fill = fill(TEAL)
    ws.cell(r, 2).font = font(bold=True, color=WHITE, size=11)
    ws.cell(r, 2).number_format = '"BDT "#,##0'
    r += 1
    write_wrapped(
        ws,
        r,
        1,
        "STEP 5 — WHY. The 1/3 exemption replaced item-wise HRA/medical/conveyance exemptions. Applying the old ITO 1984 limits would be a common (and wrong) answer. "
        "s.32(2) items are omitted before the 1/3 is calculated — if you first include the kidney bill and then 'exempt' it, you inflate the 1/3 base. "
        "The vehicle is valued by the s.33 table, not by actual running cost. Incentive bonus is a perquisite for the employer's BDT 10 lakh disallowance, but the employee is still taxed on it in full.",
        "L",
        44,
        font(size=9),
        WHITE,
    )
    r += 2

    r = close_head(
        ws,
        r,
        [
            "Do not use Indian s.10(13A) HRA (50%/40% of salary, rent − 10%). That is a frequent mix-up and will score zero.",
            "Write the working as: Gross employment income (after s.32(2)) − composite exemption = taxable employment income.",
            "Festival bonus is salary; incentive bonus is a perquisite — both are taxable to the employee. The perquisite label matters for the employer's s.55 disallowance, not for excluding it from the employee.",
            "Shareholder-director loses the s.32(2)(a) medical exclusion. Always check that fact in the question.",
            "Government-employee extra exemptions come from NBR notification, not from s.32 itself. State the notification if you use them.",
            "Employee PF is not deducted again under this head. Put it in the rebate working.",
            "If accommodation and cash HRA both appear, include both (cash + s.33 value). There is no 'either/or' under ITA 2023.",
            "Arrear salary: taxable in the year of receipt unless already taxed. Do not spread it backwards unless the question invokes a specific relief.",
        ],
        [
            f"Working year is the AY shown on the Home sheet (default 2026-27). Employment-exemption cap is the named range P_EmpCap.",
            "Vehicle monthly values follow the s.33 table as summarised by PwC (Dec 2025). If your ICAB manual prints a different table, overwrite the calculator note and the monthly-value formula.",
            "Employer contribution to recognised PF is treated as excluded. If the fund is unrecognised, change that row to Include.",
            "No LFA / leave-passage exemption is built in (removed as a separate deduction under ITA 2023).",
        ],
        [
            "ITA 2023 ss.32–34 (Chapter II — Income from employment).",
            "s.33 valuation table of perquisites, allowances and benefits.",
            "s.34 employee share scheme.",
            "s.76 / s.77 and Sixth Schedule, Part A — employment exemption (paragraph number: VERIFY).",
            "s.86 TDS from employment; s.150 credit of tax deducted.",
            "Finance Ordinance 2025 — cap raised to BDT 500,000. Subsequent Finance Act: VERIFY.",
            "NBR notification on government-employee allowances (if the assessee is a public servant).",
        ],
    )

    # Named ranges for outputs — use the actual cells
    define_name(wb, "OUT_EMP_TAXABLE", ws.title, C["EMP_TAXABLE"])
    define_name(wb, "OUT_EMP_GROSS", ws.title, C["EMP_GROSS"])
    define_name(wb, "OUT_EMP_EXEMPT", ws.title, C["EMP_EXEMPT"])
    return r


if __name__ == "__main__":
    import pathlib

    here = pathlib.Path(__file__).resolve().parent
    ns = globals()
    exec((here / "build_heads_rest.py").read_text(encoding="utf-8"), ns)
    exec((here / "build_heads_bus_cg_os.py").read_text(encoding="utf-8"), ns)
    out = here / "ICAB Professional Taxation – 7 Heads of Income.xlsx"
    ns["build_workbook"](str(out))
    print("Wrote", out)

