"""Customize reference.docx — force every style to GB/T 9704-2012 at definition level."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import os

path = r"C:\Users\cheng\zhongpu-consulting-advisory\templates\reference.docx"
doc = Document(path)

# Page: A4 with GB/T margins
for sec in doc.sections:
    sec.page_width = Cm(21); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(3.7); sec.bottom_margin = Cm(3.5)
    sec.left_margin = Cm(2.8); sec.right_margin = Cm(2.6)

# Normal: 仿宋 16pt 28pt line spacing
ns = doc.styles['Normal']
ns.font.name = '仿宋'; ns.font.size = Pt(16); ns.font.color.rgb = RGBColor(0,0,0)
ns.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
ns.paragraph_format.line_spacing = Pt(28)
ns.paragraph_format.space_before = Pt(0); ns.paragraph_format.space_after = Pt(0)

# Heading 1: 宋体 22pt centered
h1 = doc.styles['Heading 1']
h1.font.name = '宋体'; h1.font.size = Pt(22); h1.font.bold = True; h1.font.color.rgb = RGBColor(0,0,0)
h1.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
h1.paragraph_format.line_spacing = Pt(28)

# Heading 2: 黑体 16pt
h2 = doc.styles['Heading 2']
h2.font.name = '黑体'; h2.font.size = Pt(16); h2.font.bold = False; h2.font.color.rgb = RGBColor(0,0,0)
h2.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
h2.paragraph_format.line_spacing = Pt(28)

# Heading 3: 楷体 16pt bold
h3 = doc.styles['Heading 3']
h3.font.name = '楷体'; h3.font.size = Pt(16); h3.font.bold = True; h3.font.color.rgb = RGBColor(0,0,0)
h3.element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
h3.paragraph_format.line_spacing = Pt(28)

# Heading 4: 仿宋 16pt bold
h4 = doc.styles['Heading 4']
h4.font.name = '仿宋'; h4.font.size = Pt(16); h4.font.bold = True; h4.font.color.rgb = RGBColor(0,0,0)
h4.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
h4.paragraph_format.line_spacing = Pt(28)

# Body Text: 仿宋 16pt (pandoc uses this for body paragraphs)
for sn in ['Body Text', 'Body Text 2', 'Body Text 3', 'Body Text Indent']:
    try:
        bt = doc.styles[sn]
        bt.font.name = '仿宋'; bt.font.size = Pt(16); bt.font.color.rgb = RGBColor(0,0,0)
        bt.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
        bt.paragraph_format.line_spacing = Pt(28)
    except: pass

# Table: 仿宋 10.5pt
ts = doc.styles['Table']
ts.font.name = '仿宋'; ts.font.size = Pt(10.5); ts.font.color.rgb = RGBColor(0,0,0)
ts.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
ts.paragraph_format.line_spacing = Pt(16)

# TOC styles
for sn in ['TOC 1', 'TOC 2', 'TOC Heading']:
    try:
        toc = doc.styles[sn]
        toc.font.name = '仿宋'; toc.font.size = Pt(12)
        toc.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    except: pass

doc.save(path)
print(f"Template: {os.path.getsize(path)} bytes — All styles GB/T 9704-2012")
