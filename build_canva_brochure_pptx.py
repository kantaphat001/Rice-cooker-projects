# -*- coding: utf-8 -*-
"""
build_canva_brochure_pptx.py
Generates an editable PowerPoint presentation (.pptx) formatted as a professional
Tri-Fold Brochure (แผ่นพับ 3 พับ 6 หน้า) for Canva import.
Canva can directly import and edit this .pptx file with 100% editable text, shapes, and images.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

OUTPUT_PPTX = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects\แผ่นพับ_กล่องเตือนทานยาอัจฉริยะ_Canva_Editable.pptx"

# Color Palette (Smart Healthcare & AI Theme)
C_NAVY = RGBColor(15, 23, 42)       # Slate 900
C_PRIMARY = RGBColor(14, 116, 144)   # Teal/Cyan 700
C_ACCENT = RGBColor(16, 185, 129)    # Emerald 500
C_BG_LIGHT = RGBColor(248, 250, 252) # Slate 50
C_PANEL_BG = RGBColor(255, 255, 255) # White
C_BORDER = RGBColor(226, 232, 240)   # Slate 200
C_TEXT_DARK = RGBColor(30, 41, 59)   # Slate 800
C_TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
C_BLUE_GRAD = RGBColor(238, 242, 255) # Indigo 50
C_BAR_BOTTOM = RGBColor(2, 132, 199) # Sky 600

def create_brochure():
    prs = Presentation()
    # A4 Landscape dimensions (297mm x 210mm)
    prs.slide_width = Inches(11.693)
    prs.slide_height = Inches(8.268)
    blank_layout = prs.slide_layouts[6] # Blank slide

    # Images dictionary
    img_dir = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects"
    imgs = {
        'logo_vec': os.path.join(img_dir, 'extracted_images', 'doc_main_image1.png'),
        'logo_inv': os.path.join(img_dir, 'extracted_images', 'doc_main_image2.png'),
        'proto_real': os.path.join(img_dir, 'extracted_images', 'doc_main_image12.jpg'),
        'cad_model': os.path.join(img_dir, 'cad_models', 'smart_companion_cad_front.jpg'),
        'web_ui': os.path.join(img_dir, 'extracted_images', 'doc_main_image14.jpeg'),
        'rpi4': os.path.join(img_dir, 'extracted_images', 'doc_main_image7.png'),
        'dev_cad': os.path.join(img_dir, 'extracted_images', 'doc_b_image5.png'),
        'dev_code': os.path.join(img_dir, 'extracted_images', 'doc_b_image6.png'),
        'dev_wire': os.path.join(img_dir, 'extracted_images', 'doc_b_image9.jpeg'),
        'dev_test': os.path.join(img_dir, 'extracted_images', 'doc_b_image11.jpeg'),
    }

    # =========================================================================
    # SLIDE 1: แผ่นด้านนอก (OUTER SIDE)
    # Panel 1 (Left): เครื่องมือ / คุณสมบัติ / ประโยชน์
    # Panel 2 (Middle): คณะผู้จัดทำ / ครูที่ปรึกษา / ข้อมูลติดต่อ / Thank You
    # Panel 3 (Right): หน้าปกหลัก (ชื่อโครงการ, สอศ., ภาพผลงานจริง)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)

    # 3 Panel Dimensions
    panel_w = Inches(3.65)
    panel_h = Inches(7.70)
    top_pos = Inches(0.28)
    left_p1 = Inches(0.28)
    left_p2 = Inches(4.02)
    left_p3 = Inches(7.76)

    # Draw 3 panel card backgrounds for clean separation
    for l_pos in [left_p1, left_p2, left_p3]:
        bg_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l_pos, top_pos, panel_w, panel_h)
        bg_card.fill.solid()
        bg_card.fill.fore_color.rgb = C_PANEL_BG
        bg_card.line.color.rgb = C_BORDER
        bg_card.line.width = Pt(1)

    # -------------------------------------------------------------------------
    # SLIDE 1 - PANEL 1 (LEFT): เครื่องมือ / คุณสมบัติ / ประโยชน์
    # -------------------------------------------------------------------------
    # Header Banner: เครื่องมือที่ใช้ในการพัฒนา
    h_box1 = s1.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(0.15), panel_w - Inches(0.3), Inches(0.45))
    tf1 = h_box1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "เครื่องมือที่ใช้ในการพัฒนา"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    # Tools badges text
    tb_tools = s1.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(0.55), panel_w - Inches(0.3), Inches(0.95))
    tf_tools = tb_tools.text_frame
    tf_tools.word_wrap = True
    p = tf_tools.paragraphs[0]
    p.text = "• บอร์ดสมองกลฝังตัว: Raspberry Pi 4 Model B (Edge AI)\n• ปัญญาประดิษฐ์: Python, OpenCV, YuNet & SFace (ONNX)\n• เสียงสังเคราะห์: Microsoft Edge-TTS (สำเนียงสุภาพ)\n• เซนเซอร์ตรวจจับ: Ultrasonic HC-SR04 & กล้อง USB HD\n• เว็บพอร์ทัล: Web Management Portal (PWA: JS/HTML5)"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(13)
    p.font.color.rgb = C_TEXT_DARK

    # Header: คุณสมบัติของสิ่งประดิษฐ์
    h_box2 = s1.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(2.20), panel_w - Inches(0.3), Inches(0.40))
    p = h_box2.text_frame.paragraphs[0]
    p.text = "คุณสมบัติเด่นของสิ่งประดิษฐ์"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_feat = s1.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(2.60), panel_w - Inches(0.3), Inches(2.20))
    tf_feat = tb_feat.text_frame
    tf_feat.word_wrap = True
    feats = [
        "ไร้สัมผัส 100% (Zero-Touch Hands-Free): เดินเข้ามาในระยะ 30–45 ซม. ระบบจะตรวจจับและสแกนใบหน้าอัตโนมัติ ไม่ต้องกดปุ่มใดๆ",
        "Edge AI On-Device: ประมวลผลโครงข่ายประสาทเทียมตรวจจับและจำแนกใบหน้าบนบอร์ดทันที ไม่ต้องต่ออินเทอร์เน็ต (Offline 100%)",
        "แจ้งเตือนเสียงพูดภาษาไทยสุภาพ: ขานชื่อสมาชิก มื้อยา ระบุชื่อยา ปริมาณ และระบุ 'สีของซองยา' อย่างชัดเจน เหมาะกับผู้สูงอายุ",
        "ระบบป้องกันการทานยาซ้ำ (Anti-Double Dose): บันทึกสถานะการทานยาอัตโนมัติและเข้าสู่ช่วง Cooldown ป้องกันอันตราย",
        "จัดการง่ายผ่านสมาร์ตโฟน: มี Web Management Portal รองรับการสแกน QR Code เพื่อจัดการตารางยาและลงทะเบียนใบหน้า",
        "ระบบระบายความร้อน Eco-Sleep: มีรีเลย์ควบคุมพัดลมอัตโนมัติและโหมดพักเครื่องเพื่อความปลอดภัยและทนทาน"
    ]
    for i, f_text in enumerate(feats):
        p = tf_feat.paragraphs[0] if i == 0 else tf_feat.add_paragraph()
        p.text = f"• {f_text}"
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # Header: ประโยชน์ที่คาดว่าจะได้รับ
    h_box3 = s1.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(5.15), panel_w - Inches(0.3), Inches(0.40))
    p = h_box3.text_frame.paragraphs[0]
    p.text = "ประโยชน์ที่คาดว่าจะได้รับ"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_bene = s1.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(5.55), panel_w - Inches(0.3), Inches(1.80))
    tf_bene = tb_bene.text_frame
    tf_bene.word_wrap = True
    benes = [
        "ลดปัญหาการลืมรับประทานยา (Missed Dose) และขจัดความเสี่ยงจากการรับประทานยาซ้ำซ้อน (Overdose) ในผู้สูงอายุได้อย่างมีประสิทธิภาพ",
        "ช่วยให้ผู้สูงอายุที่มีปัญหาด้านสายตาสามารถหยิบซองยาได้อย่างถูกต้องแม่นยำ ผ่านการขานชื่อยาและระบุสัญลักษณ์สีของซองยา",
        "ผู้ดูแลและลูกหลานสามารถจัดการข้อมูลยาและติดตามประวัติการทานยาของสมาชิกในบ้านได้อย่างสะดวกรวดเร็วผ่านสมาร์ตโฟน",
        "ส่งเสริมการพึ่งพาตนเองของผู้สูงอายุ และยกระดับคุณภาพชีวิตของสมาชิกในครอบครัวให้มีความสุขและปลอดภัย"
    ]
    for i, b_text in enumerate(benes):
        p = tf_bene.paragraphs[0] if i == 0 else tf_bene.add_paragraph()
        p.text = f"• {b_text}"
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # -------------------------------------------------------------------------
    # SLIDE 1 - PANEL 2 (MIDDLE): คณะผู้จัดทำ / ครูที่ปรึกษา / ติดต่อ / ขอบคุณ
    # -------------------------------------------------------------------------
    h_team = s1.shapes.add_textbox(left_p2 + Inches(0.15), top_pos + Inches(0.15), panel_w - Inches(0.3), Inches(0.40))
    p = h_team.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "คณะผู้จัดทำ"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_members = s1.shapes.add_textbox(left_p2 + Inches(0.15), top_pos + Inches(0.55), panel_w - Inches(0.3), Inches(1.10))
    tf_mem = tb_members.text_frame
    tf_mem.word_wrap = True
    mems = [
        ("นายกัณตพัฒน์  กระปุกทอง", "นักศึกษาระดับ ปวส. เทคนิคคอมพิวเตอร์"),
        ("นายณัฏฐวี  ไกรทอง", "นักศึกษาระดับ ปวส. เทคนิคคอมพิวเตอร์"),
    ]
    for i, (m_name, m_sub) in enumerate(mems):
        p = tf_mem.paragraphs[0] if i == 0 else tf_mem.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = m_name
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_DARK
        p_sub = tf_mem.add_paragraph()
        p_sub.alignment = PP_ALIGN.CENTER
        p_sub.text = m_sub
        p_sub.font.name = "TH SarabunPSK"
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = C_TEXT_MUTED
        p_sub.space_after = Pt(4)

    # ครูที่ปรึกษา
    h_adv = s1.shapes.add_textbox(left_p2 + Inches(0.15), top_pos + Inches(1.85), panel_w - Inches(0.3), Inches(0.40))
    p = h_adv.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "ครูที่ปรึกษาโครงการ"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_adv = s1.shapes.add_textbox(left_p2 + Inches(0.15), top_pos + Inches(2.25), panel_w - Inches(0.3), Inches(1.50))
    tf_adv = tb_adv.text_frame
    tf_adv.word_wrap = True
    advisors = [
        "นายนิพนธ์  แก้วเกิด          (ครูที่ปรึกษาหลัก)",
        "นางสาวสุภาพร  ชุ่มวารี      (ครูที่ปรึกษาร่วม)",
        "นายศิวกร  บุญอุ้ม           (ครูที่ปรึกษาร่วม)",
        "ว่าที่ร้อยโทกฤษฎินทร์  สีแก้ว  (ครูที่ปรึกษาร่วม)"
    ]
    for i, adv_name in enumerate(advisors):
        p = tf_adv.paragraphs[0] if i == 0 else tf_adv.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = adv_name
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(13.5)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # Organization & Contact Box
    h_org = s1.shapes.add_textbox(left_p2 + Inches(0.15), top_pos + Inches(3.90), panel_w - Inches(0.3), Inches(1.80))
    tf_org = h_org.text_frame
    tf_org.word_wrap = True
    p = tf_org.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "แผนกวิชาเทคนิคคอมพิวเตอร์"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    contacts = [
        "วิทยาลัยเทคนิคสิงห์บุรี อาชีวศึกษาจังหวัดสิงห์บุรี",
        "สำนักงานคณะกรรมการการอาชีวศึกษา",
        "เลขที่ 4 ถนนวิไลจิตต์ ตำบลบางพุทรา อำเภอเมืองสิงห์บุรี 16000",
        "📞 โทรศัพท์ : 036-511232",
        "🌐 Facebook : สาขาวิชาเทคโนโลยีคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี"
    ]
    for c_text in contacts:
        p_c = tf_org.add_paragraph()
        p_c.alignment = PP_ALIGN.CENTER
        p_c.text = c_text
        p_c.font.name = "TH SarabunPSK"
        p_c.font.size = Pt(12)
        p_c.font.color.rgb = C_TEXT_DARK

    # Bottom Decorative Bar: Thank you
    bar_ty = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_p2, top_pos + Inches(7.10), panel_w, Inches(0.60))
    bar_ty.fill.solid()
    bar_ty.fill.fore_color.rgb = C_PRIMARY
    bar_ty.line.fill.background()
    p_ty = bar_ty.text_frame.paragraphs[0]
    p_ty.alignment = PP_ALIGN.CENTER
    p_ty.text = "Smart Medication Reminder Box • Thank You"
    p_ty.font.name = "Arial"
    p_ty.font.size = Pt(13)
    p_ty.font.bold = True
    p_ty.font.color.rgb = RGBColor(255, 255, 255)

    # -------------------------------------------------------------------------
    # SLIDE 1 - PANEL 3 (RIGHT): หน้าปกหลัก (FRONT COVER)
    # -------------------------------------------------------------------------
    # Logos (สอศ. + สิ่งประดิษฐ์คนรุ่นใหม่)
    if os.path.exists(imgs['logo_vec']):
        s1.shapes.add_picture(imgs['logo_vec'], left_p3 + Inches(0.85), top_pos + Inches(0.20), width=Inches(0.85))
    if os.path.exists(imgs['logo_inv']):
        s1.shapes.add_picture(imgs['logo_inv'], left_p3 + Inches(1.95), top_pos + Inches(0.20), width=Inches(0.85))

    # Competition details
    tb_header = s1.shapes.add_textbox(left_p3 + Inches(0.15), top_pos + Inches(1.15), panel_w - Inches(0.3), Inches(0.90))
    tf_h = tb_header.text_frame
    tf_h.word_wrap = True
    p = tf_h.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "สิ่งประดิษฐ์ของคนรุ่นใหม่ ประจำปีการศึกษา 2569"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_MUTED

    p2 = tf_h.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "สิ่งประดิษฐ์ประเภทที่ 2 ด้านนวัตกรรมและเทคโนโลยี\nปัญญาประดิษฐ์ อุปกรณ์อัจฉริยะ (AI & Smart Device)"
    p2.font.name = "TH SarabunPSK"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = C_PRIMARY

    # Main Project Title
    tb_title = s1.shapes.add_textbox(left_p3 + Inches(0.10), top_pos + Inches(2.15), panel_w - Inches(0.2), Inches(1.10))
    tf_t = tb_title.text_frame
    tf_t.word_wrap = True
    p_th = tf_t.paragraphs[0]
    p_th.alignment = PP_ALIGN.CENTER
    p_th.text = "กล่องเตือนทานยาอัจฉริยะ"
    p_th.font.name = "TH SarabunPSK"
    p_th.font.size = Pt(26)
    p_th.font.bold = True
    p_th.font.color.rgb = C_NAVY

    p_en = tf_t.add_paragraph()
    p_en.alignment = PP_ALIGN.CENTER
    p_en.text = "Smart Medication Reminder Box"
    p_en.font.name = "Arial"
    p_en.font.size = Pt(14)
    p_en.font.bold = True
    p_en.font.color.rgb = C_PRIMARY

    # Prototype Real Image
    if os.path.exists(imgs['proto_real']):
        s1.shapes.add_picture(imgs['proto_real'], left_p3 + Inches(0.70), top_pos + Inches(3.30), width=Inches(2.25))

    # By Organization
    tb_dept = s1.shapes.add_textbox(left_p3 + Inches(0.15), top_pos + Inches(6.50), panel_w - Inches(0.3), Inches(0.95))
    tf_dept = tb_dept.text_frame
    tf_dept.word_wrap = True
    p_d1 = tf_dept.paragraphs[0]
    p_d1.alignment = PP_ALIGN.CENTER
    p_d1.text = "จัดทำโดย"
    p_d1.font.name = "TH SarabunPSK"
    p_d1.font.size = Pt(13)
    p_d1.font.bold = True
    p_d1.font.color.rgb = C_TEXT_MUTED

    p_d2 = tf_dept.add_paragraph()
    p_d2.alignment = PP_ALIGN.CENTER
    p_d2.text = "แผนกวิชาเทคนิคคอมพิวเตอร์ วิทยาลัยเทคนิคสิงห์บุรี\nอาชีวศึกษาจังหวัดสิงห์บุรี สำนักงานคณะกรรมการการอาชีวศึกษา"
    p_d2.font.name = "TH SarabunPSK"
    p_d2.font.size = Pt(13)
    p_d2.font.bold = True
    p_d2.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 2: แผ่นด้านใน (INNER SIDE)
    # Panel 1 (Left): ที่มาและความสำคัญ / วัตถุประสงค์ของการวิจัย
    # Panel 2 (Middle): ขั้นตอนการดำเนินงาน 4 ขั้นตอน (มีภาพประกอบ)
    # Panel 3 (Right): วิธีการใช้งาน (5 ขั้นตอน) / ผลการทดลอง
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)

    for l_pos in [left_p1, left_p2, left_p3]:
        bg_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l_pos, top_pos, panel_w, panel_h)
        bg_card.fill.solid()
        bg_card.fill.fore_color.rgb = C_PANEL_BG
        bg_card.line.color.rgb = C_BORDER
        bg_card.line.width = Pt(1)

    # -------------------------------------------------------------------------
    # SLIDE 2 - PANEL 1 (LEFT): ที่มาและความสำคัญ / วัตถุประสงค์
    # -------------------------------------------------------------------------
    h_bg = s2.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(0.15), panel_w - Inches(0.3), Inches(0.40))
    p = h_bg.text_frame.paragraphs[0]
    p.text = "ที่มาและความสำคัญ"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_bg_body = s2.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(0.55), panel_w - Inches(0.3), Inches(3.60))
    tf_bg_b = tb_bg_body.text_frame
    tf_bg_b.word_wrap = True
    bg_paragraphs = [
        "   ปัจจุบันประเทศไทยได้ก้าวเข้าสู่ 'สังคมผู้สูงอายุอย่างสมบูรณ์' (Complete Aged Society) ส่งผลให้มีสัดส่วนผู้สูงอายุเพิ่มขึ้นอย่างต่อเนื่อง ซึ่งผู้สูงอายุส่วนใหญ่มักมีโรคเรื้อรังประจำตัว เช่น ความดันโลหิตสูง เบาหวาน หัวใจ และไขมันในเลือดสูง ทำให้จำเป็นต้องรับประทานยาหลายชนิดทุกวันอย่างต่อเนื่อง",
        "   ปัญหาสำคัญที่พบบ่อยและเป็นอันตรายถึงแก่ชีวิตคือ 'การลืมรับประทานยา (Missed Dose)' และ 'การรับประทานยาซ้ำซ้อน (Accidental Overdose)' เนื่องจากภาวะความเสื่อมถอยของความจำและสายตาตามวัย การแจ้งเตือนแบบเดิม เช่น นาฬิกาปลุก หรือสมาร์ตโฟน ยังมีข้อจำกัดเพราะผู้สูงอายุไม่ได้พกพาติดตัวตลอดเวลา หรือใช้งานหน้าจอยุ่งยาก",
        "   จากพฤติกรรมในครัวเรือนไทย ผู้วิจัยพบว่า 'หม้อหุงข้าว' เป็นจุดศูนย์รวมประจำวันที่ทุกคนต้องเดินเข้ามาทุกมื้ออาหาร คณะผู้วิจัยจึงพัฒนากล่องเตือนทานยาอัจฉริยะข้างหม้อหุงข้าว ทำงานแบบไร้สัมผัส 100% (Zero-Touch Hands-Free) ตรวจจับบุคคลอัตโนมัติ สแกนใบหน้าด้วย Edge AI และขานเสียงเตือนมื้อยาพร้อมระบุสีซองยาได้อย่างปลอดภัย"
    ]
    for i, bg_p in enumerate(bg_paragraphs):
        p = tf_bg_b.paragraphs[0] if i == 0 else tf_bg_b.add_paragraph()
        p.text = bg_p
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(12.5)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(4)

    # วัตถุประสงค์ของการวิจัย
    h_obj = s2.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(4.30), panel_w - Inches(0.3), Inches(0.40))
    p = h_obj.text_frame.paragraphs[0]
    p.text = "วัตถุประสงค์ของการวิจัย"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_obj = s2.shapes.add_textbox(left_p1 + Inches(0.15), top_pos + Inches(4.70), panel_w - Inches(0.3), Inches(2.60))
    tf_obj = tb_obj.text_frame
    tf_obj.word_wrap = True
    objs = [
        "1. เพื่อศึกษาและพัฒนากล่องเตือนทานยาอัจฉริยะข้างหม้อหุงข้าวที่ทำงานแบบไร้สัมผัส (Hands-Free) ด้วยระบบ Edge AI",
        "2. เพื่อทดสอบและประเมินประสิทธิภาพของระบบ Edge AI ในการตรวจจับบุคคล การระบุตัวตนใบหน้าสมาชิกในครอบครัว และการแจ้งเตือนมื้อยาแบบออฟไลน์",
        "3. เพื่อศึกษาความพึงพอใจของผู้ใช้งานที่มีต่อการใช้งานกล่องเตือนทานยาอัจฉริยะ"
    ]
    for i, o_text in enumerate(objs):
        p = tf_obj.paragraphs[0] if i == 0 else tf_obj.add_paragraph()
        p.text = o_text
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(13)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(4)

    # -------------------------------------------------------------------------
    # SLIDE 2 - PANEL 2 (MIDDLE): ขั้นตอนการดำเนินงาน (4 ขั้นตอน มีรูป)
    # -------------------------------------------------------------------------
    h_proc = s2.shapes.add_textbox(left_p2 + Inches(0.15), top_pos + Inches(0.15), panel_w - Inches(0.3), Inches(0.40))
    p = h_proc.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "ขั้นตอนการดำเนินงาน"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    steps_data = [
        ("ขั้นตอนที่ 1 : วางแผนและออกแบบ 3D CAD", imgs['dev_cad'], "ออกแบบโครงสร้าง 3 มิติ ขนาดกะทัดรัดสำหรับติดตั้งข้างหม้อหุงข้าว", top_pos + Inches(0.55)),
        ("ขั้นตอนที่ 2 : เขียนโปรแกรมและเทรน AI", imgs['dev_code'], "พัฒนาโปรแกรม Python, FSM, โมเดล YuNet/SFace และ Neural TTS", top_pos + Inches(2.35)),
        ("ขั้นตอนที่ 3 : ประกอบวงจรและสร้างชิ้นงาน", imgs['dev_wire'], "ต่อบอร์ด Raspberry Pi 4, เซนเซอร์ Ultrasonic, กล้อง, ลำโพง, รีเลย์", top_pos + Inches(4.15)),
        ("ขั้นตอนที่ 4 : ทดสอบการทำงานจริง", imgs['dev_test'], "ทดสอบระยะตรวจจับบุคคล การจำแนกใบหน้า และระบบเสียงออฟไลน์", top_pos + Inches(5.95)),
    ]

    for title_s, img_s, desc_s, y_s in steps_data:
        # Title
        tb_st = s2.shapes.add_textbox(left_p2 + Inches(0.15), y_s, panel_w - Inches(0.3), Inches(0.30))
        p = tb_st.text_frame.paragraphs[0]
        p.text = title_s
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = C_NAVY

        # Image
        if os.path.exists(img_s):
            s2.shapes.add_picture(img_s, left_p2 + Inches(0.20), y_s + Inches(0.32), width=Inches(1.50))

        # Description
        tb_sd = s2.shapes.add_textbox(left_p2 + Inches(1.80), y_s + Inches(0.30), panel_w - Inches(1.95), Inches(1.20))
        tf_sd = tb_sd.text_frame
        tf_sd.word_wrap = True
        p_desc = tf_sd.paragraphs[0]
        p_desc.text = desc_s
        p_desc.font.name = "TH SarabunPSK"
        p_desc.font.size = Pt(11.5)
        p_desc.font.color.rgb = C_TEXT_DARK

    # -------------------------------------------------------------------------
    # SLIDE 2 - PANEL 3 (RIGHT): วิธีการใช้งาน / สรุปผลการทดลอง
    # -------------------------------------------------------------------------
    h_use = s2.shapes.add_textbox(left_p3 + Inches(0.15), top_pos + Inches(0.15), panel_w - Inches(0.3), Inches(0.40))
    p = h_use.text_frame.paragraphs[0]
    p.text = "วิธีการใช้งาน (Hands-Free)"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_use = s2.shapes.add_textbox(left_p3 + Inches(0.15), top_pos + Inches(0.55), panel_w - Inches(0.3), Inches(3.40))
    tf_use = tb_use.text_frame
    tf_use.word_wrap = True
    how_to = [
        "1. เสียบสายจ่ายไฟ 5V: ระบบเปิดทำงานอัตโนมัติและเข้าสู่สถานะสแตนด์บาย (ไฟ LED สีแดงติดสว่าง)",
        "2. จัดการข้อมูลยาผ่านมือถือ: ผู้ดูแลสแกน QR Code เข้า Web Management Portal เพื่อลงทะเบียนสมาชิกและตารางยา",
        "3. เดินเข้าสู่ระยะตรวจจับ: เมื่อถึงมื้ออาหาร ผู้สูงอายุเดินเข้ามาในระยะ 30–45 ซม. หน้าหม้อหุงข้าว",
        "4. สแกนใบหน้าอัตโนมัติ: เซนเซอร์ปลุกกล้องตรวจจับใบหน้า (ไฟ LED สีเหลือง) ยืนยันตัวตนสำเร็จ (ไฟ LED สีเขียว)",
        "5. ขานเตือนยาพร้อมสีซองยา: ระบบเล่นเสียงพูดภาษาไทยสุภาพ ระบุชื่อยา ขนาด และสีซองยา เช่น ซองสีเขียว",
        "6. ป้องกันการทานยาซ้ำ (Cooldown): ระบบบันทึกสถานะเรียบร้อย และเริ่มพักการเตือนซ้ำเพื่อความปลอดภัย"
    ]
    for i, ht_text in enumerate(how_to):
        p = tf_use.paragraphs[0] if i == 0 else tf_use.add_paragraph()
        p.text = ht_text
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # Web UI screenshot in Right Panel
    if os.path.exists(imgs['web_ui']):
        s2.shapes.add_picture(imgs['web_ui'], left_p3 + Inches(0.95), top_pos + Inches(3.85), width=Inches(1.75))

    # Research Results Card
    h_res = s2.shapes.add_textbox(left_p3 + Inches(0.15), top_pos + Inches(5.60), panel_w - Inches(0.3), Inches(0.35))
    p = h_res.text_frame.paragraphs[0]
    p.text = "สรุปผลการวิจัยและประเมินผล"
    p.font.name = "TH SarabunPSK"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    tb_res = s2.shapes.add_textbox(left_p3 + Inches(0.15), top_pos + Inches(5.95), panel_w - Inches(0.3), Inches(1.50))
    tf_res = tb_res.text_frame
    tf_res.word_wrap = True
    results = [
        "• ประสิทธิภาพความสำเร็จของระบบ Edge AI รวมเฉลี่ย: 93.33%",
        "   - การตรวจจับและระบุตัวตนใบหน้า: สำเร็จ 100.00%",
        "   - การแจ้งเตือนมื้อยาตามตารางเวลา: สำเร็จ 90.00%",
        "   - การสังเคราะห์เสียงภาษาไทยออฟไลน์: สำเร็จ 90.00%",
        "• ความพึงพอใจของผู้ใช้งานกลุ่มตัวอย่าง (N = 30 คน):",
        "   - ค่าเฉลี่ยรวมทุกด้าน x̄ = 4.56, S.D. = 0.53 อยู่ในระดับ 'มากที่สุด'"
    ]
    for i, r_text in enumerate(results):
        p = tf_res.paragraphs[0] if i == 0 else tf_res.add_paragraph()
        p.text = r_text
        p.font.name = "TH SarabunPSK"
        p.font.size = Pt(11.5)
        p.font.bold = ("ค่าเฉลี่ย" in r_text or "ประสิทธิภาพ" in r_text or "ความพึงพอใจ" in r_text)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(1)

    prs.save(OUTPUT_PPTX)
    print(f"✅ Successfully built: {OUTPUT_PPTX} ({os.path.getsize(OUTPUT_PPTX)} bytes)")

if __name__ == "__main__":
    create_brochure()
