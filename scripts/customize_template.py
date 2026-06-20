"""Customize pandoc reference.docx for Zhongpu Consulting document standards."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import os

ref_path = r"C:\Users\cheng\zhongpu-consulting-advisory\templates\reference.docx"
doc = Document(ref_path)

# Normal style
style = doc.styles['Normal']
font = style.font
font.name = '等线'
font.size = Pt(10.5)
font.color.rgb = RGBColor(0x22, 0x22, 0x22)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '等线')

# Page margins (A4 Chinese standard)
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

# Heading styles: 黑体
for i, size in [(1, 22), (2, 15), (3, 12), (4, 11)]:
    sn = f'Heading {i}'
    if sn in [s.name for s in doc.styles]:
        hs = doc.styles[sn]
        hs.font.name = '黑体'
        hs.font.size = Pt(size)
        hs.font.bold = True
        hs.font.color.rgb = RGBColor(0, 0, 0)
        hs.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        if i == 1:
            hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            hs.paragraph_format.space_before = Pt(24)

doc.save(ref_path)
print(f"Template OK: {os.path.getsize(ref_path)} bytes")
