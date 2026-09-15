"""
Forex & Gold Risk Calculator Generator for Exness
Generates: Forex_Risk_Calculator_Exness.xlsx

Features:
- Supports Forex (EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD) + Gold XAUUSD
- Auto pip value calculation
- Lot size based on Risk % (professional risk management)
- Margin calculation based on Exness leverage and contract size
- Exness account types reference
- Educational only - not financial advice

Requirements:
pip install openpyxl --break-system-packages

Usage:
python generate_forex_calculator.py
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Risk Calculator"

header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
sub_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
red_fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
white_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
bold_font = Font(name="Calibri", bold=True, size=11)
normal_font = Font(name="Calibri", size=11)
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
left_wrap = Alignment(horizontal='left', vertical='center', wrap_text=True)

# Title
ws['A1'] = "Exness Forex & Gold (XAUUSD) Risk & Lot Size Calculator - Educational Only"
ws['A1'].font = Font(bold=True, size=14)
ws.merge_cells('A1:F1')
ws['A2'] = "Not Financial Advice - For Demo Learning Only | Formula: Lot = Risk$ / (SL pips * PipValue)"
ws['A2'].font = Font(italic=True, size=10, color="FF0000")
ws.merge_cells('A2:F2')

ws['A4'] = "INPUTS - Fill YELLOW cells only"
ws['A4'].font = white_font
ws['A4'].fill = header_fill
ws.merge_cells('A4:F4')

# Inputs - row 5 onwards
inputs = [
    ("Account Balance (USD)", 1000, "Your demo balance, e.g., 1000"),
    ("Risk per Trade %", 1, "Pro use 0.5-1%, max 2%. 1% of $1000 = $10 risk"),
    ("Stop Loss (pips)", 30, "For Forex: pips. For Gold XAUUSD: enter in cents, e.g., 100 = $1.00 move = 100 cents"),
    ("Take Profit (pips)", 60, "For 1:2 RR, TP = 2x SL. e.g., SL 30 => TP 60"),
    ("Trading Pair / Instrument", "EURUSD", "Choose: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, XAUUSD"),
    ("Current Market Price", 1.08500, "EURUSD=1.08, USDJPY=150.00, XAUUSD=2030.00 - needed for USDXXX & Gold margin"),
    ("Account Leverage (Exness)", 500, "e.g., 100, 200, 500, 1000, 2000 - Exness allows up to 1:2000"),
    ("Exness Account Type", "Standard", "Standard / Pro / Raw Spread / Zero - margin same formula, spread differs"),
]

r = 5
for label, value, note in inputs:
    ws.cell(row=r, column=1, value=label).font = bold_font
    ws.cell(row=r, column=1).border = thin_border
    ws.cell(row=r, column=2, value=value).fill = yellow_fill
    ws.cell(row=r, column=2).font = bold_font
    ws.cell(row=r, column=2).border = thin_border
    ws.cell(row=r, column=3, value=note).font = normal_font
    ws.cell(row=r, column=3).alignment = left_wrap
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
    r += 1

# Outputs
r += 1
ws[f'A{r}'] = "OUTPUTS - Auto calculated (Do not edit)"
ws[f'A{r}'].font = white_font
ws[f'A{r}'].fill = header_fill
ws.merge_cells(f'A{r}:F{r}')
r += 1

# Risk Amount
ws.cell(row=r, column=1, value="Risk Amount (USD) = Balance * Risk%").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=B5*B6/100").font = bold_font
ws.cell(row=r, column=2).fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value="Max loss if SL hits").font = normal_font
r += 1

# Contract size
ws.cell(row=r, column=1, value="Contract Size").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value='=IF(B9="XAUUSD",100,100000)').font = bold_font
ws.cell(row=r, column=2).fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value='If XAUUSD => 100 oz, else Forex => 100,000').font = normal_font
r += 1

# Pip value per 1 lot
ws.cell(row=r, column=1, value="Pip Value per 1.0 Lot (USD)").font = bold_font
ws.cell(row=r, column=1).border = thin_border
# Complex formula: 
# If XAUUSD: Gold pip value - for 1 lot (100 oz), $0.01 move = $1, $0.10 = $10, $1.00 = $100. So per 1 cent (our pip definition) = $1
# For simplicity: For Gold, we define 1 pip = $0.01, so pip value per 1 lot = $1
# For Forex: if JPY => 1000/Price, if USDXXX => 10/Price, else 10
formula_pip = '=IF(B9="XAUUSD",1,IF(ISNUMBER(SEARCH("JPY",B9)),1000/B10,IF(LEFT(B9,3)="USD",10/B10,10)))'
ws.cell(row=r, column=2, value=formula_pip).font = bold_font
ws.cell(row=r, column=2).fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value='EURUSD= $10 | USDJPY=1000/Price | USDCHF=10/Price | XAUUSD=$1 per $0.01').font = normal_font
r += 1

# Pip value per 0.01 lot
ws.cell(row=r, column=1, value="Pip Value per 0.01 Lot").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=B15*0.01").fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=2).font = bold_font
r += 1

# Lot size
ws.cell(row=r, column=1, value="Recommended Lot Size (Standard Lots)").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=IF(B7=0,0,B13/(B7*B15))").font = Font(bold=True, size=12)
ws.cell(row=r, column=2).fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value="Formula: Risk$ / (SL pips * PipValue per 1 lot)").font = normal_font
r += 1

ws.cell(row=r, column=1, value="Recommended Lot Size (Rounded Down to 0.01)").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=FLOOR(B17*100,1)/100").font = Font(bold=True, size=12, color="006100")
ws.cell(row=r, column=2).fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value="USE THIS in MT5 - rounded down for safety. If <0.01, cannot trade with this SL.").font = bold_font
r += 1

ws.cell(row=r, column=1, value="Position Value / Notional (USD)").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=B18*B14*B10").fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value="Lot * Contract Size * Price").font = normal_font
r += 1

ws.cell(row=r, column=1, value="Required Margin (USD) = Notional / Leverage").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=IF(B11=0,0,B19/B11)").fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value="Exness blocks this margin. Lower leverage = higher margin needed.").font = normal_font
r += 1

ws.cell(row=r, column=1, value="Risk:Reward Ratio").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=IF(B7=0,0,B8/B7)").fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value="2 = 1:2 RR, risk $10 to make $20").font = normal_font
r += 1

ws.cell(row=r, column=1, value="Potential Profit if TP hits (USD)").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=B13*B21").fill = green_fill
ws.cell(row=r, column=2).border = thin_border
r += 1

ws.cell(row=r, column=1, value="Potential Loss if SL hits (USD) - Should = Risk Amount").font = bold_font
ws.cell(row=r, column=1).border = thin_border
ws.cell(row=r, column=2, value="=B18*B7*B15").fill = green_fill
ws.cell(row=r, column=2).border = thin_border
ws.cell(row=r, column=3, value="Cross-check: should equal Risk Amount").font = normal_font
r += 1

# Warnings
r += 1
ws[f'A{r}'] = "RISK WARNINGS & EXNESS ACCOUNT INFO"
ws[f'A{r}'].font = white_font
ws[f'A{r}'].fill = red_fill
ws.merge_cells(f'A{r}:F{r}')
r += 1
warnings = [
    "1. NEVER risk >2% per trade. Pro traders use 0.5%-1% on demo/live.",
    "2. Lot size auto-decreases when SL is wider - this protects your account.",
    "3. Exness minimum lot: Standard = 0.01 lot. If calculator shows <0.01, you must reduce SL or skip trade.",
    "4. GOLD XAUUSD: In this calculator, 1 pip = $0.01 move. So SL 100 pips = $1.00 move (2030.00 -> 2029.00). Exness Gold spread is higher, check live spread.",
    "5. Margin: Higher leverage (1:2000) = lower margin but HIGHER risk of wipeout. Lower leverage (1:100) = safer.",
    "6. Exness Account Types: Standard (spread from 0.3), Raw Spread (from 0.0 + commission), Pro, Zero - lot calculation same, margin same formula.",
    "7. This is EDUCATIONAL ONLY - not BUY/SELL signal. No AI can guarantee profit. Test 30+ trades on demo.",
    "8. For Bangladesh: Check Bangladesh Bank regulations on forex trading before live funding.",
    "9. Always set Stop Loss - trading without SL can blow account in seconds.",
]
for w in warnings:
    ws.cell(row=r, column=1, value=w).font = normal_font
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    ws.cell(row=r, column=1).alignment = left_wrap
    ws.cell(row=r, column=1).border = thin_border
    r += 1

# Sheet 2: Pip Table
ws2 = wb.create_sheet("Pip Value & Contract Table")
ws2['A1'] = "Reference - Exness Contract Specs (Approximate, check Exness website for live values)"
ws2['A1'].font = bold_font
ws2['A1'].fill = sub_fill
ws2.merge_cells('A1:E1')
r = 2
headers = ["Instrument", "Type", "Contract Size", "Pip / Point Size", "Pip Value per 1.0 Lot (USD)"]
for c, h in enumerate(headers, start=1):
    ws2.cell(row=r, column=c, value=h).font = white_font
    ws2.cell(row=r, column=c).fill = header_fill
    ws2.cell(row=r, column=c).border = thin_border
r += 1
data = [
    ["EURUSD", "Forex Major", "100,000", "0.0001", "$10"],
    ["GBPUSD", "Forex Major", "100,000", "0.0001", "$10"],
    ["AUDUSD", "Forex Major", "100,000", "0.0001", "$10"],
    ["NZDUSD", "Forex Major", "100,000", "0.0001", "$10"],
    ["USDJPY", "Forex Major (JPY)", "100,000", "0.01", "1000 / Price (150 => $6.66)"],
    ["USDCHF", "Forex Major", "100,000", "0.0001", "10 / Price (0.90 => $11.11)"],
    ["USDCAD", "Forex Major", "100,000", "0.0001", "10 / Price (1.35 => $7.40)"],
    ["XAUUSD", "Gold Spot", "100 oz", "0.01", "$1 per $0.01 move (100 oz * $0.01) => $0.10 move = $10"],
    ["XAUUSD", "Gold Spot", "100 oz", "0.10", "$10 per $0.10 move"],
    ["XAUUSD", "Gold Spot", "100 oz", "1.00", "$100 per $1.00 move"],
]
for row in data:
    for c, v in enumerate(row, start=1):
        ws2.cell(row=r, column=c, value=v).border = thin_border
    r += 1

ws2.column_dimensions['A'].width = 14
ws2.column_dimensions['B'].width = 18
ws2.column_dimensions['C'].width = 14
ws2.column_dimensions['D'].width = 14
ws2.column_dimensions['E'].width = 55

# Sheet 3: Examples
ws3 = wb.create_sheet("Examples")
ws3['A1'] = "Example Scenarios (Hypothetical $1000 account - Not Recommendations)"
ws3['A1'].font = bold_font
ws3['A1'].fill = sub_fill
ws3.merge_cells('A1:H1')
r = 2
headers = ["Balance", "Risk %", "Risk $", "SL pips", "TP pips", "Pair @ Price", "Lot Size", "Notes"]
for c, h in enumerate(headers, start=1):
    ws3.cell(row=r, column=c, value=h).font = white_font
    ws3.cell(row=r, column=c).fill = header_fill
    ws3.cell(row=r, column=c).border = thin_border
r += 1
examples = [
    [1000, "1%", 10, 20, 40, "EURUSD @1.08", 0.05, "Tight SL => larger lot, same $ risk"],
    [1000, "1%", 10, 50, 100, "EURUSD @1.08", 0.02, "Wider SL => smaller lot"],
    [1000, "2%", 20, 30, 60, "EURUSD @1.08", 0.06, "2% risk doubles lot vs 1%"],
    [500, "1%", 5, 30, 60, "EURUSD @1.08", 0.01, "Small account => min 0.01 lot"],
    [1000, "1%", 10, 30, 60, "USDJPY @150", 0.05, "1000/150=6.66 pip value"],
    [1000, "1%", 10, 100, 200, "XAUUSD @2030 ($1 SL)", 0.10, "Gold: SL 100 pips = $1.00 move, lot=10/(100*1)=0.10"],
    [1000, "1%", 10, 200, 400, "XAUUSD @2030 ($2 SL)", 0.05, "Gold: SL 200 pips = $2.00 move, lot=0.05"],
]
for row in examples:
    for c, v in enumerate(row, start=1):
        ws3.cell(row=r, column=c, value=v).border = thin_border
    r += 1

# Sheet 4: Exness Info
ws4 = wb.create_sheet("Exness Account Types")
ws4['A1'] = "Exness Account Types - Margin & Lot Info (Check exness.com for live specs)"
ws4['A1'].font = bold_font
ws4['A1'].fill = sub_fill
ws4.merge_cells('A1:D1')
r = 2
headers = ["Account Type", "Min Deposit", "Min Lot", "Spread / Commission"]
for c, h in enumerate(headers, start=1):
    ws4.cell(row=r, column=c, value=h).font = white_font
    ws4.cell(row=r, column=c).fill = header_fill
    ws4.cell(row=r, column=c).border = thin_border
r += 1
acc_data = [
    ["Standard", "$10", "0.01", "From 0.3 pip, no commission"],
    ["Standard Cent", "$10", "0.01 (cent lot)", "From 0.3 pip"],
    ["Pro", "$200", "0.01", "From 0.1 pip, no commission"],
    ["Raw Spread", "$200", "0.01", "From 0.0 pip + up to $3.5 commission per lot"],
    ["Zero", "$200", "0.01", "0.0 pip on 30 pairs + commission"],
]
for row in acc_data:
    for c, v in enumerate(row, start=1):
        ws4.cell(row=r, column=c, value=v).border = thin_border
    r += 1

# Column widths
ws.column_dimensions['A'].width = 42
ws.column_dimensions['B'].width = 18
ws.column_dimensions['C'].width = 60
ws2.column_dimensions['A'].width = 14
ws3.column_dimensions['A'].width = 12
ws3.column_dimensions['F'].width = 18
ws3.column_dimensions['G'].width = 12
ws3.column_dimensions['H'].width = 45

wb.save("Forex_Risk_Calculator_Exness.xlsx")
print("Generated: Forex_Risk_Calculator_Exness.xlsx with Gold + Margin")
