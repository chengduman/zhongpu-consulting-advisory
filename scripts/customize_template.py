"""Customize reference.docx per GB/T 9704-2012 党政机关公文格式 (latest)."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

ref_path = r"C:\Users\cheng\zhongpu-consulting-advisory\templates\reference.docx"
doc = Document(ref_path)

# ═══════════════════════════════════════════════════
# GB/T 9704-2012 党政机关公文格式
# 
# 页边距: 上37mm 下35mm 左28mm 右26mm
# 标题: 小标宋体 二号(22pt), 居中 (无则用宋体代替)
# 一级标题: 黑体 三号(16pt)  
# 二级标题: 楷体 三号(16pt) 加粗
# 三级标题: 仿宋 三号(16pt) 加粗
# 正文: 仿宋 三号(16pt)  
# 行距: 28磅固定值
# 页码: 宋体 四号(14pt) 左右各"一"字线
# ═══════════════════════════════════════════════════

# Page margins (exact from standard)
for section in doc.sections:
    section.top_margin = Cm(3.7)
    section.bottom_margin = Cm(3.5)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.6)

# ── Normal: 仿宋 三号(16pt), 28pt fixed line spacing ──
style = doc.styles['Normal']
style.font.name = '仿宋'
style.font.size = Pt(16)
style.font.color.rgb = RGBColor(0, 0, 0)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
pf = style.paragraph_format
pf.line_spacing = Pt(28)
pf.space_before = Pt(0)
pf.space_after = Pt(0)

# ── Heading 1: 宋体 二号(22pt) centered (代替小标宋) ──
if 'Heading 1' in [s.name for s in doc.styles]:
    hs = doc.styles['Heading 1']
    hs.font.name = '宋体'
    hs.font.size = Pt(22)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hs.paragraph_format.space_before = Pt(0)
    hs.paragraph_format.space_after = Pt(0)
    hs.paragraph_format.line_spacing = Pt(28)

# ── Heading 2: 黑体 三号(16pt) ──
if 'Heading 2' in [s.name for s in doc.styles]:
    hs = doc.styles['Heading 2']
    hs.font.name = '黑体'
    hs.font.size = Pt(16)
    hs.font.bold = False  # 公文一级标题不加粗
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    hs.paragraph_format.space_before = Pt(0)
    hs.paragraph_format.space_after = Pt(0)
    hs.paragraph_format.line_spacing = Pt(28)

# ── Heading 3: 楷体 三号(16pt) ──
if 'Heading 3' in [s.name for s in doc.styles]:
    hs = doc.styles['Heading 3']
    hs.font.name = '楷体'
    hs.font.size = Pt(16)
    hs.font.bold = True  # 公文二级标题加粗
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    hs.paragraph_format.space_before = Pt(0)
    hs.paragraph_format.space_after = Pt(0)
    hs.paragraph_format.line_spacing = Pt(28)

# ── Heading 4: 仿宋 三号(16pt) bold ──
if 'Heading 4' in [s.name for s in doc.styles]:
    hs = doc.styles['Heading 4']
    hs.font.name = '仿宋'
    hs.font.size = Pt(16)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    hs.paragraph_format.space_before = Pt(0)
    hs.paragraph_format.space_after = Pt(0)
    hs.paragraph_format.line_spacing = Pt(28)

# ── Table style: 仿宋 五号(10.5pt) ──
if 'Table' in [s.name for s in doc.styles]:
    ts = doc.styles['Table']
    ts.font.name = '仿宋'
    ts.font.size = Pt(10.5)
    ts.font.color.rgb = RGBColor(0, 0, 0)
    ts.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    ts.paragraph_format.line_spacing = Pt(16)
    ts.paragraph_format.space_before = Pt(0)
    ts.paragraph_format.space_after = Pt(0)

doc.save(ref_path)
print(f"GB/T 9704-2012 template: {os.path.getsize(ref_path)} bytes")
print("  仿宋16pt | 28磅行距 | 页边距37/35/28/26mm")
