# -*- coding: utf-8 -*-
"""
generate_flowcharts.py
Generates 5 high-resolution flowcharts and diagrams for the Research Report (ว-สอศ-3).
Uses matplotlib with Leelawadee UI font for crisp, beautiful Thai typography.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager

# Configure Thai Font
plt.rcParams['font.family'] = 'Leelawadee UI'
plt.rcParams['font.sans-serif'] = ['Leelawadee UI', 'Tahoma', 'Cordia New', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = "flowcharts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_conceptual_framework():
    """1. ภาพกรอบแนวคิดในการวิจัย (Conceptual Framework)"""
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.5)
    ax.axis('off')

    # Background canvas
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # Title
    ax.text(5.5, 5.1, 'กรอบแนวคิดในการวิจัย (Conceptual Framework)', 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#1E293B')
    ax.text(5.5, 4.75, 'การพัฒนากล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box)', 
            ha='center', va='center', fontsize=12, color='#64748B')

    # Box 1: Independent Variables (ตัวแปรต้น)
    box1 = patches.FancyBboxPatch((0.6, 0.7), 4.2, 3.7,
                                  boxstyle="round,pad=0.15,rounding_size=0.25",
                                  facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=2)
    ax.add_patch(box1)

    # Box 1 Header
    hdr1 = patches.FancyBboxPatch((0.6, 3.8), 4.2, 0.6,
                                  boxstyle="round,pad=0.1,rounding_size=0.2",
                                  facecolor='#3B82F6', edgecolor='#3B82F6', linewidth=1)
    ax.add_patch(hdr1)
    ax.text(2.7, 4.1, 'ตัวแปรต้น (Independent Variables)', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#FFFFFF')

    content1 = (
        "กล่องเตือนทานยาอัจฉริยะ\n"
        "(Smart Medication Reminder Box)\n\n"
        "• ฮาร์ดแวร์ประมวลผลเอดจ์:\n"
        "  - บอร์ด Raspberry Pi 4 Model B (Quad-Core)\n"
        "  - เซนเซอร์คลื่นอัลตราโซนิก HC-SR04 ตรวจจับบุคคล\n"
        "  - กล้อง USB Web Camera ความละเอียด HD\n"
        "  - ไฟแสดงสถานะ 3 สี (LED แดง, เหลือง, เขียว)\n"
        "  - ลำโพงเสียงพูดภาษาไทย (Mini Speaker 3.5mm)\n\n"
        "• ซอฟต์แวร์และโมเดลปัญญาประดิษฐ์:\n"
        "  - โครงข่ายตรวจจับใบหน้า YuNet ONNX (~230KB)\n"
        "  - โครงข่ายสกัดเวกเตอร์จำแนกใบหน้า SFace ONNX\n"
        "  - ระบบสังเคราะห์เสียงพูดภาษาไทย Neural TTS\n"
        "  - ระบบบริหารจัดการผ่านเว็บแอปพลิเคชัน (PWA)"
    )
    ax.text(0.85, 2.35, content1, ha='left', va='center', fontsize=9.5, color='#1E293B', linespacing=1.25)

    # Arrow between boxes
    ax.annotate('', xy=(6.0, 2.55), xytext=(5.0, 2.55),
                arrowprops=dict(facecolor='#0EA5E9', edgecolor='#0284C7', width=4, headwidth=12, headlength=10))

    # Box 2: Dependent Variables (ตัวแปรตาม)
    box2 = patches.FancyBboxPatch((6.2, 0.7), 4.2, 3.7,
                                  boxstyle="round,pad=0.15,rounding_size=0.25",
                                  facecolor='#ECFDF5', edgecolor='#10B981', linewidth=2)
    ax.add_patch(box2)

    # Box 2 Header
    hdr2 = patches.FancyBboxPatch((6.2, 3.8), 4.2, 0.6,
                                  boxstyle="round,pad=0.1,rounding_size=0.2",
                                  facecolor='#10B981', edgecolor='#10B981', linewidth=1)
    ax.add_patch(hdr2)
    ax.text(8.3, 4.1, 'ตัวแปรตาม (Dependent Variables)', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#FFFFFF')

    content2 = (
        "ประสิทธิภาพและความพึงพอใจต่อระบบ\n\n"
        "1. ประสิทธิภาพการตรวจจับและระบุตัวตน:\n"
        "   - ความถูกต้องในการตรวจจับบุคคล (< 45 ซม.)\n"
        "   - ความแม่นยำในการรู้จำใบหน้าสมาชิก (YuNet & SFace)\n\n"
        "2. ประสิทธิภาพการแจ้งเตือนตามตารางยา:\n"
        "   - ความถูกต้องตามช่วงเวลามื้ออาหาร 4 มื้อ\n"
        "   - การแจ้งเตือนชื่อยา ขนาดยา และสีซองยา\n"
        "   - ระบบป้องกันการรับประทานยาซ้ำซ้อน\n"
        "     (Anti-Double Dose Cooldown)\n\n"
        "3. ความพึงพอใจของผู้ใช้งาน:\n"
        "   - ผลการประเมินจากกลุ่มตัวอย่าง นักศึกษา ปวส.\n"
        "     แผนกวิชาเทคนิคคอมพิวเตอร์ จำนวน 20 คน"
    )
    ax.text(6.45, 2.35, content2, ha='left', va='center', fontsize=9.5, color='#1E293B', linespacing=1.25)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_conceptual_framework.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {path}")

def create_design_process():
    """2. ภาพขั้นตอนการออกแบบโครงงาน (Project Design Process)"""
    fig, ax = plt.subplots(figsize=(12, 3.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.5)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Title
    ax.text(6.0, 3.1, 'ขั้นตอนการดำเนินงานและออกแบบโครงงาน (Project Design Process)', 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1E293B')

    steps = [
        ("ขั้นที่ 1", "ศึกษาปัญหา\nและความต้องการ", "สำรวจพฤติกรรมการทานยา\nและข้อจำกัดของผู้สูงอายุ\nในชีวิตประจำวัน", "#EFF6FF", "#3B82F6"),
        ("ขั้นที่ 2", "ออกแบบสถาปัตยกรรม\nและระบบวงจร", "กำหนดฮาร์ดแวร์ Pi 4,\nเซนเซอร์ HC-SR04,\nกล้อง USB, ไฟ LED 3 สี", "#F0FDF4", "#22C55E"),
        ("ขั้นที่ 3", "ประกอบฮาร์ดแวร์\nและต่อวงจร", "เชื่อมต่อพิน GPIO,\nวงจรแบ่งแรงดัน 1k/2.2k,\nจัดวางอุปกรณ์ในกล่อง", "#FEF3C7", "#F59E0B"),
        ("ขั้นที่ 4", "พัฒนาซอฟต์แวร์ AI\nและระบบเสียง", "เขียนโปรแกรม YuNet, SFace,\nระบบเสียง Neural TTS\nและ Web Manager", "#F5F3FF", "#8B5CF6"),
        ("ขั้นที่ 5", "ทดสอบประสิทธิภาพ\nและประเมินผล", "ทดสอบการทำงาน 24/7,\nประเมินกลุ่มตัวอย่าง ปวส.\nจำนวน 20 คน", "#FFF1F2", "#F43F5E"),
    ]

    box_w = 2.0
    box_h = 2.1
    spacing = 0.35
    start_x = 0.35

    for i, (num, title, desc, bg, border) in enumerate(steps):
        x = start_x + i * (box_w + spacing)
        y = 0.5
        box = patches.FancyBboxPatch((x, y), box_w, box_h,
                                      boxstyle="round,pad=0.08,rounding_size=0.18",
                                      facecolor=bg, edgecolor=border, linewidth=2)
        ax.add_patch(box)

        # Header tag
        tag = patches.FancyBboxPatch((x + 0.3, y + box_h - 0.35), box_w - 0.6, 0.3,
                                     boxstyle="round,pad=0.04,rounding_size=0.1",
                                     facecolor=border, edgecolor=border)
        ax.add_patch(tag)
        ax.text(x + box_w/2, y + box_h - 0.2, num, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='#FFFFFF')

        ax.text(x + box_w/2, y + 1.25, title, ha='center', va='center',
                fontsize=10, fontweight='bold', color='#1E293B', linespacing=1.1)

        ax.text(x + box_w/2, y + 0.55, desc, ha='center', va='center',
                fontsize=7.8, color='#475569', linespacing=1.15)

        # Draw arrow to next step
        if i < len(steps) - 1:
            ax.annotate('', xy=(x + box_w + spacing - 0.05, y + box_h/2),
                        xytext=(x + box_w + 0.05, y + box_h/2),
                        arrowprops=dict(facecolor='#64748B', edgecolor='#475569', width=2.5, headwidth=7, headlength=7))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_design_process.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {path}")

def create_main_program_flowchart():
    """3. ภาพผังงานการทำงานของโปรแกรมหลัก (Main Program Flowchart)"""
    fig, ax = plt.subplots(figsize=(10, 15), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Title
    ax.text(5.0, 14.6, 'ผังงานการทำงานของระบบโปรแกรมหลัก (Main Program Flowchart)', 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1E293B')
    ax.text(5.0, 14.25, 'ระบบกล่องเตือนทานยาอัจฉริยะ (Hands-Free Edge AI Architecture)', 
            ha='center', va='center', fontsize=10.5, color='#64748B')

    def draw_rounded(x, y, w, h, text, bg='#EFF6FF', border='#3B82F6', fsize=9.5, bold=False):
        box = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                      boxstyle="round,pad=0.08,rounding_size=0.15",
                                      facecolor=bg, edgecolor=border, linewidth=1.8)
        ax.add_patch(box)
        weight = 'bold' if bold else 'normal'
        ax.text(x, y, text, ha='center', va='center', fontsize=fsize, fontweight=weight, color='#0F172A', linespacing=1.2)

    def draw_oval(x, y, w, h, text, bg='#E2E8F0', border='#475569'):
        box = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                      boxstyle="round,pad=0.1,rounding_size=0.45",
                                      facecolor=bg, edgecolor=border, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0F172A')

    def draw_diamond(x, y, w, h, text, bg='#FEF3C7', border='#F59E0B', fsize=8.8):
        pts = [[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]]
        poly = patches.Polygon(pts, facecolor=bg, edgecolor=border, linewidth=1.8, closed=True)
        ax.add_patch(poly)
        ax.text(x, y, text, ha='center', va='center', fontsize=fsize, fontweight='bold', color='#1E293B', linespacing=1.1)

    def draw_arrow(x1, y1, x2, y2, label=None, label_side='right'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor='#334155', edgecolor='#334155', width=1.5, headwidth=6, headlength=6))
        if label:
            offset_x = 0.2 if label_side == 'right' else -0.2
            ha = 'left' if label_side == 'right' else 'right'
            ax.text((x1 + x2)/2 + offset_x, (y1 + y2)/2, label, ha=ha, va='center',
                    fontsize=8.5, fontweight='bold', color='#0284C7')

    # Step 1: Start
    draw_oval(5.0, 13.6, 2.4, 0.6, "เริ่มต้น (Start)", bg='#DCFCE7', border='#16A34A')

    # Step 2: Init & Load models
    draw_rounded(5.0, 12.5, 5.6, 0.75, "เปิดระบบและโหลดโมเดล AI (YuNet & SFace)\nพร้อมแคชเสียงสังเคราะห์เข้าหน่วยความจำ RAM", bg='#F1F5F9', border='#64748B')
    draw_arrow(5.0, 13.3, 5.0, 12.88)

    # Step 3: Standby State
    draw_rounded(5.0, 11.35, 5.2, 0.7, "เข้าสู่สถานะ STANDBY\n[ไฟ LED สีแดงติดค้าง] (กล้อง Standby 1 FPS)", bg='#FEE2E2', border='#EF4444', bold=True)
    draw_arrow(5.0, 12.12, 5.0, 11.7)

    # Step 4: Decision - Ultrasonic detects person?
    draw_diamond(5.0, 9.9, 4.4, 1.3, "เซนเซอร์ Ultrasonic HC-SR04\nตรวจพบคนระยะ <= 45 ซม.?\n(ผ่านการกรอง 3 Burst Samples)")
    draw_arrow(5.0, 11.0, 5.0, 10.55)

    # Branch No -> Idle / Eco-Sleep check
    draw_diamond(8.3, 9.9, 2.6, 1.2, "ไม่มีคนเกิน\n60 วินาที?", bg='#F3E8FF', border='#A855F7', fsize=8.2)
    draw_arrow(7.2, 9.9, 7.0, 9.9, label="ไม่ใช่", label_side='right')

    # Eco-Sleep box
    draw_rounded(8.3, 8.2, 2.6, 0.8, "เข้าสู่โหมด ECO_SLEEP\n(ดับไฟ LED ทุกดวง,\nเซนเซอร์เข้า Sniffer 1.2s)", bg='#FAF5FF', border='#9333EA', fsize=7.5)
    draw_arrow(8.3, 9.3, 8.3, 8.6, label="ใช่")
    # Loop back from Eco-Sleep to Standby
    ax.plot([8.3, 8.3, 8.9, 8.9, 5.0], [7.8, 7.4, 7.4, 11.35, 11.35], color='#64748B', linestyle='--', linewidth=1.2)

    # Branch Yes -> Detecting State
    draw_rounded(5.0, 8.3, 5.2, 0.8, "เข้าสู่สถานะ DETECTING\n[ไฟ LED สีเหลืองติดสว่าง]\nปลุกกล้อง 15 FPS (Warm-up 8 เฟรมแรก)", bg='#FEF9C3', border='#EAB308', bold=True)
    draw_arrow(5.0, 9.25, 5.0, 8.7, label="ใช่", label_side='right')

    # Step 5: YuNet & SFace processing
    draw_rounded(5.0, 7.0, 5.4, 0.9, "ประมวลผลระบบปัญญาประดิษฐ์ใบหน้า:\n1. YuNet ตรวจจับพิกัดกรอบใบหน้า (Face Detection)\n2. SFace สกัดเวกเตอร์ 128 มิติ (128-D Feature Embedding)", bg='#E0F2FE', border='#0284C7')
    draw_arrow(5.0, 7.9, 5.0, 7.45)

    # Step 6: Decision - Member recognized?
    draw_diamond(5.0, 5.5, 4.4, 1.2, "ตรวจพบสมาชิกในครอบครัว?\n(Cosine Similarity >= 0.70)")
    draw_arrow(5.0, 6.55, 5.0, 6.1)

    # Branch Unknown visitor
    draw_rounded(1.5, 5.5, 2.4, 0.8, "บุคคลภายนอก/แขก\nเล่นเสียงต้อนรับสุภาพ\n(Anti-Spam Cooldown)", bg='#F1F5F9', border='#94A3B8', fsize=8.0)
    draw_arrow(2.8, 5.5, 2.7, 5.5, label="ไม่ใช่", label_side='left')
    ax.plot([1.5, 1.5, 1.5, 5.0], [5.1, 1.8, 1.8, 1.8], color='#64748B', linestyle='--', linewidth=1.2)

    # Step 7: Check medication slot & already taken
    draw_diamond(5.0, 3.9, 4.4, 1.2, "สมาชิกรับประทานยา\nในมื้อนี้เรียบร้อยแล้วหรือไม่?\n(Double-Dosing Hazard Check)")
    draw_arrow(5.0, 4.9, 5.0, 4.5, label="ใช่", label_side='right')

    # Branch Already taken -> Reassurance
    draw_rounded(8.5, 3.9, 2.4, 0.8, "ทานแล้ว (ปลอดภัย)\nพูดชมเชยและให้ความมั่นใจ\n'ไม่ต้องทานซ้ำแล้วนะคะ'", bg='#DCFCE7', border='#16A34A', fsize=8.0)
    draw_arrow(7.2, 3.9, 7.3, 3.9, label="ทานแล้ว", label_side='right')
    ax.plot([8.5, 8.5, 8.5, 5.0], [3.5, 1.8, 1.8, 1.8], color='#64748B', linestyle='--', linewidth=1.2)

    # Step 8: Announcing State
    draw_rounded(5.0, 2.4, 5.4, 0.9, "เข้าสู่สถานะ ANNOUNCING\n[ไฟ LED สีเขียวติดสว่าง]\nเล่นเสียงเตือนยาภาษาไทย (ขานชื่อ, มื้อ, สีซองยา)\nพร้อมบันทึกสถานะ Dual-Layer และส่ง Telegram", bg='#DCFCE7', border='#16A34A', bold=True)
    draw_arrow(5.0, 3.3, 5.0, 2.85, label="ยังไม่ทาน", label_side='right')

    # Step 9: Cooldown and Return
    draw_rounded(5.0, 1.2, 4.8, 0.65, "บันทึกสถานะทานยาสำเร็จ + เข้าสู่ช่วง Cooldown\nดับไฟเขียว -> กลับมาหยุดค้างที่ไฟสีแดง", bg='#EFF6FF', border='#3B82F6')
    draw_arrow(5.0, 1.95, 5.0, 1.52)

    # Step 10: End
    draw_oval(5.0, 0.35, 2.2, 0.5, "สิ้นสุด (End)", bg='#E2E8F0', border='#475569')
    draw_arrow(5.0, 0.88, 5.0, 0.6)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_program_flowchart.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {path}")

def create_state_machine_flowchart():
    """4. ภาพผังงานระบบอัตโนมัติ / สเตตแมชชีน (Autonomous State Machine)"""
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    ax.text(5.5, 7.1, 'ผังงานระบบอัตโนมัติและสถานะการทำงาน (Finite State Machine - FSM)', 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1E293B')
    ax.text(5.5, 6.7, 'การควบคุมการใช้พลังงาน, ไฟสถานะ 3 สี, และการประมวลผล Edge AI 24/7', 
            ha='center', va='center', fontsize=11, color='#64748B')

    # 4 Main States
    # State 1: STANDBY (Top Left)
    s1 = patches.FancyBboxPatch((0.8, 3.6), 3.8, 2.4, boxstyle="round,pad=0.1,rounding_size=0.2",
                                facecolor='#FEE2E2', edgecolor='#EF4444', linewidth=2.5)
    ax.add_patch(s1)
    ax.text(2.7, 5.65, '1. STANDBY (โหมดพร้อมทำงาน)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#991B1B')
    desc1 = (
        "• ไฟ LED สีแดงติดค้างนิ่ง\n"
        "• เซนเซอร์ HC-SR04 สแกนระยะบุคคล\n"
        "• กล้องรันโหมดประหยัด 1.0 FPS (ลดความร้อน)\n"
        "• ซีพียูสแตนด์บายต่ำกว่า 1% (RAM ~110MB)\n"
        "• พร้อมตอบสนองทันทีเมื่อมีคนเดินเข้ามา"
    )
    ax.text(1.05, 4.6, desc1, ha='left', va='center', fontsize=9.2, color='#1E293B', linespacing=1.2)

    # State 2: DETECTING (Top Right)
    s2 = patches.FancyBboxPatch((6.4, 3.6), 3.8, 2.4, boxstyle="round,pad=0.1,rounding_size=0.2",
                                facecolor='#FEF9C3', edgecolor='#EAB308', linewidth=2.5)
    ax.add_patch(s2)
    ax.text(8.3, 5.65, '2. DETECTING (โหมดสแกนใบหน้า)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#854D0E')
    desc2 = (
        "• ไฟ LED สีเหลืองติดสว่าง\n"
        "• ปลุกกล้องเร่งเฟรมเป็น 15 FPS อัตโนมัติ\n"
        "• Warm-up 8 เฟรมแรก ปรับสมดุลแสง AE/AWB\n"
        "• AI YuNet สแกนตรวจจับกรอบใบหน้า\n"
        "• AI SFace สกัดเวกเตอร์ Cosine Similarity"
    )
    ax.text(6.65, 4.6, desc2, ha='left', va='center', fontsize=9.2, color='#1E293B', linespacing=1.2)

    # State 3: ANNOUNCING (Bottom Right)
    s3 = patches.FancyBboxPatch((6.4, 0.6), 3.8, 2.3, boxstyle="round,pad=0.1,rounding_size=0.2",
                                facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=2.5)
    ax.add_patch(s3)
    ax.text(8.3, 2.55, '3. ANNOUNCING (โหมดแจ้งเตือนยา)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#166534')
    desc3 = (
        "• ไฟ LED สีเขียวติดสว่าง\n"
        "• ดึงข้อมูลมื้อยาประจำเวลาจาก med_config.json\n"
        "• เล่นเสียงสังเคราะห์ Neural TTS ชัดเจน นุ่มนวล\n"
        "• ขานชื่อ, มื้อยา, รายการยา และระบุสีซองยา\n"
        "• ส่งสรุปผลเข้ากลุ่ม Telegram ผู้ดูแลทันที"
    )
    ax.text(6.65, 1.55, desc3, ha='left', va='center', fontsize=9.2, color='#1E293B', linespacing=1.2)

    # State 4: ECO_SLEEP (Bottom Left)
    s4 = patches.FancyBboxPatch((0.8, 0.6), 3.8, 2.3, boxstyle="round,pad=0.1,rounding_size=0.2",
                                facecolor='#F3E8FF', edgecolor='#A855F7', linewidth=2.5)
    ax.add_patch(s4)
    ax.text(2.7, 2.55, '4. ECO_SLEEP (โหมดพักอุปกรณ์)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#6B21A8')
    desc4 = (
        "• ดับไฟ LED ทุกดวง (ประหยัดพลังงาน)\n"
        "• ทำงานเมื่อไม่มีคนหน้าหม้อหุงข้าวเกิน 60s\n"
        "• Ultrasonic เข้า Sniffer Mode (1.2s พัลส์)\n"
        "• ฮาร์ดแวร์ V4L2 คงสถานะ Ready ไร้ Deadlock\n"
        "• ตื่นทันทีใน 0.1s เมื่อมีคนเดินเข้ามา"
    )
    ax.text(1.05, 1.55, desc4, ha='left', va='center', fontsize=9.2, color='#1E293B', linespacing=1.2)

    # Transition Arrows
    # 1 -> 2: Standby to Detecting
    ax.annotate('', xy=(6.35, 4.9), xytext=(4.65, 4.9),
                arrowprops=dict(facecolor='#D97706', edgecolor='#B45309', width=2.5, headwidth=8, headlength=8))
    ax.text(5.5, 5.15, 'ตรวจพบคน\n<= 45 ซม.', ha='center', va='center', fontsize=8.8, fontweight='bold', color='#B45309')

    # 2 -> 3: Detecting to Announcing
    ax.annotate('', xy=(8.3, 2.95), xytext=(8.3, 3.55),
                arrowprops=dict(facecolor='#16A34A', edgecolor='#15803D', width=2.5, headwidth=8, headlength=8))
    ax.text(9.4, 3.25, 'รู้จำใบหน้าสำเร็จ\nหรือผู้มาเยือน', ha='left', va='center', fontsize=8.5, fontweight='bold', color='#15803D')

    # 3 -> 1: Announcing to Standby (Diagonal Return)
    ax.annotate('', xy=(4.65, 4.2), xytext=(6.35, 2.5),
                arrowprops=dict(facecolor='#3B82F6', edgecolor='#2563EB', width=2.5, headwidth=8, headlength=8))
    ax.text(5.5, 3.2, 'เตือนเสร็จสิ้น +\nบันทึก Cooldown', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2563EB')

    # 1 -> 4: Standby to Eco Sleep
    ax.annotate('', xy=(2.7, 2.95), xytext=(2.7, 3.55),
                arrowprops=dict(facecolor='#9333EA', edgecolor='#7E22CE', width=2.5, headwidth=8, headlength=8))
    ax.text(1.6, 3.25, 'ไม่มีความเคลื่อนไหว\nเกิน 60 วินาที', ha='right', va='center', fontsize=8.5, fontweight='bold', color='#7E22CE')

    # 4 -> 2: Eco Sleep to Detecting (Instant Wakeup)
    ax.annotate('', xy=(6.35, 4.3), xytext=(4.65, 2.0),
                arrowprops=dict(facecolor='#EA580C', edgecolor='#C2410C', width=2.5, headwidth=8, headlength=8))
    ax.text(5.5, 2.0, 'ตรวจพบคน\nปลุกระบบทันที', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#C2410C')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_state_machine.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {path}")

def create_system_architecture():
    """5. ภาพรวมโครงงาน / บล็อกไดอะแกรมระบบ (System Architecture Overview)"""
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    ax.text(6.0, 7.1, 'ภาพรวมโครงสร้างสถาปัตยกรรมระบบ (System Architecture Block Diagram)', 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#1E293B')
    ax.text(6.0, 6.7, 'การบูรณาการระบบสมองกลฝังตัว Edge AI, เซนเซอร์, ระบบเสียง และ Web Portal', 
            ha='center', va='center', fontsize=11, color='#64748B')

    # 3 Main Columns: Input, Edge Controller, Output

    # Column 1: Input Units (Left)
    col1 = patches.FancyBboxPatch((0.5, 0.7), 3.0, 5.6, boxstyle="round,pad=0.1,rounding_size=0.2",
                                  facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=2)
    ax.add_patch(col1)
    ax.text(2.0, 6.0, 'ส่วนรับข้อมูล (Input Unit)', ha='center', va='center', fontsize=12, fontweight='bold', color='#166534')

    in_items = [
        ("เซนเซอร์ Ultrasonic HC-SR04\n(Trig Pin 16 / Echo Pin 18)\nตรวจจับระยะบุคคล 30-45 ซม.", "#DCFCE7", 4.8),
        ("กล้อง USB Web Camera\n(ความละเอียด HD 720p/1080p)\nจับภาพใบหน้าสดระดับสายตา", "#DCFCE7", 3.4),
        ("เว็บพอร์ทัลจัดการข้อมูล (Web Portal)\n(PWA Responsive & QR Code)\nบันทึกรูปหน้า, ตารางยา และ Wi-Fi", "#DCFCE7", 1.8),
    ]
    for text, bg, y in in_items:
        b = patches.FancyBboxPatch((0.8, y - 0.55), 2.4, 1.1, boxstyle="round,pad=0.06,rounding_size=0.15",
                                  facecolor=bg, edgecolor='#86EFAC', linewidth=1.5)
        ax.add_patch(b)
        ax.text(2.0, y, text, ha='center', va='center', fontsize=8.8, color='#1E293B', linespacing=1.2)

    # Column 2: Central Edge Controller (Center)
    col2 = patches.FancyBboxPatch((4.1, 0.7), 3.8, 5.6, boxstyle="round,pad=0.1,rounding_size=0.2",
                                  facecolor='#EFF6FF', edgecolor='#2563EB', linewidth=2.5)
    ax.add_patch(col2)
    ax.text(6.0, 6.0, 'สมองกลฝังตัวหลัก (Edge AI Controller)', ha='center', va='center', fontsize=12, fontweight='bold', color='#1E40AF')

    core_items = [
        ("Raspberry Pi 4 Model B (Quad-Core 64-bit)\nระบบปฏิบัติการ Linux 64-bit (Debian)", "#DBEAFE", 5.0, 0.8),
        ("OpenCV YuNet Face Detector (~230KB)\nตรวจจับพิกัดใบหน้าความเร็วสูงใน RAM", "#FFFFFF", 4.05, 0.8),
        ("OpenCV SFace Recognizer (~37MB)\nสกัดคุณลักษณะใบหน้าเวกเตอร์ 128 มิติ", "#FFFFFF", 3.15, 0.8),
        ("Thai Phrase Builder & Edge-TTS Neural\nประกอบประโยคเสียงพูดสุภาพ ขานชื่อ และบอกสีซองยา", "#FFFFFF", 2.25, 0.8),
        ("Dual-Layer Medication Adherence Tracker\nบันทึกสถานะ RAM Disk (/dev/shm) + SD Card", "#FFFFFF", 1.35, 0.8),
    ]
    for text, bg, y, h in core_items:
        b = patches.FancyBboxPatch((4.3, y - h/2), 3.4, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                                  facecolor=bg, edgecolor='#93C5FD', linewidth=1.2)
        ax.add_patch(b)
        ax.text(6.0, y, text, ha='center', va='center', fontsize=8.5, color='#1E293B', linespacing=1.15)

    # Column 3: Output Units (Right)
    col3 = patches.FancyBboxPatch((8.5, 0.7), 3.0, 5.6, boxstyle="round,pad=0.1,rounding_size=0.2",
                                  facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=2)
    ax.add_patch(col3)
    ax.text(10.0, 6.0, 'ส่วนแสดงผลและแจ้งเตือน (Output Unit)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#991B1B')

    out_items = [
        ("หลอดไฟแสดงสถานะ 3 สี (LED)\n[สีแดง] (Pin 11): Standby\n[สีเหลือง] (Pin 13): Detecting\n[สีเขียว] (Pin 15): Announcing", "#FEE2E2", 4.8),
        ("ลำโพงเสียงพูดภาษาไทย\n(Mini Speaker 3.5mm / USB Audio)\nเล่นเสียงแจ้งเตือนผ่าน mpg123", "#FEE2E2", 3.4),
        ("การแจ้งเตือนทางไกล Telegram Bot\nส่งสรุปรายการยาที่ทานเข้ากลุ่มครอบครัว\nพร้อมเวลาและสถานะทันที", "#FEE2E2", 1.8),
    ]
    for text, bg, y in out_items:
        b = patches.FancyBboxPatch((8.8, y - 0.55), 2.4, 1.1, boxstyle="round,pad=0.06,rounding_size=0.15",
                                  facecolor=bg, edgecolor='#FCA5A5', linewidth=1.5)
        ax.add_patch(b)
        ax.text(10.0, y, text, ha='center', va='center', fontsize=8.8, color='#1E293B', linespacing=1.2)

    # Connecting Arrows
    ax.annotate('', xy=(4.05, 4.8), xytext=(3.55, 4.8), arrowprops=dict(facecolor='#16A34A', edgecolor='#16A34A', width=2, headwidth=6, headlength=6))
    ax.annotate('', xy=(4.05, 3.4), xytext=(3.55, 3.4), arrowprops=dict(facecolor='#16A34A', edgecolor='#16A34A', width=2, headwidth=6, headlength=6))
    ax.annotate('', xy=(4.05, 1.8), xytext=(3.55, 1.8), arrowprops=dict(facecolor='#16A34A', edgecolor='#16A34A', width=2, headwidth=6, headlength=6))

    ax.annotate('', xy=(8.45, 4.8), xytext=(7.95, 4.8), arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=2, headwidth=6, headlength=6))
    ax.annotate('', xy=(8.45, 3.4), xytext=(7.95, 3.4), arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=2, headwidth=6, headlength=6))
    ax.annotate('', xy=(8.45, 1.8), xytext=(7.95, 1.8), arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=2, headwidth=6, headlength=6))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig_system_architecture.png")
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {path}")

if __name__ == '__main__':
    print("Generating all 5 Flowcharts & Diagrams...")
    create_conceptual_framework()
    create_design_process()
    create_main_program_flowchart()
    create_state_machine_flowchart()
    create_system_architecture()
    print("All 5 Flowcharts & Diagrams successfully generated!")
