# -*- coding: utf-8 -*-
"""
generate_bw_flowcharts.py
Generates 5 pure Black & White (Monochrome) Academic Flowcharts & Diagrams
Matches the standard Thai vocational/university research format (B&W thesis style).
White background, white box fills, black borders, black text, clean orthogonal lines.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configure Thai Font
plt.rcParams['font.family'] = 'Leelawadee UI'
plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'Tahoma', 'Cordia New', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = "flowcharts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LINE_COLOR = '#000000'
FILL_COLOR = '#FFFFFF'
TEXT_COLOR = '#000000'

def create_bw_conceptual_framework():
    """1. กรอบแนวคิดในการวิจัย (ขาว-ดำ)"""
    fig, ax = plt.subplots(figsize=(10.5, 5.0), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 5.0)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Title
    ax.text(5.25, 4.65, 'กรอบแนวคิดในการวิจัย (Conceptual Framework)', 
            ha='center', va='center', fontsize=14, fontweight='bold', color=TEXT_COLOR)

    # Box 1: Independent Variables
    box1 = patches.Rectangle((0.6, 0.6), 4.2, 3.6, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(box1)

    # Header line
    ax.plot([0.6, 4.8], [3.6, 3.6], color=LINE_COLOR, linewidth=1.2)
    ax.text(2.7, 3.85, 'ตัวแปรต้น (Independent Variables)', ha='center', va='center',
            fontsize=11.5, fontweight='bold', color=TEXT_COLOR)

    c1 = (
        "กล่องเตือนทานยาอัจฉริยะ\n"
        "(Smart Medication Reminder Box)\n\n"
        "1. ฮาร์ดแวร์ประมวลผลเอดจ์:\n"
        "   - บอร์ด Raspberry Pi 4 Model B\n"
        "   - เซนเซอร์ Ultrasonic HC-SR04\n"
        "   - กล้อง USB Web Camera\n"
        "   - หลอดไฟ LED แสดงสถานะ 3 สี\n"
        "   - ลำโพงเสียงพูดภาษาไทย (3.5mm)\n\n"
        "2. ซอฟต์แวร์และปัญญาประดิษฐ์:\n"
        "   - โมเดล YuNet ตรวจจับใบหน้า\n"
        "   - โมเดล SFace สกัดเวกเตอร์รู้จำใบหน้า\n"
        "   - ระบบสังเคราะห์เสียง Neural TTS\n"
        "   - เว็บพอร์ทัลจัดการข้อมูล (PWA)"
    )
    ax.text(0.85, 2.05, c1, ha='left', va='center', fontsize=9.2, color=TEXT_COLOR, linespacing=1.22)

    # Arrow between boxes
    ax.annotate('', xy=(5.6, 2.4), xytext=(4.9, 2.4),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.5, headwidth=8, headlength=8))

    # Box 2: Dependent Variables
    box2 = patches.Rectangle((5.7, 0.6), 4.2, 3.6, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(box2)

    # Header line
    ax.plot([5.7, 9.9], [3.6, 3.6], color=LINE_COLOR, linewidth=1.2)
    ax.text(7.8, 3.85, 'ตัวแปรตาม (Dependent Variables)', ha='center', va='center',
            fontsize=11.5, fontweight='bold', color=TEXT_COLOR)

    c2 = (
        "ประสิทธิภาพและความพึงพอใจต่อระบบ\n\n"
        "1. ประสิทธิภาพการตรวจจับและระบุตัวตน:\n"
        "   - ความถูกต้องในการตรวจจับบุคคล (<= 45 ซม.)\n"
        "   - ความแม่นยำในการรู้จำใบหน้าสมาชิก\n\n"
        "2. ประสิทธิภาพการแจ้งเตือนตามตารางยา:\n"
        "   - ความถูกต้องตามมื้ออาหาร 4 มื้อ\n"
        "   - การแจ้งเตือนชื่อยา ขนาดยา และสีซองยา\n"
        "   - ระบบป้องกันการรับประทานยาซ้ำซ้อน\n"
        "     (Anti-Double Dose Cooldown)\n\n"
        "3. ความพึงพอใจของผู้ใช้งาน:\n"
        "   - ผลการประเมินจากกลุ่มตัวอย่าง นักศึกษา ปวส.\n"
        "     แผนกวิชาเทคนิคคอมพิวเตอร์ จำนวน 20 คน"
    )
    ax.text(5.95, 2.05, c2, ha='left', va='center', fontsize=9.2, color=TEXT_COLOR, linespacing=1.22)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_conceptual_framework.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] B&W Generated: {path}")

def create_bw_design_process():
    """2. ขั้นตอนการออกแบบโครงงาน (ขาว-ดำ)"""
    fig, ax = plt.subplots(figsize=(11.5, 3.0), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 3.0)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(5.75, 2.65, 'ขั้นตอนการดำเนินงานและออกแบบโครงงาน (Project Design Process)', 
            ha='center', va='center', fontsize=13.5, fontweight='bold', color=TEXT_COLOR)

    steps = [
        ("ศึกษาปัญหา\nและความต้องการ", "สำรวจพฤติกรรมการทานยา\nและปัญหาของผู้สูงอายุ"),
        ("ออกแบบระบบ\nและวงจรฮาร์ดแวร์", "กำหนดสเปก Pi 4, HC-SR04,\nกล้อง USB, LED 3 สี"),
        ("ประกอบฮาร์ดแวร์\nและต่อวงจร", "เชื่อมต่อพิน GPIO,\nวงจรแบ่งแรงดัน 1k/2.2k"),
        ("พัฒนาซอฟต์แวร์\nAI และระบบเสียง", "เขียนโปรแกรม YuNet, SFace,\nNeural TTS และ PWA"),
        ("ทดสอบประสิทธิภาพ\nและประเมินผล", "ทดสอบการทำงาน 24/7,\nประเมินกลุ่มตัวอย่าง 20 คน"),
    ]

    box_w = 1.9
    box_h = 1.6
    spacing = 0.38
    start_x = 0.35

    for i, (title, desc) in enumerate(steps):
        x = start_x + i * (box_w + spacing)
        y = 0.5
        box = patches.Rectangle((x, y), box_w, box_h, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.3)
        ax.add_patch(box)

        ax.text(x + box_w/2, y + 1.15, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=TEXT_COLOR, linespacing=1.15)
        ax.text(x + box_w/2, y + 0.45, desc, ha='center', va='center',
                fontsize=7.8, color=TEXT_COLOR, linespacing=1.15)

        if i < len(steps) - 1:
            ax.annotate('', xy=(x + box_w + spacing - 0.04, y + box_h/2),
                        xytext=(x + box_w + 0.04, y + box_h/2),
                        arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=6, headlength=6))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_design_process.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] B&W Generated: {path}")

def create_bw_program_flowchart():
    """3. ผังงานการทำงานของระบบโปรแกรมหลัก (ขาว-ดำ สไตล์วิชาการแบบของเพื่อน - แก้ไขระยะห่าง 0% ทับซ้อน)"""
    fig, ax = plt.subplots(figsize=(11.0, 16.5), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 16.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Shapes helpers
    def draw_oval(x, y, w, h, text):
        box = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                      boxstyle="round,pad=0.08,rounding_size=0.35",
                                      facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.4)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=10.5, fontweight='bold', color=TEXT_COLOR)

    def draw_rect(x, y, w, h, text, fsize=9.2, bold=False):
        box = patches.Rectangle((x - w/2, y - h/2), w, h,
                                facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.4)
        ax.add_patch(box)
        weight = 'bold' if bold else 'normal'
        ax.text(x, y, text, ha='center', va='center', fontsize=fsize, fontweight=weight, color=TEXT_COLOR, linespacing=1.25)

    def draw_diamond(x, y, w, h, text, fsize=8.8):
        pts = [[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]]
        poly = patches.Polygon(pts, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.4, closed=True)
        ax.add_patch(poly)
        ax.text(x, y, text, ha='center', va='center', fontsize=fsize, color=TEXT_COLOR, linespacing=1.2)

    def draw_arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=6, headlength=6))

    # Grid coordinates
    cx = 5.75        # Center spine
    x_left = 1.6     # Left track for visitor
    x_right = 9.9    # Right track for eco-sleep & already taken
    w_main = 4.6     # Main box width (spans from 3.45 to 8.05)
    w_sub = 2.4      # Side box width

    # 1. เริ่มต้น (Start)
    draw_oval(cx, 15.6, 2.2, 0.55, "เริ่ม")
    draw_arrow(cx, 15.325, cx, 14.9)

    # 2. เปิดระบบและโหลดโมเดล
    draw_rect(cx, 14.5, w_main, 0.8, "เปิดระบบและโหลดโมเดล AI (YuNet & SFace)\nพร้อมแคชเสียงสังเคราะห์เข้าหน่วยความจำ RAM")
    draw_arrow(cx, 14.1, cx, 13.7)

    # 3. เข้าสู่สถานะ STANDBY
    draw_rect(cx, 13.3, w_main, 0.8, "เข้าสู่สถานะ STANDBY\nไฟ LED สีแดงติดค้าง (กล้องสแตนด์บาย 1.0 FPS)")
    draw_arrow(cx, 12.9, cx, 12.55)

    # 4. ตรวจสอบระยะทาง Ultrasonic <= 45 ซม.
    draw_diamond(cx, 11.9, w_main, 1.3, "เซนเซอร์ Ultrasonic HC-SR04\nตรวจพบบุคคลระยะ <= 45 ซม.?")

    # Branch No -> ไม่มีคนเกิน 60s (Right track)
    draw_arrow(cx + w_main/2, 11.9, x_right, 11.9)
    ax.text(8.5, 12.1, "ไม่ใช่", ha='center', va='bottom', fontsize=8.8, color=TEXT_COLOR)
    draw_arrow(x_right, 11.9, x_right, 11.2)

    draw_diamond(x_right, 10.6, w_sub, 1.2, "ไม่มีคนเกิน\n60 วินาที?", fsize=8.0)

    # Eco-Sleep Branch Yes
    draw_arrow(x_right, 10.0, x_right, 9.35)
    ax.text(x_right + 0.15, 9.7, "ใช่", ha='left', va='center', fontsize=8.2, color=TEXT_COLOR)

    draw_rect(x_right, 9.0, w_sub, 0.7, "เข้าสู่โหมด ECO_SLEEP\n(ดับไฟ LED พักระบบ)", fsize=7.8)

    # Loop back from Eco-Sleep to Standby (Dedicated outer right track at x=11.2)
    ax.plot([x_right, x_right, 11.2, 11.2, cx + w_main/2], [8.65, 8.3, 8.3, 13.3, 13.3], color=LINE_COLOR, linewidth=1.2)
    ax.annotate('', xy=(cx + w_main/2, 13.3), xytext=(cx + w_main/2 + 0.3, 13.3),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=6, headlength=6))

    # Eco-Sleep Branch No (loop back to Standby)
    ax.plot([x_right + w_sub/2, 11.2], [10.6, 10.6], color=LINE_COLOR, linewidth=1.2)
    ax.text(x_right + w_sub/2 + 0.1, 10.8, "ไม่ใช่", ha='left', va='bottom', fontsize=7.8, color=TEXT_COLOR)

    # Branch Yes -> DETECTING (Center track)
    draw_arrow(cx, 11.25, cx, 10.5)
    ax.text(cx + 0.15, 10.9, "ใช่", ha='left', va='center', fontsize=8.8, color=TEXT_COLOR)

    # 5. DETECTING state
    draw_rect(cx, 10.1, w_main, 0.8, "เข้าสู่สถานะ DETECTING\nไฟ LED สีเหลืองติดสว่าง (ปลุกกล้อง 15 FPS)")
    draw_arrow(cx, 9.7, cx, 9.3)

    # 6. YuNet & SFace processing
    draw_rect(cx, 8.9, w_main, 0.8, "ประมวลผลระบบปัญญาประดิษฐ์ใบหน้า\n(YuNet ตรวจจับกรอบ + SFace สกัดเวกเตอร์)")
    draw_arrow(cx, 8.5, cx, 8.15)

    # 7. ตรวจพบสมาชิกในครอบครัว?
    draw_diamond(cx, 7.5, w_main, 1.3, "ตรวจพบสมาชิกในครอบครัว?\n(Cosine Similarity >= 0.70)")

    # Branch No -> บุคคลภายนอก (Left track x_left=1.6)
    draw_arrow(cx - w_main/2, 7.5, x_left, 7.5)
    ax.text(2.6, 7.7, "ไม่ใช่", ha='center', va='bottom', fontsize=8.8, color=TEXT_COLOR)
    draw_arrow(x_left, 7.5, x_left, 6.8)

    draw_rect(x_left, 6.4, w_sub, 0.8, "บุคคลภายนอก/แขก\nเล่นเสียงต้อนรับสุภาพ", fsize=8.2)

    # Visitor line drops down to Cooldown box at y=1.6
    ax.plot([x_left, x_left, cx - w_main/2], [6.0, 1.6, 1.6], color=LINE_COLOR, linewidth=1.2)
    ax.annotate('', xy=(cx - w_main/2, 1.6), xytext=(cx - w_main/2 - 0.3, 1.6),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=6, headlength=6))

    # Branch Yes -> ตรวจสอบการทานยา
    draw_arrow(cx, 6.85, cx, 6.15)
    ax.text(cx + 0.15, 6.5, "ใช่", ha='left', va='center', fontsize=8.8, color=TEXT_COLOR)

    # 8. รับประทานยาในมื้อนี้แล้วหรือไม่?
    draw_diamond(cx, 5.5, w_main, 1.3, "รับประทานยาในมื้อนี้แล้วหรือไม่?\n(Double-Dosing Hazard Guard)")

    # Branch Yes -> Already taken (Right track x_right=9.9)
    draw_arrow(cx + w_main/2, 5.5, x_right, 5.5)
    ax.text(8.5, 5.7, "ทานแล้ว", ha='center', va='bottom', fontsize=8.8, color=TEXT_COLOR)
    draw_arrow(x_right, 5.5, x_right, 4.8)

    draw_rect(x_right, 4.4, w_sub, 0.8, "พูดชมเชยและให้ความมั่นใจ\n'ไม่ต้องทานซ้ำแล้วนะคะ'", fsize=8.0)

    # Already taken line drops down to Cooldown box at y=1.6
    ax.plot([x_right, x_right, cx + w_main/2], [4.0, 1.6, 1.6], color=LINE_COLOR, linewidth=1.2)
    ax.annotate('', xy=(cx + w_main/2, 1.6), xytext=(cx + w_main/2 + 0.3, 1.6),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=6, headlength=6))

    # Branch No -> ANNOUNCING
    draw_arrow(cx, 4.85, cx, 4.1)
    ax.text(cx + 0.15, 4.5, "ยังไม่ทาน", ha='left', va='center', fontsize=8.8, color=TEXT_COLOR)

    # 9. เข้าสู่สถานะ ANNOUNCING
    draw_rect(cx, 3.7, w_main, 0.8, "เข้าสู่สถานะ ANNOUNCING\nไฟ LED สีเขียวติดสว่าง (ดึงตารางยา 4 มื้อ)")
    draw_arrow(cx, 3.3, cx, 3.0)

    # 10. เล่นเสียงเตือนยาภาษาไทย
    draw_rect(cx, 2.6, w_main, 0.8, "เล่นเสียงเตือนยาภาษาไทย (ขานชื่อ, มื้อ, สีซองยา)\nพร้อมบันทึกสถานะ Dual-Layer และส่ง Telegram")
    draw_arrow(cx, 2.2, cx, 2.0)

    # 11. บันทึกและเข้าสู่ช่วง Cooldown
    draw_rect(cx, 1.6, w_main, 0.8, "บันทึกสถานะทานยาสำเร็จ และเข้าสู่ช่วง Cooldown\nดับไฟเขียว -> กลับมาหยุดค้างที่ไฟสีแดง")
    draw_arrow(cx, 1.2, cx, 0.875)

    # 12. สิ้นสุด (End)
    draw_oval(cx, 0.6, 2.2, 0.55, "สิ้นสุด")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_program_flowchart.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] B&W Generated (Overlap Fixed): {path}")

def create_bw_state_machine():
    """4. ผังงานระบบอัตโนมัติ / สเตตแมชชีน (ขาว-ดำ)"""
    fig, ax = plt.subplots(figsize=(10.5, 7.0), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 7.0)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(5.25, 6.6, 'ผังงานระบบอัตโนมัติและสถานะการทำงาน (Finite State Machine - FSM)', 
            ha='center', va='center', fontsize=14, fontweight='bold', color=TEXT_COLOR)

    # 4 Main State Boxes (pure white, black borders)
    # State 1: STANDBY (Top Left)
    s1 = patches.Rectangle((0.8, 3.6), 3.8, 2.4, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(s1)
    ax.text(2.7, 5.65, '1. STANDBY (โหมดพร้อมทำงาน)', ha='center', va='center', fontsize=11, fontweight='bold', color=TEXT_COLOR)
    ax.plot([0.8, 4.6], [5.35, 5.35], color=LINE_COLOR, linewidth=1.0)
    desc1 = (
        "- ไฟ LED สีแดงติดค้างนิ่ง\n"
        "- เซนเซอร์ HC-SR04 ตรวจวัดระยะบุคคล\n"
        "- กล้องรันโหมดประหยัด 1.0 FPS (ลดความร้อน)\n"
        "- ซีพียูสแตนด์บายต่ำกว่า 1% (RAM ~110MB)\n"
        "- พร้อมตอบสนองทันทีเมื่อมีคนเดินเข้ามา"
    )
    ax.text(1.05, 4.35, desc1, ha='left', va='center', fontsize=8.8, color=TEXT_COLOR, linespacing=1.2)

    # State 2: DETECTING (Top Right)
    s2 = patches.Rectangle((5.9, 3.6), 3.8, 2.4, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(s2)
    ax.text(7.8, 5.65, '2. DETECTING (โหมดสแกนใบหน้า)', ha='center', va='center', fontsize=11, fontweight='bold', color=TEXT_COLOR)
    ax.plot([5.9, 9.7], [5.35, 5.35], color=LINE_COLOR, linewidth=1.0)
    desc2 = (
        "- ไฟ LED สีเหลืองติดสว่าง\n"
        "- ปลุกกล้องเร่งเฟรมเป็น 15 FPS อัตโนมัติ\n"
        "- Warm-up 8 เฟรมแรก ปรับสมดุลแสง AE/AWB\n"
        "- AI YuNet สแกนตรวจจับกรอบใบหน้า\n"
        "- AI SFace สกัดเวกเตอร์ Cosine Similarity"
    )
    ax.text(6.15, 4.35, desc2, ha='left', va='center', fontsize=8.8, color=TEXT_COLOR, linespacing=1.2)

    # State 3: ANNOUNCING (Bottom Right)
    s3 = patches.Rectangle((5.9, 0.6), 3.8, 2.3, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(s3)
    ax.text(7.8, 2.55, '3. ANNOUNCING (โหมดแจ้งเตือนยา)', ha='center', va='center', fontsize=11, fontweight='bold', color=TEXT_COLOR)
    ax.plot([5.9, 9.7], [2.25, 2.25], color=LINE_COLOR, linewidth=1.0)
    desc3 = (
        "- ไฟ LED สีเขียวติดสว่าง\n"
        "- ดึงข้อมูลมื้อยาประจำเวลาจาก med_config.json\n"
        "- เล่นเสียงสังเคราะห์ Neural TTS ชัดเจน นุ่มนวล\n"
        "- ขานชื่อ, มื้อยา, รายการยา และระบุสีซองยา\n"
        "- ส่งสรุปผลเข้ากลุ่ม Telegram ผู้ดูแลทันที"
    )
    ax.text(6.15, 1.35, desc3, ha='left', va='center', fontsize=8.8, color=TEXT_COLOR, linespacing=1.2)

    # State 4: ECO_SLEEP (Bottom Left)
    s4 = patches.Rectangle((0.8, 0.6), 3.8, 2.3, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(s4)
    ax.text(2.7, 2.55, '4. ECO_SLEEP (โหมดพักอุปกรณ์)', ha='center', va='center', fontsize=11, fontweight='bold', color=TEXT_COLOR)
    ax.plot([0.8, 4.6], [2.25, 2.25], color=LINE_COLOR, linewidth=1.0)
    desc4 = (
        "- ดับไฟ LED ทุกดวง (ประหยัดพลังงาน)\n"
        "- ทำงานเมื่อไม่มีคนหน้าหม้อหุงข้าวเกิน 60s\n"
        "- Ultrasonic เข้า Sniffer Mode (1.2s พัลส์)\n"
        "- ฮาร์ดแวร์ V4L2 คงสถานะ Ready ไร้ Deadlock\n"
        "- ตื่นทันทีใน 0.1s เมื่อมีคนเดินเข้ามา"
    )
    ax.text(1.05, 1.35, desc4, ha='left', va='center', fontsize=8.8, color=TEXT_COLOR, linespacing=1.2)

    # Transition Arrows (black lines)
    # 1 -> 2: Standby to Detecting
    ax.annotate('', xy=(5.85, 4.8), xytext=(4.65, 4.8),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.3, headwidth=6, headlength=6))
    ax.text(5.25, 5.05, 'ตรวจพบคน\n<= 45 ซม.', ha='center', va='center', fontsize=8.2, color=TEXT_COLOR)

    # 2 -> 3: Detecting to Announcing
    ax.annotate('', xy=(7.8, 2.95), xytext=(7.8, 3.55),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.3, headwidth=6, headlength=6))
    ax.text(8.8, 3.25, 'รู้จำใบหน้าสำเร็จ\nหรือผู้มาเยือน', ha='left', va='center', fontsize=8.0, color=TEXT_COLOR)

    # 3 -> 1: Announcing to Standby
    ax.annotate('', xy=(4.65, 4.1), xytext=(5.85, 2.4),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.3, headwidth=6, headlength=6))
    ax.text(5.25, 3.1, 'เตือนเสร็จสิ้น +\nเข้าช่วง Cooldown', ha='center', va='center', fontsize=8.0, color=TEXT_COLOR)

    # 1 -> 4: Standby to Eco Sleep
    ax.annotate('', xy=(2.7, 2.95), xytext=(2.7, 3.55),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.3, headwidth=6, headlength=6))
    ax.text(1.6, 3.25, 'ไม่มีความเคลื่อนไหว\nเกิน 60 วินาที', ha='right', va='center', fontsize=8.0, color=TEXT_COLOR)

    # 4 -> 2: Eco Sleep to Detecting (Instant Wakeup)
    ax.annotate('', xy=(5.85, 4.2), xytext=(4.65, 1.9),
                arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.3, headwidth=6, headlength=6))
    ax.text(5.25, 1.9, 'ตรวจพบคน\nปลุกระบบทันที', ha='center', va='center', fontsize=8.0, color=TEXT_COLOR)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_state_machine.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] B&W Generated: {path}")

def create_bw_system_architecture():
    """5. ภาพรวมโครงงาน / บล็อกไดอะแกรมระบบ (ขาว-ดำ)"""
    fig, ax = plt.subplots(figsize=(11.5, 7.0), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 7.0)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(5.75, 6.6, 'ภาพรวมโครงสร้างสถาปัตยกรรมระบบ (System Architecture Block Diagram)', 
            ha='center', va='center', fontsize=14, fontweight='bold', color=TEXT_COLOR)

    # 3 Columns
    # Column 1: Input Units (Left)
    col1 = patches.Rectangle((0.5, 0.7), 2.8, 5.4, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(col1)
    ax.text(1.9, 5.8, 'ส่วนรับข้อมูล (Input Unit)', ha='center', va='center', fontsize=11, fontweight='bold', color=TEXT_COLOR)
    ax.plot([0.5, 3.3], [5.5, 5.5], color=LINE_COLOR, linewidth=1.0)

    in_items = [
        ("เซนเซอร์ Ultrasonic HC-SR04\n(Trig Pin 16 / Echo Pin 18)\nตรวจจับระยะบุคคล 30-45 ซม.", 4.5),
        ("กล้อง USB Web Camera\n(ความละเอียด HD 720p/1080p)\nจับภาพใบหน้าสดระดับสายตา", 3.1),
        ("เว็บพอร์ทัลจัดการข้อมูล (Web Portal)\n(PWA Responsive & QR Code)\nบันทึกรูปหน้า, ตารางยา, Wi-Fi", 1.7),
    ]
    for text, y in in_items:
        b = patches.Rectangle((0.7, y - 0.5), 2.4, 1.0, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.1)
        ax.add_patch(b)
        ax.text(1.9, y, text, ha='center', va='center', fontsize=8.2, color=TEXT_COLOR, linespacing=1.2)

    # Column 2: Central Edge Controller (Center)
    col2 = patches.Rectangle((3.9, 0.7), 3.7, 5.4, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.8)
    ax.add_patch(col2)
    ax.text(5.75, 5.8, 'สมองกลฝังตัวหลัก (Edge AI Controller)', ha='center', va='center', fontsize=11, fontweight='bold', color=TEXT_COLOR)
    ax.plot([3.9, 7.6], [5.5, 5.5], color=LINE_COLOR, linewidth=1.0)

    core_items = [
        ("Raspberry Pi 4 Model B (Quad-Core 64-bit)\nระบบปฏิบัติการ Linux 64-bit (Debian)", 4.85, 0.75),
        ("OpenCV YuNet Face Detector (~230KB)\nตรวจจับพิกัดใบหน้าความเร็วสูงใน RAM", 3.95, 0.75),
        ("OpenCV SFace Recognizer (~37MB)\nสกัดคุณลักษณะใบหน้าเวกเตอร์ 128 มิติ", 3.05, 0.75),
        ("Thai Phrase Builder & Neural TTS\nประกอบประโยคเสียงพูดสุภาพ และบอกสีซองยา", 2.15, 0.75),
        ("Dual-Layer Medication Adherence Tracker\nบันทึกสถานะ RAM Disk (/dev/shm) + SD Card", 1.25, 0.75),
    ]
    for text, y, h in core_items:
        b = patches.Rectangle((4.1, y - h/2), 3.3, h, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.1)
        ax.add_patch(b)
        ax.text(5.75, y, text, ha='center', va='center', fontsize=8.2, color=TEXT_COLOR, linespacing=1.15)

    # Column 3: Output Units (Right)
    col3 = patches.Rectangle((8.2, 0.7), 2.8, 5.4, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5)
    ax.add_patch(col3)
    ax.text(9.6, 5.8, 'ส่วนแสดงผล (Output Unit)', ha='center', va='center', fontsize=11, fontweight='bold', color=TEXT_COLOR)
    ax.plot([8.2, 11.0], [5.5, 5.5], color=LINE_COLOR, linewidth=1.0)

    out_items = [
        ("หลอดไฟแสดงสถานะ 3 สี (LED)\n- สีแดง (Pin 11): Standby\n- สีเหลือง (Pin 13): Detecting\n- สีเขียว (Pin 15): Announcing", 4.5),
        ("ลำโพงเสียงพูดภาษาไทย\n(Mini Speaker 3.5mm / USB Audio)\nเล่นเสียงแจ้งเตือนผ่าน mpg123", 3.1),
        ("การแจ้งเตือนทางไกล Telegram Bot\nส่งสรุปรายการยาที่ทานเข้ากลุ่มครอบครัว\nพร้อมเวลาและสถานะทันที", 1.7),
    ]
    for text, y in out_items:
        b = patches.Rectangle((8.4, y - 0.5), 2.4, 1.0, facecolor=FILL_COLOR, edgecolor=LINE_COLOR, linewidth=1.1)
        ax.add_patch(b)
        ax.text(9.6, y, text, ha='center', va='center', fontsize=8.2, color=TEXT_COLOR, linespacing=1.2)

    # Connecting Arrows (black)
    ax.annotate('', xy=(3.85, 4.5), xytext=(3.35, 4.5), arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=5, headlength=5))
    ax.annotate('', xy=(3.85, 3.1), xytext=(3.35, 3.1), arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=5, headlength=5))
    ax.annotate('', xy=(3.85, 1.7), xytext=(3.35, 1.7), arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=5, headlength=5))

    ax.annotate('', xy=(8.15, 4.5), xytext=(7.65, 4.5), arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=5, headlength=5))
    ax.annotate('', xy=(8.15, 3.1), xytext=(7.65, 3.1), arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=5, headlength=5))
    ax.annotate('', xy=(8.15, 1.7), xytext=(7.65, 1.7), arrowprops=dict(facecolor=LINE_COLOR, edgecolor=LINE_COLOR, width=1.2, headwidth=5, headlength=5))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_system_architecture.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] B&W Generated: {path}")

if __name__ == '__main__':
    print("Generating 5 pure Black & White academic flowcharts...")
    create_bw_conceptual_framework()
    create_bw_design_process()
    create_bw_program_flowchart()
    create_bw_state_machine()
    create_bw_system_architecture()
    print("All 5 B&W Flowcharts & Diagrams successfully generated!")
