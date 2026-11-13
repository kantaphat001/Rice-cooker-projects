# -*- coding: utf-8 -*-
"""
generate_merged_appendix_doc.py
Merges and adapts:
1. DOC A (df3b50a0): ภาคผนวก ก คู่มือการใช้งาน (Thai & English)
2. Main Doc (77929ef3): ภาคผนวก ข ประวัติผู้วิจัย
3. DOC B (e178585b): ภาคผนวก ค การทดสอบประสิทธิภาพ, ภาคผนวก ง ภาพขั้นตอนการพัฒนา, ภาคผนวก จ แบบสอบถามและตารางสถิติ
Adapts all content to: กล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box)
Preserves all original images exactly.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

EXTRACTED_DIR = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects\extracted_images"
OUTPUT_DOCX = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects\ภาคผนวก_กล่องเตือนทานยาอัจฉริยะ_ฉบับสมบูรณ์.docx"

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="B0BEC5", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def format_run(run, font_name="TH SarabunPSK", font_size=16, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)

def add_p(doc, text="", font_name="TH SarabunPSK", font_size=16, bold=False, italic=False, 
          align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.15, color_rgb=(0,0,0)):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        format_run(r, font_name, font_size, bold, italic, color_rgb)
    return p

def add_img(doc, img_name, width_inches=4.5, caption=None):
    img_path = os.path.join(EXTRACTED_DIR, img_name)
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run()
        r.add_picture(img_path, width=Inches(width_inches))
        if caption:
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(6)
            r_cap = p_cap.add_run(caption)
            format_run(r_cap, "TH SarabunPSK", 15, bold=True, color_rgb=(50, 50, 50))
    else:
        print(f"Warning: Image not found: {img_path}")

def build_document():
    doc = docx.Document()
    
    # Page setup - Standard A4 with 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    print("Building Merged Appendix Document...")

    # ==========================================
    # COVER / SECTION HEADER: ภาคผนวก
    # ==========================================
    add_p(doc, "ภาคผนวก", font_size=26, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=180, space_after=12)
    add_p(doc, "โครงการวิจัยเรื่อง กล่องเตือนทานยาอัจฉริยะ", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    add_p(doc, "(Smart Medication Reminder Box)", font_size=16, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)
    doc.add_page_break()

    # ==========================================
    # ภาคผนวก ก คู่มือการใช้งาน (DOC A)
    # ==========================================
    add_p(doc, "ภาคผนวก ก", font_size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p(doc, "คู่มือการใช้งาน กล่องเตือนทานยาอัจฉริยะ", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    # Thai Manual
    add_p(doc, "คู่มือการใช้งานระบบ (ภาษาไทย)", font_size=16, bold=True, space_before=6, space_after=4)

    # Step 1
    add_p(doc, "ขั้นตอนที่ 1 : การลงทะเบียนสมาชิกและข้อมูลยาผ่านระบบ Web Management Portal", font_size=16, bold=True, space_before=4, space_after=2)
    add_p(doc, "   ผู้ดูแลหรือสมาชิกในครอบครัวเข้าสู่ระบบบริหารจัดการผ่านสมาร์ตโฟนหรือคอมพิวเตอร์ เพื่อลงทะเบียนสมาชิกใหม่ พร้อมทั้งกรอกข้อมูลชื่อสมาชิก และกำหนดตารางเวลามื้ออาหาร", space_after=4)
    add_img(doc, "doc_a_image1.jpeg", width_inches=4.2, caption="จอแสดงผลและโครงสร้างตัวเครื่อง")
    add_img(doc, "doc_a_image3.jpeg", width_inches=3.8, caption="หน้าจอสร้างบัญชีและลงทะเบียนสมาชิกใหม่")

    # Step 2
    add_p(doc, "ขั้นตอนที่ 2 : การเข้าสู่ระบบจัดการข้อมูลยาและตารางมื้อยา", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   เข้าสู่ระบบจัดการข้อมูลยาด้วยชื่อสมาชิกหรือหมายเลขประจำตัว เพื่อบันทึกรายการยา ปริมาณการรับประทาน และกำหนดสีของซองยา (เช่น สีเขียว สีฟ้า สีส้ม) ประจำแต่ละมื้อ", space_after=4)
    add_img(doc, "doc_a_image4.jpeg", width_inches=3.8, caption="หน้าจอเข้าสู่ระบบจัดการข้อมูลสมาชิกและยา")

    # Step 3
    add_p(doc, "ขั้นตอนที่ 3 : การเข้าใช้งานระบบเตือนยาอัตโนมัติแบบไร้สัมผัส (Hands-Free)", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   เมื่อถึงช่วงเวลามื้ออาหาร ผู้สูงอายุหรือสมาชิกในครอบครัวเดินเข้ามาในระยะตรวจจับ 30–45 เซนติเมตร บริเวณด้านหน้ากล่องเตือนทานยาอัจฉริยะข้างหม้อหุงข้าว โดยไม่ต้องกดปุ่มใด ๆ ทั้งสิ้น", space_after=4)
    add_img(doc, "doc_a_image5.jpeg", width_inches=4.2, caption="การเข้าสู่ระยะตรวจจับของกล่องเตือนทานยาอัจฉริยะ")

    # Step 4
    add_p(doc, "ขั้นตอนที่ 4 : การตรวจจับบุคคลและเริ่มระบบสแกนใบหน้าด้วย Edge AI", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   เซนเซอร์อัลตราโซนิกตรวจพบบุคคลและส่งสัญญาณปลุกกล้องอัตโนมัติ ไฟ LED สีเหลืองจะสว่างขึ้น เพื่อแสดงสถานะว่าระบบ AI (YuNet & SFace) กำลังสแกนและรู้จำใบหน้าของสมาชิก", space_after=4)
    add_img(doc, "doc_a_image6.jpeg", width_inches=4.2, caption="สถานะระบบเริ่มสแกนและประมวลผลใบหน้า (ไฟ LED สีเหลือง)")

    # Step 5
    add_p(doc, "ขั้นตอนที่ 5 : การยืนยันตัวตนสำเร็จและขานเตือนรายการยาด้วยเสียงพูดภาษาไทย", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   เมื่อระบบ AI ยืนยันตัวตนสมาชิกถูกต้อง ไฟ LED สีเขียวจะสว่างขึ้น พร้อมระบบเสียงพูดภาษาไทยสำเนียงสุภาพ นุ่มนวล ชัดเจน จะขานชื่อสมาชิก แจ้งเตือนมื้อยา ระบุชื่อยา ปริมาณ และสีของซองยาอย่างถูกต้อง", space_after=4)
    add_img(doc, "doc_a_image7.jpeg", width_inches=3.4, caption="หน้าจอแสดงผลข้อมูลยาและรายการยาประจำมื้อบนสมาร์ตโฟน")

    # Step 6
    add_p(doc, "ขั้นตอนที่ 6 : การรับประทานยาและระบบป้องกันการแจ้งเตือนซ้ำซ้อน (Anti-Double Dose Cooldown)", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   ผู้ใช้งานหยิบยาตามที่ระบบขานเตือนได้อย่างถูกต้อง ระบบจะทำการบันทึกประวัติการรับประทานยาลงฐานข้อมูลอัตโนมัติ และเข้าสู่ช่วง Cooldown เพื่อป้องกันการแจ้งเตือนซ้ำซ้อนหากเดินผ่านอีกครั้ง", space_after=4)
    add_img(doc, "doc_a_image8.jpeg", width_inches=3.4, caption="หน้าจอแสดงประวัติการทานยาและการยืนยันสถานะความถูกต้อง")

    # English User Manual
    doc.add_page_break()
    add_p(doc, "User Manual", font_size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=4)
    add_p(doc, "Smart Medication Reminder Box", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    add_p(doc, "Step 1 : Member Registration & Medication Setup via Web Portal", font_size=16, bold=True, space_before=4, space_after=2)
    add_p(doc, "   Caregivers connect to the local Web Management Portal using a smartphone or computer to register family members, upload facial training images, and configure scheduled mealtimes.", space_after=4)
    add_img(doc, "doc_a_image1.jpeg", width_inches=4.0, caption="Front display and hardware structure")
    add_img(doc, "doc_a_image3.jpeg", width_inches=3.6, caption="Account creation and member enrollment portal")

    add_p(doc, "Step 2 : Accessing and Configuring Medication Schedules", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   Log in with member credentials to customize specific prescriptions, dosages, and corresponding pouch colors (e.g., green, blue, yellow) for each meal slot.", space_after=4)
    add_img(doc, "doc_a_image4.jpeg", width_inches=3.6, caption="Medication management login screen")

    add_p(doc, "Step 3 : Contactless Presence Approach (Zero-Touch / Hands-Free)", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   During mealtimes, the senior member approaches within 30–45 cm of the smart medication box beside the household rice cooker without having to touch any buttons.", space_after=4)
    add_img(doc, "doc_a_image5.jpeg", width_inches=4.0, caption="Approaching within detection range of the device")

    add_p(doc, "Step 4 : Automatic Presence Detection & Edge AI Facial Scanning", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   The ultrasonic sensor triggers the system instantly. The Yellow LED turns on, indicating that the on-device Edge AI vision models (YuNet & SFace) are actively recognizing the person.", space_after=4)
    add_img(doc, "doc_a_image6.jpeg", width_inches=4.0, caption="System actively scanning face (Yellow LED status)")

    add_p(doc, "Step 5 : Natural Thai Voice Reminders with Pouch Color Identification", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   Upon positive face identification, the Green LED illuminates. The device plays a clear, polite Thai voice alert greeting the member, stating the meal, exact medication names, doses, and pouch colors.", space_after=4)
    add_img(doc, "doc_a_image7.jpeg", width_inches=3.4, caption="Real-time medication reminder and adherence board")

    add_p(doc, "Step 6 : Medication Intake and Anti-Double-Dose Safety Cooldown", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "   The senior takes the prescribed medicine accurately. The device logs adherence state automatically and enters a cooldown window to eliminate accidental duplicate alarms.", space_after=4)
    add_img(doc, "doc_a_image8.jpeg", width_inches=3.4, caption="Adherence confirmation and timestamp logging display")

    # ==========================================
    # ภาคผนวก ข ประวัติผู้วิจัย
    # ==========================================
    doc.add_page_break()
    add_p(doc, "ภาคผนวก ข", font_size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p(doc, "ประวัติผู้วิจัย", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "ประวัติผู้วิจัยคนที่ 1", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "ชื่อ – นามสกุล : นายกัณตพัฒน์ กระปุกทอง", space_after=2)
    add_p(doc, "สถานที่เกิด : จังหวัดสิงห์บุรี ประเทศไทย", space_after=2)
    add_p(doc, "ประวัติการศึกษา : ปัจจุบันกำลังศึกษาระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) สาขาวิชาเทคโนโลยีคอมพิวเตอร์ แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", space_after=2)
    add_p(doc, "ที่อยู่ที่ติดต่อ : แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี เลขที่ 4 ถนนวิไลจิตต์ ตำบลบางพุทรา อำเภอเมืองสิงห์บุรี จังหวัดสิงห์บุรี 16000", space_after=8)

    add_p(doc, "ประวัติผู้วิจัยคนที่ 2", font_size=16, bold=True, space_before=6, space_after=2)
    add_p(doc, "ชื่อ – นามสกุล : นายณัฏฐวี ไกรทอง", space_after=2)
    add_p(doc, "สถานที่เกิด : จังหวัดสิงห์บุรี ประเทศไทย", space_after=2)
    add_p(doc, "ประวัติการศึกษา : ปัจจุบันกำลังศึกษาระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) สาขาวิชาเทคโนโลยีคอมพิวเตอร์ แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", space_after=2)
    add_p(doc, "ที่อยู่ที่ติดต่อ : แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี เลขที่ 4 ถนนวิไลจิตต์ ตำบลบางพุทรา อำเภอเมืองสิงห์บุรี จังหวัดสิงห์บุรี 16000", space_after=12)

    # ==========================================
    # ภาคผนวก ค การทดสอบประสิทธิภาพ (DOC B)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "ภาคผนวก ค", font_size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p(doc, "การทดสอบประสิทธิภาพของกล่องเตือนทานยาอัจฉริยะ", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    add_p(doc, "ตารางที่ ค-1 บันทึกผลการทดลองประสิทธิภาพของกล่องเตือนทานยาอัจฉริยะ (จำนวน 10 ครั้ง)", font_size=15, bold=True, space_after=4)

    # Table C-1: 10 trials
    table_c1 = doc.add_table(rows=4, cols=13)
    table_c1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_c1)

    headers = ["รายการทดสอบ", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "ผลรวม", "ร้อยละ"]
    for col_idx, h in enumerate(headers):
        cell = table_c1.cell(0, col_idx)
        cell.text = h
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=80, bottom=80, left=60, right=60)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format_run(p.runs[0], font_size=14, bold=True)

    rows_data = [
        ("การตรวจจับและระบุตัวตนใบหน้าด้วยกล้อง AI", ["✓"]*10, "10/10", "100.00%"),
        ("การแจ้งเตือนมื้อยาและรายการยาถูกต้องตามตารางเวลา", ["✓","✓","✓","✓","✓","✓","✗","✓","✓","✓"], "9/10", "90.00%"),
        ("การสังเคราะห์เสียงภาษาไทยและการทำงานแบบออฟไลน์", ["✓","✓","✗","✓","✓","✓","✓","✓","✓","✓"], "9/10", "90.00%"),
    ]

    for row_idx, (title, marks, total, pct) in enumerate(rows_data, start=1):
        # col 0: title
        c0 = table_c1.cell(row_idx, 0)
        c0.text = title
        set_cell_margins(c0, top=60, bottom=60, left=80, right=60)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        format_run(p0.runs[0], font_size=13, bold=False)

        # cols 1-10: marks
        for i, m in enumerate(marks, start=1):
            ci = table_c1.cell(row_idx, i)
            ci.text = m
            set_cell_margins(ci, top=60, bottom=60, left=40, right=40)
            pi = ci.paragraphs[0]
            pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
            color = (22, 101, 52) if m == "✓" else (185, 28, 28)
            format_run(pi.runs[0], font_size=13, bold=True, color_rgb=color)

        # col 11: total
        c11 = table_c1.cell(row_idx, 11)
        c11.text = total
        set_cell_margins(c11, top=60, bottom=60, left=40, right=40)
        p11 = c11.paragraphs[0]
        p11.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format_run(p11.runs[0], font_size=13, bold=True)

        # col 12: pct
        c12 = table_c1.cell(row_idx, 12)
        c12.text = pct
        set_cell_margins(c12, top=60, bottom=60, left=40, right=40)
        p12 = c12.paragraphs[0]
        p12.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format_run(p12.runs[0], font_size=13, bold=True)

    add_p(doc, "หมายเหตุ: เครื่องหมาย ✓ หมายถึง ระบบทำงานได้ถูกต้องสมบูรณ์ | เครื่องหมาย ✗ หมายถึง พบข้อผิดพลาดในการทดลอง", font_size=13, italic=True, space_before=4, space_after=8)
    add_p(doc, "   จากตารางที่ ค-1 ผลการทดสอบประสิทธิภาพการทำงานของกล่องเตือนทานยาอัจฉริยะ จำนวน 10 ครั้ง พบว่า ระบบสามารถตรวจจับและระบุตัวตนใบหน้าได้สำเร็จ 10 ครั้ง (ร้อยละ 100.00) แจ้งเตือนมื้อยาถูกต้อง 9 ครั้ง (ร้อยละ 90.00 โดยพบข้อผิดพลาดครั้งที่ 7) และสังเคราะห์เสียงภาษาไทยแบบออฟไลน์ถูกต้อง 9 ครั้ง (ร้อยละ 90.00 โดยพบข้อผิดพลาดครั้งที่ 3) คิดเป็นประสิทธิภาพความสำเร็จรวมเฉลี่ยร้อยละ 93.33", font_size=15, space_after=10)

    # Images for Appendix C
    add_img(doc, "doc_b_image1.jpeg", width_inches=4.2, caption="ภาพที่ ค-1 ทดสอบการตรวจจับและสแกนใบหน้าด้วยกล้อง AI (Edge AI Face Detection)")
    add_img(doc, "doc_b_image2.png", width_inches=4.4, caption="ภาพที่ ค-2 ทดสอบการทำงานของระบบประมวลผลและอุปกรณ์ควบคุมภายในกล่องเตือนทานยาอัจฉริยะ")
    add_img(doc, "doc_b_image3.png", width_inches=3.4, caption="ภาพที่ ค-3 (ก) ทดสอบระบบจัดการข้อมูลยาและการเชื่อมต่อเว็บแอปพลิเคชัน")
    add_img(doc, "doc_b_image4.jpeg", width_inches=3.4, caption="ภาพที่ ค-3 (ข) ทดสอบการแสดงผลประวัติและสถานะการรับประทานยาบนสมาร์ตโฟน")

    # ==========================================
    # ภาคผนวก ง ภาพประกอบขั้นตอนการพัฒนา (DOC B)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "ภาคผนวก ง", font_size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p(doc, "ภาพประกอบขั้นตอนการพัฒนากล่องเตือนทานยาอัจฉริยะ", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    dev_steps = [
        ("doc_b_image5.png", 4.2, "ภาพที่ ง-1 การออกแบบภาพโครงร่าง 3 มิติ และขนาดสัดส่วนของกล่องเตือนทานยาอัจฉริยะ"),
        ("doc_b_image6.png", 4.6, "ภาพที่ ง-2 การพัฒนาชุดคำสั่งควบคุมระบบฮาร์ดแวร์และโมเดล AI ด้วยภาษา Python"),
        ("doc_b_image7.jpeg", 4.2, "ภาพที่ ง-3 การจัดเตรียมชุดข้อมูลและสร้างการเรียนรู้ของโมเดล AI ในการตรวจจับและรู้จำใบหน้า"),
        ("doc_b_image8.jpeg", 4.0, "ภาพที่ ง-4 การวัดขนาด ตัดแผ่นพลาสวูด และประกอบโครงตู้สำหรับติดตั้งอุปกรณ์"),
        ("doc_b_image9.jpeg", 4.2, "ภาพที่ ง-5 การประกอบติดตั้งวงจรอิเล็กทรอนิกส์ แหล่งจ่ายไฟ และบอร์ด Raspberry Pi 4B"),
        ("doc_b_image10.jpeg", 4.0, "ภาพที่ ง-6 การประกอบอุปกรณ์เข้ากล่องบรรจุ ตกแต่งรูปลักษณ์ และเตรียมนำไปทดสอบ"),
        ("doc_b_image11.jpeg", 4.2, "ภาพที่ ง-7 การทดสอบความแม่นยำของเซนเซอร์ตรวจจับระยะบุคคลและกล้องสแกนใบหน้า"),
        ("doc_b_image12.jpeg", 3.4, "ภาพที่ ง-8 การทดสอบระบบจัดการตารางยาและลงทะเบียนใบหน้าผ่านสมาร์ตโฟน (Web Portal)"),
    ]

    for img_fn, width, cap in dev_steps:
        add_img(doc, img_fn, width_inches=width, caption=cap)

    # ==========================================
    # ภาคผนวก จ แบบสอบถามความพึงพอใจและผลการวิเคราะห์ข้อมูล (DOC B)
    # ==========================================
    doc.add_page_break()
    add_p(doc, "ภาคผนวก จ", font_size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    add_p(doc, "แบบประเมินความพึงพอใจและผลการวิเคราะห์ข้อมูลทางสถิติ", font_size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    add_p(doc, "แบบประเมินความพึงพอใจของผู้ใช้งานต่อ กล่องเตือนทานยาอัจฉริยะ ฉบับปรับปรุง", font_size=16, bold=True, space_after=4)
    add_p(doc, "คำชี้แจง : แบบสอบถามนี้จัดทำขึ้นเพื่อประเมินความพึงพอใจของผู้ใช้งานที่มีต่อการทำงานของกล่องเตือนทานยาอัจฉริยะ โดยแบ่งออกเป็น 3 ส่วน ดังนี้", font_size=15, space_after=4)
    add_p(doc, "ส่วนที่ 1 ข้อมูลทั่วไปของผู้ตอบแบบสอบถาม", font_size=15, bold=True, space_before=4, space_after=2)
    add_p(doc, "   เพศ :  [  ] ชาย      [  ] หญิง      [  ] อื่น ๆ", space_after=2)
    add_p(doc, "   อายุ :  [  ] ต่ำกว่า 18 ปี      [  ] 18–25 ปี      [  ] มากกว่า 25 ปี", space_after=2)
    add_p(doc, "   ระดับชั้น :  [  ] ปวช.1   [  ] ปวช.2   [  ] ปวช.3   [  ] ปวส.1   [  ] ปวส.2", space_after=6)

    add_p(doc, "ส่วนที่ 2 แบบประเมินความพึงพอใจต่อระบบกล่องเตือนทานยาอัจฉริยะ", font_size=15, bold=True, space_before=4, space_after=2)
    add_p(doc, "กรุณาทำเครื่องหมาย ✓ ในช่องที่ตรงกับระดับความคิดเห็นของท่าน (5 = มากที่สุด, 4 = มาก, 3 = ปานกลาง, 2 = น้อย, 1 = น้อยที่สุด)", font_size=14, italic=True, space_after=4)

    # Survey Table
    eval_table = doc.add_table(rows=12, cols=6)
    eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(eval_table)

    cols_h = ["หัวข้อการประเมิน", "5", "4", "3", "2", "1"]
    for ci, ch in enumerate(cols_h):
        c = eval_table.cell(0, ci)
        c.text = ch
        set_cell_background(c, "F1F5F9")
        set_cell_margins(c, top=80, bottom=80, left=60, right=60)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format_run(p.runs[0], font_size=14, bold=True)

    items = [
        ("ด้านที่ 1: ด้านประสิทธิภาพของระบบการแจ้งเตือน", None),
        ("  1. ระบบสามารถตรวจจับบุคคลและระบุตัวตนใบหน้าได้ถูกต้องแม่นยำ", [""*5]),
        ("  2. ระบบแจ้งเตือนรายการยาและระบุสีของซองยาได้รวดเร็วและเหมาะสมตรงตามเวลา", [""*5]),
        ("  3. การทำงานของระบบมีความราบรื่นและต่อเนื่อง ไม่ติดขัด", [""*5]),
        ("ด้านที่ 2: ด้านความสะดวกและการใช้งาน", None),
        ("  4. ระบบตอบสนองต่อผู้ใช้งานได้อย่างรวดเร็วแบบไร้สัมผัส (Hands-Free)", [""*5]),
        ("  5. ระบบเสียงพูดภาษาไทยมีความชัดเจน นุ่มนวล และเข้าใจง่าย", [""*5]),
        ("  6. การจัดการข้อมูลยาและตารางเวลาผ่านเว็บแอปพลิเคชัน (Web Portal) ใช้งานง่าย", [""*5]),
        ("ด้านที่ 3: ด้านความปลอดภัยและความน่าเชื่อถือของระบบ", None),
        ("  7. อุปกรณ์ทำงานได้อย่างปลอดภัย ไม่มีความร้อนสะสมเกินเกณฑ์", [""*5]),
        ("  8. ระบบมีความเสถียร สามารถทำงานแบบออฟไลน์ได้โดยไม่เกิดข้อผิดพลาด", [""*5]),
    ]

    for ri, (text, opts) in enumerate(items, start=1):
        if opts is None:
            # Section header
            c = eval_table.cell(ri, 0)
            c.text = text
            set_cell_background(c, "F8FAFC")
            set_cell_margins(c, top=60, bottom=60, left=80, right=60)
            p = c.paragraphs[0]
            format_run(p.runs[0], font_size=13.5, bold=True)
            for ci in range(1, 6):
                cell_empty = eval_table.cell(ri, ci)
                set_cell_background(cell_empty, "F8FAFC")
        else:
            c = eval_table.cell(ri, 0)
            c.text = text
            set_cell_margins(c, top=50, bottom=50, left=80, right=60)
            p = c.paragraphs[0]
            format_run(p.runs[0], font_size=13, bold=False)
            for ci in range(1, 6):
                cell_box = eval_table.cell(ri, ci)
                set_cell_margins(cell_box, top=50, bottom=50, left=40, right=40)

    add_p(doc, "ส่วนที่ 3 ข้อเสนอแนะเพิ่มเติม", font_size=15, bold=True, space_before=8, space_after=2)
    add_p(doc, "………………………………………………………………………………………………………………………………………………………", space_after=2)
    add_p(doc, "………………………………………………………………………………………………………………………………………………………", space_after=8)

    # Statistical Analysis Table (SPSS output table from DOC B)
    add_p(doc, "ตารางแสดงผลการวิเคราะห์ความพึงพอใจของผู้ใช้งานกลุ่มตัวอย่าง (N=30)", font_size=15, bold=True, space_before=6, space_after=4)

    stat_table = doc.add_table(rows=8, cols=12)
    stat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(stat_table)

    stat_headers = ["สถิติ", "เพศ", "อายุ", "ระดับชั้น", "ข้อ 1", "ข้อ 2", "ข้อ 3", "ข้อ 4", "ข้อ 5", "ข้อ 6", "ข้อ 7", "ข้อ 8"]
    for ci, ch in enumerate(stat_headers):
        c = stat_table.cell(0, ci)
        c.text = ch
        set_cell_background(c, "F1F5F9")
        set_cell_margins(c, top=60, bottom=60, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format_run(p.runs[0], font_size=12.5, bold=True)

    stat_rows = [
        ("N (จำนวน)", ["30"]*11),
        ("Missing", ["0"]*11),
        ("Mean (ค่าเฉลี่ย)", ["1.30", "1.43", "2.57", "4.73", "4.40", "4.50", "4.47", "4.70", "4.60", "4.47", "4.63"]),
        ("Median (มัธยฐาน)", ["1.00", "1.00", "2.00", "5.00", "4.00", "4.50", "5.00", "5.00", "5.00", "4.50", "5.00"]),
        ("Sum (ผลรวม)", ["39", "43", "77", "142", "132", "135", "134", "141", "138", "134", "139"]),
        ("S.D. (ส่วนเบี่ยงเบน)", ["0.47", "0.50", "1.19", "0.45", "0.56", "0.51", "0.68", "0.47", "0.50", "0.57", "0.56"]),
        ("Min - Max", ["1-2", "1-2", "1-5", "4-5", "3-5", "4-5", "3-5", "4-5", "4-5", "3-5", "3-5"]),
    ]

    for ri, (stat_name, vals) in enumerate(stat_rows, start=1):
        c0 = stat_table.cell(ri, 0)
        c0.text = stat_name
        set_cell_margins(c0, top=50, bottom=50, left=50, right=50)
        p0 = c0.paragraphs[0]
        format_run(p0.runs[0], font_size=12, bold=True)

        for ci, val in enumerate(vals, start=1):
            c = stat_table.cell(ri, ci)
            c.text = val
            set_cell_margins(c, top=50, bottom=50, left=30, right=30)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            format_run(p.runs[0], font_size=12, bold=(stat_name == "Mean (ค่าเฉลี่ย)"))

    add_p(doc, "   จากตารางผลการวิเคราะห์ข้อมูลความพึงพอใจของกลุ่มตัวอย่าง จำนวน 30 คน พบว่า ความพึงพอใจต่อกล่องเตือนทานยาอัจฉริยะโดยรวมอยู่ในระดับมากที่สุด โดยมีค่าเฉลี่ยรวมเท่ากับ 4.56 และส่วนเบี่ยงเบนมาตรฐานรวมเท่ากับ 0.53 ซึ่งข้อที่มีค่าเฉลี่ยความพึงพอใจสูงสุด ได้แก่ ข้อ 1 การตรวจจับบุคคลและระบุตัวตนใบหน้าได้ถูกต้องแม่นยำ (Mean = 4.73) และข้อ 5 ระบบเสียงพูดภาษาไทยมีความชัดเจน นุ่มนวล และเข้าใจง่าย (Mean = 4.70)", font_size=15, space_before=6, space_after=12)

    doc.save(OUTPUT_DOCX)
    print(f"✅ Successfully built: {OUTPUT_DOCX} ({os.path.getsize(OUTPUT_DOCX)} bytes)")

if __name__ == "__main__":
    build_document()
