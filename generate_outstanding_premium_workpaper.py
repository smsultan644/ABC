"""
Net Outstanding Premium - Comprehensive Audit Workpaper Generator
Client: American Life Insurance Company, Bangladesh Branch (MetLife)
Period: 01 Jan 2025 - 31 Dec 2025
Firm: Nurul Faruk Hasan & Co, Chartered Accountants
Amount: Tk. 1,435,719,236

Requirements:
pip install openpyxl --break-system-packages

Usage:
python generate_outstanding_premium_workpaper.py
Output: Workpaper_Net_Outstanding_Premium_MetLife_2025.xlsx
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# Styles
header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
subheader_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
white_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
bold_font = Font(name="Calibri", bold=True, size=11)
normal_font = Font(name="Calibri", size=11)
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
center = Alignment(horizontal='center', vertical='center', wrap_text=True)
left_wrap = Alignment(horizontal='left', vertical='center', wrap_text=True)

def add_firm_header(ws, subject, purpose=""):
    ws['A1'] = "Nurul Faruk Hasan & Co"
    ws['A1'].font = Font(name="Calibri", bold=True, size=14)
    ws['A2'] = "Chartered Accountants"
    ws['A2'].font = Font(name="Calibri", bold=True, size=12)
    ws['A4'] = "Client name: American Life Insurance Company, Bangladesh Branch (MetLife)"
    ws['A4'].font = bold_font
    ws['A5'] = "Accounting period: 01 January 2025 to 31 December 2025"
    ws['A5'].font = bold_font
    ws['A6'] = "Prepared by: [Name]"
    ws['G6'] = "Date: [DD/MM/YYYY]"
    ws['A7'] = "Reviewed by: [Name]"
    ws['G7'] = "Date: [DD/MM/YYYY]"
    ws['A8'] = "Further reviewed by: Faruk Uddin Ahammed, FCA"
    ws['G8'] = "Date: [DD/MM/YYYY]"
    ws['A10'] = f"Subject: {subject}"
    ws['A10'].font = Font(name="Calibri", bold=True, size=12)
    if purpose:
        ws['A11'] = f"Purpose: {purpose}"
        ws['A11'].font = normal_font
        ws['A11'].alignment = left_wrap
        return 13
    return 12

def style_header_row(ws, row, max_col, fill=header_fill, font=white_font):
    for col in range(1, max_col+1):
        cell = ws.cell(row=row, column=col)
        cell.fill = fill
        cell.font = font
        cell.alignment = center
        cell.border = thin_border

def style_range_border(ws, min_row, max_row, min_col, max_col):
    for r in range(min_row, max_row+1):
        for c in range(min_col, max_col+1):
            ws.cell(row=r, column=c).border = thin_border
            ws.cell(row=r, column=c).alignment = left_wrap
            ws.cell(row=r, column=c).font = normal_font

# === 1. Index ===
ws_index = wb.active
ws_index.title = "Index & Instructions"
add_firm_header(ws_index, "Index and Instructions for Net Outstanding Premium Workpaper", "To provide navigation and guidance")
r = 13
ws_index[f'A{r}'] = "WORKPAPER INDEX"
ws_index[f'A{r}'].font = white_font
ws_index[f'A{r}'].fill = header_fill
r+=1
index_data = [
    ["Sheet No", "Sheet Name", "Purpose / Contents", "Key Assertions", "Status"],
    ["1", "Index & Instructions", "Navigation, key definitions", "N/A", ""],
    ["2", "Understanding & RoMM", "Business understanding, RoMM", "All", ""],
    ["3", "Audit Program", "Detailed audit procedures", "All", ""],
    ["4", "Lead & Summary", "FS to GL to Sub-ledger rec", "C, A, V", ""],
    ["5", "GL Reconciliation", "TB vs GL vs Sub-ledger", "C, A", ""],
    ["6", "Aging & Grace Analysis", "Aging bucket, 90-day grace calc", "E, V, Cut-off", ""],
    ["7", "MUS Sampling", "MUS plan, 5 samples selection", "Sampling", ""],
    ["8", "Sample Testing", "Detailed testing of 5 MUS samples", "E, V, R&O", ""],
    ["9", "Subsequent Realization", "100% subsequent collection for certificate", "E, V", ""],
    ["10", "Policy Loan & Surrender", "Auto loan & surrender logic test", "E, V, R&O", ""],
    ["11", "Cut-off & Analytics", "Cut-off, analytics, duplicates", "C, Cut-off", ""],
    ["12", "Exceptions Summary", "Log of exceptions", "N/A", ""],
    ["13", "Conclusion & Certificate", "Overall conclusion and draft certificate", "N/A", ""],
    ["14", "PBC & Documents", "PBC list", "N/A", ""],
]
for row in index_data:
    r+=1
    for c, val in enumerate(row, start=1):
        ws_index.cell(row=r, column=c, value=val)
    if r==14:
        style_header_row(ws_index, r, 5)
    else:
        style_range_border(ws_index, r, r, 1, 5)
r+=2
ws_index[f'A{r}'] = "KEY DEFINITIONS & INSTRUCTIONS"
ws_index[f'A{r}'].font = bold_font
ws_index[f'A{r}'].fill = subheader_fill
r+=1
instructions = [
    "1. Net Outstanding Premium = Due premium not received as at 31 Dec 2025 but within 90-day grace.",
    "2. Grace Period: 90 calendar days from due date. Policy remains in-force.",
    "3. After grace: If cash value sufficient => Auto Policy Loan created. If not => Auto Surrender on last day of grace.",
    "4. Certificate: Must confirm ALL outstanding as at 31 Dec either (a) Subsequently realized OR (b) Adjusted via loan OR (c) Adjusted via surrender.",
    "5. Approach: (i) Reconcile FS-GL-Subledger, (ii) Aging & grace logic, (iii) MUS 5 samples, (iv) 100% subsequent test for certificate (Tk. 1,435,719,236).",
    "6. Assertions: E=Existence, C=Completeness, V=Valuation, R&O=Rights & Obligations, P=Presentation, Cut-off.",
    "7. For each sample, attach: Policy schedule, receipt, bank stmt, loan ledger, surrender voucher.",
    "8. Document exceptions in Sheet 12.",
    "9. Fill YELLOW cells only, keep formulas intact.",
    "10. IDRA: Outstanding premium as current asset only if within grace and policy in-force.",
]
for ins in instructions:
    ws_index.cell(row=r, column=1, value=ins)
    ws_index.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
    ws_index.cell(row=r, column=1).alignment = left_wrap
    r+=1
ws_index.column_dimensions['A'].width = 15
ws_index.column_dimensions['B'].width = 25
ws_index.column_dimensions['C'].width = 60
ws_index.column_dimensions['D'].width = 20

# === 2. Understanding & RoMM ===
ws2 = wb.create_sheet("Understanding & RoMM")
start_row = add_firm_header(ws2, "Understanding of Net Outstanding Premium and Risk Assessment", "Document understanding and RoMM")
r = start_row
ws2[f'A{r}'] = "A. BUSINESS PROCESS"
ws2[f'A{r}'].font = bold_font
ws2[f'A{r}'].fill = subheader_fill
r+=1
process_text = [
    ["Process Step", "Description", "System/Control", "Owner", "Auditor Notes"],
    ["1. Premium Due", "Premium due as per policy schedule", "Life Asia", "Premium Accounting", ""],
    ["2. Billing", "Notice 15 days before due", "Automated", "Operations", ""],
    ["3. Outstanding Recognition", "If not received, moved to Outstanding Premium Asset", "Life Asia", "Finance", "Check auto creation"],
    ["4. Grace Period", "90 days grace, policy in-force", "Policy Terms", "N/A", "Verify 90 days per product"],
    ["5. Collection during grace", "If collected, outstanding reversed", "Cashier / Bank", "Finance", ""],
    ["6a. After Grace - Cash Value Available", "Auto Policy Loan created at end of grace", "Life Asia Auto Job", "Actuarial", "Test loan logic"],
    ["6b. After Grace - No Cash Value", "Auto-surrendered on last day of grace", "Life Asia Auto Job", "Operations", "Test surrender"],
    ["7. Reporting", "Outstanding as Current Asset", "Financial Reporting", "Finance", ""],
]
for row_data in process_text:
    for c, val in enumerate(row_data, start=1):
        ws2.cell(row=r, column=c, value=val)
    if r==start_row+1:
        style_header_row(ws2, r, 5)
    r+=1
style_range_border(ws2, start_row+2, r-1, 1, 5)
r+=1
ws2[f'A{r}'] = "B. RoMM"
ws2[f'A{r}'].font = bold_font
ws2[f'A{r}'].fill = subheader_fill
r+=1
romm_header = ["Sl", "Risk Description", "Assertion", "Rating", "Fraud?", "Response", "WP Ref"]
for c, val in enumerate(romm_header, start=1):
    ws2.cell(row=r, column=c, value=val)
style_header_row(ws2, r, 7)
r+=1
romm_data = [
    ["1", "Outstanding includes >90 days overdue (overstated)", "E, V", "High", "No", "Aging + grace recalc 100%", ""],
    ["2", "Includes lapsed/surrendered policies (fictitious)", "E", "High", "Yes", "Verify status + lapsed cross-check", ""],
    ["3", "Premium amount incorrect", "V", "Medium", "No", "Vouch to policy schedule", ""],
    ["4", "Not subsequently realized but certificate issued", "E, Subsequent", "High", "Yes", "100% subsequent test", ""],
    ["5", "Cut-off error", "C, Cut-off", "Medium", "No", "Cut-off testing", ""],
    ["6", "Duplicate policy", "E, V", "Medium", "No", "Duplicate check", ""],
    ["7", "Auto loan logic failure", "V, C", "Medium", "No", "Test auto loan batch", ""],
]
for row_data in romm_data:
    for c, val in enumerate(row_data, start=1):
        ws2.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws2, r-len(romm_data), r-1, 1, 7)
for col in ['A','B','C','D','E','F','G']:
    ws2.column_dimensions[col].width = 20
ws2.column_dimensions['B'].width = 50
ws2.column_dimensions['F'].width = 45

# === 3. Audit Program ===
ws3 = wb.create_sheet("Audit Program")
start_row = add_firm_header(ws3, "Audit Program - Net Outstanding Premium", "Document planned and performed procedures")
r = start_row
headers = ["Sl", "Audit Objective", "Assertion", "Audit Procedure", "By", "Date", "WP Ref", "Result", "Remarks"]
for c, h in enumerate(headers, start=1):
    ws3.cell(row=r, column=c, value=h)
style_header_row(ws3, r, len(headers))
r+=1
program = [
    ["1", "Reconciliation", "C, A, V", "Obtain detailed list as at 31 Dec 2025 and reconcile with GL and FS", "", "", "Lead & GL Rec", "", ""],
    ["2", "Completeness", "C, A", "Re-perform aging: Due+90 = Grace End. Ensure no >90 days", "", "", "Aging", "", ""],
    ["3", "Existence", "E, R&O", "MUS 5 samples vouch to policy docs and status", "", "", "Sample Testing", "", ""],
    ["4", "Valuation", "V", "Agree premium amount to policy schedule for samples", "", "", "Sample Testing", "", ""],
    ["5", "Subsequent Realization for certificate", "E, V, Subsequent", "100% population verify subsequent collection/adjustment up to 31 Mar 2026", "", "", "Subsequent", "", "Critical for certificate"],
    ["6", "Auto policy loan", "E, V", "Verify auto loan created on last day of grace where cash value available", "", "", "Policy Loan", "", ""],
    ["7", "Auto surrender", "E", "Verify auto surrender on last day of grace where no cash value", "", "", "Policy Loan", "", ""],
    ["8", "Cut-off", "Cut-off, C", "Select 10 policies due 15 days before/after year end", "", "", "Cut-off", "", ""],
    ["9", "Duplicate/Negative", "E, V", "Check duplicates and negatives", "", "", "Analytics", "", ""],
    ["10", "Analytics", "C, V", "Compare Outstanding/Gross Premium ratio PY vs CY", "", "", "Analytics", "", ""],
    ["11", "Lapsed cross-check", "E", "Ensure lapsed list not included", "", "", "Cut-off", "", ""],
    ["12", "Presentation", "P", "Check FS presentation as Current Asset", "", "", "Lead", "", ""],
    ["13", "Certificate", "Subsequent", "Draft certificate if 100% realized/adjusted", "", "", "Conclusion", "", ""],
]
for row_data in program:
    for c, val in enumerate(row_data, start=1):
        ws3.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws3, start_row+1, r-1, 1, len(headers))
ws3.column_dimensions['D'].width = 70

# === 4. Lead & Summary ===
ws4 = wb.create_sheet("Lead & Summary")
start_row = add_firm_header(ws4, "Lead Schedule - Net Outstanding Premium", "Reconcile FS with GL and Sub-ledger")
r = start_row
ws4[f'A{r}'] = "FS Reference: Balance Sheet - Current Assets - Net Outstanding Premium"
ws4[f'A{r}'].font = bold_font
r+=2
summary_headers = ["Particulars", "Amount (BDT)", "GL Code", "As per Sub-ledger", "Difference", "Remarks", "FY/RN"]
for c, h in enumerate(summary_headers, start=1):
    ws4.cell(row=r, column=c, value=h)
style_header_row(ws4, r, len(summary_headers))
r+=1
summary_data = [
    ["Net Outstanding Premium as per FS as at 31 Dec 2025", 1435719236, "", "", "", "BS", "Total"],
    ["Breakup as per Sub-ledger", "", "", 1435719236, "=D14-D18", "PBC", ""],
    ["First Year Premium Outstanding", 350000000, "XXXX-FY", "", "", "Aging", "FY"],
    ["Renewal Premium Outstanding", 1085719236, "XXXX-RN", "", "", "Aging", "RN"],
    ["Gross Outstanding", "=SUM(B15:B16)", "", "=SUM(D15:D16)", "", "", ""],
    ["Less: Provision", 0, "", 0, "", "", ""],
    ["Net as per Sub-ledger", "=B17-B18", "", "=D17-D18", "=B19-D19", "", ""],
    ["", "", "", "", "", "", ""],
    ["Materiality", "", "", "", "", "", ""],
    ["Overall Materiality", 50000000, "", "", "", "", ""],
    ["Performance Materiality 75%", "=B22*0.75", "", "", "", "", ""],
    ["Tolerable Error 50% of PM", "=B23*0.5", "", "", "", "", ""],
]
for row_data in summary_data:
    for c, val in enumerate(row_data, start=1):
        ws4.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws4, start_row+2, r-1, 1, len(summary_headers))

# === 5. GL Reconciliation ===
ws5 = wb.create_sheet("GL Reconciliation")
start_row = add_firm_header(ws5, "GL to Sub-ledger Reconciliation", "Ensure GL matches detailed list")
r = start_row
headers = ["GL Code", "Description", "TB Balance", "GL Ledger", "Sub-ledger", "Diff TB vs Sub", "Diff GL vs Sub", "Remarks", "WP Ref"]
for c, h in enumerate(headers, start=1):
    ws5.cell(row=r, column=c, value=h)
style_header_row(ws5, r, len(headers))
r+=1
gl_data = [
    ["1568000090", "Outstanding Premium - FY", 350000000, 350000000, 350000000, "=C14-E14", "=D14-E14", "Agreed", "Aging"],
    ["1568000091", "Outstanding Premium - RN", 1085719236, 1085719236, 1085719236, "=C15-E15", "=D15-E15", "Agreed", "Aging"],
    ["", "Total", "=SUM(C14:C15)", "=SUM(D14:D15)", "=SUM(E14:E15)", "=C16-E16", "=D16-E16", "", ""],
]
for row_data in gl_data:
    for c, val in enumerate(row_data, start=1):
        ws5.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws5, start_row+1, r-1, 1, len(headers))

# === 6. Aging & Grace ===
ws6 = wb.create_sheet("Aging & Grace Analysis")
start_row = add_firm_header(ws6, "Aging Analysis and 90-Day Grace Verification", "Verify no outstanding beyond grace")
r = start_row
headers = ["Sl", "Policy No", "Policyholder", "Due Date", "Due Amount", "FY/RN", "Product", "Mode", "Days Overdue as at 31 Dec (=31Dec-Due)", "Grace End (=Due+90)", "Bucket", "Status Per System", "Expected", "Cash Value", "Exception", "Remarks"]
for c, h in enumerate(headers, start=1):
    ws6.cell(row=r, column=c, value=h)
style_header_row(ws6, r, len(headers))
r+=1
example_data = [
    [1, "POL12345678", "Mr. Rahman", "2025-10-15", 50000, "RN", "Endowment", "Q", "", "", "", "In-force (Outstanding)", "", 200000, "", ""],
    [2, "POL87654321", "Ms. Akter", "2025-11-20", 25000, "FY", "Term", "M", "", "", "", "In-force", "", 0, "", ""],
    [3, "POL11223344", "Mr. Hossain", "2025-12-10", 100000, "RN", "Whole Life", "Y", "", "", "", "In-force", "", 500000, "", ""],
]
for row_data in example_data:
    for c, val in enumerate(row_data, start=1):
        cell = ws6.cell(row=r, column=c, value=val)
        if c==9:
            cell.value = f"=DATE(2025,12,31)-D{r}"
        if c==10:
            cell.value = f"=D{r}+90"
            cell.number_format = 'YYYY-MM-DD'
        if c==11:
            cell.value = f"=IF(I{r}<=30,\"0-30\",IF(I{r}<=60,\"31-60\",IF(I{r}<=90,\"61-90\",\">90\")))"
    r+=1
for i in range(20):
    ws6.cell(row=r, column=1, value=len(example_data)+i+1)
    ws6.cell(row=r, column=9, value=f"=IF(D{r}=\"\",\"\",DATE(2025,12,31)-D{r})")
    ws6.cell(row=r, column=10, value=f"=IF(D{r}=\"\",\"\",D{r}+90)")
    ws6.cell(row=r, column=11, value=f"=IF(I{r}=\"\",\"\",IF(I{r}<=30,\"0-30\",IF(I{r}<=60,\"31-60\",IF(I{r}<=90,\"61-90\",\">90\")))")
    r+=1
style_range_border(ws6, start_row+1, r-1, 1, len(headers))
r+=1
ws6[f'A{r}'] = "Aging Summary"
ws6[f'A{r}'].font = bold_font
ws6[f'A{r}'].fill = subheader_fill
r+=1
summary_headers = ["Bucket", "Count", "Total Amount", "FY Amount", "RN Amount", "Exception >90"]
for c, h in enumerate(summary_headers, start=1):
    ws6.cell(row=r, column=c, value=h)
style_header_row(ws6, r, len(summary_headers))
r+=1
for bucket in ["0-30", "31-60", "61-90", ">90"]:
    ws6.cell(row=r, column=1, value=bucket)
    ws6.cell(row=r, column=2, value=f"=COUNTIF(K{start_row+1}:K{start_row+23},A{r})")
    ws6.cell(row=r, column=3, value=f"=SUMIF(K{start_row+1}:K{start_row+23},A{r},E{start_row+1}:E{start_row+23})")
    r+=1
ws6.cell(row=r, column=1, value="Total")
ws6.cell(row=r, column=2, value=f"=SUM(B{r-4}:B{r-1})")
ws6.cell(row=r, column=3, value=f"=SUM(C{r-4}:C{r-1})")
style_range_border(ws6, r-5, r, 1, 6)

# === 7. MUS Sampling ===
ws7 = wb.create_sheet("MUS Sampling")
start_row = add_firm_header(ws7, "MUS Sampling Plan and Selection", "Document MUS methodology")
r = start_row
ws7[f'A{r}'] = "A. MUS Parameters"
ws7[f'A{r}'].font = bold_font
ws7[f'A{r}'].fill = subheader_fill
r+=1
mus_params = [
    ["Population Value", 1435719236, "As per Lead", ""],
    ["Tolerable Misstatement", 18750000, "50% of PM", ""],
    ["Expected Misstatement", 0, "Assumed 0", ""],
    ["Confidence Factor", 3.0, "95% confidence", ""],
    ["Sampling Interval = TM / Factor", "=B14/B16", "", ""],
    ["No of Samples = Pop / Interval", "=B13/B17", "", ""],
    ["Actual Samples Selected", 5, "Judgmental", ""],
]
for row_data in mus_params:
    for c, val in enumerate(row_data, start=1):
        ws7.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws7, start_row+1, r-1, 1, 4)
r+=1
ws7[f'A{r}'] = "B. Sample Selection Log"
ws7[f'A{r}'].font = bold_font
ws7[f'A{r}'].fill = subheader_fill
r+=1
headers = ["Sample No", "Interval Point", "Cumulative", "Policy No", "Name", "Due Date", "Amount", "FY/RN", "Reason", "Running Total", "Remarks"]
for c, h in enumerate(headers, start=1):
    ws7.cell(row=r, column=c, value=h)
style_header_row(ws7, r, len(headers))
r+=1
sample_data = [
    [1, 1000000, 1000000, "POL12345678", "Mr. Rahman", "2025-10-15", 50000, "RN", "MUS", "", ""],
    [2, 300000000, 300000000, "POL87654321", "Ms. Akter", "2025-11-20", 25000, "FY", "MUS", "", ""],
    [3, 600000000, 600000000, "POL11223344", "Mr. Hossain", "2025-12-10", 100000, "RN", "MUS", "", ""],
    [4, 900000000, 900000000, "POL55667788", "Mr. Islam", "2025-12-01", 75000, "RN", "MUS", "", ""],
    [5, 1200000000, 1200000000, "POL99887766", "Ms. Chowdhury", "2025-10-30", 120000, "FY", "MUS+High", "", ""],
]
for row_data in sample_data:
    for c, val in enumerate(row_data, start=1):
        ws7.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws7, r-len(sample_data), r-1, 1, len(headers))

# === 8. Sample Testing ===
ws8 = wb.create_sheet("Sample Testing")
start_row = add_firm_header(ws8, "Detailed Sample Testing - 5 MUS Samples", "Vouching for existence, accuracy, subsequent")
r = start_row
headers = ["Sl", "Attribute / Test", "Assertion", "Sample1", "Sample2", "Sample3", "Sample4", "Sample5", "Evidence", "Result"]
for c, h in enumerate(headers, start=1):
    ws8.cell(row=r, column=c, value=h)
style_header_row(ws8, r, len(headers))
r+=1
tests = [
    ["1", "Policy exists in PAS", "E", "", "", "", "", "", "PAS screenshot", ""],
    ["2", "Policy status = In-force Outstanding", "E, R&O", "", "", "", "", "", "PAS status", ""],
    ["3", "Due date <=31 Dec and per schedule", "E, Cut-off", "", "", "", "", "", "Policy schedule", ""],
    ["4", "Amount per schedule", "V", "", "", "", "", "", "Premium table", ""],
    ["5", "FY/RN classification correct", "P, V", "", "", "", "", "", "Policy year", ""],
    ["6", "Aging & Grace recalc correct <=90", "V, Cut-off", "", "", "", "", "", "Recalc", ""],
    ["7", "Cash value sufficient/insufficient correctly", "V", "", "", "", "", "", "Cash value report", ""],
    ["8", "Subsequent Receipt Date within 90 days", "E, Subsequent", "", "", "", "", "", "Receipt/Bank", ""],
    ["9", "Subsequent Amount = Outstanding", "V", "", "", "", "", "", "Receipt", ""],
    ["10", "Mode verified with bank/cash", "E, V", "", "", "", "", "", "Bank stmt", ""],
    ["11", "If not cash: Auto Loan date = Grace End", "E, V", "", "", "", "", "", "Loan ledger", ""],
    ["12", "Loan amount = outstanding", "V", "", "", "", "", "", "Loan ledger", ""],
    ["13", "If no cash value: Surrender date = Grace End", "E", "", "", "", "", "", "Surrender voucher", ""],
    ["14", "Accounting entries correctly posted", "V, P", "", "", "", "", "", "GL entry", ""],
    ["15", "Overall conclusion", "All", "", "", "", "", "", "", ""],
]
for row_data in tests:
    for c, val in enumerate(row_data, start=1):
        ws8.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws8, start_row+1, r-1, 1, len(headers))

# === 9. Subsequent Realization ===
ws9 = wb.create_sheet("Subsequent Realization")
start_row = add_firm_header(ws9, "Subsequent Realization Testing - For Certificate (100% Population)", "Verify ALL outstanding realized/adjusted within grace")
r = start_row
ws9[f'A{r}'] = "Cut-off for Certificate: 31 March 2026 (90 days after year end)"
ws9[f'A{r}'].font = bold_font
r+=1
ws9[f'A{r}'] = "Total Outstanding: Tk. 1,435,719,236"
ws9[f'A{r}'].font = bold_font
r+=1
headers = ["Sl", "Policy No", "Name", "Due Date", "Due Amount", "FY/RN", "Grace End (Due+90)", "Subsequent Date", "Days to Realization", "Within 90? Y/N", "Mode (Bank/Cash/Loan/Surrender)", "Amount Realized", "Balance", "Doc Ref", "Bank/Ledger Verified?", "Verified By", "Remarks"]
for c, h in enumerate(headers, start=1):
    ws9.cell(row=r, column=c, value=h)
style_header_row(ws9, r, len(headers))
r+=1
example = [
    [1, "POL12345678", "Mr. Rahman", "2025-10-15", 50000, "RN", "", "2026-01-10", "", "", "Bank", 50000, 0, "Rct-001", "Y", "", "Realized"],
    [2, "POL87654321", "Ms. Akter", "2025-11-20", 25000, "FY", "", "2026-02-15", "", "", "Policy Loan", 25000, 0, "Loan-002", "Y", "", "Loan"],
    [3, "POL11223344", "Mr. Hossain", "2025-12-10", 100000, "RN", "", "2026-03-10", "", "", "Surrender", 100000, 0, "Surr-003", "Y", "", "Surrender"],
]
for row_data in example:
    for c, val in enumerate(row_data, start=1):
        cell = ws9.cell(row=r, column=c, value=val)
        if c==7:
            cell.value = f"=D{r}+90"
            cell.number_format = 'YYYY-MM-DD'
        if c==9:
            cell.value = f"=IF(H{r}=\"\",\"\",H{r}-D{r})"
        if c==10:
            cell.value = f"=IF(I{r}=\"\",\"\",IF(I{r}<=90,\"Y\",\"N\"))"
        if c==13:
            cell.value = f"=E{r}-L{r}"
    r+=1
for i in range(30):
    ws9.cell(row=r, column=1, value=len(example)+i+1)
    ws9.cell(row=r, column=7, value=f"=IF(D{r}=\"\",\"\",D{r}+90)")
    ws9.cell(row=r, column=9, value=f"=IF(H{r}=\"\",\"\",H{r}-D{r})")
    ws9.cell(row=r, column=10, value=f"=IF(I{r}=\"\",\"\",IF(I{r}<=90,\"Y\",\"N\"))")
    ws9.cell(row=r, column=13, value=f"=IF(E{r}=\"\",\"\",E{r}-L{r})")
    r+=1
style_range_border(ws9, start_row+3, r-1, 1, len(headers))
r+=1
ws9[f'A{r}'] = "Summary for Certificate"
ws9[f'A{r}'].font = bold_font
ws9[f'A{r}'].fill = subheader_fill
r+=1
summary = [
    ["Total Outstanding (A)", 1435719236, "=SUM(E14:E10000)", ""],
    ["Realized Cash/Bank (B)", "", "=SUMIF(K14:K10000,\"Bank\",L14:L10000)+SUMIF(K14:K10000,\"Cash\",L14:L10000)", ""],
    ["Adjusted via Loan (C)", "", "=SUMIF(K14:K10000,\"Policy Loan\",L14:L10000)", ""],
    ["Adjusted via Surrender (D)", "", "=SUMIF(K14:K10000,\"Surrender\",L14:L10000)", ""],
    ["Total Realized (E)=B+C+D", "", "=B{r-3}+B{r-2}+B{r-1}", "Must = A"],
    ["Balance Un-realized (F)=A-E", "", "=B{r-4}-B{r-1}", "Must be ZERO"],
    ["Certificate Can Be Issued?", "", "=IF(AND(B{r-2}=0,COUNTIF(J14:J10000,\"N\")=0),\"YES\",\"NO\")", ""],
]
for row_data in summary:
    for c, val in enumerate(row_data, start=1):
        ws9.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws9, r-len(summary), r-1, 1, 4)

# === 10. Policy Loan & Surrender ===
ws10 = wb.create_sheet("Policy Loan & Surrender")
start_row = add_firm_header(ws10, "Auto Policy Loan and Auto Surrender Logic Test", "Verify system auto creates loan/surrender")
r = start_row
headers = ["Sl", "Policy No", "Due Date", "Grace End", "Cash Value", "Existing Loan", "Net Cash Value", "Sufficient? Y/N", "Outstanding", "Expected Action", "Actual Action", "Action Date", "Loan/Surr No", "Loan Amount", "Interest %", "Outstanding Reversed?", "Status After", "Verified?", "Exception", "Remarks"]
for c, h in enumerate(headers, start=1):
    ws10.cell(row=r, column=c, value=h)
style_header_row(ws10, r, len(headers))
r+=1
example_loan = [
    [1, "POL87654321", "2025-11-20", "", 100000, 20000, "", "", 25000, "Loan", "Loan", "", "LN-001", 25000, 8, "Y", "In-force", "Y", "N", ""],
    [2, "POL11223344", "2025-12-10", "", 0, 0, "", "", 100000, "Surrender", "Surrender", "", "Surr-003", 0, "", "Y", "Surrendered", "Y", "N", ""],
]
for row_data in example_loan:
    for c, val in enumerate(row_data, start=1):
        cell = ws10.cell(row=r, column=c, value=val)
        if c==4:
            cell.value = f"=C{r}+90"
        if c==7:
            cell.value = f"=E{r}-F{r}"
        if c==8:
            cell.value = f"=IF(G{r}>=I{r},\"Y\",\"N\")"
    r+=1
for i in range(15):
    ws10.cell(row=r, column=1, value=len(example_loan)+i+1)
    ws10.cell(row=r, column=4, value=f"=IF(C{r}=\"\",\"\",C{r}+90)")
    ws10.cell(row=r, column=7, value=f"=IF(E{r}=\"\",\"\",E{r}-F{r})")
    ws10.cell(row=r, column=8, value=f"=IF(OR(G{r}=\"\",I{r}=\"\"),\"\",IF(G{r}>=I{r},\"Y\",\"N\"))")
    r+=1
style_range_border(ws10, start_row+1, r-1, 1, len(headers))

# === 11. Cut-off & Analytics ===
ws11 = wb.create_sheet("Cut-off & Analytics")
start_row = add_firm_header(ws11, "Cut-off Testing and Analytical Procedures", "Cut-off and analytics")
r = start_row
ws11[f'A{r}'] = "A. Cut-off Testing"
ws11[f'A{r}'].font = bold_font
ws11[f'A{r}'].fill = subheader_fill
r+=1
headers = ["Sl", "Policy No", "Due Date", "Should Included? Y/N", "Actually Included? Y/N", "Grace End", "Subsequent Status", "Exception?", "Remarks"]
for c, h in enumerate(headers, start=1):
    ws11.cell(row=r, column=c, value=h)
style_header_row(ws11, r, len(headers))
r+=1
cutoff_data = [
    [1, "POLCUT001", "2025-12-20", "Y", "", "", "", "", "Should be included"],
    [2, "POLCUT002", "2025-12-31", "Y", "", "", "", "", "Due on year end"],
    [3, "POLCUT003", "2026-01-05", "N", "", "", "", "", "Should NOT be included"],
]
for row_data in cutoff_data:
    for c, val in enumerate(row_data, start=1):
        ws11.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws11, start_row+2, r-1, 1, len(headers))
r+=1
ws11[f'A{r}'] = "B. Analytics"
ws11[f'A{r}'].font = bold_font
ws11[f'A{r}'].fill = subheader_fill
r+=1
analytics_headers = ["Particulars", "31 Dec 2025", "31 Dec 2024", "Change", "Change %", "Benchmark", "Reason", "Comment"]
for c, h in enumerate(analytics_headers, start=1):
    ws11.cell(row=r, column=c, value=h)
style_header_row(ws11, r, len(analytics_headers))
r+=1
analytics_data = [
    ["Gross Premium", "", "", "=B{r}-C{r}", "=IF(C{r}=0,\"\",D{r}/C{r})", "", "", ""],
    ["Net Outstanding", 1435719236, 1200000000, "=B{r}-C{r}", "=IF(C{r}=0,\"\",D{r}/C{r})", "2-5% of gross", "", ""],
    ["Outstanding as % of Gross", "=B{r-1}/B{r-2}", "=C{r-1}/C{r-2}", "", "", "", "", ""],
]
for row_data in analytics_data:
    for c, val in enumerate(row_data, start=1):
        ws11.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws11, r-len(analytics_data), r-1, 1, len(analytics_headers))

# === 12. Exceptions ===
ws12 = wb.create_sheet("Exceptions Summary")
start_row = add_firm_header(ws12, "Summary of Exceptions", "Log all exceptions")
r = start_row
headers = ["Sl", "WP Ref", "Policy No", "Exception Description", "Amount", "Assertion", "Impact FS", "Impact Certificate?", "Management Response", "Recommendation", "Adjusted?", "Status"]
for c, h in enumerate(headers, start=1):
    ws12.cell(row=r, column=c, value=h)
style_header_row(ws12, r, len(headers))
r+=1
for i in range(15):
    ws12.cell(row=r, column=1, value=i+1)
    r+=1
style_range_border(ws12, start_row+1, r-1, 1, len(headers))

# === 13. Conclusion & Certificate ===
ws13 = wb.create_sheet("Conclusion & Certificate")
start_row = add_firm_header(ws13, "Overall Conclusion and Draft Certificate", "Conclude and draft certificate")
r = start_row
ws13[f'A{r}'] = "A. Overall Audit Conclusion"
ws13[f'A{r}'].font = bold_font
ws13[f'A{r}'].fill = subheader_fill
r+=1
conclusion_points = [
    "1. Reconciliation: FS 1,435,719,236 agreed with GL and sub-ledger? [Yes/No]",
    "2. Aging: No outstanding beyond 90 days? [Yes/No]",
    "3. Existence: All 5 MUS samples verified in-force? [Yes/No]",
    "4. Valuation: Premium amounts agreed to schedule? [Yes/No]",
    "5. Subsequent: 100% verified as realized/adjusted within 90 days? [Yes/No]",
    "6. Loan/Surrender logic correct? [Yes/No]",
    "7. Cut-off correct? [Yes/No]",
    "8. Exceptions? If yes, summarized. [Yes/No]",
    "9. Overall: Net Outstanding Premium fairly stated? [Yes/No]",
]
for point in conclusion_points:
    ws13.cell(row=r, column=1, value=point)
    ws13.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    ws13.cell(row=r, column=1).alignment = left_wrap
    r+=1
r+=1
ws13[f'A{r}'] = "B. Draft Auditor's Certificate"
ws13[f'A{r}'].font = bold_font
ws13[f'A{r}'].fill = subheader_fill
r+=1
cert_text = [
    "AUDITOR'S CERTIFICATE ON OUTSTANDING NET PREMIUM",
    "",
    "We, as the statutory Auditors of American Life Insurance Company, Bangladesh Branch (the \"Company\"), Dhaka, Bangladesh, have verified the outstanding net premium of Taka 1,435,719,236 (Taka One Hundred Forty-Three Crore Fifty-Seven Lakh Nineteen Thousand and Two Hundred Thirty-Six) only as at 31 December 2025. To the best of our knowledge and on the basis of information provided to us both the outstanding first year and renewal premium have subsequently been realized or adjusted.",
    "",
    "Our verification procedures included:",
    "1. Obtaining and reconciling detailed policy-wise list with GL and FS.",
    "2. Testing aging and 90-day grace period for entire population.",
    "3. Selecting 5 samples using MUS and verifying existence, accuracy, status.",
    "4. Verifying subsequent realization/adjustment for 100% population up to [Certificate Date]:",
    "   a) Collection in cash/bank verified with receipts and bank statements.",
    "   b) Adjustment via auto policy loan verified with loan ledger.",
    "   c) Adjustment via auto surrender verified with surrender register.",
    "5. Testing cut-off, duplicates, analytics.",
    "",
    "Breakup:",
    "Total Outstanding as at 31 Dec 2025: Tk. 1,435,719,236",
    "  - Realized Cash/Bank: Tk. [___]",
    "  - Adjusted via Auto Policy Loan: Tk. [___]",
    "  - Adjusted via Auto Surrender: Tk. [___]",
    "  - Balance Un-realized: Tk. NIL",
    "",
    "Based on our verification, outstanding net premium as at 31 Dec 2025 has been fully realized or adjusted within 90-day grace period.",
    "",
    "For Nurul Faruk Hasan & Co.",
    "Chartered Accountants",
    "Place: Dhaka",
    "Date: [Certificate Date]",
    "[Signature]",
    "Faruk Uddin Ahammed, FCA, Partner",
]
for line in cert_text:
    ws13.cell(row=r, column=1, value=line)
    ws13.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    ws13.cell(row=r, column=1).alignment = left_wrap
    r+=1

# === 14. PBC ===
ws14 = wb.create_sheet("PBC & Documents")
start_row = add_firm_header(ws14, "PBC List", "Track PBC requests")
r = start_row
headers = ["Sl", "Document Description", "Requested", "Received", "From", "Format", "WP Ref", "Status", "Remarks"]
for c, h in enumerate(headers, start=1):
    ws14.cell(row=r, column=c, value=h)
style_header_row(ws14, r, len(headers))
r+=1
pbc_data = [
    ["1", "Detailed outstanding list as at 31 Dec 2025 (policy-wise)", "", "", "", "Excel", "Aging", "", "Critical"],
    ["2", "Trial Balance / GL Ledger for Outstanding GL codes", "", "", "", "Excel", "GL Rec", "", ""],
    ["3", "PAS screenshot for policy status for 5 samples", "", "", "", "PDF", "Sample Testing", "", ""],
    ["4", "Policy schedule for 5 samples", "", "", "", "PDF", "Sample Testing", "", ""],
    ["5", "Subsequent collection report 01 Jan to 31 Mar 2026", "", "", "", "Excel", "Subsequent", "", "For certificate 100%"],
    ["6", "Bank statements for subsequent collections", "", "", "", "PDF", "Subsequent", "", ""],
    ["7", "Policy loan ledger for auto loans Jan-Mar 2026", "", "", "", "Excel", "Loan", "", ""],
    ["8", "Surrender register Jan-Mar 2026", "", "", "", "Excel", "Loan", "", ""],
    ["9", "Cash value report as at grace end", "", "", "", "Excel", "Loan", "", ""],
    ["10", "Lapsed policy list as at 31 Dec 2025", "", "", "", "Excel", "Cut-off", "", ""],
    ["11", "IT logic doc for auto loan/surrender batch", "", "", "", "PDF", "Loan", "", ""],
    ["12", "Management Representation Letter", "", "", "", "PDF", "Conclusion", "", ""],
]
for row_data in pbc_data:
    for c, val in enumerate(row_data, start=1):
        ws14.cell(row=r, column=c, value=val)
    r+=1
style_range_border(ws14, start_row+1, r-1, 1, len(headers))

# Save
wb.save("Workpaper_Net_Outstanding_Premium_MetLife_2025.xlsx")
print("Excel generated: Workpaper_Net_Outstanding_Premium_MetLife_2025.xlsx")
