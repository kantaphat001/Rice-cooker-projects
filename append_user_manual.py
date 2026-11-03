# -*- coding: utf-8 -*-
"""
append_user_manual.py
Appends "คู่มือการใช้งาน" (Thai) and "User Manual" (English) to the research report:
- ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ.docx
- ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ_ขาวดำ.docx
Without modifying or altering any other part of the document.
"""

import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# Set console output to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=260, bottom=260, left=200, right=200):
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


def add_placeholder_box(doc, caption_text, subtext="คลิกขวาเพื่อแทรกรูปภาพอุปกรณ์จริง"):
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
    r1.font.name = "TH Sarabun New"
    r1.font.size = Pt(14)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(71, 85, 105)

    p2 = cell.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(f"({subtext})")
    r2.font.name = "TH Sarabun New"
    r2.font.size = Pt(12)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(148, 163, 184)

    # Caption paragraph below box
    cap_p = doc.add_paragraph()
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_r = cap_p.add_run(caption_text)
    cap_r.font.name = "TH Sarabun New"
    cap_r.font.size = Pt(13)
    cap_r.font.bold = True
    cap_r.font.color.rgb = RGBColor(71, 85, 105)
    cap_p.paragraph_format.space_before = Pt(4)
    cap_p.paragraph_format.space_after = Pt(12)


def set_run_font(run, size=15, bold=False, italic=False, color_rgb=(30, 41, 59), font_name="TH Sarabun New"):
    run.font.name = font_name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)


def add_p(doc, text="", size=15, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.15):
    par = doc.add_paragraph()
    par.alignment = align
    par.paragraph_format.space_before = Pt(space_before)
    par.paragraph_format.space_after = Pt(space_after)
    par.paragraph_format.line_spacing = line_spacing
    if text:
        r = par.add_run(text)
        set_run_font(r, size=size, bold=bold, italic=italic)
    return par


