# -*- coding: utf-8 -*-
"""
build_full_report_docx.py
Builds the complete Vocational Education Research Report (ว-สอศ.-3)
Title: กล่องเตือนทานยาอัจฉริยะ (Smart Medication Reminder Box)
Year: 2569 (2026)
Authors: นายกัณตพัฒน์ กระปุกทอง, นายณัฏฐวี ไกรทอง
Advisor: นายนิพนธ์ แก้วเกิด
Target Sample: นักศึกษา ปวส. แผนกวิชาเทคนิคคอมพิวเตอร์ จำนวน 20 คน
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOC_FILENAME = "ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ.docx"
FLOWCHART_DIR = "flowcharts"

def set_cell_background(cell, fill_hex):
    """Sets background shading of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets inner padding for a table cell."""
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
    """Applies clean, subtle borders to a table."""
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

def add_placeholder_box(doc, caption_text, subtext="คลิกขวาเพื่อแทรกรูปภาพอุปกรณ์จริง"):
    """Creates a clean, styled placeholder box for equipment photos that the user will insert."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(5.8)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=280, bottom=280, left=200, right=200)

    # Dashed border for the placeholder
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
    cap_p.paragraph_format.space_after = Pt(12)

def add_heading_styled(doc, text, level=1):
    h = doc.add_paragraph()
    r = h.add_run(text)
    r.font.name = "TH Sarabun New"
    r.font.bold = True
    if level == 1:
        h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r.font.size = Pt(18)
        r.font.color.rgb = RGBColor(15, 23, 42)
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r.font.size = Pt(16)
        r.font.color.rgb = RGBColor(30, 41, 59)
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
    else:
        h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r.font.size = Pt(15)
        r.font.color.rgb = RGBColor(51, 65, 85)
        h.paragraph_format.space_before = Pt(6)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_body_p(doc, text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text)
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_figure_image(doc, img_path, caption_text, width_inches=5.8):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(14)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = "TH Sarabun New"
        r_cap.font.size = Pt(13.5)
        r_cap.font.bold = True
        r_cap.font.color.rgb = RGBColor(71, 85, 105)
    else:
        add_placeholder_box(doc, caption_text, subtext=f"ไม่พบไฟล์ {img_path}")

print("Helper functions ready.")
