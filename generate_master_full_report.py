# -*- coding: utf-8 -*-
"""
generate_master_full_report.py
Combines:
- Full Report from media_1794383665051_77929ef3.docx (Cover up to References)
- Inserts/Enhances Chapter 4 with the requested "4.2 สรุปผลการทดลองจากตาราง"
- Appends the complete adapted Appendices (ก, ข, ค, ง, จ) with all preserved images.
Output: ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ_รวมสมบูรณ์.docx
"""

import os
import copy
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls

MAIN_DOCX = r"C:\Users\TC-14\.gemini\antigravity\brain\1e427055-8308-42c9-a3e9-2ec63c0fdbc4\.user_uploaded\media_1794383665051_77929ef3.docx"
APPENDIX_DOCX = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects\ภาคผนวก_กล่องเตือนทานยาอัจฉริยะ_ฉบับสมบูรณ์.docx"
OUTPUT_MASTER = r"c:\Users\TC-14\Documents\GitHub\Rice-cooker-projects\ว-สอศ-3_2569_กล่องเตือนทานยาอัจฉริยะ_รวมสมบูรณ์.docx"

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

def format_run(run, font_name="TH SarabunPSK", font_size=16, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)

def add_p_styled(doc, text="", font_size=16, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if text:
        r = p.add_run(text)
        format_run(r, font_size=font_size, bold=bold, italic=italic)
    return p

def build_master():
    print("Loading main docx...")
    doc = docx.Document(MAIN_DOCX)
    
    # 1. Check Chapter 4 and find where to insert 4.2 สรุปผลการทดลอง
    # In MAIN_DOCX:
    # Find paragraph "บทที่ 4" and "บทที่ 5"
    p_indices = {}
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if "บทที่  4" in t or "บทที่ 4" in t:
            p_indices["ch4"] = i
        elif "บทที่  5" in t or "บทที่ 5" in t:
            p_indices["ch5"] = i
        elif "บรรณานุกรม" in t and i > 300:
            p_indices["bib"] = i
        elif "ภาคผนวก ก" in t and i > 350:
            p_indices["app_start"] = i
            break

    print("Key indices:", p_indices)

    # If ch4 and ch5 exist, let's see if 4.2 is present
    has_4_2 = any("4.2 สรุปผลการทดลอง" in doc.paragraphs[i].text for i in range(p_indices.get("ch4", 0), p_indices.get("ch5", len(doc.paragraphs))))
    print("Has 4.2 in Ch4:", has_4_2)

    # If not present, insert 4.2 before Chapter 5
    if not has_4_2 and "ch5" in p_indices:
        ch5_idx = p_indices["ch5"]
        p_ch5 = doc.paragraphs[ch5_idx]
        
        # We can insert paragraphs before p_ch5
        def insert_p_before(ref_p, text, font_size=16, bold=False, italic=False, space_before=4, space_after=4):
            new_p = OxmlElement('w:p')
            ref_p._p.addprevious(new_p)
            p_obj = docx.text.paragraph.Paragraph(new_p, ref_p._parent)
            p_obj.paragraph_format.space_before = Pt(space_before)
            p_obj.paragraph_format.space_after = Pt(space_after)
            p_obj.paragraph_format.line_spacing = 1.15
            if text:
                r = p_obj.add_run(text)
                format_run(r, font_size=font_size, bold=bold, italic=italic)
            return p_obj

        insert_p_before(p_ch5, "4.2 สรุปผลการทดลอง", font_size=16, bold=True, space_before=10, space_after=4)
        insert_p_before(p_ch5, "   จากการทดลองประสิทธิภาพและการศึกษาความพึงพอใจของกล่องเตือนทานยาอัจฉริยะ สามารถสรุปผลจากตารางที่ 4.1 และตารางที่ 4.2 ได้ดังนี้", font_size=16, space_after=4)
        insert_p_before(p_ch5, "   1. สรุปผลจากตารางที่ 4.1 ด้านประสิทธิภาพการทำงานของอุปกรณ์: ในการทดลองจำนวน 10 ครั้ง พบว่า ระบบสามารถตรวจจับและระบุตัวตนใบหน้าด้วยกล้อง AI (YuNet & SFace) ได้สำเร็จ 10 ครั้ง คิดเป็นร้อยละ 100.00 การแจ้งเตือนมื้อยาและรายการยาถูกต้องตามตารางเวลาสำเร็จ 9 ครั้ง คิดเป็นร้อยละ 90.00 และการสังเคราะห์เสียงภาษาไทยและการทำงานแบบออฟไลน์สำเร็จ 9 ครั้ง คิดเป็นร้อยละ 90.00 โดยมีค่าเฉลี่ยความสำเร็จรวมอยู่ที่ร้อยละ 93.33 แสดงให้เห็นว่าระบบกล่องเตือนทานยาอัจฉริยะมีประสิทธิภาพและความแม่นยำสูง สามารถทำงานแบบออฟไลน์ได้โดยไม่ต้องพึ่งพาอินเทอร์เน็ต", font_size=16, space_after=4)
        insert_p_before(p_ch5, "   2. สรุปผลจากตารางที่ 4.2 ด้านความพึงพอใจของผู้ใช้งานกลุ่มตัวอย่าง: จากกลุ่มตัวอย่างนักเรียน นักศึกษา จำนวน 30 คน พบว่า มีความพึงพอใจต่อกล่องเตือนทานยาอัจฉริยะโดยรวมอยู่ในระดับมากที่สุด (x̄ = 4.56, S.D. = 0.53) โดยเรียงตามลำดับรายด้านได้แก่ ด้านความสะดวกและการใช้งาน มีค่าเฉลี่ยสูงสุดเท่ากับ 4.59 (S.D. = 0.54) รองลงมาคือ ด้านความปลอดภัยและความน่าเชื่อถือของระบบ มีค่าเฉลี่ยเท่ากับ 4.55 (S.D. = 0.56) และด้านประสิทธิภาพของระบบการแจ้งเตือน มีค่าเฉลี่ยเท่ากับ 4.54 (S.D. = 0.50) ซึ่งสอดคล้องกับสมมติฐานการวิจัยที่ตั้งไว้", font_size=16, space_after=12)
        print("Inserted 4.2 into Chapter 4 successfully!")

    # 2. Now remove old incomplete appendices after bibliography and append the new complete appendices!
    # Let's find bibliography end
    bib_end_idx = None
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if "ภาคผนวก ก" in t and i > 350:
            bib_end_idx = i
            break

    if bib_end_idx is not None:
        print(f"Removing old appendices starting from paragraph {bib_end_idx}...")
        # Remove paragraphs from bib_end_idx to end
        for p in list(doc.paragraphs[bib_end_idx:]):
            p._p.getparent().remove(p._p)
        # Also remove tables that belong to old appendices (if any after bibliography)
        # Keep tables in chapters 1-5

    # 3. Append the complete new appendices from APPENDIX_DOCX
    print("Appending new complete appendices...")
    app_doc = docx.Document(APPENDIX_DOCX)
    
    # We can copy elements or build them directly using the helper
    # To ensure perfect styles and relations, let's copy body elements or call our builder
    # Since generate_merged_appendix_doc.py already built it cleanly, let's append all elements:
    for element in app_doc.part.element.body:
        # Don't copy sectPr unless at very end
        tag = element.tag.split('}')[-1]
        if tag != 'sectPr':
            doc.part.element.body.append(copy.deepcopy(element))
            
    # Copy images relations from app_doc to doc
    for rel_id, rel in app_doc.part.rels.items():
        if 'image' in rel.target_ref:
            doc.part.relate_to(rel.target_part, rel.reltype)

    doc.save(OUTPUT_MASTER)
    print(f"✅ Successfully created Master Document: {OUTPUT_MASTER} ({os.path.getsize(OUTPUT_MASTER)} bytes)")

if __name__ == "__main__":
    build_master()