def add_manual_sections(doc):
    # Page Break before Manual
    doc.add_page_break()

    # =========================================================================
    # คู่มือการใช้งาน (ภาษาไทย)
    # =========================================================================
    add_p(doc, "คู่มือการใช้งาน", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    add_p(doc, "กล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box)", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    # 1. ส่วนประกอบของเครื่อง
    add_p(doc, "1. ส่วนประกอบของเครื่อง แสดงรูปตามหมายเลข", size=16, bold=True, space_before=6, space_after=4)
    add_p(doc, "1.1 บอร์ดประมวลผลหลัก Raspberry Pi 4 Model B (Quad-Core 64-bit)", space_after=2)
    add_p(doc, "1.2 เซนเซอร์วัดระยะทางอัลตราโซนิก (Ultrasonic Sensor HC-SR04)", space_after=2)
    add_p(doc, "1.3 กล้องตรวจจับและสแกนใบหน้า USB Web Camera (EMEET SmartCam C100)", space_after=2)
    add_p(doc, "1.4 หลอดไฟ LED แสดงสถานะการทำงาน 3 สี (แดง: Standby, เหลือง: Detecting, เขียว: Announcing)", space_after=2)
    add_p(doc, "1.5 ชุดลำโพงขับเสียงพูดแจ้งเตือนภาษาไทย (Stereo Gaming Speaker / USB Audio)", space_after=2)
    add_p(doc, "1.6 พัดลมระบายความร้อนพร้อมโมดูลรีเลย์ 5V (5V Relay Module & Cooling Fan)", space_after=2)
    add_p(doc, "1.7 กล่องเคสโครงสร้างสำหรับติดตั้งข้างหม้อหุงข้าว (Companion Box Enclosure)", space_after=8)

    add_placeholder_box(doc, "ภาพที่ 1.1 ภาพแสดงส่วนประกอบของกล่องเตือนทานยาอัจฉริยะ")

    # 2. คุณลักษณะเฉพาะของเครื่อง
    add_p(doc, "2. คุณลักษณะเฉพาะของเครื่อง", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "2.1 สามารถตรวจจับบุคคลอัตโนมัติแบบไร้สัมผัส 100% (Hands-Free Zero-Touch) ปลุกระบบและตรวจจับคนเข้าใกล้ในระยะ 30–45 เซนติเมตร", space_after=2)
    add_p(doc, "2.2 สามารถตรวจจับและระบุตัวตนใบหน้าสมาชิกในครอบครัวด้วยปัญญาประดิษฐ์ Edge AI (โมเดล YuNet และ SFace ONNX) ประมวลผลบนตัวเครื่องโดยตรง มีความแม่นยำสูงและปลอดภัยต่อข้อมูลส่วนบุคคล", space_after=2)
    add_p(doc, "2.3 สามารถแจ้งเตือนด้วยเสียงพูดภาษาไทยสังเคราะห์ที่เป็นธรรมชาติ สุภาพ อ่อนโยน (Neural TTS) ระบุชื่อสมาชิก มื้ออาหาร รายการยา ปริมาณ และสีของซองยาอย่างชัดเจน", space_after=2)
    add_p(doc, "2.4 สามารถทำงานแบบออฟไลน์ 100% (Offline Standalone) มีระบบแคชเสียงและข้อมูลยาในหน่วยความจำเครื่อง ไม่จำเป็นต้องเชื่อมต่ออินเทอร์เน็ตในเวลาใช้งานประจำวัน", space_after=2)
    add_p(doc, "2.5 มีโหมดประหยัดพลังงานอัจฉริยะ (Eco-Sleep Mode) พักการทำงานของกล้องและตัดไฟพัดลมระบายความร้อนเมื่อไม่มีบุคคลใช้งานเกิน 60 วินาที เพื่อยืดอายุการใช้งานและลดความร้อนสะสม", space_after=2)
    add_p(doc, "2.6 สามารถบริหารจัดการข้อมูลยาและลงทะเบียนใบหน้าสมาชิกผ่านเครือข่ายไร้สาย (Web Management Portal) รองรับการเปิดใช้งานบนสมาร์ตโฟนและคอมพิวเตอร์", space_after=2)
    add_p(doc, "2.7 สามารถบันทึกประวัติความสม่ำเสมอในการรับประทานยา (Proof of Adherence) บันทึกภาพถ่าย WebP และข้อความคำพูดเตือนลงในตัวเครื่องอัตโนมัติ", space_after=8)

    # 3. ขั้นตอนการทำงานของผลงานสิ่งประดิษฐ์
    add_p(doc, "3. ขั้นตอนการทำงานของผลงานสิ่งประดิษฐ์", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "3.1 เสียบปลั๊กอะแดปเตอร์จ่ายไฟ 5V (3A ขึ้นไป) เข้าที่ช่อง USB Type-C ของตัวเครื่อง ระบบจะเปิดทำงานอัตโนมัติ พัดลมระบายความร้อนจะเริ่มหมุน และไฟ LED สีแดงจะติดค้างเพื่อเข้าสู่สถานะพร้อมทำงาน (STANDBY)", space_after=2)
    add_p(doc, "3.2 เมื่อผู้สูงอายุหรือสมาชิกในครอบครัวเดินเข้ามาหน้าหม้อหุงข้าวในระยะไม่เกิน 45 เซนติเมตร เซนเซอร์อัลตราโซนิกจะตรวจจับความเคลื่อนไหวและปลุกกล้องขึ้นมาทำงาน ไฟ LED จะเปลี่ยนเป็นสีเหลืองเพื่อเข้าสู่สถานะสแกนใบหน้า (DETECTING)", space_after=2)
    add_p(doc, "3.3 ระบบ Edge AI จะทำการตรวจจับพิกัดใบหน้าและจำแนกอัตลักษณ์บุคคลเปรียบเทียบกับฐานข้อมูลสมาชิกในบ้าน", space_after=2)
    add_p(doc, "3.4 เมื่อระบุตัวตนสมาชิกถูกต้อง ไฟ LED จะเปลี่ยนเป็นสีเขียวเพื่อเข้าสู่สถานะแจ้งเตือน (ANNOUNCING) ระบบจะขานชื่อและเปล่งเสียงพูดเตือนรายการยาประจำมื้อนั้นๆ อย่างสุภาพ พร้อมทั้งบันทึกภาพถ่าย Snapshot และสถานะการทานยาลงในเครื่อง", space_after=2)
    add_p(doc, "3.5 หลังสิ้นสุดเสียงพูดเตือน ระบบจะเข้าสู่ช่วงพักรอ (Cooldown) และสลับกลับไปสถานะ STANDBY (ไฟสีแดง)", space_after=2)
    add_p(doc, "3.6 หากไม่มีบุคคลเดินผ่านหรือใช้งานเกิน 60 วินาที ระบบจะเข้าสู่โหมดประหยัดพลังงาน (ECO-SLEEP) โดยดับไฟ LED และตัดไฟพัดลมระบายความร้อนอัตโนมัติเพื่อลดความร้อนและประหยัดพลังงาน", space_after=8)

    # 4. ข้อควรระวังในการใช้งาน
    add_p(doc, "4. ข้อควรระวังในการใช้งาน", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "4.1 ควรใช้แหล่งจ่ายไฟ (Adapter) ขนาด 5V 3A ขึ้นไปที่มีคุณภาพมาตรฐาน เพื่อให้บอร์ดและอุปกรณ์ต่อพ่วงทำงานได้อย่างมีเสถียรภาพสูงสุด", space_after=2)
    add_p(doc, "4.2 ควรติดตั้งกล่องอุปกรณ์ให้พ้นจากทิศทางที่ไอน้ำจากฝาหม้อหุงข้าวพ่นใส่ตัวกล้องหรือเซนเซอร์โดยตรง เพื่อป้องกันคราบไอน้ำเกาะหน้าเลนส์", space_after=2)
    add_p(doc, "4.3 ไม่ควรนำสิ่งของมาวางบดบังหน้าเลนส์กล้อง เซนเซอร์อัลตราโซนิก หรือช่องระบายอากาศของพัดลม", space_after=2)
    add_p(doc, "4.4 หลีกเลี่ยงการใช้งานในบริเวณที่มีน้ำกระเด็นเปียก หรือบริเวณที่มีความชื้นและฝุ่นละอองสูง", space_after=8)

    # 5. การบำรุงรักษา
    add_p(doc, "5. การบำรุงรักษา", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "5.1 ใช้ผ้านุ่มแห้งหรือผ้าไมโครไฟเบอร์เช็ดทำความสะอาดหน้าเลนส์กล้องและเซนเซอร์อัลตราโซนิกเป็นประจำ เพื่อป้องกันคราบไอน้ำหรือฝุ่นสะสม", space_after=2)
    add_p(doc, "5.2 หมั่นตรวจเช็คช่องดูดอากาศและใบพัดลมระบายความร้อน อย่าให้มีเศษฝุ่นสะสมหนาแน่น", space_after=2)
    add_p(doc, "5.3 ตรวจสอบความแน่นหนาของสายเชื่อมต่อ USB และสายไฟเลี้ยงเข้าตัวเครื่องอย่างสม่ำเสมอ", space_after=8)

    # 6. สถานที่ติดต่อ
    add_p(doc, "6. สถานที่ติดต่อ", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "วิทยาลัยเทคนิคสิงห์บุรี แผนกวิชาเทคนิคคอมพิวเตอร์ ที่ตั้ง เลขที่ 4 ถนนวิไลจิตต์ ตำบลบางพุทรา อำเภอเมืองสิงห์บุรี จังหวัดสิงห์บุรี 16000 สำนักงานคณะกรรมการการอาชีวศึกษา", space_after=14)

    # Page Break before English User Manual
    doc.add_page_break()

    # =========================================================================
    # User Manual (English)
    # =========================================================================
    add_p(doc, "User Manual", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    add_p(doc, "Smart Medication Reminder Box", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    # 1. Machine Components
    add_p(doc, "1. Machine Components (as numbered in the figure)", size=16, bold=True, space_before=6, space_after=4)
    add_p(doc, "1.1 Main Processing Unit: Raspberry Pi 4 Model B (Quad-Core 64-bit)", space_after=2)
    add_p(doc, "1.2 Distance Detection Sensor: Ultrasonic Sensor (HC-SR04)", space_after=2)
    add_p(doc, "1.3 Facial Recognition Camera: USB Web Camera (EMEET SmartCam C100)", space_after=2)
    add_p(doc, "1.4 Status Indicator Lights: 3-Color Traffic LEDs (Red: Standby, Yellow: Detecting, Green: Announcing)", space_after=2)
    add_p(doc, "1.5 Audio Spoken Announcement: Stereo Sound Speakers (Signo ZAGGO / USB Audio)", space_after=2)
    add_p(doc, "1.6 Thermal Cooling Unit: 5V Relay Module & 12V Blower Fan", space_after=2)
    add_p(doc, "1.7 Protective Housing: Rice Cooker Companion Enclosure Box", space_after=8)

    add_placeholder_box(doc, "Figure 1.1 Machine Components of Smart Medication Reminder Box")

    # 2. Machine Specifications
    add_p(doc, "2. Machine Specifications", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "2.1 100% Hands-Free & Zero-Touch operation with automatic proximity detection at 30–45 cm range.", space_after=2)
    add_p(doc, "2.2 On-device Edge AI facial detection and recognition using deep neural network models (YuNet & SFace ONNX) for fast and privacy-preserving verification.", space_after=2)
    add_p(doc, "2.3 Natural, respectful Thai voice synthesis (Neural TTS) announcing member name, meal slot, medication details, dosage, and package color tags.", space_after=2)
    add_p(doc, "2.4 True 100% Offline Standalone functionality with precompiled voice caching; operates seamlessly without internet connectivity.", space_after=2)
    add_p(doc, "2.5 Intelligent Eco-Sleep power-saving mode that suspends camera grab and de-energizes cooling fan after 60 seconds of inactivity.", space_after=2)
    add_p(doc, "2.6 Responsive Web Management Portal accessible via local Wi-Fi / LAN for medication scheduling and family face enrollment.", space_after=2)
    add_p(doc, "2.7 Automated Medication Adherence Tracking with compressed WebP snapshot storage and spoken transcript logging.", space_after=8)

    # 3. Operating Steps of the Invention
    add_p(doc, "3. Operating Steps of the Invention", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "3.1 Connect the 5V power adapter (3A or higher) to the USB Type-C port. The appliance boots automatically, starts the cooling fan, and illuminates the RED LED indicating STANDBY mode.", space_after=2)
    add_p(doc, "3.2 When an elderly family member approaches the rice cooker within 45 cm, the ultrasonic sensor detects presence and activates the camera. The LED switches to YELLOW indicating DETECTING mode.", space_after=2)
    add_p(doc, "3.3 The Edge AI engine processes the video frame to detect and verify the individual against registered family member face embeddings.", space_after=2)
    add_p(doc, "3.4 Upon positive identification, the LED switches to GREEN indicating ANNOUNCING mode. The system warmly announces the prescribed medications for the meal in Thai, saves a WebP face snapshot, and records the adherence status.", space_after=2)
    add_p(doc, "3.5 After announcement completion, the system enters a short hardware cooldown and returns to STANDBY mode (RED LED).", space_after=2)
    add_p(doc, "3.6 When no person is detected for over 60 seconds, the device enters ECO-SLEEP mode, turning off LEDs and fan to conserve energy and minimize heat.", space_after=8)

    # 4. Precautions for Use
    add_p(doc, "4. Precautions for Use", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "4.1 Always use a certified 5V 3A (or higher) power adapter to ensure stable electrical operation.", space_after=2)
    add_p(doc, "4.2 Avoid placing the device directly in the pathway of exhaust steam emitted from the rice cooker vent.", space_after=2)
    add_p(doc, "4.3 Keep the camera lens, ultrasonic sensor cones, and cooling fan exhaust vents unobstructed.", space_after=2)
    add_p(doc, "4.4 Avoid exposing the internal circuitry to direct liquids, extreme humidity, or heavy grease.", space_after=8)

    # 5. Maintenance
    add_p(doc, "5. Maintenance", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "5.1 Gently wipe the camera lens and ultrasonic sensors with a clean, dry microfiber cloth regularly.", space_after=2)
    add_p(doc, "5.2 Periodically inspect the cooling fan inlet to clear any accumulated household dust.", space_after=2)
    add_p(doc, "5.3 Periodically verify that all USB and power cable connectors are securely plugged in.", space_after=8)

    # 6. Contact Information
    add_p(doc, "6. Contact Information", size=16, bold=True, space_before=8, space_after=4)
    add_p(doc, "Singburi Technical College, Address: No. 4, Vilaijit Road, Bang Phutsa Subdistrict, Mueang District, Singburi Province 16000, Thailand, Department of Computer Technology", space_after=14)


def process_file(filepath):
    print(f"[*] Processing: {filepath}...")
    doc = docx.Document(filepath)

    # Check if already added
    full_text = "\n".join(p.text for p in doc.paragraphs)
    if "คู่มือการใช้งาน" in full_text and "User Manual" in full_text:
        print(f"[-] Already contains manual sections. Skipping.")
        return

    add_manual_sections(doc)
    doc.save(filepath)
    print(f"[+] Successfully appended 'คู่มือการใช้งาน' and 'User Manual' to {filepath}!")


if __name__ == '__main__':
    targets = [
        "ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ.docx",
        "ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ_ขาวดำ.docx"
    ]
    for target in targets:
        process_file(target)
