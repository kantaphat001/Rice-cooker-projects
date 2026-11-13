# -*- coding: utf-8 -*-
"""
build_canva_brochure_pdf.py
Generates a 2-page landscape A4 PDF brochure for Canva PDF import.
Canva PDF Editor allows direct upload of this PDF and converts it into fully editable text/images.
"""

import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

OUTPUT_PDF = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects\แผ่นพับ_กล่องเตือนทานยาอัจฉริยะ_Canva_Editable.pdf"

# We can draw directly on canvas for exact tri-fold brochure layout (Landscape A4: 841.89 x 595.27 points)
def draw_brochure():
    c = canvas.Canvas(OUTPUT_PDF, pagesize=landscape(A4))
    width, height = landscape(A4) # 841.89, 595.27

    img_dir = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects"
    imgs = {
        'logo_vec': os.path.join(img_dir, 'extracted_images', 'doc_main_image1.png'),
        'logo_inv': os.path.join(img_dir, 'extracted_images', 'doc_main_image2.png'),
        'proto_real': os.path.join(img_dir, 'extracted_images', 'doc_main_image12.jpg'),
        'dev_cad': os.path.join(img_dir, 'extracted_images', 'doc_b_image5.png'),
        'dev_code': os.path.join(img_dir, 'extracted_images', 'doc_b_image6.png'),
        'dev_wire': os.path.join(img_dir, 'extracted_images', 'doc_b_image9.jpeg'),
        'dev_test': os.path.join(img_dir, 'extracted_images', 'doc_b_image11.jpeg'),
        'web_ui': os.path.join(img_dir, 'extracted_images', 'doc_main_image14.jpeg'),
    }

    # 3 Panels dimensions
    p_w = (width - 40) / 3 # ~267 pt
    p_h = height - 30      # ~565 pt
    y_top = height - 15

    # =========================================================================
    # PAGE 1: ด้านนอก (OUTER SIDE)
    # Panel 1: เครื่องมือ/คุณสมบัติ/ประโยชน์ | Panel 2: คณะผู้จัดทำ/ที่ปรึกษา | Panel 3: หน้าปก
    # =========================================================================
    for i in range(3):
        x = 15 + i * (p_w + 5)
        c.setFillColor(colors.HexColor('#FFFFFF'))
        c.setStrokeColor(colors.HexColor('#E2E8F0'))
        c.roundRect(x, 15, p_w, p_h, 8, fill=1, stroke=1)

    # Panel 3 (Right - Front Cover):
    x3 = 15 + 2 * (p_w + 5)
    if os.path.exists(imgs['logo_vec']):
        c.drawImage(imgs['logo_vec'], x3 + 55, y_top - 65, width=50, height=50, preserveAspectRatio=True, mask='auto')
    if os.path.exists(imgs['logo_inv']):
        c.drawImage(imgs['logo_inv'], x3 + 145, y_top - 65, width=50, height=50, preserveAspectRatio=True, mask='auto')

    if os.path.exists(imgs['proto_real']):
        c.drawImage(imgs['proto_real'], x3 + 45, y_top - 360, width=170, height=220, preserveAspectRatio=True, mask='auto')

    # Panel 2 (Middle):
    x2 = 15 + 1 * (p_w + 5)
    c.setFillColor(colors.HexColor('#0E7490'))
    c.rect(x2, 15, p_w, 35, fill=1, stroke=0)

    # Panel 1 (Left):
    x1 = 15

    c.showPage()

    # =========================================================================
    # PAGE 2: ด้านใน (INNER SIDE)
    # Panel 1: ที่มา/วัตถุประสงค์ | Panel 2: ขั้นตอนการดำเนินงาน | Panel 3: วิธีใช้งาน/สรุปผล
    # =========================================================================
    for i in range(3):
        x = 15 + i * (p_w + 5)
        c.setFillColor(colors.HexColor('#FFFFFF'))
        c.setStrokeColor(colors.HexColor('#E2E8F0'))
        c.roundRect(x, 15, p_w, p_h, 8, fill=1, stroke=1)

    # Draw step images on middle panel
    x_mid = 15 + 1 * (p_w + 5)
    step_imgs = [imgs['dev_cad'], imgs['dev_code'], imgs['dev_wire'], imgs['dev_test']]
    y_step = y_top - 100
    for simg in step_imgs:
        if os.path.exists(simg):
            c.drawImage(simg, x_mid + 15, y_step, width=95, height=75, preserveAspectRatio=True, mask='auto')
        y_step -= 125

    # Draw Web UI on right panel
    x_right = 15 + 2 * (p_w + 5)
    if os.path.exists(imgs['web_ui']):
        c.drawImage(imgs['web_ui'], x_right + 60, y_top - 360, width=145, height=140, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    print(f"✅ Successfully built: {OUTPUT_PDF} ({os.path.getsize(OUTPUT_PDF)} bytes)")

if __name__ == "__main__":
    draw_brochure()
