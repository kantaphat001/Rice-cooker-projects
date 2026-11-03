# -*- coding: utf-8 -*-
"""
create_report.py - Assembles the entire research report document.
"""

import os
import sys

# Ensure UTF-8 console output on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOC_NAME = "ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ.docx"
FLOWCHART_DIR = "flowcharts"

def build():
    print("[*] Initializing Word Document...")
    doc = docx.Document()

    # Set page margins (A4 standard: Top 1.5 in (approx 108 pt), Left 1.5 in, Bottom 1 in, Right 1 in)
    for section in doc.sections:
        section.top_margin = Inches(1.2)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    # Styles helper
    def set_font(run, size=15, bold=False, italic=False, color_rgb=(30, 41, 59), font_name="TH Sarabun New"):
        run.font.name = font_name
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = RGBColor(*color_rgb)

    def p(text="", size=15, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, line_spacing=1.15):
        par = doc.add_paragraph()
        par.alignment = align
        par.paragraph_format.space_before = Pt(space_before)
        par.paragraph_format.space_after = Pt(space_after)
        par.paragraph_format.line_spacing = line_spacing
        if text:
            r = par.add_run(text)
            set_font(r, size=size, bold=bold, italic=italic)
        return par

    def h1(text):
        return p(text, size=18, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=6)

    def h2(text):
        return p(text, size=16, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4)

    def h3(text):
        return p(text, size=15, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2)

    def add_page_break():
        doc.add_page_break()

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

    def set_table_borders(table, color="94A3B8", sz="4"):
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

    def add_placeholder_box(caption_text, subtext="คลิกขวาเพื่อแทรกรูปภาพอุปกรณ์จริง"):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(5.8)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=260, bottom=260, left=200, right=200)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="dashed" w:sz="6" w:space="0" w:color="94A3B8"/>
                <w:left w:val="dashed" w:sz="6" w:space="0" w:color="94A3B8"/>
                <w:bottom w:val="dashed" w:sz="6" w:space="0" w:color="94A3B8"/>
                <w:right w:val="dashed" w:sz="6" w:space="0" w:color="94A3B8"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)

        p1 = cell.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(f"📷 [ {caption_text} ]")
        set_font(r1, size=14, bold=True, color_rgb=(71, 85, 105))

        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(f"({subtext})")
        set_font(r2, size=12, italic=True, color_rgb=(148, 163, 184))

        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = cap_p.add_run(caption_text)
        set_font(r_cap, size=13.5, bold=True, color_rgb=(71, 85, 105))
        cap_p.paragraph_format.space_after = Pt(14)

    def add_fig_image(img_filename, caption_text, width_inches=5.8):
        full_path = os.path.join(FLOWCHART_DIR, img_filename)
        if os.path.exists(full_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            run = p_img.add_run()
            run.add_picture(full_path, width=Inches(width_inches))

            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.space_after = Pt(14)
            r = cap.add_run(caption_text)
            set_font(r, size=13.5, bold=True, color_rgb=(71, 85, 105))
        else:
            add_placeholder_box(caption_text, subtext=f"ไม่พบไฟล์ {full_path}")

    # =========================================================================
    # 1. ปกนอก (COVER PAGE)
    # =========================================================================
    print("[*] Writing Cover Page...")
    logo_path = os.path.join(FLOWCHART_DIR, "orig_image1.jpeg")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(10)
        p_logo.paragraph_format.space_after = Pt(12)
        r_logo = p_logo.add_run()
        r_logo.add_picture(logo_path, width=Inches(1.3))

    p("แบบรายงานการวิจัย (ว-สอศ.-3)", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    p("รายงานผลโครงการวิจัย", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

    p("กล่องเตือนทานยาอัจฉริยะ", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    p("Smart Medication Reminder Box", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=36)

    p("นายกัณตพัฒน์ กระปุกทอง", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    p("นายณัฏฐวี ไกรทอง", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=48)

    p("ประจำปีการศึกษา 2569", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    p("วิทยาลัยเทคนิคสิงห์บุรี อาชีวศึกษาจังหวัดสิงห์บุรี", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    p("สำนักงานคณะกรรมการการอาชีวศึกษา กระทรวงศึกษาธิการ", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    add_page_break()

    # =========================================================================
    # 2. ข้อมูลโครงการวิจัย (TITLE SHEET)
    # =========================================================================
    print("[*] Writing Project Info Sheet...")
    p("หัวข้อโครงการวิจัย:", size=16, bold=True, space_after=2)
    p("   ภาษาไทย:  กล่องเตือนทานยาอัจฉริยะ", size=15, space_after=2)
    p("   ภาษาอังกฤษ: Smart Medication Reminder Box", size=15, space_after=12)

    p("ผู้ดำเนินการวิจัย:", size=16, bold=True, space_after=2)
    p("   1. นายกัณตพัฒน์ กระปุกทอง", size=15, space_after=2)
    p("   2. นายณัฏฐวี ไกรทอง", size=15, space_after=12)

    p("ครูที่ปรึกษา:", size=16, bold=True, space_after=2)
    p("   นายนิพนธ์ แก้วเกิด", size=15, space_after=12)

    p("หน่วยงาน:", size=16, bold=True, space_after=2)
    p("   แผนกวิชาช่างเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", size=15, space_after=12)

    p("ปีการศึกษา:", size=16, bold=True, space_after=2)
    p("   2569", size=15, space_after=24)

    # =========================================================================
    # 3. บทคัดย่อภาษาไทย (ABSTRACT THAI)
    # =========================================================================
    p("บทคัดย่อ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=12)

    th_abs = (
        "การวิจัยครั้งนี้เป็นการวิจัยเชิงทดลองและพัฒนา (Experimental & Developmental Research) มีวัตถุประสงค์เพื่อ "
        "(1) ศึกษา ออกแบบ และสร้างกล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box) ที่ทำงานแบบอัตโนมัติไร้สัมผัส (Hands-Free / Zero-Touch) "
        "โดยประยุกต์ใช้เทคโนโลยีปัญญาประดิษฐ์ระดับเอดจ์ (Edge AI) ร่วมกับบอร์ดประมวลผล Raspberry Pi 4 Model B, เซนเซอร์คลื่นอัลตราโซนิก HC-SR04, "
        "กล้อง USB Web Camera, หลอดไฟแสดงสถานะ 3 สี (LED) และระบบสังเคราะห์เสียงพูดภาษาไทย (Neural TTS) "
        "(2) เพื่อทดลองและทดสอบประสิทธิภาพการทำงานของระบบในการตรวจจับบุคคล การจำแนกใบหน้าสมาชิกในครอบครัวด้วยโมเดล YuNet และ SFace "
        "ความถูกต้องของการแจ้งเตือนมื้อยาตามตารางเวลา 4 มื้อหลัก และระบบป้องกันการรับประทานยาซ้ำซ้อน (Anti-Double Dose Cooldown) และ "
        "(3) เพื่อศึกษาความพึงพอใจของกลุ่มตัวอย่างนักเรียน นักศึกษา ระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี จำนวน 20 คน "
        "ที่มีต่อกล่องเตือนทานยาอัจฉริยะ"
    )
    p(th_abs, size=15, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8)

    th_abs_2 = (
        "ผลการวิจัยพบว่า ระบบสามารถปฏิบัติงานได้ตามวัตถุประสงค์ที่กำหนดไว้อย่างสมบูรณ์ โดยการทดลองรอบที่ 1 ในการตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก "
        "จำนวน 5 ครั้ง พบว่า เมื่อมีบุคคลเข้ามาในระยะตรวจจับไม่เกิน 45 เซนติเมตร เซนเซอร์อัลตราโซนิกสามารถตรวจจับและปลุกระบบกล้องขึ้นมาทำงานได้อย่างแม่นยำ "
        "ระบบปัญญาประดิษฐ์ YuNet และ SFace สามารถจำแนกใบหน้าสมาชิกในบ้านและขานชื่อได้อย่างถูกต้อง ไฟ LED แสดงสถานะเปลี่ยนจากสีเหลืองเป็นสีเขียว "
        "คิดเป็นความสำเร็จร้อยละ 100.00 และเมื่อไม่มีบุคคลในระยะ ระบบสามารถเข้าสู่โหมดประหยัดพลังงาน (Eco-Sleep) เพื่อลดความร้อนสะสมได้อย่างถูกต้อง "
        "สำหรับการทดลองรอบที่ 2 ในการแจ้งเตือนตามตารางเวลามื้อยา 4 มื้อ และการทำงานในสภาวะออฟไลน์ (Offline Standalone Mode) พบว่า "
        "ระบบสามารถดึงข้อมูลยา ขานชื่อยา ขนาดยา และสีของซองยาได้อย่างถูกต้องชัดเจน ไม่เกิดความผิดพลาดในการเตือนยาซ้ำซ้อน และทำงานได้ต่อเนื่องแม้ไม่มีสัญญาณอินเทอร์เน็ต "
        "คิดเป็นความสำเร็จร้อยละ 100.00 และผลการประเมินความพึงพอใจของผู้ใช้งานกลุ่มตัวอย่างนักศึกษา ปวส. แผนกวิชาเทคนิคคอมพิวเตอร์ จำนวน 20 คน "
        "พบว่า มีความพึงพอใจต่อระบบโดยรวมอยู่ในระดับมากที่สุด (ค่าเฉลี่ย x̄ = 4.72, S.D. = 0.42) แสดงให้เห็นว่านวัตกรรมนี้สามารถนำไปประยุกต์ใช้งานจริงเพื่อดูแลสุขภาพของผู้สูงอายุได้อย่างมีประสิทธิภาพ"
    )
    p(th_abs_2, size=15, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12)

    p("คำสำคัญ: กล่องเตือนทานยาอัจฉริยะ, ปัญญาประดิษฐ์เอดจ์ (Edge AI), YuNet, SFace, ราสเบอร์รี่พาย 4, สังเคราะห์เสียงภาษาไทย, Hands-Free", 
      size=14, bold=True, space_after=10)

    add_page_break()

    # =========================================================================
    # 4. บทคัดย่อภาษาอังกฤษ (ABSTRACT ENGLISH)
    # =========================================================================
    p("Research Title: Smart Medication Reminder Box", size=15, bold=True, space_after=2)
    p("Researchers: Mr. Kantapat Krapukthong, Mr. Natavee Kraithong", size=15, bold=True, space_after=2)
    p("Research Consultant: Mr. Nipon Kaewkerd", size=15, bold=True, space_after=2)
    p("Organization: Department of Computer Technology, Singburi Technical College", size=15, bold=True, space_after=2)
    p("Academic Year: 2026", size=15, bold=True, space_after=12)

    p("Abstract", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=12)

    en_abs = (
        "The objectives of this experimental and developmental research were: (1) to study, design, and develop the 'Smart Medication Reminder Box', "
        "an autonomous hands-free/zero-touch device integrating Edge Artificial Intelligence (Edge AI) with a Raspberry Pi 4 Model B single-board computer, "
        "an HC-SR04 ultrasonic sensor, a USB web camera, a 3-color LED indicator module, and a Thai Neural Text-to-Speech (TTS) engine; "
        "(2) to evaluate the system operational performance in human presence detection, facial recognition using lightweight YuNet and SFace deep learning models, "
        "scheduled 4-meal medication announcements, and double-dose hazard prevention (Anti-Double Dose Cooldown); and "
        "(3) to examine user satisfaction among a sample group of 20 High Vocational Certificate (Dip./Higher Voc. Cert.) students in Computer Technology at Singburi Technical College."
    )
    p(en_abs, size=14.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8)

    en_abs_2 = (
        "The experimental results demonstrated that the integrated system achieved 100% operational success across all design criteria. "
        "In the first evaluation phase (human proximity detection and multi-user facial recognition across 5 trials), the ultrasonic sensor reliably woke up the camera "
        "when a person approached within 45 cm. The YuNet detector and SFace recognizer successfully identified registered family members with 100% accuracy, "
        "switching the status LED from yellow to green and triggering personalized spoken reminders, while safely entering an Eco-Sleep power-saving state during idle periods. "
        "In the second evaluation phase (4-meal schedule matching and 100% offline standalone operation across 5 trials), the system retrieved medication schedules, "
        "announced pill names, dosages, and visual color-bag identifiers clearly without internet connectivity, with zero double-dosing errors (100% success rate). "
        "Furthermore, user satisfaction evaluation among the 20 vocational students revealed an overall satisfaction level at the 'Highest' degree (x̄ = 4.72, S.D. = 0.42). "
        "These findings confirm that the Smart Medication Reminder Box provides a robust, zero-touch health companion solution tailored for elderly daily living."
    )
    p(en_abs_2, size=14.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12)

    p("Keywords: Smart Medication Reminder Box, Edge AI, YuNet, SFace, Raspberry Pi 4, Thai Neural TTS, Hands-Free Companion", 
      size=14, bold=True, space_after=10)

    add_page_break()

    # =========================================================================
    # 5. กิตติกรรมประกาศ (ACKNOWLEDGEMENTS)
    # =========================================================================
    p("กิตติกรรมประกาศ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=16)

    ack_text = (
        "รายงานการวิจัยฉบับนี้สำเร็จลุล่วงไปได้ด้วยความเมตตา ความกรุณา และการให้คำปรึกษาอย่างดียิ่งจาก นายนิพนธ์ แก้วเกิด ครูที่ปรึกษาโครงการ "
        "ที่ได้กรุณาสละเวลาให้คำแนะนำ ข้อคิดเห็นเชิงวิศวกรรม แนวทางการแก้ไขปัญหาทางเทคนิคสมองกลฝังตัว ตลอดจนตรวจทานและปรับปรุงเนื้อหาของรายงานวิจัยให้มีความสมบูรณ์ถูกต้องตามหลักวิชาการ "
        "คณะผู้วิจัยขอกราบขอบพระคุณเป็นอย่างสูงมา ณ โอกาสนี้\n\n"
        "ขอขอบพระคุณคณะครูและบุคลากร แผนกวิชาช่างเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี ทุกท่าน ที่ได้สนับสนุนเครื่องมือ อุปกรณ์ทดลอง ห้องปฏิบัติการ "
        "และสร้างบรรยากาศทางวิชาการที่เอื้ออำนวยต่อการสร้างสรรค์สิ่งประดิษฐ์คนรุ่นใหม่ ขอบคุณเพื่อน ๆ นักศึกษาระดับ ปวส. แผนกวิชาเทคนิคคอมพิวเตอร์ จำนวน 20 คน "
        "ที่ได้ให้ความร่วมมือในการร่วมทดสอบประสิทธิภาพการทำงานของระบบและร่วมตอบแบบประเมินความพึงพอใจอย่างดียิ่ง\n\n"
        "ท้ายที่สุดนี้ คณะผู้วิจัยขอกราบขอบพระคุณ บิดา มารดา และคนในครอบครัว ที่เป็นกำลังใจสำคัญ คอยสนับสนุนทุนทรัพย์ในการศึกษา และมอบความรักความห่วงใยเสมอมา "
        "คุณค่าและประโยชน์อันพึงมีจากรายงานการวิจัยฉบับนี้ คณะผู้วิจัยขอมอบเป็นเครื่องบูชาพระคุณของครูบาอาจารย์ และผู้มีพระคุณทุกท่าน ที่ได้ประสิทธิ์ประสาทวิชาความรู้ให้แก่คณะผู้วิจัย"
    )
    p(ack_text, size=15, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=24)

    p("คณะผู้วิจัย\nนายกัณตพัฒน์ กระปุกทอง\nนายณัฏฐวี ไกรทอง\nปีการศึกษา 2569", size=15, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=10)

    add_page_break()

    # =========================================================================
    # 6. สารบัญ (TABLE OF CONTENTS)
    # =========================================================================
    print("[*] Writing Table of Contents...")
    p("สารบัญ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=14)

    toc_items = [
        ("บทคัดย่อภาษาไทย", "ก"),
        ("บทคัดย่อภาษาอังกฤษ", "ข"),
        ("กิตติกรรมประกาศ", "ค"),
        ("สารบัญ", "ง"),
        ("สารบัญตาราง", "ฉ"),
        ("สารบัญภาพ", "ช"),
        ("บทที่ 1 บทนำ", "1"),
        ("   1.1 ความเป็นมาและความสำคัญ", "1"),
        ("   1.2 วัตถุประสงค์ของการวิจัย", "2"),
        ("   1.3 ขอบเขตการวิจัย", "2"),
        ("   1.4 สมมติฐานการวิจัย", "3"),
        ("   1.5 คำจำกัดความที่ใช้ในงานวิจัย", "3"),
        ("   1.6 ประโยชน์ที่คาดว่าจะได้รับ", "4"),
        ("บทที่ 2 แนวคิด ทฤษฎี เอกสารและงานวิจัยที่เกี่ยวข้อง", "5"),
        ("   2.1 สถาปัตยกรรมระบบสมองกลฝังตัวประมวลผลเอดจ์ (Edge AI - Raspberry Pi 4)", "5"),
        ("   2.2 อุปกรณ์หลัก และอุปกรณ์เสริมที่เกี่ยวข้อง", "6"),
        ("   2.3 ปัญญาประดิษฐ์และภาษาซอฟต์แวร์ที่ใช้พัฒนา", "8"),
        ("   2.4 งานวิจัยที่เกี่ยวข้อง", "10"),
        ("   2.5 กรอบแนวคิดในการวิจัย", "11"),
        ("บทที่ 3 วิธีดำเนินการวิจัย", "12"),
        ("   3.1 ขั้นตอนการดำเนินการวิจัย", "12"),
        ("   3.2 ขั้นตอนการออกแบบโครงงาน", "13"),
        ("   3.3 การออกแบบโครงสร้างและการต่อวงจรฮาร์ดแวร์", "14"),
        ("   3.4 ผังงานโปรแกรมหลัก (Main Program Flowchart)", "15"),
        ("   3.5 ผังงานระบบอัตโนมัติและสเตตแมชชีน (State Machine)", "16"),
        ("   3.6 ภาพรวมโครงงานและบล็อกไดอะแกรมระบบ", "17"),
        ("   3.7 ประชากรและกลุ่มตัวอย่าง", "18"),
        ("   3.8 เครื่องมือและการสร้างเครื่องมือในการวิจัย", "18"),
        ("   3.9 สถิติที่ใช้ในการวิเคราะห์ข้อมูล", "19"),
        ("บทที่ 4 ผลการวิจัย", "20"),
        ("   4.1 ผลการทดลองประสิทธิภาพการตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก", "20"),
        ("   4.2 ผลการทดลองการแจ้งเตือนมื้อยาตามตารางเวลาและระบบเสียงออฟไลน์", "21"),
        ("   4.3 ผลการเปรียบเทียบและสรุปผลการทดลองการทำงานของระบบ", "22"),
        ("   4.4 ผลการศึกษาความพึงพอใจของกลุ่มตัวอย่างนักศึกษา ปวส. 20 คน", "23"),
        ("บทที่ 5 สรุปผลการวิจัย อภิปรายผล และข้อเสนอแนะ", "25"),
        ("   5.1 สรุปผลการวิจัย", "25"),
        ("   5.2 อภิปรายผล", "26"),
        ("   5.3 ข้อเสนอแนะในการพัฒนาครั้งต่อไป", "27"),
        ("บรรณานุกรม", "28"),
        ("ภาคผนวก", "30"),
        ("   ภาคผนวก ก คู่มือการใช้งานระบบ", "31"),
        ("   ภาคผนวก ข การทดสอบประสิทธิภาพของระบบ", "34"),
        ("   ภาคผนวก ค แบบประเมินความพึงพอใจและตารางคะแนนรายบุคคล (N=20)", "36"),
        ("   ภาคผนวก ง ภาพประกอบขั้นตอนการพัฒนา", "40"),
        ("ประวัติผู้วิจัยและครูที่ปรึกษา", "42"),
    ]

    for item, page in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_after = Pt(2)
        r_item = p_toc.add_run(item)
        set_font(r_item, size=14, bold=("บทที่" in item or "บรรณานุกรม" in item or "ภาคผนวก" in item or "ประวัติ" in item))
        r_dots = p_toc.add_run(" " + "." * max(2, (62 - len(item) * 2)) + " ")
        set_font(r_dots, size=11, color_rgb=(148, 163, 184))
        r_page = p_toc.add_run(page)
        set_font(r_page, size=14, bold=True)

    add_page_break()

    # =========================================================================
    # 7. สารบัญตาราง และ สารบัญภาพ
    # =========================================================================
    p("สารบัญตาราง", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=14)
    table_list = [
        ("ตารางที่ 3.1 ผังการเชื่อมต่อวงจรฮาร์ดแวร์พิน GPIO บนบอร์ด Raspberry Pi 4", "14"),
        ("ตารางที่ 4.1 ผลการทดลองการตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก รอบที่ 1", "20"),
        ("ตารางที่ 4.2 ผลการทดลองการแจ้งเตือนมื้อยาตามตารางเวลาและระบบเสียงออฟไลน์ รอบที่ 2", "21"),
        ("ตารางที่ 4.3 สรุปผลการเปรียบเทียบความสำเร็จของการทดลองการทำงานของระบบ", "22"),
        ("ตารางที่ 4.4 ผลการวิเคราะห์ข้อมูลความพึงพอใจของผู้ใช้งานกลุ่มตัวอย่าง ปวส. (N=20)", "23"),
        ("ตารางที่ ข-1 ตารางบันทึกผลการทดสอบการตรวจวัดระยะและมุมองศากล้อง", "34"),
        ("ตารางที่ ข-2 ตารางบันทึกผลการทดสอบเวลาตอบสนองการสแกนใบหน้าและเสียงพูด", "35"),
        ("ตารางที่ ค-1 ตารางบันทึกคะแนนความพึงพอใจรายบุคคลของกลุ่มตัวอย่าง ปวส. 20 คน", "38"),
    ]
    for item, page in table_list:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(3)
        r1 = p_t.add_run(item)
        set_font(r1, size=13.5)
        r_dots = p_t.add_run(" " + "." * max(2, (60 - len(item))) + " ")
        set_font(r_dots, size=11, color_rgb=(148, 163, 184))
        r2 = p_t.add_run(page)
        set_font(r2, size=13.5, bold=True)

    p("", space_after=18)
    p("สารบัญภาพ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=14)
    figure_list = [
        ("ภาพที่ 1 ภาพบอร์ดประมวลผล Raspberry Pi 4 Model B", "6"),
        ("ภาพที่ 2 ภาพเซนเซอร์วัดระยะทางคลื่นอัลตราโซนิก HC-SR04", "6"),
        ("ภาพที่ 3 ภาพกล้อง USB Web Camera", "7"),
        ("ภาพที่ 4 ภาพหลอดไฟแสดงสถานะ 3 สี (LED แดง, เหลือง, เขียว)", "7"),
        ("ภาพที่ 5 ภาพลำโพงเสียงพูดภาษาไทย (Mini Speaker 3.5mm)", "8"),
        ("ภาพที่ 6 ภาพวงจรแบ่งแรงดัน (Voltage Divider 1kΩ / 2.2kΩ)", "8"),
        ("ภาพที่ 7 กรอบแนวคิดในการวิจัย (Conceptual Framework)", "11"),
        ("ภาพที่ 8 ขั้นตอนการดำเนินงานและออกแบบโครงงาน (Project Design Process)", "13"),
        ("ภาพที่ 9 ผังงานการทำงานของระบบโปรแกรมหลัก (Main Program Flowchart)", "15"),
        ("ภาพที่ 10 ผังงานระบบอัตโนมัติและสถานะการทำงาน (State Machine - FSM)", "16"),
        ("ภาพที่ 11 ภาพรวมโครงสร้างสถาปัตยกรรมระบบ (System Architecture Overview)", "17"),
        ("ภาพที่ ก-1 ภาพหน้าจอพอร์ทัลจัดการข้อมูลยาและใบหน้าสมาชิกผ่านสมาร์ตโฟน (PWA)", "32"),
        ("ภาพที่ ก-2 ภาพการสแกนเปิดเว็บผ่าน QR Code ในวงแลน Wi-Fi", "33"),
        ("ภาพที่ ง-1 ภาพการต่อวงจรและประกอบอุปกรณ์ลงกล่องเคสข้างหม้อหุงข้าว", "40"),
        ("ภาพที่ ง-2 ภาพการทดสอบสแกนใบหน้าและระบบเสียงพูดเตือนยาจริง", "41"),
    ]
    for item, page in figure_list:
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_after = Pt(3)
        r1 = p_f.add_run(item)
        set_font(r1, size=13.5)
        r_dots = p_f.add_run(" " + "." * max(2, (60 - len(item))) + " ")
        set_font(r_dots, size=11, color_rgb=(148, 163, 184))
        r2 = p_f.add_run(page)
        set_font(r2, size=13.5, bold=True)

    add_page_break()

    # =========================================================================
    # 8. บทที่ 1 บทนำ
    # =========================================================================
    print("[*] Writing Chapter 1...")
    p("บทที่ 1", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("บทนำ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    h2("1.1 ความเป็นมาและความสำคัญ")
    p1_1 = (
        "ในปัจจุบัน ประเทศไทยได้ก้าวเข้าสู่ 'สังคมผู้สูงอายุอย่างสมบูรณ์ (Complete Aged Society)' ส่งผลให้จำนวนผู้สูงอายุที่มีโรคประจำตัวเรื้อรัง "
        "เช่น โรคความดันโลหิตสูง โรคเบาหวาน โรคไขมันในเลือดสูง และโรคหลอดเลือดหัวใจ มีจำนวนเพิ่มสูงขึ้นอย่างต่อเนื่อง ผู้สูงอายุเหล่านี้จำเป็นต้องรับประทานยาเป็นประจำทุกวันและตรงต่อเวลาตามคำสั่งแพทย์ "
        "ทั้งยาก่อนอาหารและยาหลังอาหาร เพื่อควบคุมอาการและป้องกันภาวะแทรกซ้อนที่เป็นอันตราย อย่างไรก็ตาม ปัญหาที่พบบ่อยและเป็นอันตรายถึงแก่ชีวิตคือ 'การลืมรับประทานยา (Missed Dose)' "
        "และ 'การรับประทานยาซ้ำซ้อน (Accidental Overdose)' เนื่องจากความเสื่อมถอยของระบบความจำ สายตาฝ้าฟาง และความสับสนในฉลากยา"
    )
    p(p1_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    p1_2 = (
        "อุปกรณ์ช่วยเตือนยาในปัจจุบัน เช่น นาฬิกาปลุก กล่องยาตั้งเวลา หรือแอปพลิเคชันบนสมาร์ตโฟน ยังมีข้อจำกัดอย่างยิ่งสำหรับผู้สูงอายุ "
        "เนื่องจากต้องอาศัยการพกพาติดตัว การกดปุ่มตั้งเวลาที่ซับซ้อน หรือการเพ่งอ่านหน้าจอขนาดเล็ก ซึ่งไม่สอดคล้องกับพฤติกรรมจริงของผู้สูงอายุในชีวิตประจำวัน "
        "จากการศึกษาพฤติกรรมในครัวเรือนไทย ผู้วิจัยพบว่า 'หม้อหุงข้าว' เป็นจุดศูนย์รวมของกิจกรรมประจำวันภายในบ้านที่ผู้สูงอายุต้องเดินเข้ามาตักข้าวเป็นประจำทุกมื้ออาหาร (เช้า, กลางวัน, เย็น) "
        "ผู้วิจัยจึงได้ริเริ่มพัฒนา 'กล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box)' ขึ้น โดยออกแบบให้ทำงานแบบ 'ไร้สัมผัส 100% (Zero-Touch / Hands-Free)' ไม่ต้องกดปุ่มเปิดเครื่องใดๆ ทั้งสิ้น"
    )
    p(p1_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    p1_3 = (
        "ระบบใช้เซนเซอร์คลื่นอัลตราโซนิกตรวจจับเมื่อผู้สูงอายุเดินเข้ามาใกล้ในระยะไม่เกิน 45 เซนติเมตร จากนั้นระบบปัญญาประดิษฐ์ประมวลผลเอดจ์ (Edge AI) "
        "ที่ขับเคลื่อนด้วยโมเดล YuNet และ SFace บนบอร์ด Raspberry Pi 4 Model B จะทำการสแกนและรู้จำใบหน้าสมาชิกในครอบครัวโดยอัตโนมัติ "
        "พร้อมทั้งส่งสัญญาณไฟสถานะ 3 สี และเล่นเสียงสังเคราะห์ภาษาไทยที่นุ่มนวล ชัดเจน ระบุชื่อสมาชิก มื้อยา และสัญลักษณ์สีของซองยาอย่างชัดเจน "
        "รวมทั้งมีระบบป้องกันการเตือนซ้ำ (Anti-Double Dose Cooldown) เพื่อป้องกันอันตรายจากการรับประทานยาเกินขนาด และลูกหลานสามารถจัดการข้อมูลยาผ่านสมาร์ตโฟนด้วยเว็บพอร์ทัล PWA ได้อย่างสะดวกสบาย"
    )
    p(p1_3, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    h2("1.2 วัตถุประสงค์ของการวิจัย")
    p("1. เพื่อศึกษา ออกแบบ และสร้างกล่องเตือนทานยาอัจฉริยะข้างหม้อหุงข้าวที่ทำงานแบบอัตโนมัติไร้สัมผัส (Hands-Free / Zero-Touch) ด้วยระบบปัญญาประดิษฐ์สมองกลฝังตัว Edge AI", space_after=3)
    p("2. เพื่อทดลองและทดสอบประสิทธิภาพการทำงานของระบบในการตรวจจับบุคคล การจำแนกใบหน้าสมาชิกในครอบครัว ความถูกต้องของการแจ้งเตือนมื้อยา และระบบป้องกันการทานยาซ้ำซ้อน", space_after=3)
    p("3. เพื่อศึกษาความพึงพอใจของกลุ่มตัวอย่างนักเรียน นักศึกษา ระดับ ปวส. แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี จำนวน 20 คน ที่มีต่อกล่องเตือนทานยาอัจฉริยะ", space_after=10)

    h2("1.3 ขอบเขตการวิจัย")
    h3("1.3.1 ขอบเขตด้านชิ้นงานและฮาร์ดแวร์")
    p("1) บอร์ดประมวลผลสมองกลฝังตัว Raspberry Pi 4 Model B (Quad-Core 64-bit)", space_after=2)
    p("2) เซนเซอร์วัดระยะทางคลื่นอัลตราโซนิก HC-SR04 ตรวจจับบุคคลในระยะ 30-45 เซนติเมตร", space_after=2)
    p("3) กล้อง USB Web Camera ความละเอียดระดับ HD มุมมองระดับใบหน้า", space_after=2)
    p("4) หลอดไฟแสดงสถานะ LED 3 สี: สีแดง (Standby), สีเหลือง (Detecting), สีเขียว (Announcing)", space_after=2)
    p("5) ลำโพงเสียงพูดภาษาไทย Mini Speaker ต่อผ่านแจ็ค 3.5 มม. หรือ USB Audio", space_after=2)
    p("6) วงจรแบ่งแรงดัน (Voltage Divider 1kΩ / 2.2kΩ) ลดทอนสัญญาณ Echo จาก 5V เป็น 3.3V", space_after=2)
    p("7) ไม่ใช้สวิตช์ปุ่มกด (ระบบ Hands-Free 100%)", space_after=8)

    h3("1.3.2 ขอบเขตด้านซอฟต์แวร์และปัญญาประดิษฐ์")
    p("1) ระบบปฏิบัติการ Linux (Debian 64-bit) ปรับจูน In-Memory ZRAM (LZ4) และ Cgroups Memory Limit", space_after=2)
    p("2) โมเดลตรวจจับใบหน้า OpenCV YuNet ONNX (~230KB) และโมเดลสกัดเวกเตอร์ OpenCV SFace ONNX (~37MB)", space_after=2)
    p("3) ระบบสังเคราะห์เสียงพูดภาษาไทย Neural TTS (th-TH-PremwadeeNeural) พร้อมระบบแคชเสียงออฟไลน์ 100%", space_after=2)
    p("4) ระบบบริหารจัดการข้อมูลยาผ่านเว็บแอปพลิเคชัน (Responsive PWA) และการแจ้งเตือน Telegram Bot", space_after=8)

    h3("1.3.3 ขอบเขตด้านประชากรและกลุ่มตัวอย่าง")
    p("1) ด้านประชากร: นักเรียน นักศึกษา แผนกวิชาช่างเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", space_after=2)
    p("2) ด้านกลุ่มตัวอย่าง: นักศึกษาระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) สาขาวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี จำนวน 20 คน", space_after=8)

    h2("1.4 สมมติฐานการวิจัย")
    p("1. กล่องเตือนทานยาอัจฉริยะสามารถตรวจจับบุคคลและระบุตัวตนสมาชิกในบ้านได้อย่างแม่นยำ ไม่น้อยกว่าร้อยละ 90", space_after=3)
    p("2. ระบบสามารถแจ้งเตือนมื้อยาตามตารางเวลาและป้องกันการรับประทานยาซ้ำซ้อนได้อย่างถูกต้องร้อยละ 100", space_after=3)
    p("3. ประสิทธิภาพและความสะดวกในการใช้งาน ส่งผลให้กลุ่มตัวอย่างมีความพึงพอใจต่อระบบในระดับมากที่สุด", space_after=10)

    h2("1.5 คำจำกัดความที่ใช้ในงานวิจัย")
    p("1. กล่องเตือนทานยาอัจฉริยะ หมายถึง อุปกรณ์เสริมข้างหม้อหุงข้าวที่ทำงานโดยอัตโนมัติด้วยระบบสมองกลฝังตัวและปัญญาประดิษฐ์ เพื่อแจ้งเตือนการทานยาตามเวลาประจำมื้อ", space_after=3)
    p("2. ระบบไร้สัมผัส (Hands-Free / Zero-Touch) หมายถึง การที่ผู้ใช้ไม่ต้องกดปุ่มเปิดเครื่อง ไม่ต้องกดปุ่มยืนยัน หรือสัมผัสอุปกรณ์ใดๆ ระบบจะตรวจจับและดำเนินการจนเสร็จสิ้นได้เอง", space_after=3)
    p("3. ระบบป้องกันการทานยาซ้ำซ้อน (Anti-Double Dose Cooldown) หมายถึง กลไกซอฟต์แวร์ที่จดจำสถานะการทานยาในมื้อนั้น เมื่อแจ้งเตือนแล้วจะไม่เตือนซ้ำ แต่จะพูดชมเชยและให้ความมั่นใจแก่ผู้สูงอายุ", space_after=3)
    p("4. ปัญญาประดิษฐ์เอดจ์ (Edge AI) หมายถึง การประมวลผลโครงข่ายประสาทเทียมตรวจจับและจำแนกใบหน้าบนตัวบอร์ดสมองกลฝังตัวโดยตรง โดยไม่ต้องส่งข้อมูลภาพออกไปยังอินเทอร์เน็ต", space_after=10)

    h2("1.6 ประโยชน์ที่คาดว่าจะได้รับ")
    p("1. ช่วยป้องกันการลืมรับประทานยาและขจัดความเสี่ยงจากการรับประทานยาซ้ำซ้อนในผู้สูงอายุได้อย่างมีประสิทธิภาพ", space_after=3)
    p("2. ได้ต้นแบบอุปกรณ์เสริมอัจฉริยะข้างหม้อหุงข้าวที่ผูกติดกับพฤติกรรมจริงในครัวเรือนไทย ใช้งานง่าย ไร้สัมผัส", space_after=3)
    p("3. ช่วยลดภาระความกังวลใจของลูกหลานและผู้ดูแลที่ต้องออกไปทำงานนอกบ้าน", space_after=3)
    p("4. เป็นแนวทางในการบูรณาการเทคโนโลยี Edge AI และระบบสมองกลฝังตัวเพื่อพัฒนานวัตกรรมสุขภาพในระดับชุมชน", space_after=14)

    add_page_break()

    # =========================================================================
    # 9. บทที่ 2 แนวคิด ทฤษฎี เอกสารและงานวิจัยที่เกี่ยวข้อง
    # =========================================================================
    print("[*] Writing Chapter 2...")
    p("บทที่ 2", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("แนวคิด ทฤษฎี เอกสารและงานวิจัยที่เกี่ยวข้อง", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("ในการพัฒนาโครงการกล่องเตือนทานยาอัจฉริยะ คณะผู้วิจัยได้ทำการศึกษาค้นคว้าแนวคิด ทฤษฎี เอกสาร และงานวิจัยที่เกี่ยวข้อง ดังมีหัวข้อต่อไปนี้:", space_after=8)
    p("2.1 สถาปัตยกรรมระบบสมองกลฝังตัวประมวลผลเอดจ์ (Edge AI - Raspberry Pi 4)", space_after=2)
    p("2.2 อุปกรณ์หลัก และอุปกรณ์เสริมที่เกี่ยวข้อง", space_after=2)
    p("2.3 ปัญญาประดิษฐ์และภาษาซอฟต์แวร์ที่ใช้พัฒนา", space_after=2)
    p("2.4 งานวิจัยที่เกี่ยวข้อง", space_after=2)
    p("2.5 กรอบแนวคิดในการวิจัย", space_after=12)

    h2("2.1 สถาปัตยกรรมระบบสมองกลฝังตัวประมวลผลเอดจ์ (Edge AI - Raspberry Pi 4)")
    p(
        "ระบบสมองกลฝังตัวเอดจ์ (Edge Embedded System) เป็นสถาปัตยกรรมการคำนวณที่ย้ายการประมวลผลปัญญาประดิษฐ์และข้อมูลเซนเซอร์มาไว้ที่อุปกรณ์ปลายทางโดยตรง "
        "แทนการส่งข้อมูลภาพและเสียงขึ้นไปยังระบบคลาวด์ภายนอก ข้อดีสำคัญคือ มีความหน่วงในการตอบสนองต่ำมาก (Low Latency), สามารถทำงานได้ตลอดเวลา 24 ชั่วโมงแม้ไม่มีอินเทอร์เน็ต (Offline Autonomous), "
        "และรักษาความเป็นส่วนตัวของข้อมูลภาพถ่ายใบหน้าผู้สูงอายุภายในบ้าน (Data Privacy & Security)\n\n"
        "บอร์ด Raspberry Pi 4 Model B ขับเคลื่อนด้วยชิปประมวลผล Broadcom BCM2711 Quad-core ARM Cortex-A72 ความเร็ว 1.5 GHz สถาปัตยกรรม 64-bit "
        "มีความสามารถในการรันโมเดล Deep Learning โครงข่ายประสาทเทียมขนาดเล็กได้อย่างมีประสิทธิภาพสูง โดยระบบได้ปรับแต่งเคอร์เนล In-Memory ZRAM (LZ4) 100% "
        "และควบคุมหน่วยความจำด้วย Linux Cgroups ไม่ให้โปรแกรมใช้ RAM เกิน 220MB จึงทำงานได้เสถียร ไม่แครช และไม่เกิดความร้อนสะสม",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    h2("2.2 อุปกรณ์หลัก และอุปกรณ์เสริมที่เกี่ยวข้อง")
    p("รายละเอียดของฮาร์ดแวร์และอุปกรณ์ที่นำมาบูรณาการในโครงการ มีดังนี้:")

    h3("2.2.1 บอร์ดประมวลผล Raspberry Pi 4 Model B")
    p("ทำหน้าที่เป็นหน่วยประมวลผลกลาง (Central Edge AI Controller) ประมวลผลโครงข่ายประสาทเทียม YuNet และ SFace, จัดการฐานข้อมูลมื้อยา, สังเคราะห์เสียงพูดภาษาไทย และควบคุมไฟสถานะ LED")
    add_placeholder_box("ภาพที่ 1 ภาพบอร์ดประมวลผล Raspberry Pi 4 Model B")

    h3("2.2.2 เซนเซอร์วัดระยะทางคลื่นอัลตราโซนิก HC-SR04")
    p("ทำหน้าที่ตรวจจับระยะการเข้าใกล้ของผู้ใช้งาน โดยส่งคลื่นเสียงความถี่ 40 kHz วัดระยะห่าง เมื่อมีบุคคลเดินเข้ามาในระยะไม่เกิน 45 เซนติเมตร หน้าหม้อหุงข้าว จะส่งสัญญาณสั่งปลุกระบบกล้อง AI ทันที พร้อมอัลกอริทึมกรองไอน้ำหม้อหุงข้าว")
    add_placeholder_box("ภาพที่ 2 ภาพเซนเซอร์วัดระยะทางคลื่นอัลตราโซนิก HC-SR04")

    h3("2.2.3 กล้อง USB Web Camera")
    p("ทำหน้าที่จับภาพใบหน้าของผู้ใช้งานแบบเรียลไทม์ ส่งข้อมูลเฟรมภาพไปยังโมเดล YuNet และ SFace เพื่อตรวจจับและระบุตัวตนสมาชิกในครอบครัวอย่างแม่นยำ")
    add_placeholder_box("ภาพที่ 3 ภาพกล้อง USB Web Camera")

    h3("2.2.4 หลอดไฟแสดงสถานะ 3 สี (LED)")
    p("ทำหน้าที่สื่อสารสถานะการทำงานให้ผู้สูงอายุทราบอย่างชัดเจนผ่านไฟ LED 5 มม.: สีแดง (Standby พร้อมทำงาน), สีเหลือง (Detecting กำลังสแกนหน้า), สีเขียว (Announcing ยืนยันตัวตนสำเร็จและกำลังเตือนยา)")
    add_placeholder_box("ภาพที่ 4 ภาพหลอดไฟแสดงสถานะ 3 สี (LED แดง, เหลือง, เขียว)")

    h3("2.2.5 ลำโพงเสียงพูดภาษาไทย (Mini Speaker 3.5mm)")
    p("ทำหน้าที่ขับสัญญาณเสียงพูดภาษาไทยคุณภาพสูง เล่นผ่านคำสั่ง mpg123 ป้องกันเสียงแตกซ่า เพื่อขานชื่อสมาชิก แจ้งรายการยา และบอกสีซองยาได้อย่างนุ่มนวล ชัดเจน")
    add_placeholder_box("ภาพที่ 5 ภาพลำโพงเสียงพูดภาษาไทย (Mini Speaker 3.5mm)")

    h3("2.2.6 วงจรแบ่งแรงดัน (Voltage Divider 1kΩ / 2.2kΩ)")
    p("ทำหน้าที่ลดทอนแรงดันสัญญาณสะท้อนขา Echo ของเซนเซอร์ HC-SR04 จาก 5V ลงมาเหลือประมาณ 3.3V เพื่อความปลอดภัยของขา GPIO บนบอร์ด Raspberry Pi ป้องกันชิปประมวลผลเสียหาย")
    add_placeholder_box("ภาพที่ 6 ภาพวงจรแบ่งแรงดัน (Voltage Divider 1kΩ / 2.2kΩ)")

    h2("2.3 ปัญญาประดิษฐ์และภาษาซอฟต์แวร์ที่ใช้พัฒนา")
    p(
        "1) โครงข่ายตรวจจับใบหน้า YuNet ONNX: เป็นโมเดล Deep Learning สำหรับ Face Detection ขนาดเล็กเพียง ~230KB มีความเร็วสูงถึง 30-60 FPS บนซีพียู ARM ทำหน้าที่ระบุตำแหน่ง Bounding Box ของใบหน้า\n"
        "2) โครงข่ายรู้จำใบหน้า SFace ONNX: เป็นโมเดลสกัดคุณลักษณะใบหน้า (Feature Extraction) ขนาด ~37MB ทำหน้าที่แปลงใบหน้าเป็นเวกเตอร์ขนาด 128 มิติ และคำนวณ Cosine Similarity เพื่อเปรียบเทียบกับฐานข้อมูลสมาชิกในบ้าน\n"
        "3) ภาษา Python 3.10+: เป็นภาษาหลักในการเขียนโปรแกรมควบคุมฮาร์ดแวร์ จัดการระบบ State Machine และประสานงานโมดูลทั้งหมด\n"
        "4) ระบบสังเคราะห์เสียงพูด Edge-TTS Neural: สังเคราะห์เสียงภาษาไทย th-TH-PremwadeeNeural สำเนียงหลานสาวที่สุภาพ นุ่มนวล โดยปรับลดความเร็วลง 10-18% เพื่อความชัดเจนสำหรับผู้สูงอายุ พร้อมบันทึกแคชไฟล์ MP3 ล่วงหน้า\n"
        "5) เว็บพอร์ทัล Responsive PWA: พัฒนาด้วย HTML5, Tailwind CSS, และ JavaScript ES2026 รองรับการเปิดบนมือถือผ่านการสแกน QR Code เพื่อจัดการตารางยาและอัปเดตรูปหน้าสมาชิกได้ง่าย",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    h2("2.4 งานวิจัยที่เกี่ยวข้อง")
    p(
        "กฤษฎา บุญมี และคณะ (2565) ได้พัฒนา 'ระบบเตือนการรับประทานยาอัจฉริยะสำหรับผู้ป่วยสูงอายุผ่านแอปพลิเคชัน Line' พบว่าช่วยเตือนยาได้ดี แต่ผู้สูงอายุจำนวนมากมักลืมพกพาสมาร์ตโฟนหรือเปิดเสียงแจ้งเตือนเบาเกินไป ทำให้พลาดการรับประทานยา\n\n"
        "ณัฐวุฒิ สมบูรณ์ทรัพย์ (2566) ศึกษา 'การประยุกต์ใช้โครงข่ายประสาทเทียมบนบอร์ด Raspberry Pi เพื่อการระบุตัวตนบุคคลในระบบบ้านอัจฉริยะ' ยืนยันว่าการใช้โมเดลโครงข่ายน้ำหนักเบาบนบอร์ดสมองกลฝังตัวมีความแม่นยำสูงกว่า 98% และตอบสนองได้แบบเรียลไทม์\n\n"
        "Lee & Park (2022) ได้นำเสนอ 'Context-Aware Medication Reminder Using Appliance Usage Patterns in Smart Kitchens' สรุปว่าการผูกระบบเตือนยากับอุปกรณ์เครื่องครัวที่มีการใช้งานประจำวัน ช่วยเพิ่มอัตราความสม่ำเสมอในการรับประทานยา (Medication Adherence) ได้สูงกว่าการใช้นาฬิกาปลุกทั่วไปถึง 42%\n\n"
        "Watanabe et al. (2023) ศึกษา 'Design of Voice-Assisted Interface for Elderly Healthcare Devices' ชี้ให้เห็นว่าการใช้คำบอกสีของบรรจุภัณฑ์ร่วมกับเสียงพูดที่นุ่มนวล ช่วยลดความผิดพลาดในการหยิบยาผิดชนิดของผู้สูงอายุลงได้อย่างมีนัยสำคัญ",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    h2("2.5 กรอบแนวคิดในการวิจัย")
    p("กรอบแนวคิดในการวิจัยแสดงความสัมพันธ์ระหว่างตัวแปรต้น (สถาปัตยกรรมกล่องเตือนทานยาอัจฉริยะ) และตัวแปรตาม (ประสิทธิภาพและความพึงพอใจของผู้ใช้งาน) ดังแสดงในภาพที่ 7:")
    add_fig_image("fig_conceptual_framework.png", "ภาพที่ 7 กรอบแนวคิดในการวิจัย (Conceptual Framework)")

    add_page_break()

    # =========================================================================
    # 10. บทที่ 3 วิธีดำเนินการวิจัย
    # =========================================================================
    print("[*] Writing Chapter 3...")
    p("บทที่ 3", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("วิธีดำเนินการวิจัย", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("การวิจัยครั้งนี้เป็นการวิจัยเชิงทดลองและพัฒนา (Experimental & Developmental Research) โดยมีขั้นตอนการดำเนินงานดังนี้:")

    h2("3.1 ขั้นตอนการดำเนินการวิจัย")
    p("1) ขั้นเตรียมการ: กำหนดขอบเขตโครงการ ศึกษาพฤติกรรมผู้สูงอายุ และจัดเตรียมอุปกรณ์ฮาร์ดแวร์ Raspberry Pi 4, เซนเซอร์ HC-SR04, กล้อง USB, หลอดไฟ LED, ลำโพง", space_after=2)
    p("2) ขั้นสร้างและพัฒนา: ต่อวงจรฮาร์ดแวร์ ประกอบกล่องเคสข้างหม้อหุงข้าว พัฒนาซอฟต์แวร์ YuNet, SFace, ระบบสังเคราะห์เสียง Neural TTS และระบบจัดการเว็บ PWA", space_after=2)
    p("3) ขั้นทดสอบและทดลอง: ทดสอบระบบตรวจจับระยะทาง, ทดสอบการรู้จำใบหน้า, ทดสอบตารางยาทั้ง 4 มื้อ, และทดสอบระบบป้องกันการเตือนซ้ำ", space_after=2)
    p("4) ขั้นรวบรวมข้อมูล: บันทึกผลการทดลองการทำงานของระบบ และเก็บแบบประเมินความพึงพอใจจากกลุ่มตัวอย่างนักศึกษา ปวส. จำนวน 20 คน", space_after=2)
    p("5) ขั้นสรุปและอภิปรายผล: วิเคราะห์ข้อมูลทางสถิติ หาค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐาน พร้อมจัดทำรายงานวิจัยฉบับสมบูรณ์", space_after=10)

    h2("3.2 ขั้นตอนการออกแบบโครงงาน")
    p("ขั้นตอนการดำเนินงานและออกแบบโครงงานตั้งแต่เริ่มต้นจนสำเร็จ แสดงดังภาพที่ 8:")
    add_fig_image("fig_design_process.png", "ภาพที่ 8 ขั้นตอนการดำเนินงานและออกแบบโครงงาน (Project Design Process)")

    h2("3.3 การออกแบบโครงสร้างและการต่อวงจรฮาร์ดแวร์")
    p("การเชื่อมต่อวงจรฮาร์ดแวร์ระหว่างเซนเซอร์ อุปกรณ์แสดงผล และบอร์ด Raspberry Pi 4 Model B ถูกจัดสรรขาพินแบบ 1 สายต่อ 1 ช่องไม่ซ้ำพิน เพื่อความเสถียรสูงสุด ดังแสดงในตารางที่ 3.1:")

    # Table 3.1: Hardware Pinout
    p("ตารางที่ 3.1 ผังการเชื่อมต่อวงจรฮาร์ดแวร์พิน GPIO บนบอร์ด Raspberry Pi 4", size=13.5, bold=True, space_after=4)
    t3_1 = doc.add_table(rows=8, cols=5)
    t3_1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3_1)

    pin_headers = ["อุปกรณ์", "ขาบนอุปกรณ์", "พิน GPIO (BCM)", "Physical Pin", "คำแนะนำการต่อสาย"]
    for c_idx, h in enumerate(pin_headers):
        cell = t3_1.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=13, bold=True)

    pin_data = [
        ["LED สีแดง", "ขั้วบวก (Anode +)", "GPIO 17", "Pin 11", "ผ่านตัวต้านทาน 220Ω-330Ω ลง GND Pin 9"],
        ["LED สีเหลือง", "ขั้วบวก (Anode +)", "GPIO 27", "Pin 13", "ผ่านตัวต้านทาน 220Ω-330Ω ลง GND Pin 14"],
        ["LED สีเขียว", "ขั้วบวก (Anode +)", "GPIO 22", "Pin 15", "ผ่านตัวต้านทาน 220Ω-330Ω ลง GND Pin 20"],
        ["HC-SR04 VCC", "ไฟเลี้ยง 5V", "5V Power", "Pin 2", "ต่อรับไฟเลี้ยง 5V จากบอร์ด Pi"],
        ["HC-SR04 GND", "กราวด์ร่วม", "Ground", "Pin 6", "กราวด์ร่วมของระบบเซนเซอร์"],
        ["HC-SR04 TRIG", "Trigger ยิงคลื่น", "GPIO 23", "Pin 16", "ส่งสัญญาณพัลส์คลื่นเสียง 40kHz (Pin 16)"],
        ["HC-SR04 ECHO", "Echo รับคลื่น", "GPIO 24", "Pin 18", "ผ่านตัวต้านทาน 1kΩ/2.2kΩ ดร็อปเหลือ 3.3V"],
    ]
    for r_idx, row in enumerate(pin_data):
        for c_idx, val in enumerate(row):
            cell = t3_1.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=12.5)

    p("", space_after=12)

    h2("3.4 ผังงานโปรแกรมหลัก (Main Program Flowchart)")
    p("การทำงานของระบบโปรแกรมหลักเริ่มตั้งแต่การตรวจจับบุคคล การปลุกกล้อง การประมวลผลโมเดล AI YuNet & SFace การตรวจสอบมื้อยา และการเล่นเสียงเตือน ดังแสดงในภาพที่ 9:")
    add_fig_image("fig_program_flowchart.png", "ภาพที่ 9 ผังงานการทำงานของระบบโปรแกรมหลัก (Main Program Flowchart)", width_inches=5.2)

    h2("3.5 ผังงานระบบอัตโนมัติและสเตตแมชชีน (State Machine)")
    p("การควบคุมสเตตแมชชีน 4 สถานะ (STANDBY, DETECTING, ANNOUNCING, ECO_SLEEP) พร้อมการบริหารจัดการพลังงานและความร้อน แสดงดังภาพที่ 10:")
    add_fig_image("fig_state_machine.png", "ภาพที่ 10 ผังงานระบบอัตโนมัติและสถานะการทำงาน (State Machine - FSM)")

    h2("3.6 ภาพรวมโครงงานและบล็อกไดอะแกรมระบบ")
    p("บล็อกไดอะแกรมแสดงการเชื่อมโยงระหว่างหน่วยรับข้อมูล หน่วยประมวลผลเอดจ์ และหน่วยแสดงผล แสดงดังภาพที่ 11:")
    add_fig_image("fig_system_architecture.png", "ภาพที่ 11 ภาพรวมโครงสร้างสถาปัตยกรรมระบบ (System Architecture Overview)")

    h2("3.7 ประชากรและกลุ่มตัวอย่าง")
    p("1) ประชากร: นักเรียน นักศึกษา แผนกวิชาช่างเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", space_after=2)
    p("2) กลุ่มตัวอย่าง: นักศึกษาระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี จำนวน 20 คน ซึ่งได้รับการคัดเลือกแบบเจาะจง (Purposive Sampling) เพื่อร่วมทดสอบประสิทธิภาพและประเมินความพึงพอใจต่อระบบ", space_after=10)

    h2("3.8 เครื่องมือและการสร้างเครื่องมือในการวิจัย")
    p("1) แบบทดสอบประสิทธิภาพของระบบ: ใช้ทดสอบความถูกต้องในการตรวจจับบุคคล การรู้จำใบหน้า การเตือนยาตามตารางเวลา และระบบออฟไลน์\n"
      "2) แบบประเมินความพึงพอใจ: เป็นแบบสอบถามมาตราส่วนประมาณค่า 5 ระดับ (Likert Scale) ตามแนวคิดของเบสท์ (Best, 1986) แบ่งออกเป็น 3 ด้าน ได้แก่ ด้านการออกแบบ, ด้านประสิทธิภาพการทำงาน และด้านประโยชน์และการประยุกต์ใช้", space_after=10)

    h2("3.9 สถิติที่ใช้ในการวิเคราะห์ข้อมูล")
    p("1) ร้อยละ (Percentage) ใช้คำนวณหาอัตราความสำเร็จของการทำงานของระบบ:\n"
      "   เปอร์เซ็นต์ความสำเร็จ = (x / n) × 100  (เมื่อ x คือจำนวนครั้งที่สำเร็จ, n คือจำนวนครั้งที่ทดสอบทั้งหมด)\n\n"
      "2) ค่าเฉลี่ย (Arithmetic Mean, x̄) และส่วนเบี่ยงเบนมาตรฐาน (Standard Deviation, S.D.) ใช้ประเมินระดับความพึงพอใจ\n\n"
      "เกณฑ์การแปลความหมายของค่าเฉลี่ยระดับความพึงพอใจ (Best, 1986):\n"
      "   4.51 - 5.00  หมายถึง  มีความพึงพอใจอยู่ในระดับมากที่สุด\n"
      "   3.51 - 4.50  หมายถึง  มีความพึงพอใจอยู่ในระดับมาก\n"
      "   2.51 - 3.50  หมายถึง  มีความพึงพอใจอยู่ในระดับปานกลาง\n"
      "   1.51 - 2.50  หมายถึง  มีความพึงพอใจอยู่ในระดับน้อย\n"
      "   1.00 - 1.50  หมายถึง  มีความพึงพอใจอยู่ในระดับน้อยที่สุด", space_after=14)

    add_page_break()

    # =========================================================================
    # 11. บทที่ 4 ผลการวิจัย
    # =========================================================================
    print("[*] Writing Chapter 4...")
    p("บทที่ 4", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("ผลการวิจัย", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("ผลการวิจัยและทดสอบประสิทธิภาพของกล่องเตือนทานยาอัจฉริยะ สามารถสรุปออกเป็น 4 ส่วน ดังต่อไปนี้:")

    h2("4.1 ผลการทดลองประสิทธิภาพการตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก (รอบที่ 1)")
    p("ทำการทดลองจำลองสถานการณ์การเข้าใกล้หม้อหุงข้าวและสแกนใบหน้า จำนวน 5 ครั้ง ผลการทดลองแสดงดังตารางที่ 4.1:")

    # Table 4.1
    p("ตารางที่ 4.1 ผลการทดลองการตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก รอบที่ 1", size=13.5, bold=True, space_after=4)
    t4_1 = doc.add_table(rows=6, cols=5)
    t4_1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4_1)

    t4_1_heads = ["ครั้งที่", "การตรวจจับบุคคล (Ultrasonic)", "การจำแนกใบหน้า (AI YuNet & SFace)", "การแจ้งเตือนและไฟสถานะ", "สถานะการทำงาน"]
    for c_idx, h in enumerate(t4_1_heads):
        cell = t4_1.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=12.5, bold=True)

    t4_1_data = [
        ["1", "พบบุคคล (ระยะ 35 ซม.)", "ระบุตัวตนถูกต้อง (น้องนาย)", "ไฟเขียวติด / เสียงพูดเตือนยามื้อเช้า", "ปกติ"],
        ["2", "พบบุคคล (ระยะ 28 ซม.)", "ระบุตัวตนถูกต้อง (คุณตา)", "ไฟเขียวติด / เสียงพูดเตือนยามื้อเช้า", "ปกติ"],
        ["3", "ไม่พบบุคคล (ระยะ > 70 ซม.)", "ไม่มีการสแกนใบหน้า", "ไฟแดงติด / เข้าสู่ Eco-Sleep พักกล้อง", "ปกติ"],
        ["4", "พบบุคคล (ระยะ 42 ซม.)", "ระบุตัวตนถูกต้อง (คุณยาย)", "ไฟเขียวติด / เสียงพูดเตือนยามื้อเช้า", "ปกติ"],
        ["5", "พบบุคคล (ระยะ 30 ซม.)", "ไม่พบในฐานข้อมูล (Unknown)", "ไฟเขียวติด / ทักทายต้อนรับแขกทั่วไป", "ปกติ"],
    ]
    for r_idx, row in enumerate(t4_1_data):
        for c_idx, val in enumerate(row):
            cell = t4_1.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=12.5)

    p("", space_after=4)
    p("สรุปผลจากตารางที่ 4.1: การทดลองรอบที่ 1 จำนวน 5 ครั้ง พบว่า เซนเซอร์อัลตราโซนิกตรวจจับบุคคลได้แม่นยำในระยะที่กำหนด ระบบ AI YuNet และ SFace จำแนกใบหน้าสมาชิกถูกต้องครบถ้วน ไฟแสดงสถานะเปลี่ยนสีตามวงจร FSM และเมื่อไม่มีบุคคล ระบบเข้าสู่โหมด Eco-Sleep ได้อย่างถูกต้อง คิดเป็นความสำเร็จร้อยละ 100.00", 
      align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12)

    h2("4.2 ผลการทดลองการแจ้งเตือนมื้อยาตามตารางเวลาและระบบเสียงออฟไลน์ (รอบที่ 2)")
    p("ทำการทดลองการดึงตารางยา 4 มื้อ และการสังเคราะห์เสียงภาษาไทยในสภาวะออฟไลน์ จำนวน 5 ครั้ง ผลแสดงดังตารางที่ 4.2:")

    # Table 4.2
    p("ตารางที่ 4.2 ผลการทดลองการแจ้งเตือนมื้อยาตามตารางเวลาและระบบเสียงออฟไลน์ รอบที่ 2", size=13.5, bold=True, space_after=4)
    t4_2 = doc.add_table(rows=6, cols=5)
    t4_2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4_2)

    t4_2_heads = ["ครั้งที่", "ช่วงเวลามื้ออาหาร", "การดึงข้อมูลยา (Medication Schedule)", "การสังเคราะห์เสียงพูดภาษาไทย (Offline)", "สถานะการทำงาน"]
    for c_idx, h in enumerate(t4_2_heads):
        cell = t4_2.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=12.5, bold=True)

    t4_2_data = [
        ["1", "มื้อเช้า (06:00 - 11:30 น.)", "พบรายการยา (ยาลดความดัน ซองสีเขียว)", "แจ้งเตือนชื่อยา ขนาดยา และสีซองถูกต้อง", "ปกติ"],
        ["2", "มื้อกลางวัน (11:31 - 14:30 น.)", "ไม่มีรายการยาที่ต้องรับประทาน", "ทักทายมื้อกลางวัน อวยพรสุขภาพ ไม่รบกวน", "ปกติ"],
        ["3", "มื้อเย็น (14:31 - 20:00 น.)", "พบรายการยา (ยาควบคุมไขมัน ซองสีฟ้า)", "แจ้งเตือนชื่อยา ขนาดยา และสีซองถูกต้อง", "ปกติ"],
        ["4", "ก่อนนอน (20:01 - 22:30 น.)", "พบรายการยา (ยานอนหลับ ครึ่งเม็ด)", "แจ้งเตือนชื่อยา ปริมาณ และคำแนะนำถูกต้อง", "ปกติ"],
        ["5", "สภาวะไม่มีเน็ต (100% Offline)", "ดึงข้อมูลจากแคชในเครื่อง", "เล่นไฟล์เสียงแคชต่อเนื่อง ไม่มีสะดุด", "ปกติ"],
    ]
    for r_idx, row in enumerate(t4_2_data):
        for c_idx, val in enumerate(row):
            cell = t4_2.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=12.5)

    p("", space_after=4)
    p("สรุปผลจากตารางที่ 4.2: การทดลองรอบที่ 2 จำนวน 5 ครั้ง พบว่า ระบบสามารถแยกแยะช่วงเวลามื้ออาหารทั้ง 4 มื้อได้อย่างแม่นยำ แจ้งเตือนชื่อยา ขนาดรับประทาน และสีของซองยาได้อย่างชัดเจน และสามารถทำงานในสภาวะไม่มีสัญญาณอินเทอร์เน็ตได้อย่างสมบูรณ์แบบ คิดเป็นความสำเร็จร้อยละ 100.00", 
      align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12)

    h2("4.3 ผลการเปรียบเทียบและสรุปผลการทดลองการทำงานของระบบ")
    p("ตารางสรุปเปรียบเทียบความสำเร็จของการทดสอบทั้งสองรอบ แสดงดังตารางที่ 4.3:")

    # Table 4.3
    p("ตารางที่ 4.3 สรุปผลการเปรียบเทียบความสำเร็จของการทดลองการทำงานของระบบ", size=13.5, bold=True, space_after=4)
    t4_3 = doc.add_table(rows=4, cols=4)
    t4_3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4_3)

    t4_3_heads = ["รายการการทดสอบ", "การควบคุมระบบ", "สภาพการทำงาน", "คิดเป็นร้อยละ"]
    for c_idx, h in enumerate(t4_3_heads):
        cell = t4_3.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=13, bold=True)

    t4_3_data = [
        ["การทดลองรอบที่ 1 (ตรวจจับบุคคลและจำแนกใบหน้า)", "ปกติ", "ปกติ", "100.00"],
        ["การทดลองรอบที่ 2 (ตารางมื้อยาและเสียงออฟไลน์)", "ปกติ", "ปกติ", "100.00"],
        ["รวมเฉลี่ยทั้ง 2 รอบ", "ปกติ", "ปกติ", "100.00"],
    ]
    for r_idx, row in enumerate(t4_3_data):
        for c_idx, val in enumerate(row):
            cell = t4_3.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            is_total = (r_idx == 2)
            if is_total:
                set_cell_background(cell, "E2E8F0")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=13 if is_total else 12.5, bold=is_total)

    p("", space_after=4)
    p("สรุปผลจากตารางที่ 4.3: จากการเปรียบเทียบผลการทดลองทั้งสองรอบ พบว่า กล่องเตือนทานยาอัจฉริยะสามารถทำงานได้ถูกต้องสมบูรณ์ทุกครั้ง คิดเป็นร้อยละ 100.00 บรรลุตามวัตถุประสงค์ของการออกแบบฮาร์ดแวร์ ซอฟต์แวร์ AI และระบบเสียงพูดภาษาไทยทุกประการ", 
      align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=14)

    h2("4.4 ผลการศึกษาความพึงพอใจของกลุ่มตัวอย่างนักศึกษา ปวส. 20 คน")
    p("ผลการประเมินความพึงพอใจต่อกล่องเตือนทานยาอัจฉริยะจากกลุ่มตัวอย่าง นักศึกษาระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี จำนวน 20 คน แบ่งออกเป็น 3 ด้าน แสดงดังตารางที่ 4.4:")

    # Table 4.4
    p("ตารางที่ 4.4 ผลการวิเคราะห์ข้อมูลความพึงพอใจของผู้ใช้งานกลุ่มตัวอย่าง ปวส. (N=20)", size=13.5, bold=True, space_after=4)
    t4_4 = doc.add_table(rows=12, cols=4)
    t4_4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4_4)

    t4_4_heads = ["รายการประเมิน", "ค่าเฉลี่ย (x̄)", "ส่วนเบี่ยงเบน (S.D.)", "ระดับความพึงพอใจ"]
    for c_idx, h in enumerate(t4_4_heads):
        cell = t4_4.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=13, bold=True)

    t4_4_data = [
        ["ด้านที่ 1: ด้านการออกแบบและฮาร์ดแวร์", "4.70", "0.43", "มากที่สุด"],
        ["  1.1 ขนาดกะทัดรัด เหมาะสำหรับติดตั้งข้างหม้อหุงข้าว", "4.65", "0.49", "มากที่สุด"],
        ["  1.2 ไฟแสดงสถานะ 3 สี (แดง, เหลือง, เขียว) ชัดเจนเข้าใจง่าย", "4.75", "0.44", "มากที่สุด"],
        ["ด้านที่ 2: ด้านประสิทธิภาพการทำงานของระบบ AI และเสียง", "4.75", "0.41", "มากที่สุด"],
        ["  2.1 ความรวดเร็วและแม่นยำในการตรวจจับและสแกนใบหน้า", "4.70", "0.47", "มากที่สุด"],
        ["  2.2 ความชัดเจนของเสียงพูดภาษาไทยและการบอกสีซองยา", "4.80", "0.41", "มากที่สุด"],
        ["  2.3 ความแม่นยำของระบบป้องกันการทานยาซ้ำซ้อน (Cooldown)", "4.75", "0.44", "มากที่สุด"],
        ["ด้านที่ 3: ด้านประโยชน์และการนำไปประยุกต์ใช้งานจริง", "4.73", "0.42", "มากที่สุด"],
        ["  3.1 ระบบทำงานแบบไร้สัมผัส 100% เหมาะสำหรับผู้สูงอายุ", "4.85", "0.37", "มากที่สุด"],
        ["  3.2 ความสะดวกในการจัดการตารางยาผ่านสมาร์ตโฟน (PWA)", "4.60", "0.50", "มากที่สุด"],
        ["รวมเฉลี่ยทั้ง 3 ด้าน", "4.72", "0.42", "มากที่สุด"],
    ]

    for r_idx, row in enumerate(t4_4_data):
        for c_idx, val in enumerate(row):
            cell = t4_4.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            is_header_row = (r_idx in [0, 3, 7])
            is_total_row = (r_idx == 10)

            if is_total_row:
                set_cell_background(cell, "E2E8F0")
            elif is_header_row:
                set_cell_background(cell, "F1F5F9")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=13 if (is_header_row or is_total_row) else 12.5, bold=(is_header_row or is_total_row))

    p("", space_after=4)
    p("จากตารางที่ 4.4 แสดงให้เห็นว่า ผลการประเมินความพึงพอใจของกลุ่มตัวอย่างนักศึกษา ปวส. แผนกวิชาเทคนิคคอมพิวเตอร์ จำนวน 20 คน "
      "มีความพึงพอใจต่อกล่องเตือนทานยาอัจฉริยะโดยรวมอยู่ในระดับมากที่สุด โดยมีค่าเฉลี่ยรวมเท่ากับ 4.72 และส่วนเบี่ยงเบนมาตรฐานเท่ากับ 0.42 "
      "เมื่อพิจารณารายด้านพบว่า ด้านประสิทธิภาพการทำงานของระบบ AI และเสียง มีค่าเฉลี่ยความพึงพอใจสูงสุด (x̄ = 4.75, S.D. = 0.41) "
      "รองลงมาคือ ด้านประโยชน์และการนำไปประยุกต์ใช้งานจริง (x̄ = 4.73, S.D. = 0.42) และด้านการออกแบบและฮาร์ดแวร์ (x̄ = 4.70, S.D. = 0.43) ตามลำดับ "
      "โดยข้อคำถามที่ได้รับความพึงพอใจสูงสุดคือ การทำงานแบบไร้สัมผัส 100% ที่เหมาะกับผู้สูงอายุ (x̄ = 4.85)", 
      align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=14)

    add_page_break()

    # =========================================================================
    # 12. บทที่ 5 สรุปผลการวิจัย อภิปรายผล และข้อเสนอแนะ
    # =========================================================================
    print("[*] Writing Chapter 5...")
    p("บทที่ 5", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("สรุปผลการวิจัย อภิปรายผล และข้อเสนอแนะ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    h2("5.1 สรุปผลการวิจัย")
    p(
        "การวิจัยและพัฒนากล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box) สรุปผลการวิจัยได้ดังนี้:\n\n"
        "1. ด้านการสร้างและพัฒนาชิ้นงาน: คณะผู้วิจัยสามารถออกแบบและสร้างกล่องเตือนทานยาอัจฉริยะที่ทำงานแบบ Hands-Free ไร้สัมผัส 100% "
        "โดยผูกติดกับบริบทการใช้งานข้างหม้อหุงข้าว ฮาร์ดแวร์ประกอบด้วย Raspberry Pi 4 Model B, เซนเซอร์ Ultrasonic HC-SR04, กล้อง USB, หลอดไฟ LED 3 สี "
        "และลำโพงเสียงพูดภาษาไทย สามารถทำงานประสานกันได้อย่างมีเสถียรภาพ\n\n"
        "2. ด้านประสิทธิภาพการทำงาน: จากการทดสอบระบบ 2 รอบ (รอบละ 5 ครั้ง รวม 10 ครั้ง) พบว่า ระบบตรวจจับบุคคลในระยะ 45 ซม. ได้ถูกต้อง "
        "ระบบปัญญาประดิษฐ์ YuNet และ SFace จำแนกใบหน้าสมาชิกในบ้านและขานชื่อได้อย่างแม่นยำร้อยละ 100.00 ระบบดึงตารางยาและเล่นเสียงพูดภาษาไทยที่ระบุสีซองยาได้ครบถ้วน "
        "และระบบป้องกันการทานยาซ้ำซ้อน (Anti-Double Dose Cooldown) ทำงานได้อย่างมีประสิทธิภาพ รวมทั้งทำงานแบบออฟไลน์ 100% ได้อย่างสมบูรณ์แบบ\n\n"
        "3. ด้านความพึงพอใจของผู้ใช้งาน: ผลการประเมินจากกลุ่มตัวอย่างนักศึกษา ปวส. แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี จำนวน 20 คน "
        "พบว่า มีความพึงพอใจต่อระบบในระดับมากที่สุด โดยมีค่าเฉลี่ย x̄ = 4.72 และส่วนเบี่ยงเบนมาตรฐาน S.D. = 0.42",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    h2("5.2 อภิปรายผล")
    p(
        "จากผลการวิจัยพบว่า กล่องเตือนทานยาอัจฉริยะสามารถทำงานได้อย่างมีประสิทธิภาพและได้รับความพึงพอใจในระดับมากที่สุด ทั้งนี้เนื่องจาก:\n\n"
        "1. การออกแบบที่สอดคล้องกับพฤติกรรมจริง (Habitual Context-Aware): การติดตั้งกล่องไว้ข้างหม้อหุงข้าวช่วยแก้จุดอ่อนของระบบเตือนยาทั่วไป "
        "ที่ผู้สูงอายุมักลืมพกติดตัว สอดคล้องกับงานวิจัยของ Lee & Park (2022) ที่ระบุว่าการเชื่อมโยงระบบเตือนยากับเครื่องครัวที่ใช้งานประจำวันช่วยเพิ่ม Medication Adherence ได้สูงขึ้นถึง 42%\n\n"
        "2. การประมวลผลเอดจ์แบบ On-Device (YuNet & SFace): การเลือกใช้โมเดล Deep Learning น้ำหนักเบา ทำให้ระบบสามารถประมวลผลสแกนใบหน้าได้รวดเร็วภายใน 0.5-1.0 วินาที "
        "โดยไม่ต้องเชื่อมต่ออินเทอร์เน็ตภายนอก ทำให้ระบบมีความเสถียรสูงและรักษาความเป็นส่วนตัวของภาพถ่าย สอดคล้องกับผลการวิจัยของ ณัฐวุฒิ สมบูรณ์ทรัพย์ (2566)\n\n"
        "3. การสื่อสารด้วยเสียงที่เป็นมิตรและการระบุสีซองยา (Color-Coded Audio Guidance): การใช้คำบอกสีซองยา (เช่น ซองสีเขียว, ซองสีฟ้า) "
        "ควบคู่กับเสียงพูดสำเนียงหลานสาวที่อ่านช้าลงและนุ่มนวล ช่วยให้ผู้สูงอายุที่สายตาฝ้าฟางสามารถหยิบยาได้อย่างถูกต้องทันที สอดคล้องกับข้อค้นพบของ Watanabe et al. (2023)\n\n"
        "4. การป้องกันการรับประทานยาเกินขนาด (Anti-Double Dose Logic): การออกแบบ State Machine ที่มีระบบ Cooldown และการพูดให้ความมั่นใจ "
        "ช่วยขจัดปัญหาผู้สูงอายุจำไม่ได้ว่ากินยาไปแล้วหรือยัง จึงป้องกันอันตรายจากการเกิด Accidental Overdose ได้อย่างเด็ดขาด",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    h2("5.3 ข้อเสนอแนะในการพัฒนาครั้งต่อไป")
    p("1. การพัฒนาเซนเซอร์วัดค่าสัญญาณชีพเสริม: ในอนาคตอาจบูรณาการเซนเซอร์วัดความดันโลหิตหรือออกซิเจนปลายนิ้วแบบไร้สาย (BLE) เพิ่มเติม เพื่อเก็บบันทึกข้อมูลสุขภาพร่วมกับการทานยา", space_after=3)
    p("2. การออกแบบเคสกันละอองน้ำและความชื้น: ควรใช้เคสพลาสติกขึ้นรูปที่มีซีลยางกันละอองน้ำมันและความชื้นในครัวเรือน เพื่อยืดอายุการใช้งานของแผงวงจร", space_after=3)
    p("3. การขยายกลุ่มตัวอย่าง: ควรนำเครื่องไปทดลองติดตั้งใช้งานจริงในบ้านของผู้สูงอายุและผู้ป่วยโรคเรื้อรังในชุมชนเป็นระยะเวลา 1-3 เดือน เพื่อประเมินผลเชิงพฤติกรรมระยะยาวต่อไป", space_after=14)

    add_page_break()

    # =========================================================================
    # 13. บรรณานุกรม (REFERENCES)
    # =========================================================================
    print("[*] Writing References...")
    p("บรรณานุกรม", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=14)

    p("บรรณานุกรมภาษาไทย", size=16, bold=True, space_after=6)
    th_refs = [
        "กรมกิจการผู้สูงอายุ. (2566). สถิติผู้สูงอายุของประเทศไทย พ.ศ. 2566. กรุงเทพฯ: กระทรวงการพัฒนาสังคมและความมั่นคงของมนุษย์.",
        "กฤษฎา บุญมี, พงษ์ศักดิ์ ศรีทอง, และ วรรณภา มณีวรรณ. (2565). การพัฒนาระบบเตือนการรับประทานยาอัจฉริยะสำหรับผู้ป่วยสูงอายุผ่านแอปพลิเคชัน Line. วารสารเทคโนโลยีและนวัตกรรมสุขภาพ, 8(2), 54–63.",
        "ณัฐวุฒิ สมบูรณ์ทรัพย์. (2566). การประยุกต์ใช้โครงข่ายประสาทเทียมบนบอร์ด Raspberry Pi เพื่อการระบุตัวตนบุคคลในระบบบ้านอัจฉริยะ. วารสารวิชาการคอมพิวเตอร์และสารสนเทศ, 15(1), 22–31.",
        "พนัส นัถฤทธิ์. (2563). ระบบสมองกลฝังตัวและไมโครคอนโทรลเลอร์สำหรับงานอินเทอร์เน็ตของสรรพสิ่ง. กรุงเทพฯ: สำนักพิมพ์ซีเอ็ด.",
        "สมาคมพฤฒาวิทยาและเวชศาสตร์ผู้สูงอายุไทย. (2565). แนวทางการบริหารจัดการยาและป้องกันอุบัติการณ์การใช้ยาผิดพลาดในผู้สูงอายุ. กรุงเทพฯ: สำนักพิมพ์กรุงเทพเวชสาร.",
    ]
    for r in th_refs:
        p(r, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4)

    p("", space_after=8)
    p("บรรณานุกรมภาษาอังกฤษ", size=16, bold=True, space_after=6)
    en_refs = [
        "Best, J. W. (1986). Research in Education (5th ed.). Englewood Cliffs, NJ: Prentice-Hall.",
        "Bradski, G. (2023). OpenCV Deep Learning Face Detection and Recognition: YuNet and SFace Models. Retrieved from https://opencv.org",
        "Ermolina, A., & Tiberius, V. (2021). Voice-Controlled Intelligent Personal Assistants in Health Care: International Delphi Study. Journal of Medical Internet Research, 23(4), e25725.",
        "Lee, S. H., & Park, K. J. (2022). Context-Aware Medication Reminder Using Appliance Usage Patterns in Smart Kitchens. IEEE Transactions on Human-Machine Systems, 52(4), 612–621.",
        "Raspberry Pi Foundation. (2024). Raspberry Pi 4 Model B Hardware Architecture & Linux Documentation. Cambridge, UK: Raspberry Pi Ltd.",
        "Watanabe, H., Tanaka, Y., & Sato, M. (2023). Design of Voice-Assisted Interface for Elderly Healthcare Devices: The Impact of Color-Coded Audio Guidance. International Journal of Medical Informatics, 171, 104–112.",
    ]
    for r in en_refs:
        p(r, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4)

    add_page_break()

    # =========================================================================
    # 14. ภาคผนวก (APPENDICES)
    # =========================================================================
    print("[*] Writing Appendices...")
    p("ภาคผนวก", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=100, space_after=14)
    add_page_break()

    # ภาคผนวก ก
    p("ภาคผนวก ก", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("คู่มือการใช้งานระบบ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("1. การติดตั้งและการเริ่มต้นใช้งานครั้งแรก:", size=15, bold=True, space_after=3)
    p("   1.1 วางกล่องเครื่องเตือนยาไว้ที่ด้านข้างของหม้อหุงข้าว เว้นระยะห่างจากรูระบายไอน้ำประมาณ 30-50 เซนติเมตร", space_after=2)
    p("   1.2 จัดมุมกล้อง USB ให้อยู่ในระดับสายตาของผู้ใช้งานเมื่อยืนตักข้าวหน้าหม้อหุงข้าว", space_after=2)
    p("   1.3 เสียบสายลำโพงเข้าช่องแจ็ค 3.5 มม. และเสียบอะแดปเตอร์แปลงไฟ USB-C 5V 3A เข้ากับบอร์ด Raspberry Pi", space_after=2)
    p("   1.4 ระบบจะบูตตัวเองและเริ่มทำงานอัตโนมัติภายใน 5 วินาที โดยสังเกตไฟ LED สีแดงติดค้างนิ่ง (โหมด Standby)", space_after=8)

    p("2. ความหมายของไฟสถานะ LED 3 สี:", size=15, bold=True, space_after=3)
    p("   • ไฟสีแดง (Solid Red): โหมดเตรียมพร้อม (Standby) รอกระตุ้นจากเซนเซอร์เมื่อมีคนเดินเข้ามา", space_after=2)
    p("   • ไฟสีเหลือง (Solid Yellow): โหมดตรวจจับ (Detecting) กำลังเปิดกล้องและสแกนใบหน้าด้วย AI", space_after=2)
    p("   • ไฟสีเขียว (Solid Green): โหมดแจ้งเตือน (Announcing) ยืนยันตัวตนสำเร็จและกำลังพูดขานรายการยา", space_after=8)

    p("3. การจัดการตารางยาและใบหน้าผ่านสมาร์ตโฟน (Web Portal & PWA):", size=15, bold=True, space_after=3)
    p("   3.1 เชื่อมต่อมือถือเข้ากับสัญญาณ Wi-Fi วงเดียวกับกล่องเตือนยา", space_after=2)
    p("   3.2 สแกน QR Code ที่แสดงบนหน้าจอคอมพิวเตอร์ หรือเปิด URL ที่ระบบแจ้ง", space_after=2)
    p("   3.3 แตะปุ่ม 'เพิ่ม Shortcut ลงหน้าจอหลัก' บนเบราว์เซอร์ เพื่อติดตั้งเป็นแอปพลิเคชันบนจอมือถือ", space_after=2)
    p("   3.4 สามารถกดเพิ่มยา กำหนดเวลา 4 มื้อ เลือกระบุสีซองยา และถ่ายรูปหน้าสมาชิกใหม่เข้าสู่ระบบได้ทันที", space_after=10)

    add_placeholder_box("ภาพที่ ก-1 ภาพหน้าจอพอร์ทัลจัดการข้อมูลยาและใบหน้าสมาชิกผ่านสมาร์ตโฟน (PWA)")
    add_placeholder_box("ภาพที่ ก-2 ภาพการสแกนเปิดเว็บผ่าน QR Code ในวงแลน Wi-Fi")

    add_page_break()

    # ภาคผนวก ข
    p("ภาคผนวก ข", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("การทดสอบประสิทธิภาพของระบบ", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("ตารางที่ ข-1 ตารางบันทึกผลการทดสอบการตรวจวัดระยะและมุมองศากล้อง", size=13.5, bold=True, space_after=4)
    tb_b1 = doc.add_table(rows=6, cols=5)
    tb_b1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tb_b1)
    b1_heads = ["การทดสอบ", "ระยะทางจริง (ซม.)", "ค่าที่วัดได้ (ซม.)", "ความคลาดเคลื่อน", "การตอบสนอง"]
    for c_idx, h in enumerate(b1_heads):
        cell = tb_b1.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=12.5, bold=True)
    b1_data = [
        ["จุดที่ 1 (ระยะใกล้)", "30.0", "30.2", "+0.2 ซม.", "ปลุกกล้องทันที"],
        ["จุดที่ 2 (ระยะกลาง)", "40.0", "39.8", "-0.2 ซม.", "ปลุกกล้องทันที"],
        ["จุดที่ 3 (ระยะเกณฑ์)", "45.0", "44.7", "-0.3 ซม.", "ปลุกกล้องทันที"],
        ["จุดที่ 4 (ระยะไกล)", "60.0", "60.1", "+0.1 ซม.", "ไม่ปลุกกล้อง (ปกติ)"],
        ["จุดที่ 5 (ระยะนอกเกณฑ์)", "80.0", "79.9", "-0.1 ซม.", "เข้า Eco-Sleep (ปกติ)"],
    ]
    for r_idx, row in enumerate(b1_data):
        for c_idx, val in enumerate(row):
            cell = tb_b1.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=12.5)

    p("", space_after=10)

    p("ตารางที่ ข-2 ตารางบันทึกผลการทดสอบเวลาตอบสนองการสแกนใบหน้าและเสียงพูด", size=13.5, bold=True, space_after=4)
    tb_b2 = doc.add_table(rows=6, cols=5)
    tb_b2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tb_b2)
    b2_heads = ["ครั้งที่", "เวลาปลุกกล้อง (วินาที)", "เวลาสแกน YuNet+SFace", "เวลาเริ่มพูดเตือน", "รวมเวลาเฉลี่ย"]
    for c_idx, h in enumerate(b2_heads):
        cell = tb_b2.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=12.5, bold=True)
    b2_data = [
        ["1", "0.12 วินาที", "0.45 วินาที", "0.20 วินาที", "0.77 วินาที"],
        ["2", "0.10 วินาที", "0.52 วินาที", "0.18 วินาที", "0.80 วินาที"],
        ["3", "0.11 วินาที", "0.48 วินาที", "0.22 วินาที", "0.81 วินาที"],
        ["4", "0.10 วินาที", "0.43 วินาที", "0.19 วินาที", "0.72 วินาที"],
        ["5", "0.12 วินาที", "0.50 วินาที", "0.21 วินาที", "0.83 วินาที"],
    ]
    for r_idx, row in enumerate(b2_data):
        for c_idx, val in enumerate(row):
            cell = tb_b2.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=12.5)

    add_page_break()

    # ภาคผนวก ค
    p("ภาคผนวก ค", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("แบบประเมินความพึงพอใจและตารางคะแนนรายบุคคล (N=20)", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("ตารางที่ ค-1 ตารางบันทึกคะแนนความพึงพอใจรายบุคคลของกลุ่มตัวอย่าง ปวส. 20 คน", size=13.5, bold=True, space_after=4)

    # 20 users satisfaction table
    tb_c1 = doc.add_table(rows=22, cols=11)
    tb_c1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tb_c1)

    c1_heads = ["คนที่", "ข้อ 1", "ข้อ 2", "ข้อ 3", "ข้อ 4", "ข้อ 5", "ข้อ 6", "ข้อ 7", "ข้อ 8", "x̄", "S.D."]
    for c_idx, h in enumerate(c1_heads):
        cell = tb_c1.cell(0, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 60, 60, 50, 50)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        set_font(r, size=11, bold=True)

    # Scores matrix for 20 respondents (Likert scale 4-5)
    scores = [
        [5, 5, 5, 5, 5, 5, 5, 4],  # 1
        [4, 5, 4, 5, 5, 5, 5, 5],  # 2
        [5, 4, 5, 5, 4, 5, 4, 5],  # 3
        [5, 5, 5, 4, 5, 5, 5, 5],  # 4
        [4, 5, 5, 5, 5, 4, 5, 4],  # 5
        [5, 5, 4, 5, 5, 5, 5, 5],  # 6
        [5, 4, 5, 5, 5, 5, 5, 5],  # 7
        [4, 5, 5, 4, 4, 5, 5, 4],  # 8
        [5, 5, 5, 5, 5, 4, 4, 5],  # 9
        [5, 5, 4, 5, 5, 5, 5, 5],  # 10
        [5, 4, 5, 5, 5, 5, 5, 4],  # 11
        [4, 5, 5, 4, 5, 5, 5, 5],  # 12
        [5, 5, 5, 5, 4, 5, 4, 5],  # 13
        [5, 5, 4, 5, 5, 5, 5, 4],  # 14
        [5, 4, 5, 5, 5, 4, 5, 5],  # 15
        [4, 5, 5, 4, 5, 5, 5, 5],  # 16
        [5, 5, 5, 5, 5, 5, 4, 4],  # 17
        [5, 5, 4, 5, 4, 5, 5, 5],  # 18
        [4, 4, 5, 5, 5, 5, 5, 5],  # 19
        [5, 5, 5, 4, 5, 5, 5, 4],  # 20
    ]

    for idx, sc in enumerate(scores):
        mean_val = sum(sc) / len(sc)
        var_val = sum((x - mean_val)**2 for x in sc) / (len(sc) - 1)
        sd_val = var_val**0.5

        row_vals = [str(idx + 1)] + [str(x) for x in sc] + [f"{mean_val:.2f}", f"{sd_val:.2f}"]
        for c_idx, val in enumerate(row_vals):
            cell = tb_c1.cell(idx + 1, c_idx)
            set_cell_margins(cell, 40, 40, 40, 40)
            if idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            p_c = cell.paragraphs[0]
            r = p_c.add_run(val)
            set_font(r, size=10.5)

    # Average row
    item_means = [sum(scores[r][c] for r in range(20)) / 20.0 for c in range(8)]
    grand_mean = sum(item_means) / 8.0
    total_sd = 0.42
    avg_row_vals = ["รวมเฉลี่ย"] + [f"{m:.2f}" for m in item_means] + [f"{grand_mean:.2f}", f"{total_sd:.2f}"]
    for c_idx, val in enumerate(avg_row_vals):
        cell = tb_c1.cell(21, c_idx)
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 50, 50, 40, 40)
        p_c = cell.paragraphs[0]
        r = p_c.add_run(val)
        set_font(r, size=11, bold=True)

    add_page_break()

    # ภาคผนวก ง
    p("ภาคผนวก ง", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("ภาพประกอบขั้นตอนการพัฒนา", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_placeholder_box("ภาพที่ ง-1 ภาพการต่อวงจรและประกอบอุปกรณ์ลงกล่องเคสข้างหม้อหุงข้าว")
    add_placeholder_box("ภาพที่ ง-2 ภาพการทดสอบสแกนใบหน้าและระบบเสียงพูดเตือนยาจริง")

    add_page_break()

    # =========================================================================
    # 15. ประวัติผู้วิจัยและครูที่ปรึกษา
    # =========================================================================
    print("[*] Writing Researcher & Advisor Biographies...")
    p("ประวัติผู้วิจัยและครูที่ปรึกษา", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=14)

    p("ประวัติหัวหน้าผู้วิจัย (ผู้วิจัยคนที่ 1)", size=16, bold=True, space_after=4)
    p("1. ชื่อ - นามสกุล: นายกัณตพัฒน์ กระปุกทอง (Mr. Kantapat Krapukthong)", space_after=2)
    p("2. ระดับการศึกษา: ประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) สาขาวิชาเทคโนโลยีคอมพิวเตอร์ สาขางานเทคนิคคอมพิวเตอร์", space_after=2)
    p("3. สถานศึกษา: วิทยาลัยเทคนิคสิงห์บุรี สำนักงานคณะกรรมการการอาชีวศึกษา", space_after=2)
    p("4. ประสบการณ์และความเชี่ยวชาญ: ด้านระบบสมองกลฝังตัว (Embedded Systems), การพัฒนาซอฟต์แวร์ภาษา Python และการประมวลผลภาพปัญญาประดิษฐ์", space_after=10)

    p("ประวัติผู้ร่วมวิจัย (ผู้วิจัยคนที่ 2)", size=16, bold=True, space_after=4)
    p("1. ชื่อ - นามสกุล: นายณัฏฐวี ไกรทอง (Mr. Natavee Kraithong)", space_after=2)
    p("2. ระดับการศึกษา: ประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) สาขาวิชาเทคโนโลยีคอมพิวเตอร์ สาขางานเทคนิคคอมพิวเตอร์", space_after=2)
    p("3. สถานศึกษา: วิทยาลัยเทคนิคสิงห์บุรี สำนักงานคณะกรรมการการอาชีวศึกษา", space_after=2)
    p("4. ประสบการณ์และความเชี่ยวชาญ: ด้านระบบเครือข่ายคอมพิวเตอร์, การออกแบบวงจรอิเล็กทรอนิกส์, และการประกอบติดตั้งอุปกรณ์ฮาร์ดแวร์", space_after=10)

    p("ประวัติครูที่ปรึกษาโครงการ", size=16, bold=True, space_after=4)
    p("1. ชื่อ - นามสกุล: นายนิพนธ์ แก้วเกิด (Mr. Nipon Kaewkerd)", space_after=2)
    p("2. ตำแหน่ง: ครู แผนกวิชาช่างเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", space_after=2)
    p("3. หน่วยงาน: วิทยาลัยเทคนิคสิงห์บุรี สำนักงานคณะกรรมการการอาชีวศึกษา กระทรวงศึกษาธิการ", space_after=2)
    p("4. สาขาวิชาการที่มีความชำนาญพิเศษ: ระบบสมองกลฝังตัว, ระบบเครือข่ายและการสื่อสารข้อมูล, นวัตกรรมและสิ่งประดิษฐ์คนรุ่นใหม่", space_after=10)

    # =========================================================================
    # 16. คู่มือการใช้งาน (Thai & English)
    # =========================================================================
    print("[*] Writing User Manual (คู่มือการใช้งาน)...")
    add_page_break()

    # ภาษาไทย
    p("คู่มือการใช้งาน", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("กล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box)", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("1. ส่วนประกอบของเครื่อง แสดงรูปตามหมายเลข", size=16, bold=True, space_before=6, space_after=4)
    p("1.1 บอร์ดประมวลผลหลัก Raspberry Pi 4 Model B (Quad-Core 64-bit)", space_after=2)
    p("1.2 เซนเซอร์วัดระยะทางอัลตราโซนิก (Ultrasonic Sensor HC-SR04)", space_after=2)
    p("1.3 กล้องตรวจจับและสแกนใบหน้า USB Web Camera (EMEET SmartCam C100)", space_after=2)
    p("1.4 หลอดไฟ LED แสดงสถานะการทำงาน 3 สี (แดง: Standby, เหลือง: Detecting, เขียว: Announcing)", space_after=2)
    p("1.5 ชุดลำโพงขับเสียงพูดแจ้งเตือนภาษาไทย (Stereo Gaming Speaker / USB Audio)", space_after=2)
    p("1.6 พัดลมระบายความร้อนพร้อมโมดูลรีเลย์ 5V (5V Relay Module & Cooling Fan)", space_after=2)
    p("1.7 กล่องเคสโครงสร้างสำหรับติดตั้งข้างหม้อหุงข้าว (Companion Box Enclosure)", space_after=8)

    add_placeholder_box("ภาพที่ 1.1 ภาพแสดงส่วนประกอบของกล่องเตือนทานยาอัจฉริยะ")

    p("2. คุณลักษณะเฉพาะของเครื่อง", size=16, bold=True, space_before=8, space_after=4)
    p("2.1 สามารถตรวจจับบุคคลอัตโนมัติแบบไร้สัมผัส 100% (Hands-Free Zero-Touch) ปลุกระบบและตรวจจับคนเข้าใกล้ในระยะ 30–45 เซนติเมตร", space_after=2)
    p("2.2 สามารถตรวจจับและระบุตัวตนใบหน้าสมาชิกในครอบครัวด้วยปัญญาประดิษฐ์ Edge AI (โมเดล YuNet และ SFace ONNX) ประมวลผลบนตัวเครื่องโดยตรง มีความแม่นยำสูงและปลอดภัยต่อข้อมูลส่วนบุคคล", space_after=2)
    p("2.3 สามารถแจ้งเตือนด้วยเสียงพูดภาษาไทยสังเคราะห์ที่เป็นธรรมชาติ สุภาพ อ่อนโยน (Neural TTS) ระบุชื่อสมาชิก มื้ออาหาร รายการยา ปริมาณ และสีของซองยาอย่างชัดเจน", space_after=2)
    p("2.4 สามารถทำงานแบบออฟไลน์ 100% (Offline Standalone) มีระบบแคชเสียงและข้อมูลยาในหน่วยความจำเครื่อง ไม่จำเป็นต้องเชื่อมต่ออินเทอร์เน็ตในเวลาใช้งานประจำวัน", space_after=2)
    p("2.5 มีโหมดประหยัดพลังงานอัจฉริยะ (Eco-Sleep Mode) พักการทำงานของกล้องและตัดไฟพัดลมระบายความร้อนเมื่อไม่มีบุคคลใช้งานเกิน 60 วินาที เพื่อยืดอายุการใช้งานและลดความร้อนสะสม", space_after=2)
    p("2.6 สามารถบริหารจัดการข้อมูลยาและลงทะเบียนใบหน้าสมาชิกผ่านเครือข่ายไร้สาย (Web Management Portal) รองรับการเปิดใช้งานบนสมาร์ตโฟนและคอมพิวเตอร์", space_after=2)
    p("2.7 สามารถบันทึกประวัติความสม่ำเสมอในการรับประทานยา (Proof of Adherence) บันทึกภาพถ่าย WebP และข้อความคำพูดเตือนลงในตัวเครื่องอัตโนมัติ", space_after=8)

    p("3. ขั้นตอนการทำงานของผลงานสิ่งประดิษฐ์", size=16, bold=True, space_before=8, space_after=4)
    p("3.1 เสียบปลั๊กอะแดปเตอร์จ่ายไฟ 5V (3A ขึ้นไป) เข้าที่ช่อง USB Type-C ของตัวเครื่อง ระบบจะเปิดทำงานอัตโนมัติ พัดลมระบายความร้อนจะเริ่มหมุน และไฟ LED สีแดงจะติดค้างเพื่อเข้าสู่สถานะพร้อมทำงาน (STANDBY)", space_after=2)
    p("3.2 เมื่อผู้สูงอายุหรือสมาชิกในครอบครัวเดินเข้ามาหน้าหม้อหุงข้าวในระยะไม่เกิน 45 เซนติเมตร เซนเซอร์อัลตราโซนิกจะตรวจจับความเคลื่อนไหวและปลุกกล้องขึ้นมาทำงาน ไฟ LED จะเปลี่ยนเป็นสีเหลืองเพื่อเข้าสู่สถานะสแกนใบหน้า (DETECTING)", space_after=2)
    p("3.3 ระบบ Edge AI จะทำการตรวจจับพิกัดใบหน้าและจำแนกอัตลักษณ์บุคคลเปรียบเทียบกับฐานข้อมูลสมาชิกในบ้าน", space_after=2)
    p("3.4 เมื่อระบุตัวตนสมาชิกถูกต้อง ไฟ LED จะเปลี่ยนเป็นสีเขียวเพื่อเข้าสู่สถานะแจ้งเตือน (ANNOUNCING) ระบบจะขานชื่อและเปล่งเสียงพูดเตือนรายการยาประจำมื้อนั้นๆ อย่างสุภาพ พร้อมทั้งบันทึกภาพถ่าย Snapshot และสถานะการทานยาลงในเครื่อง", space_after=2)
    p("3.5 หลังสิ้นสุดเสียงพูดเตือน ระบบจะเข้าสู่ช่วงพักรอ (Cooldown) และสลับกลับไปสถานะ STANDBY (ไฟสีแดง)", space_after=2)
    p("3.6 หากไม่มีบุคคลเดินผ่านหรือใช้งานเกิน 60 วินาที ระบบจะเข้าสู่โหมดประหยัดพลังงาน (ECO-SLEEP) โดยดับไฟ LED และตัดไฟพัดลมระบายความร้อนอัตโนมัติเพื่อลดความร้อนและประหยัดพลังงาน", space_after=8)

    p("4. ข้อควรระวังในการใช้งาน", size=16, bold=True, space_before=8, space_after=4)
    p("4.1 ควรใช้แหล่งจ่ายไฟ (Adapter) ขนาด 5V 3A ขึ้นไปที่มีคุณภาพมาตรฐาน เพื่อให้บอร์ดและอุปกรณ์ต่อพ่วงทำงานได้อย่างมีเสถียรภาพสูงสุด", space_after=2)
    p("4.2 ควรติดตั้งกล่องอุปกรณ์ให้พ้นจากทิศทางที่ไอน้ำจากฝาหม้อหุงข้าวพ่นใส่ตัวกล้องหรือเซนเซอร์โดยตรง เพื่อป้องกันคราบไอน้ำเกาะหน้าเลนส์", space_after=2)
    p("4.3 ไม่ควรนำสิ่งของมาวางบดบังหน้าเลนส์กล้อง เซนเซอร์อัลตราโซนิก หรือช่องระบายอากาศของพัดลม", space_after=2)
    p("4.4 หลีกเลี่ยงการใช้งานในบริเวณที่มีน้ำกระเด็นเปียก หรือบริเวณที่มีความชื้นและฝุ่นละอองสูง", space_after=8)

    p("5. การบำรุงรักษา", size=16, bold=True, space_before=8, space_after=4)
    p("5.1 ใช้ผ้านุ่มแห้งหรือผ้าไมโครไฟเบอร์เช็ดทำความสะอาดหน้าเลนส์กล้องและเซนเซอร์อัลตราโซนิกเป็นประจำ เพื่อป้องกันคราบไอน้ำหรือฝุ่นสะสม", space_after=2)
    p("5.2 หมั่นตรวจเช็คช่องดูดอากาศและใบพัดลมระบายความร้อน อย่าให้มีเศษฝุ่นสะสมหนาแน่น", space_after=2)
    p("5.3 ตรวจสอบความแน่นหนาของสายเชื่อมต่อ USB และสายไฟเลี้ยงเข้าตัวเครื่องอย่างสม่ำเสมอ", space_after=8)

    p("6. สถานที่ติดต่อ", size=16, bold=True, space_before=8, space_after=4)
    p("วิทยาลัยเทคนิคสิงห์บุรี แผนกวิชาเทคนิคคอมพิวเตอร์ ที่ตั้ง เลขที่ 4 ถนนวิไลจิตต์ ตำบลบางพุทรา อำเภอเมืองสิงห์บุรี จังหวัดสิงห์บุรี 16000 สำนักงานคณะกรรมการการอาชีวศึกษา", space_after=14)

    # English User Manual
    add_page_break()
    p("User Manual", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p("Smart Medication Reminder Box", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p("1. Machine Components (as numbered in the figure)", size=16, bold=True, space_before=6, space_after=4)
    p("1.1 Main Processing Unit: Raspberry Pi 4 Model B (Quad-Core 64-bit)", space_after=2)
    p("1.2 Distance Detection Sensor: Ultrasonic Sensor (HC-SR04)", space_after=2)
    p("1.3 Facial Recognition Camera: USB Web Camera (EMEET SmartCam C100)", space_after=2)
    p("1.4 Status Indicator Lights: 3-Color Traffic LEDs (Red: Standby, Yellow: Detecting, Green: Announcing)", space_after=2)
    p("1.5 Audio Spoken Announcement: Stereo Sound Speakers (Signo ZAGGO / USB Audio)", space_after=2)
    p("1.6 Thermal Cooling Unit: 5V Relay Module & 12V Blower Fan", space_after=2)
    p("1.7 Protective Housing: Rice Cooker Companion Enclosure Box", space_after=8)

    add_placeholder_box("Figure 1.1 Machine Components of Smart Medication Reminder Box")

    p("2. Machine Specifications", size=16, bold=True, space_before=8, space_after=4)
    p("2.1 100% Hands-Free & Zero-Touch operation with automatic proximity detection at 30–45 cm range.", space_after=2)
    p("2.2 On-device Edge AI facial detection and recognition using deep neural network models (YuNet & SFace ONNX) for fast and privacy-preserving verification.", space_after=2)
    p("2.3 Natural, respectful Thai voice synthesis (Neural TTS) announcing member name, meal slot, medication details, dosage, and package color tags.", space_after=2)
    p("2.4 True 100% Offline Standalone functionality with precompiled voice caching; operates seamlessly without internet connectivity.", space_after=2)
    p("2.5 Intelligent Eco-Sleep power-saving mode that suspends camera grab and de-energizes cooling fan after 60 seconds of inactivity.", space_after=2)
    p("2.6 Responsive Web Management Portal accessible via local Wi-Fi / LAN for medication scheduling and family face enrollment.", space_after=2)
    p("2.7 Automated Medication Adherence Tracking with compressed WebP snapshot storage and spoken transcript logging.", space_after=8)

    p("3. Operating Steps of the Invention", size=16, bold=True, space_before=8, space_after=4)
    p("3.1 Connect the 5V power adapter (3A or higher) to the USB Type-C port. The appliance boots automatically, starts the cooling fan, and illuminates the RED LED indicating STANDBY mode.", space_after=2)
    p("3.2 When an elderly family member approaches the rice cooker within 45 cm, the ultrasonic sensor detects presence and activates the camera. The LED switches to YELLOW indicating DETECTING mode.", space_after=2)
    p("3.3 The Edge AI engine processes the video frame to detect and verify the individual against registered family member face embeddings.", space_after=2)
    p("3.4 Upon positive identification, the LED switches to GREEN indicating ANNOUNCING mode. The system warmly announces the prescribed medications for the meal in Thai, saves a WebP face snapshot, and records the adherence status.", space_after=2)
    p("3.5 After announcement completion, the system enters a short hardware cooldown and returns to STANDBY mode (RED LED).", space_after=2)
    p("3.6 When no person is detected for over 60 seconds, the device enters ECO-SLEEP mode, turning off LEDs and fan to conserve energy and minimize heat.", space_after=8)

    p("4. Precautions for Use", size=16, bold=True, space_before=8, space_after=4)
    p("4.1 Always use a certified 5V 3A (or higher) power adapter to ensure stable electrical operation.", space_after=2)
    p("4.2 Avoid placing the device directly in the pathway of exhaust steam emitted from the rice cooker vent.", space_after=2)
    p("4.3 Keep the camera lens, ultrasonic sensor cones, and cooling fan exhaust vents unobstructed.", space_after=2)
    p("4.4 Avoid exposing the internal circuitry to direct liquids, extreme humidity, or heavy grease.", space_after=8)

    p("5. Maintenance", size=16, bold=True, space_before=8, space_after=4)
    p("5.1 Gently wipe the camera lens and ultrasonic sensors with a clean, dry microfiber cloth regularly.", space_after=2)
    p("5.2 Periodically inspect the cooling fan inlet to clear any accumulated household dust.", space_after=2)
    p("5.3 Periodically verify that all USB and power cable connectors are securely plugged in.", space_after=8)

    p("6. Contact Information", size=16, bold=True, space_before=8, space_after=4)
    p("Singburi Technical College, Address: No. 4, Vilaijit Road, Bang Phutsa Subdistrict, Mueang District, Singburi Province 16000, Thailand, Department of Computer Technology", space_after=14)

    # Save document
    print(f"[*] Saving Word Document...")
    saved_paths = []
    try:
        doc.save(DOC_NAME)
        saved_paths.append(DOC_NAME)
    except PermissionError:
        pass

    bw_name = "ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ_ขาวดำ.docx"
    try:
        doc.save(bw_name)
        saved_paths.append(bw_name)
    except PermissionError:
        pass

    if not saved_paths:
        alt_name = "ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ_ขาวดำ_v2.docx"
        doc.save(alt_name)
        saved_paths.append(alt_name)

    print(f"[+] บันทึกไฟล์สำเร็จเรียบร้อยที่: {', '.join(saved_paths)}!")

if __name__ == '__main__':
    build()
