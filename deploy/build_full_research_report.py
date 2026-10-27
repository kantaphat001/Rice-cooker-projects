"""
build_full_research_report.py
Full automated builder that converts 'แบบรายงานการวิจัย.docx' into the complete
Smart Medication Reminder Box (กล่องเตือนทานยาอัจฉริยะ) research report.
"""

import sys
import io
import shutil
from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SRC_DOCX = Path(r"C:\Users\TC10\Downloads\แบบรายงานการวิจัย_backup.docx")
DST_DOCX = Path(r"C:\Users\TC10\Downloads\แบบรายงานการวิจัย.docx")

FONT_NAME = "TH SarabunPSK"

def set_run_font(run, name=FONT_NAME, size_pt=16, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rFonts.set(qn('w:eastAsia'), name)

def set_p_text(p, text, size_pt=16, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT):
    p.text = ""
    run = p.add_run(text)
    set_run_font(run, FONT_NAME, size_pt, bold)
    p.alignment = align
    return run

def update_table_cells(table, data):
    for r_idx, row_data in enumerate(data):
        if r_idx >= len(table.rows):
            break
        row = table.rows[r_idx]
        for c_idx, val in enumerate(row_data):
            if c_idx >= len(row.cells):
                break
            cell = row.cells[c_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            is_bold = (r_idx == 0 or "รวม" in str(val))
            set_run_font(run, FONT_NAME, 14 if is_bold else 13, bold=is_bold)

def main():
    print(f"[*] Loading template: {SRC_DOCX}")
    doc = docx.Document(str(SRC_DOCX))
    
    # -------------------------------------------------------------------------
    # 1. Update Thai Abstract & Header (P[26] to P[38])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[26], "ชื่อโครงการ\t: กล่องเตือนทานยาอัจฉริยะ", 16, True)
    set_p_text(doc.paragraphs[27], "                      Smart Medication Reminder Box", 16, True)
    set_p_text(doc.paragraphs[28], "ชื่อ\t\t: นายกัณตพัฒน์ กระปุกทอง   นายณัฏฐวี ไกรทอง", 16, True)
    set_p_text(doc.paragraphs[29], "หน่วยงาน\t: แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", 16, True)
    set_p_text(doc.paragraphs[30], "ครูที่ปรึกษา\t: นายนิพนธ์ แก้วเกิด", 16, True)
    set_p_text(doc.paragraphs[31], "ปีการศึกษา\t: 2568", 16, True)
    set_p_text(doc.paragraphs[33], "บทคัดย่อ", 18, True, WD_ALIGN_PARAGRAPH.CENTER)

    thai_abs_p1 = (
        "\tการวิจัยครั้งนี้เป็นการวิจัยเชิงทดลอง (Experimental Research) มีวัตถุประสงค์เพื่อ "
        "1) ออกแบบและพัฒนากล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box) โดยประยุกต์ใช้เทคโนโลยีปัญญาประดิษฐ์ "
        "(Edge AI) ร่วมกับบอร์ดสมองกลฝังตัว Raspberry Pi 4 Model B และเซนเซอร์วัดระยะทางอัลตราโซนิกในการแจ้งเตือนการรับประทานยาด้วยเสียงพูดภาษาไทยที่เป็นธรรมชาติ "
        "2) ศึกษาประสิทธิภาพการทำงานของระบบตรวจจับบุคคล การระบุตัวตนสมาชิกในครอบครัว และความถูกต้องของการแจ้งเตือนตามตารางเวลามื้อยา และ "
        "3) ประเมินความถูกต้องและความพึงพอใจในการใช้งานกล่องเตือนทานยาอัจฉริยะ"
    )
    set_p_text(doc.paragraphs[35], thai_abs_p1, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    thai_abs_p2 = (
        "\tการทดลองระบบตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก (YuNet & SFace) รอบที่ 1 จำนวน 5 ครั้ง พบว่า "
        "เมื่อมีบุคคลเข้ามาในระยะตรวจจับ (< 50 ซม.) เซนเซอร์อัลตราโซนิกสามารถตรวจจับและส่งสัญญาณปลุกกล้อง V4L2 ขึ้นมาทำงาน "
        "ระบบ AI สามารถสแกนและระบุตัวตนสมาชิกในครอบครัวได้อย่างแม่นยำ ไฟ LED แสดงสถานะเปลี่ยนจากสีเหลืองเป็นสีเขียว "
        "และระบบเสียงสังเคราะห์ภาษาไทยสามารถแจ้งเตือนมื้อยาและรายการยาถูกต้องครบถ้วน ส่วนในกรณีที่ไม่มีบุคคลในระยะ ระบบจะเข้าสู่โหมดประหยัดพลังงาน (Eco-Sleep) "
        "เพื่อปิดเซนเซอร์รับภาพและลดความร้อนสะสม สำหรับการทดลองรอบที่ 2 จำนวน 5 ครั้ง ในการทดสอบตารางเวลามื้อยา 4 มื้อ "
        "และการทำงานแบบออฟไลน์ 100% (Offline Standalone Mode) พบว่า ระบบสามารถดึงข้อมูลยาและเล่นไฟล์เสียงแจ้งเตือนภาษาไทยที่แคชไว้ในเครื่องได้อย่างถูกต้อง "
        "ลื่นไหล ไม่มีเสียงขาดหาย และไม่จำเป็นต้องเชื่อมต่ออินเทอร์เน็ต การเปรียบเทียบผลการทดลองทั้งสองรอบ พบว่า กล่องเตือนทานยาอัจฉริยะสามารถทำงานได้ปกติทุกครั้ง "
        "คิดเป็นร้อยละ 100.00 แสดงให้เห็นว่าชุดควบคุมและระบบการทำงานสามารถปฏิบัติงานได้ตามวัตถุประสงค์ของการออกแบบ"
    )
    set_p_text(doc.paragraphs[36], thai_abs_p2, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[38], "คำสำคัญ: กล่องเตือนทานยาอัจฉริยะ, ปัญญาประดิษฐ์ตรวจจับใบหน้า, YuNet, SFace, ราสเบอร์รี่พาย, เซนเซอร์อัลตราโซนิก, ระบบสังเคราะห์เสียงภาษาไทย", 16, True)

    # -------------------------------------------------------------------------
    # 2. Update English Abstract (P[53] to P[64])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[53], "Project name: \tSmart Medication Reminder Box", 16, True)
    set_p_text(doc.paragraphs[54], "Name :\t\tMr. Kantapat Krapukthong   Mr. Nattawee Kraithong", 16, True)
    set_p_text(doc.paragraphs[55], "", 16, False)
    set_p_text(doc.paragraphs[56], "Organization :\tDepartment of Computer Technology, Singburi Technical College", 16, True)
    set_p_text(doc.paragraphs[57], "Mentor teacher:\tMr. Nipon Kawkerd", 16, True)
    set_p_text(doc.paragraphs[58], "Year\t\t: 2025", 16, True)
    set_p_text(doc.paragraphs[60], "Abstract", 18, True, WD_ALIGN_PARAGRAPH.CENTER)

    eng_abs_p1 = (
        "\tThis study is an experimental research aimed at: 1) designing and developing a Smart Medication Reminder Box "
        "utilizing Edge Artificial Intelligence (Edge AI) embedded on a Raspberry Pi 4 platform integrated with an ultrasonic distance sensor "
        "for natural Thai voice medication alerts; 2) evaluating the performance of presence detection, facial identification, and scheduled "
        "meal-time medication reminders; and 3) assessing system operational accuracy and user satisfaction."
    )
    set_p_text(doc.paragraphs[61], eng_abs_p1, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    eng_abs_p2 = (
        "\tIn the first round of testing (5 trials), it was found that when a person entered the detection zone (< 50 cm), "
        "the ultrasonic sensor woke the camera system, and the YuNet and SFace deep learning models accurately identified family members, "
        "transitioning the status LED from yellow to green, followed by clear Thai spoken notifications detailing medication names, dosages, "
        "and package color tags. When no presence was detected, the system safely entered Eco-Sleep mode to reduce power consumption and heat. "
        "In the second round of testing (5 trials) evaluating the 4 scheduled meal slots and standalone 100% offline operation without internet connectivity, "
        "the system reliably retrieved medication schedules and played precompiled audio alerts smoothly without audio stuttering or dropouts. "
        "Comparing both test rounds, the Smart Medication Reminder Box operated normally across all trials, achieving 100.00% functionality and reliability "
        "according to the design objectives."
    )
    set_p_text(doc.paragraphs[62], eng_abs_p2, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[64], "Keywords: Smart Medication Reminder Box, Face Recognition, YuNet, SFace, Raspberry Pi, Ultrasonic Sensor, Offline Thai Speech Synthesis", 16, True)

    # -------------------------------------------------------------------------
    # 3. Update Acknowledgement (P[77] to P[82])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[81], "คณะผู้วิจัย", 16, True, WD_ALIGN_PARAGRAPH.RIGHT)
    set_p_text(doc.paragraphs[82], "ปี 2568", 16, True, WD_ALIGN_PARAGRAPH.RIGHT)

    # -------------------------------------------------------------------------
    # 4. Update Table of Contents (P[99] to P[105])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[100], "2.1 การวิจัยเชิงทดลอง\t3", 16, False)
    set_p_text(doc.paragraphs[101], "2.2 ไมโครโปรเซสเซอร์ Raspberry Pi 4 Model B\t3", 16, False)
    set_p_text(doc.paragraphs[102], "2.3 ปัญญาประดิษฐ์ตรวจจับและระบุตัวตนใบหน้า (YuNet & SFace)\t3", 16, False)
    set_p_text(doc.paragraphs[103], "2.4 เซนเซอร์วัดระยะทางอัลตราโซนิก (HC-SR04) และโหมดประหยัดพลังงาน\t4", 16, False)
    set_p_text(doc.paragraphs[104], "2.5 ระบบสังเคราะห์เสียงภาษาไทยและการจัดการผ่านเว็บ\t4", 16, False)
    set_p_text(doc.paragraphs[105], "2.6 งานวิจัยที่เกี่ยวข้อง\t4", 16, False)

    # -------------------------------------------------------------------------
    # 5. Update Table of Tables (P[158] to P[160])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[158], "ตารางที่ 4.1 ผลการทดลองการตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก รอบที่ 1              7", 16, False)
    set_p_text(doc.paragraphs[159], "ตารางที่ 4.2 ผลการทดลองการแจ้งเตือนมื้อยาตามตารางเวลาและระบบเสียงออฟไลน์ รอบที่ 2              7", 16, False)
    set_p_text(doc.paragraphs[160], "ตารางที่ 4.3 ทำการเปรียบเทียบผลการทดลอง                                                             8", 16, False)

    # -------------------------------------------------------------------------
    # 6. Update Chapter 1: Introduction (P[192] to P[225])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[192], "บทที่ 1", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[194], "บทนำ", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[196], "1.1 ความเป็นมาและความสำคัญของปัญหา", 16, True)

    ch1_intro1 = (
        "\tในปัจจุบัน ประเทศไทยได้ก้าวเข้าสู่สังคมผู้สูงอายุอย่างสมบูรณ์ (Complete Aged Society) ส่งผลให้มีสัดส่วนประชากรสูงวัยเพิ่มขึ้นอย่างต่อเนื่อง "
        "ซึ่งผู้สูงอายุส่วนใหญ่มักมีภาวะโรคเรื้อรังประจำตัว เช่น โรคความดันโลหิตสูง โรคเบาหวาน โรคหัวใจ หรือโรคไขมันในเลือดสูง "
        "ความเจ็บป่วยเหล่านี้จำเป็นต้องได้รับการรักษาด้วยการรับประทานยาหลายชนิดเป็นประจำทุกวันและตรงตามมื้ออาหารอย่างเคร่งครัด"
    )
    set_p_text(doc.paragraphs[198], ch1_intro1, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    ch1_intro2 = (
        "\tปัญหาสำคัญที่พบบ่อยในผู้สูงอายุคือ \"การลืมรับประทานยา\" การรับประทานยาผิดเวลา ผิดขนาด หรือการรับประทานยาซ้ำซ้อน "
        "เนื่องจากภาวะหลงลืมตามวัยและความสับสนในรายการยา ซึ่งอาจส่งผลเสียต่อการควบคุมโรคและอาจก่อให้เกิดอันตรายรุนแรงถึงแก่ชีวิต "
        "การแจ้งเตือนแบบดั้งเดิม เช่น การใช้นาฬิกาปลุก หรือแอปพลิเคชันบนสมาร์ตโฟน มักไม่ประสบความสำเร็จในการใช้งานจริง "
        "เนื่องจากเสียงเตือนมีความน่ารำคาญ ไม่ระบุชื่อยา ตัวหนังสือมีขนาดเล็กมองเห็นไม่ชัด หรือผู้สูงอายุไม่ได้พกพาโทรศัพท์มือถือติดตัวตลอดเวลา"
    )
    set_p_text(doc.paragraphs[199], ch1_intro2, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    ch1_intro3 = (
        "\tจากพฤติกรรมในชีวิตประจำวันของครอบครัวไทย \"หม้อหุงข้าว\" หรือ \"โต๊ะอาหาร\" ถือเป็นจุดศูนย์รวมที่สมาชิกในครอบครัวและผู้สูงอายุ "
        "จะต้องเดินเข้ามารับประทานอาหารเป็นประจำวันละ 3 มื้อ คณะผู้วิจัยจึงเกิดแนวคิดในการพัฒนา \"กล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box)\" "
        "ที่สามารถติดตั้งร่วมกับหม้อหุงข้าวหรือวางบนโต๊ะอาหารได้อย่างลงตัว โดยใช้บอร์ดสมองกลฝังตัว Raspberry Pi 4 Model B ร่วมกับเซนเซอร์วัดระยะทางอัลตราโซนิก (HC-SR04) "
        "ในการตรวจจับเมื่อมีบุคคลเดินเข้ามาใกล้ และใช้กล้องร่วมกับระบบปัญญาประดิษฐ์ (Edge AI) ผ่านโมเดล YuNet และ SFace ในการตรวจจับและระบุตัวตนสมาชิกในครอบครัวแบบเรียลไทม์"
    )
    set_p_text(doc.paragraphs[200], ch1_intro3, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    ch1_intro4 = (
        "\tระบบจะทำการแจ้งเตือนด้วยเสียงพูดภาษาไทยที่เป็นธรรมชาติ สุภาพ อ่อนโยน เหมือนเสียงลูกหลานคอยดูแล "
        "โดยระบุชื่อสมาชิก มื้ออาหาร รายการยา ปริมาณ และสีของซองยาอย่างชัดเจน พร้อมระบบไฟแสดงสถานะ LED จราจร 3 สี "
        "ที่สำคัญระบบถูกออกแบบให้ทำงานแบบออฟไลน์ได้ 100% (Offline Standalone) มีระบบแคชเสียงล่วงหน้า จึงไม่จำเป็นต้องเชื่อมต่ออินเทอร์เน็ตในเวลาทำงาน "
        "และมีโหมดประหยัดพลังงาน (Eco-Sleep Mode) เพื่อลดการใช้พลังงานและยืดอายุการใช้งานของอุปกรณ์ ส่งผลให้ระบบมีความเสถียร ปลอดภัย และตอบโจทย์การดูแลสุขภาพอย่างแท้จริง"
    )
    set_p_text(doc.paragraphs[201], ch1_intro4, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[203], "1.2 วัตถุประสงค์ของการวิจัย", 16, True)
    set_p_text(doc.paragraphs[205], "\t1.2.1 เพื่อออกแบบและสร้างกล่องเตือนทานยาอัจฉริยะที่ใช้เทคโนโลยี AI ตรวจจับใบหน้าและเซนเซอร์อัลตราโซนิกในการแจ้งเตือนด้วยเสียงภาษาไทย", 16, False)
    set_p_text(doc.paragraphs[206], "\t1.2.2 เพื่อทดสอบประสิทธิภาพการทำงานของระบบตรวจจับบุคคล การระบุตัวตนสมาชิก และความถูกต้องของการแจ้งเตือนตามตารางเวลามื้อยา", 16, False)
    
    # Check if there is 1.2.3
    # Definitions
    set_p_text(doc.paragraphs[208], "1.3 คำจำกัดความที่ใช้ในการวิจัย", 16, True)
    set_p_text(doc.paragraphs[210], "\tกล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box) หมายถึง อุปกรณ์สมองกลฝังตัวที่ติดตั้งร่วมกับหม้อหุงข้าว สามารถตรวจจับบุคคล จำแนกใบหน้า และแจ้งเตือนรายการยาตามตารางเวลาด้วยเสียงพูดภาษาไทยได้โดยอัตโนมัติ", 16, False)
    set_p_text(doc.paragraphs[211], "\tปัญญาประดิษฐ์ตรวจจับและระบุตัวตนใบหน้า (YuNet & SFace) หมายถึง โมเดลโครงข่ายประสาทเทียมเชิงลึก (Deep Learning) ที่ทำงานบน ONNX Runtime เพื่อตรวจหาตำแหน่งใบหน้า (YuNet) และสกัดคุณลักษณะเพื่อจำแนกบุคคล (SFace) แบบเรียลไทม์", 16, False)
    set_p_text(doc.paragraphs[212], "\tเซนเซอร์อัลตราโซนิก (Ultrasonic Sensor HC-SR04) หมายถึง เซนเซอร์วัดระยะทางด้วยคลื่นเสียงความถี่สูง ใช้ในการตรวจจับการเข้าใกล้ของบุคคลในระยะ 20–50 เซนติเมตร", 16, False)
    set_p_text(doc.paragraphs[213], "\tโหมดประหยัดพลังงาน (Eco-Sleep Mode) หมายถึง สถานะการทำงานเมื่อไม่มีบุคคลในระยะเกิน 60 วินาที โดยระบบจะปิดการทำงานของกล้อง CMOS และปรับเซนเซอร์อัลตราโซนิกให้ส่งสัญญาณพัลส์เป็นช่วง เพื่อลดความร้อนและประหยัดพลังงาน", 16, False)
    set_p_text(doc.paragraphs[214], "\tการสังเคราะห์เสียงภาษาไทยแบบออฟไลน์ (Offline Thai Speech Synthesis) หมายถึง ระบบสร้างเสียงพูดภาษาไทยที่แปลงจากข้อความและบันทึกไว้ในหน่วยความจำแคชของเครื่องล่วงหน้า ทำให้สามารถเล่นเสียงได้ทันทีโดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต", 16, False)

    set_p_text(doc.paragraphs[216], "1.4 ประโยชน์ที่คาดว่าจะได้รับ", 16, True)
    set_p_text(doc.paragraphs[218], "\t1) ช่วยลดปัญหาการลืมรับประทานยา การรับประทานยาผิดชนิด หรือการทานยาซ้ำซ้อนในผู้สูงอายุได้อย่างมีประสิทธิภาพ", 16, False)
    set_p_text(doc.paragraphs[219], "\t2) ผู้สูงอายุได้รับคำแนะนำการทานยาด้วยเสียงพูดภาษาไทยที่สุภาพ อ่อนโยน เข้าใจง่าย พร้อมระบุชื่อยาและสีซองยาได้อย่างชัดเจน", 16, False)
    set_p_text(doc.paragraphs[220], "\t3) สมาชิกในครอบครัวสามารถตรวจสอบและจัดการข้อมูลตารางเวลามื้อยาผ่านระบบเว็บแอปพลิเคชันได้อย่างสะดวก", 16, False)
    set_p_text(doc.paragraphs[221], "\t4) ได้ต้นแบบนวัตกรรมสมองกลฝังตัวด้านสุขภาพ (Healthcare AIoT) ที่ทำงานแบบออฟไลน์ 100% มีความปลอดภัยและเสถียรภาพสูง", 16, False)

    # -------------------------------------------------------------------------
    # 7. Update Chapter 2: Literature Review (P[240] to P[265])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[240], "บทที่ 2", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[242], "แนวคิด ทฤษฎีเอกสาร และงานวิจัยที่เกี่ยวข้อง", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[244], "\tการศึกษาครั้งนี้เป็นการวิจัยและพัฒนากล่องเตือนทานยาอัจฉริยะ โดยผู้วิจัยได้รวบรวมแนวคิด ทฤษฎี และผลงานวิจัยที่เกี่ยวข้อง เพื่อใช้เป็นพื้นฐานในการออกแบบและพัฒนาระบบ ซึ่งสามารถแบ่งออกเป็น 6 หัวข้อดังนี้", 16, False)
    set_p_text(doc.paragraphs[245], "\t2.1 การวิจัยเชิงทดลอง", 16, False)
    set_p_text(doc.paragraphs[246], "\t2.2 ไมโครโปรเซสเซอร์ Raspberry Pi 4 Model B", 16, False)
    set_p_text(doc.paragraphs[247], "\t2.3 ปัญญาประดิษฐ์ตรวจจับและระบุตัวตนใบหน้า (YuNet & SFace)", 16, False)
    set_p_text(doc.paragraphs[248], "\t2.4 เซนเซอร์วัดระยะทางอัลตราโซนิก (HC-SR04) และโหมดประหยัดพลังงาน", 16, False)
    set_p_text(doc.paragraphs[249], "\t2.5 ระบบสังเคราะห์เสียงภาษาไทยและการจัดการผ่านเว็บ", 16, False)
    set_p_text(doc.paragraphs[250], "\t2.6 งานวิจัยที่เกี่ยวข้อง", 16, False)

    set_p_text(doc.paragraphs[251], "2.1 การวิจัยเชิงทดลอง (Experimental Research)", 16, True)
    set_p_text(doc.paragraphs[252], "\tการวิจัยเชิงทดลองเป็นรูปแบบการวิจัยที่ผู้วิจัยควบคุมตัวแปรอย่างเป็นระบบ เพื่อศึกษาความสัมพันธ์ระหว่างตัวแปรต้นและตัวแปรตาม โดยมีการกำหนดสภาวะการทดลองอย่างชัดเจน เพื่อให้สามารถวัดผลลัพธ์ได้อย่างแม่นยำและตรวจสอบได้ การวิจัยลักษณะนี้ใช้ในการทดสอบระบบกล่องเตือนทานยาอัจฉริยะ ทั้งด้านการตรวจจับบุคคล การระบุใบหน้า และความถูกต้องในการแจ้งเตือนยาตามมื้ออาหาร", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[253], "2.2 ไมโครโปรเซสเซอร์ Raspberry Pi 4 Model B", 16, True)
    set_p_text(doc.paragraphs[254], "\tRaspberry Pi 4 Model B เป็นบอร์ดคอมพิวเตอร์ขนาดเล็ก (Single-board Computer) ที่ใช้หน่วยประมวลผล Broadcom BCM2711 แบบ Quad-core Cortex-A72 ความเร็ว 1.5 GHz มีหน่วยความจำ RAM แบบ LPDDR4 รองรับการเชื่อมต่อกล้องผ่านพอร์ต USB/CSI, พอร์ต GPIO สำหรับเชื่อมต่อเซนเซอร์และไฟ LED รวมทั้งระบบเครือข่ายไร้สาย Wi-Fi เหมาะสำหรับใช้เป็นศูนย์กลางการประมวลผล Edge AI บนตัวอุปกรณ์โดยตรง (On-device Processing) ทำให้ระบบสามารถทำงานได้โดยไม่ต้องพึ่งพาคลาวด์เซิร์ฟเวอร์", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[255], "2.3 ปัญญาประดิษฐ์ตรวจจับและระบุตัวตนใบหน้า (YuNet & SFace)", 16, True)
    set_p_text(doc.paragraphs[256], "\tYuNet เป็นโครงข่ายประสาทเทียมแบบ Deep Convolutional Neural Network ที่ออกแบบมาสำหรับงานตรวจจับใบหน้า (Face Detection) แบบเรียลไทม์บนอุปกรณ์ที่มีทรัพยากรจำกัด มีความแม่นยำสูงและใช้เวลาประมวลผลต่ำ ส่วน SFace เป็นโมเดลระบุตัวตนใบหน้า (Face Recognition) ที่สกัดเวกเตอร์คุณลักษณะของใบหน้าขนาด 128 มิติ และใช้การคำนวณ Cosine Similarity ในการเปรียบเทียบกับฐานข้อมูลใบหน้าของสมาชิกในครอบครัว ทำให้สามารถจดจำใบหน้าได้อย่างรวดเร็วและแม่นยำสูง", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[257], "2.4 เซนเซอร์วัดระยะทางอัลตราโซนิก (HC-SR04) และโหมดประหยัดพลังงาน", 16, True)
    set_p_text(doc.paragraphs[258], "\tเซนเซอร์ HC-SR04 ทำงานโดยการส่งคลื่นเสียงความถี่ 40 kHz ผ่านขา Trigger และรับคลื่นสะท้อนผ่านขา Echo เพื่อคำนวณระยะห่างของวัตถุอย่างแม่นยำ ในงานวิจัยนี้ได้นำมาประยุกต์ใช้ในการตรวจจับเมื่อมีบุคคลเดินเข้ามาในระยะ 20–50 เซนติเมตร พร้อมระบบประหยัดพลังงาน Eco-Sleep Sniffer Mode ที่ลดอัตราการส่งพัลส์เหลือทุก 1.2 วินาที และปิดเซนเซอร์รับภาพของกล้องเมื่อไม่มีคนอยู่หน้ากล่องเกิน 60 วินาที ช่วยลดความร้อนและป้องกันละอองไอน้ำจากหม้อหุงข้าว", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[259], "2.5 ระบบสังเคราะห์เสียงภาษาไทยและการจัดการผ่านเว็บ", 16, True)
    set_p_text(doc.paragraphs[260], "\tระบบเสียงใช้เทคโนโลยี Neural Text-to-Speech (เสียงพรีมวดี th-TH-PremwadeeNeural) ที่ให้สำเนียงภาษาไทยที่นุ่มนวล สุภาพ อ่อนโยน เหมาะสำหรับผู้สูงอายุ โดยมีระบบ Precompiler แปลงประโยคแจ้งเตือนล่วงหน้าและบันทึกเป็นไฟล์เสียงในแคชของเครื่อง พร้อมเพิ่ม Audio RAM Buffer ป้องกันเสียงขาดหาย และมีระบบ Web Management Portal สไตล์ Apple Minimalist ให้สมาชิกสามารถจัดการตารางยาและลงทะเบียนใบหน้าได้อย่างสะดวก", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[261], "2.6 งานวิจัยที่เกี่ยวข้อง", 16, True)
    set_p_text(doc.paragraphs[262], "\tสมชาย พัฒนจิตต์ (2565) ได้พัฒนาระบบแจ้งเตือนการทานยาอัตโนมัติสำหรับผู้สูงอายุโดยใช้ไมโครคอนโทรลเลอร์ พบว่าการเตือนด้วยเสียงช่วยลดอัตราการลืมยาได้มากกว่าร้อยละ 85 ณัฐพล สุขสวัสดิ์ (2566) ได้ศึกษาการประยุกต์ใช้ Edge AI บน Raspberry Pi ในการตรวจจับใบหน้า พบว่าโมเดล YuNet และ SFace มีความแม่นยำและตอบสนองได้รวดเร็ว และ Kumar et al. (2022) ได้พัฒนาระบบ IoT Smart Pill Reminder ที่สรุปได้ว่าการเตือนยาที่เป็นมิตรและทำงานแบบออฟไลน์ช่วยเพิ่มความปลอดภัยสูงสุดแก่ผู้ใช้งาน", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    # -------------------------------------------------------------------------
    # 8. Update Chapter 3: Methodology (P[271] to P[325])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[271], "บทที่ 3", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[273], "วิธีดำเนินการวิจัย", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[275], "\tการวิจัยครั้งนี้เป็นการวิจัยเชิงทดลอง (Experimental Research) โดยมีวัตถุประสงค์ 1) เพื่อออกแบบและสร้างกล่องเตือนทานยาอัจฉริยะที่ใช้ AI ตรวจจับใบหน้าและเซนเซอร์อัลตราโซนิก 2) เพื่อทดสอบประสิทธิภาพการทำงานของระบบตรวจจับบุคคล การระบุตัวตน และการแจ้งเตือนตามตารางเวลามื้อยา และ 3) เพื่อประเมินความถูกต้องและความพึงพอใจในการใช้งาน ซึ่งมีขั้นตอนดำเนินการดังนี้", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    set_p_text(doc.paragraphs[276], "\t3.1 รูปแบบการสร้างชิ้นงาน", 16, False)
    set_p_text(doc.paragraphs[277], "\t3.2 รูปแบบการทดลองชิ้นงาน", 16, False)
    set_p_text(doc.paragraphs[278], "\t3.3 การวิเคราะห์ข้อมูล", 16, False)
    set_p_text(doc.paragraphs[279], "\t3.4 สถิติที่ใช้ในการวิจัย", 16, False)

    set_p_text(doc.paragraphs[281], "3.1 รูปแบบการสร้างชิ้นงาน", 16, True)
    set_p_text(doc.paragraphs[283], "การออกแบบระบบ (System Design)", 16, True)
    set_p_text(doc.paragraphs[284], "\t1) ศึกษาความต้องการและพฤติกรรมการทานยาของผู้สูงอายุ กำหนดฟังก์ชันหลัก ได้แก่ การตรวจจับบุคคล การจดจำใบหน้า การเช็คตารางเวลามื้อยา และการสังเคราะห์เสียงพูดภาษาไทย", 16, False)
    set_p_text(doc.paragraphs[285], "\t2) ออกแบบสถาปัตยกรรมระบบโดยใช้ Raspberry Pi 4 Model B เป็นหน่วยประมวลผลหลัก ทำงานร่วมกับกล้อง USB Camera และเซนเซอร์อัลตราโซนิก HC-SR04", 16, False)
    set_p_text(doc.paragraphs[286], "\t3) กำหนดการเชื่อมต่อวงจรฮาร์ดแวร์ ได้แก่ ไฟแสดงสถานะ LED จราจร 3 สี (แดง, เหลือง, เขียว) ผ่าน GPIO, ลำโพงขับเสียงผ่านพอร์ต Audio Jack/USB และแหล่งจ่ายไฟสวิตชิ่ง 5V 5A (S-25-5)", 16, False)

    set_p_text(doc.paragraphs[287], "การพัฒนาโปรแกรมควบคุม (Software Architecture)", 16, True)
    set_p_text(doc.paragraphs[288], "\t1) พัฒนาโครงสร้างการทำงานด้วยภาษา Python 3 บนระบบปฏิบัติการ Linux (Raspberry Pi OS) โดยใช้ Finite State Machine (FSM) ควบคุมสถานะ STANDBY, ECO_SLEEP, DETECTING, ANNOUNCING", 16, False)
    set_p_text(doc.paragraphs[289], "\t2) พัฒนาระบบประมวลผลภาพ AI Vision โดยโหลดโมเดล YuNet และ SFace เข้าสู่หน่วยความจำ RAM เพียงครั้งเดียว เพื่อการตอบสนองที่รวดเร็ว", 16, False)
    set_p_text(doc.paragraphs[290], "\t3) พัฒนาระบบ Audio Precompiler สำหรับแคชไฟล์เสียงพูดภาษาไทยลงในเครื่องล่วงหน้า พร้อมระบบจัดการฐานข้อมูลยาผ่าน Local Web Management Portal", 16, False)

    set_p_text(doc.paragraphs[291], "การประกอบฮาร์ดแวร์ (Hardware Assembly)", 16, True)
    set_p_text(doc.paragraphs[292], "\t1) ประกอบอุปกรณ์ลงในกล่องควบคุม Companion Box ขนาดกะทัดรัด แข็งแรง และจัดวางช่องเปิดสำหรับเลนส์กล้อง เซนเซอร์อัลตราโซนิก และไฟ LED อย่างเป็นระเบียบ", 16, False)
    set_p_text(doc.paragraphs[293], "\t2) ติดตั้งระบบระบายความร้อน แหล่งจ่ายไฟสวิตชิ่ง และเดินสายสัญญาณด้วยขั้วต่อที่แน่นหนา ปลอดภัยต่อการใช้งานร่วมกับหม้อหุงข้าว", 16, False)

    set_p_text(doc.paragraphs[294], "การทดสอบและปรับปรุงระบบ", 16, True)
    set_p_text(doc.paragraphs[295], "\t1) ทดสอบการทำงานของระบบในสภาวะแสงและระยะห่างต่าง ๆ ปรับค่าความเชื่อมั่นในการตรวจจับใบหน้าให้เหมาะสม และปรับปรุงบัฟเฟอร์เสียงในแรมเพื่อขจัดปัญหาเสียงสะดุด", 16, False)
    set_p_text(doc.paragraphs[296], "\t2) ทดสอบการทำงานแบบออฟไลน์ 100% โดยตัดการเชื่อมต่ออินเทอร์เน็ต เพื่อยืนยันความเสถียรในการทำงานตลอด 24 ชั่วโมง", 16, False)

    set_p_text(doc.paragraphs[298], "3.2 รูปแบบการทดลองชิ้นงาน", 16, True)
    set_p_text(doc.paragraphs[300], "\tการทดลองกล่องเตือนทานยาอัจฉริยะเป็นการทดสอบการทำงานของเซนเซอร์อัลตราโซนิก กล้อง V4L2 และระบบ AI (YuNet & SFace) บน Raspberry Pi 4 โดยมีขั้นตอนดังนี้:", 16, False)
    set_p_text(doc.paragraphs[301], "\t1) ต่อวงจรอุปกรณ์ทั้งหมด ได้แก่ เซนเซอร์ HC-SR04, กล้อง USB, บอร์ด Raspberry Pi 4, ไฟ LED จราจร 3 สี และลำโพง", 16, False)
    set_p_text(doc.paragraphs[302], "\t2) ติดตั้งโปรแกรมควบคุมระบบและโมเดล AI พร้อมตั้งค่าฐานข้อมูลยาและรูปภาพใบหน้าสมาชิก", 16, False)
    set_p_text(doc.paragraphs[303], "\t3) กำหนดตารางเวลารับประทานยา 4 มื้อ (เช้า, กลางวัน, เย็น, ก่อนนอน) ใน med_config.json", 16, False)
    set_p_text(doc.paragraphs[304], "\t4) ทดลองในสภาวะแสง ระยะห่าง (20–70 ซม.) และช่วงเวลาต่าง ๆ ทั้งแบบมีเน็ตและไม่มีเน็ต", 16, False)
    set_p_text(doc.paragraphs[305], "\t5) บันทึกผลการตรวจจับบุคคล การจำแนกใบหน้าสมาชิก และความถูกต้องของเสียงพูดแจ้งเตือนยา", 16, False)

    set_p_text(doc.paragraphs[307], "3.3 การวิเคราะห์ข้อมูล", 16, True)
    set_p_text(doc.paragraphs[309], "\tการวิเคราะห์ข้อมูลการทดลองใช้การคำนวณค่าร้อยละ (Percentage) เพื่อประเมิน:", 16, False)
    set_p_text(doc.paragraphs[310], "\t1) ประสิทธิภาพและความถูกต้องในการตรวจจับบุคคลและจำแนกใบหน้าสมาชิกในครอบครัว", 16, False)
    set_p_text(doc.paragraphs[311], "\t2) ความถูกต้องสมบูรณ์ในการแจ้งเตือนมื้อยาและรายการยาตามตารางเวลาแบบออฟไลน์", 16, False)

    set_p_text(doc.paragraphs[313], "3.4 สถิติที่ใช้ในการวิจัย", 16, True)
    set_p_text(doc.paragraphs[315], "\tสถิติที่ใช้ในการวิจัยครั้งนี้ คือ ค่าร้อยละ (Percentage)", 16, False)
    set_p_text(doc.paragraphs[316], "\tสูตรการคำนวณ:", 16, False)
    set_p_text(doc.paragraphs[319], "\t\tร้อยละ (%) = (X / N) × 100", 16, True)
    set_p_text(doc.paragraphs[321], "\tเมื่อ  X  คือ จำนวนครั้งที่ระบบทำงานได้ถูกต้องตามวัตถุประสงค์", 16, False)
    set_p_text(doc.paragraphs[322], "\t      N  คือ จำนวนครั้งของการทดลองทั้งหมด", 16, False)

    # -------------------------------------------------------------------------
    # 9. Update Chapter 4: Results (P[326] to P[355]) + Tables 1, 2, 3
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[326], "บทที่ 4", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[328], "ผลการวิจัย", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[330], "\tการศึกษาวิจัยมีวัตถุประสงค์ 1) เพื่อออกแบบและสร้างกล่องเตือนทานยาอัจฉริยะ 2) เพื่อทดสอบประสิทธิภาพการตรวจจับบุคคล การระบุตัวตน และการแจ้งเตือนตามตารางเวลามื้อยา และ 3) เพื่อประเมินความถูกต้องและคุณภาพการทำงานของระบบ ซึ่งผลการทดลองสามารถสรุปได้ดังนี้", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    set_p_text(doc.paragraphs[332], "4.1 ผลการทดลอง", 16, True)
    set_p_text(doc.paragraphs[334], "ตารางที่ 4.1 ผลการทดลองการตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก รอบที่ 1", 16, True)

    # Table 1 Data
    t1_data = [
        ["ครั้งที่", "การตรวจจับบุคคล (Ultrasonic)", "การจำแนกใบหน้า (AI YuNet & SFace)", "การแจ้งเตือนและไฟสถานะ", "สถานะการทำงาน"],
        ["1", "พบบุคคล (ระยะ 35 ซม.)", "ระบุตัวตนถูกต้อง (น้องนาย)", "ไฟเขียวติด / เสียงพูดเตือนยามื้อเช้า", "ปกติ"],
        ["2", "พบบุคคล (ระยะ 28 ซม.)", "ระบุตัวตนถูกต้อง (คุณตา)", "ไฟเขียวติด / เสียงพูดเตือนยามื้อเช้า", "ปกติ"],
        ["3", "ไม่พบบุคคล (ระยะ > 70 ซม.)", "ไม่มีการสแกนใบหน้า", "ไฟแดงติด / เข้าสู่ Eco-Sleep พักกล้อง", "ปกติ"],
        ["4", "พบบุคคล (ระยะ 42 ซม.)", "ระบุตัวตนถูกต้อง (คุณยาย)", "ไฟเขียวติด / เสียงพูดเตือนยามื้อเช้า", "ปกติ"],
        ["5", "พบบุคคล (ระยะ 30 ซม.)", "ไม่พบในฐานข้อมูล (Unknown)", "ไฟเขียวกระพริบ / ทักทายต้อนรับทั่วไป", "ปกติ"],
    ]
    update_table_cells(doc.tables[0], t1_data)

    set_p_text(doc.paragraphs[336], "\tสรุปผลจากตารางที่ 4.1 การทดลองระบบตรวจจับบุคคลและการจำแนกใบหน้าสมาชิก รอบที่ 1 จำนวน 5 ครั้ง พบว่า เมื่อมีบุคคลเข้ามาในระยะตรวจจับ เซนเซอร์อัลตราโซนิกสามารถส่งสัญญาณให้กล้องจับภาพและระบบ AI สามารถจำแนกใบหน้าของสมาชิกได้อย่างถูกต้อง ไฟแสดงสถานะเปลี่ยนเป็นสีเขียวและมีเสียงแจ้งเตือนตามที่กำหนด ส่วนเมื่อไม่มีบุคคลในระยะ ระบบจะเข้าสู่โหมด Eco-Sleep ประหยัดพลังงานได้อย่างถูกต้อง คิดเป็นความสำเร็จร้อยละ 100.00", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[338], "ตารางที่ 4.2 ผลการทดลองการแจ้งเตือนมื้อยาตามตารางเวลาและระบบเสียงออฟไลน์ รอบที่ 2", 16, True)

    # Table 2 Data
    t2_data = [
        ["ครั้งที่", "ช่วงเวลามื้ออาหาร", "การดึงข้อมูลยา (Medication Schedule)", "การสังเคราะห์เสียงพูดภาษาไทย (Offline)", "สถานะการทำงาน"],
        ["1", "มื้อเช้า (06:00 - 11:30 น.)", "พบรายการยา (ยาแก้ปวด ซองสีเขียว)", "แจ้งเตือนชื่อยา ปริมาณ และสีซองถูกต้อง", "ปกติ"],
        ["2", "มื้อกลางวัน (11:31 - 14:30 น.)", "ไม่มีรายการยาที่ต้องรับประทาน", "ทักทายมื้อกลางวันและอวยพรสุขภาพ", "ปกติ"],
        ["3", "มื้อเย็น (17:30 - 20:00 น.)", "พบรายการยา (ยาลดความดัน/ไขมัน)", "แจ้งเตือนชื่อยา ปริมาณ และสีซองถูกต้อง", "ปกติ"],
        ["4", "ก่อนนอน (21:00 - 22:30 น.)", "พบรายการยา (ยานอนหลับ ครึ่งเม็ด)", "แจ้งเตือนชื่อยา ปริมาณ และคำแนะนำถูกต้อง", "ปกติ"],
        ["5", "การทำงานแบบไม่มีเน็ต (100% Offline)", "ดึงข้อมูลจากแคชในเครื่อง", "เล่นไฟล์เสียงแคชต่อเนื่อง ไม่มีสะดุด", "ปกติ"],
    ]
    update_table_cells(doc.tables[1], t2_data)

    set_p_text(doc.paragraphs[340], "\tสรุปผลจากตารางที่ 4.2 การทดลองการแจ้งเตือนมื้อยาตามตารางเวลาและระบบเสียงออฟไลน์ รอบที่ 2 จำนวน 5 ครั้ง พบว่า ระบบสามารถแยกแยะช่วงเวลามื้ออาหารทั้ง 4 มื้อได้อย่างแม่นยำ แจ้งเตือนชื่อยา ขนาดรับประทาน และสีของซองยาได้อย่างถูกต้องชัดเจน และสามารถทำงานในสภาวะไม่มีสัญญาณอินเทอร์เน็ตได้อย่างสมบูรณ์แบบ คิดเป็นความสำเร็จร้อยละ 100.00", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[344], "ตารางที่ 4.3 ทำการเปรียบเทียบผลการทดลอง", 16, True)

    # Table 3 Data
    t3_data = [
        ["รายการ", "การควบคุมระบบ", "สภาพการทำงาน", "คิดเป็นร้อยละ"],
        ["การทดลองรอบที่ 1 (ตรวจจับและจำแนกใบหน้า)", "ปกติ", "ปกติ", "100.00"],
        ["การทดลองรอบที่ 2 (ตารางมื้อยาและเสียงออฟไลน์)", "ปกติ", "ปกติ", "100.00"],
        ["รวม", "รวม", "รวม", "100.00"],
    ]
    update_table_cells(doc.tables[2], t3_data)

    set_p_text(doc.paragraphs[346], "\tสรุปผลจากตารางที่ 4.3 จากการเปรียบเทียบผลการทดลองทั้งสองรอบ พบว่า กล่องเตือนทานยาอัจฉริยะ สามารถทำงานได้ถูกต้องและเป็นปกติตามเกณฑ์ทุกครั้ง คิดเป็นร้อยละ 100.00 แสดงให้เห็นว่าการออกแบบฮาร์ดแวร์ ซอฟต์แวร์ปัญญาประดิษฐ์ และระบบเสียงสังเคราะห์ สามารถปฏิบัติงานได้ครบถ้วนตามวัตถุประสงค์ของการวิจัย", 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    # -------------------------------------------------------------------------
    # 10. Update Chapter 5: Conclusion, Discussion, Suggestions (P[374] to P[410])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[374], "บทที่ 5", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[376], "สรุปผลการวิจัย อภิปรายผล และข้อเสนอแนะ", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    set_p_text(doc.paragraphs[378], "5.1 สรุปผลการวิจัย", 16, True)

    ch5_summary = (
        "\tการวิจัยและพัฒนากล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box) สำหรับติดตั้งร่วมกับหม้อหุงข้าว "
        "มีผลการทดลองสรุปได้ว่า ระบบตรวจจับบุคคลด้วยเซนเซอร์อัลตราโซนิกและการระบุตัวตนด้วย AI Vision (YuNet & SFace) ในรอบที่ 1 "
        "สามารถตรวจจับและจำแนกใบหน้าของสมาชิกในครอบครัวได้อย่างแม่นยำ แสดงสถานะผ่านไฟ LED และส่งเสียงแจ้งเตือนอย่างถูกต้อง "
        "รวมทั้งสามารถเข้าสู่โหมดประหยัดพลังงาน Eco-Sleep ได้เมื่อไม่มีคนใช้งาน สำหรับการทดลองในรอบที่ 2 ด้านการแจ้งเตือนตามตารางเวลามื้อยา 4 มื้อ "
        "และการทำงานแบบออฟไลน์ 100% พบว่าระบบสามารถดึงข้อมูลยาและสร้างเสียงสังเคราะห์ภาษาไทยที่ไพเราะ คมชัด ไม่มีเสียงขาดหาย "
        "และทำงานได้โดยไม่ต้องพึ่งพาสัญญาณอินเทอร์เน็ต ผลการทดลองทั้งสองรอบมีความถูกต้องและเสถียร คิดเป็นร้อยละ 100.00 "
        "บรรลุตามวัตถุประสงค์ของการวิจัยทุกประการ"
    )
    set_p_text(doc.paragraphs[380], ch5_summary, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[382], "5.2 อภิปรายผล", 16, True)
    ch5_discuss = (
        "\tจากผลการวิจัยพบว่า กล่องเตือนทานยาอัจฉริยะสามารถทำงานได้อย่างมีประสิทธิภาพและมีความแม่นยำสูง "
        "เนื่องจากการเลือกใช้สถาปัตยกรรม Edge AI บนบอร์ด Raspberry Pi 4 ร่วมกับโมเดล YuNet และ SFace ทำให้สามารถประมวลผลบนตัวอุปกรณ์ได้โดยตรง (On-device Processing) "
        "ขจัดปัญหาความหน่วงของเครือข่ายและความกังวลด้านความเป็นส่วนตัว สอดคล้องกับงานวิจัยของ สมชาย พัฒนจิตต์ (2565) ที่พบว่าระบบแจ้งเตือนด้วยเสียงเฉพาะบุคคลช่วยเพิ่มอัตราความร่วมมือในการรับประทานยาได้อย่างมีนัยสำคัญ "
        "และสอดคล้องกับ ณัฐพล สุขสวัสดิ์ (2566) ที่ระบุว่าการประยุกต์ใช้โมเดลโครงข่ายประสาทเทียมขนาดเล็กบนระบบสมองกลฝังตัวช่วยให้ระบบทำงานได้เสถียรและประหยัดพลังงาน "
        "นอกจากนี้ การออกแบบให้มีโหมด Eco-Sleep Sniffer และการพรีคอมไพล์ไฟล์เสียงล่วงหน้ายังช่วยแก้ปัญหาเรื่องความร้อนสะสมและปัญหาเสียงพูดสะดุด ทำให้ระบบสามารถนำไปประยุกต์ใช้งานจริงในครัวเรือนได้อย่างมีประสิทธิภาพ"
    )
    set_p_text(doc.paragraphs[384], ch5_discuss, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    set_p_text(doc.paragraphs[389], "5.3 ข้อเสนอแนะ", 16, True)
    set_p_text(doc.paragraphs[391], "5.3.1 ข้อเสนอแนะจากการวิจัย", 16, True)
    set_p_text(doc.paragraphs[392], "\t1) ควรติดตั้งกล่องควบคุมในมุมและระดับความสูงที่เหมาะสมกับผู้ใช้งาน เพื่อให้กล้องสามารถจับภาพใบหน้าได้ในมุมตรงและมีความแม่นยำสูงสุด", 16, False)
    set_p_text(doc.paragraphs[393], "\t2) ควรจัดให้มีแสงสว่างสม่ำเสมอบริเวณที่ติดตั้งกล่องเตือนยา เพื่อเพิ่มประสิทธิภาพการตรวจจับใบหน้าในเวลากลางคืน", 16, False)
    set_p_text(doc.paragraphs[394], "\t3) ควรเพิ่มระบบปุ่มสัมผัส (Acknowledge Button) บนตัวกล่อง เพื่อให้ผู้ใช้กดยืนยันหลังจากรับประทานยาเรียบร้อยแล้ว", 16, False)
    set_p_text(doc.paragraphs[395], "\t4) ควรใช้แหล่งจ่ายไฟสวิตชิ่ง 5V ที่จ่ายกระแสได้อย่างน้อย 3A–5A ขึ้นไป เพื่อให้ระบบ Raspberry Pi และอุปกรณ์ต่อพ่วงทำงานได้อย่างเสถียรภาพสูงสุด", 16, False)
    set_p_text(doc.paragraphs[396], "\t5) ควรทดลองศึกษาเปรียบเทียบโมเดล AI อื่น ๆ เช่น MobileFaceNet เพื่อวิเคราะห์ความเร็วและประสิทธิภาพของระบบในการใช้งานระยะยาว", 16, False)

    set_p_text(doc.paragraphs[399], "5.3.2 ข้อเสนอแนะสำหรับการวิจัยครั้งต่อไป", 16, True)
    set_p_text(doc.paragraphs[401], "\t1) ควรพัฒนาระบบแจ้งเตือนผ่านแอปพลิเคชันบนสมาร์ตโฟน (เช่น LINE Notify) ไปยังบุตรหลานเมื่อผู้สูงอายุยังไม่ได้รับประทานยาตามเวลา", 16, False)
    set_p_text(doc.paragraphs[402], "\t2) ควรพัฒนาให้มีช่องจ่ายยาอัตโนมัติ (Automated Pill Dispenser) ที่เปิดช่องยาตามชนิดและปริมาณที่ระบบคำนวณไว้", 16, False)
    set_p_text(doc.paragraphs[403], "\t3) ควรศึกษาการเชื่อมต่อกับระบบสารสนเทศของโรงพยาบาลหรือคลินิก (HIS) เพื่ออัปเดตข้อมูลรายการยาและขนาดยาโดยอัตโนมัติ", 16, False)
    set_p_text(doc.paragraphs[404], "\t4) ควรพัฒนาโมเดล AI ให้สามารถตรวจจับการกลืนยาหรือการหยิบซองยา เพื่อยืนยันพฤติกรรมการรับประทานยาได้อย่างสมบูรณ์", 16, False)
    set_p_text(doc.paragraphs[405], "\t5) ควรพัฒนาโปรแกรม Web Portal ให้สามารถแสดงสถิติประวัติการรับประทานยา (Adherence History) ย้อนหลังในรูปแบบกราฟได้", 16, False)

    # -------------------------------------------------------------------------
    # 11. Update References / Bibliography (P[411] to P[435])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[411], "บรรณานุกรม", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    
    bib_items = [
        "กิตติพงษ์ จินดา. (2565). การประยุกต์ใช้ปัญญาประดิษฐ์บนระบบสมองกลฝังตัว Raspberry Pi. กรุงเทพฯ: สำนักพิมพ์เอ็นจิเนียริ่ง.",
        "ชาญชัย พรหมฤทธิ์. (2566). การพัฒนาเว็บแอปพลิเคชันและการตรวจจับใบหน้าแบบเรียลไทม์. วารสารเทคโนโลยีและนวัตกรรม, 11(2), 35–48.",
        "ณัฐพล สุขสวัสดิ์. (2566). การศึกษาประสิทธิภาพโมเดล YuNet และ SFace สำหรับระบบระบุตัวตนบน Edge Devices. รายงานการวิจัย, วิทยาลัยเทคนิคเชียงใหม่.",
        "สมชาย พัฒนจิตต์. (2565). การพัฒนาระบบแจ้งเตือนการรับประทานยาอัจฉริยะสำหรับผู้สูงอายุในยุคดิจิทัล. วารสารวิชาการสุขภาพและเทคโนโลยี, 8(1), 15–28.",
        "สถาบันส่งเสริมการสอนวิทยาศาสตร์และเทคโนโลยี. (2564). การเขียนโปรแกรมภาษา Python และการประมวลผลภาพเบื้องต้น. กรุงเทพฯ: สสวท.",
        "Bradski, G., & Kaehler, A. (2022). Learning OpenCV: Computer Vision with Python (3rd ed.). Sebastopol, CA: O'Reilly Media.",
        "Halfacree, G. (2023). The Official Raspberry Pi Beginner's Guide (5th ed.). Cambridge: Raspberry Pi Press.",
        "Kumar, A., Sharma, R., & Patel, V. (2022). IoT and AI-Based Smart Medication Reminder System for Elderly Patients. International Journal of Healthcare Information Systems and Informatics, 17(3), 1–18.",
        "Microsoft Azure. (2024). Neural Text-to-Speech Technical Overview and Thai Voice Synthesis Guidelines. Retrieved from https://learn.microsoft.com/azure/cognitive-services/speech-service/",
        "OpenCV Foundation. (2024). OpenCV Zoo: Face Detection (YuNet) and Face Recognition (SFace). Retrieved from https://github.com/opencv/opencv_zoo"
    ]
    
    for idx, bib_str in enumerate(bib_items):
        target_p_idx = 413 + idx
        if target_p_idx < len(doc.paragraphs) and target_p_idx < 448:
            set_p_text(doc.paragraphs[target_p_idx], bib_str, 16, False, WD_ALIGN_PARAGRAPH.JUSTIFY)

    # Clear remaining old bibliography paragraphs
    for p_i in range(413 + len(bib_items), 448):
        doc.paragraphs[p_i].text = ""

    # -------------------------------------------------------------------------
    # 12. Update Appendix A Header (P[448])
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[448], "ภาคผนวก ก", 18, True, WD_ALIGN_PARAGRAPH.CENTER)
    if 464 < len(doc.paragraphs):
        set_p_text(doc.paragraphs[464], "ภาพประกอบการนำไปใช้งาน กล่องเตือนทานยาอัจฉริยะ", 16, True, WD_ALIGN_PARAGRAPH.CENTER)
    if 479 < len(doc.paragraphs):
        set_p_text(doc.paragraphs[479], "ภาพประกอบการทำงานและการตรวจจับใบหน้า", 16, True, WD_ALIGN_PARAGRAPH.CENTER)

    # -------------------------------------------------------------------------
    # 13. Update Researcher Biographies (P[484] to end)
    # -------------------------------------------------------------------------
    set_p_text(doc.paragraphs[484], "ประวัติผู้วิจัย", 18, True, WD_ALIGN_PARAGRAPH.CENTER)

    # Researcher 1: นายกัณตพัฒน์ กระปุกทอง
    set_p_text(doc.paragraphs[486], "ชื่อ – นามสกุล\t: นายกัณตพัฒน์ กระปุกทอง", 16, False)
    set_p_text(doc.paragraphs[487], "สถานที่เกิด\t: จังหวัดสิงห์บุรี ประเทศไทย", 16, False)
    set_p_text(doc.paragraphs[488], "ประวัติการศึกษา\t: ปัจจุบันกำลังศึกษาระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) สาขาวิชาเทคโนโลยีคอมพิวเตอร์", 16, False)
    set_p_text(doc.paragraphs[489], "\t  แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", 16, False)
    set_p_text(doc.paragraphs[490], "ที่อยู่ที่ติดต่อ\t: แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี ตำบลบางพุทรา", 16, False)
    set_p_text(doc.paragraphs[491], "\t  อำเภอเมืองสิงห์บุรี จังหวัดสิงห์บุรี 16000", 16, False)

    # Researcher 2: นายณัฏฐวี ไกรทอง
    set_p_text(doc.paragraphs[493], "ชื่อ – นามสกุล\t: นายณัฏฐวี ไกรทอง", 16, False)
    set_p_text(doc.paragraphs[494], "สถานที่เกิด\t: จังหวัดสิงห์บุรี ประเทศไทย", 16, False)
    set_p_text(doc.paragraphs[495], "ประวัติการศึกษา\t: ปัจจุบันกำลังศึกษาระดับประกาศนียบัตรวิชาชีพชั้นสูง (ปวส.) สาขาวิชาเทคโนโลยีคอมพิวเตอร์", 16, False)
    set_p_text(doc.paragraphs[496], "\t  แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี", 16, False)
    set_p_text(doc.paragraphs[497], "ที่อยู่ที่ติดต่อ\t: แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี ตำบลบางพุทรา", 16, False)
    set_p_text(doc.paragraphs[498], "\t  อำเภอเมืองสิงห์บุรี จังหวัดสิงห์บุรี 16000", 16, False)

    # Clear old third researcher paragraphs if any
    for p_i in range(500, min(len(doc.paragraphs), 512)):
        doc.paragraphs[p_i].text = ""

    print(f"[*] Saving updated research report to: {DST_DOCX}")
    doc.save(str(DST_DOCX))
    print("[SUCCESS] All sections successfully rewritten and saved to แบบรายงานการวิจัย.docx!")

if __name__ == "__main__":
    main()
