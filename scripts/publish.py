"""Zhongpu Consulting Document Publisher.
Converts markdown reports to DOCX (WPS/Office) with cover page + HTML5."""
import subprocess, os, sys, re, yaml, tempfile
from docx import Document as DocxDoc
from docx.shared import Pt, Cm, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

PANDOC = r"C:\Users\cheng\AppData\Local\Pandoc\pandoc"
TEMPLATE = r"C:\Users\cheng\zhongpu-consulting-advisory\templates\reference.docx"

def parse_frontmatter(md_path):
    """Extract YAML frontmatter from markdown."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1])
            body = parts[2]
            return meta, body
    return {}, content

def create_cover(meta, output_path):
    """Generate a professional cover page DOCX with geometric branding."""
    doc = DocxDoc()
    
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(0)
    section.bottom_margin = Cm(0)
    section.left_margin = Cm(0)
    section.right_margin = Cm(0)

    # Colors
    NAVY = RGBColor(0x0B, 0x1D, 0x3A)     # deep navy
    GOLD = RGBColor(0xC4, 0xA4, 0x5A)      # muted gold accent
    GRAY = RGBColor(0x66, 0x66, 0x66)
    LIGHT = RGBColor(0x99, 0x99, 0x99)

    # ── Top navy block ──
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    # Add a full-width colored paragraph with shading
    run = p.add_run(' ')
    run.font.size = Pt(80)
    # Add shading
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0B1D3A" w:val="clear"/>')
    p.paragraph_format.element.get_or_add_pPr().append(shading)

    # ── Spacer ──
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(50)
    p.paragraph_format.space_after = Pt(0)

    # ── Company name ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run('ZHONGPU')
    run.font.name = 'Arial'
    run.font.size = Pt(11)
    run.font.color.rgb = LIGHT
    run.bold = False
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(0)
    run2 = p2.add_run('中 普 咨 询')
    run2.font.name = '黑体'
    run2.font.size = Pt(26)
    run2.font.color.rgb = NAVY
    run2.bold = True
    run2.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    # ── Gold accent line ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(20)
    run = p.add_run('─' * 24)
    run.font.size = Pt(6)
    run.font.color.rgb = GOLD

    # ── Classification ──
    classification = meta.get('classification', '内部使用')
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(classification)
    run.font.name = '黑体'
    run.font.size = Pt(11)
    run.font.color.rgb = GOLD
    run.bold = True
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    # ── Project number ──
    proj = meta.get('project_number', '')
    if proj:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(32)
        run = p.add_run(proj)
        run.font.name = 'Arial'
        run.font.size = Pt(9)
        run.font.color.rgb = LIGHT

    # ── Main title ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    title = meta.get('title', '').strip('"').strip("'")
    run = p.add_run(title)
    run.font.name = '黑体'
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = NAVY
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    # ── Subtitle ──
    subtitle = meta.get('subtitle', '').strip('"').strip("'")
    if subtitle:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(50)
        run = p.add_run(subtitle)
        run.font.name = '等线'
        run.font.size = Pt(10.5)
        run.font.color.rgb = GRAY
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '等线')

    # ── Thin separator ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(24)
    run = p.add_run('─' * 20)
    run.font.size = Pt(4)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

    # ── Meta info ──
    author = meta.get('author', '中普咨询').strip('"').strip("'")
    date = meta.get('date', '2026年6月')
    info = [
        ('编制', author),
        ('日期', date),
    ]
    dept = meta.get('department', '')
    if dept:
        info.insert(0, ('部门', dept))

    for label, value in info:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(f'{label}  ')
        r1.font.name = '等线'
        r1.font.size = Pt(9)
        r1.font.color.rgb = LIGHT
        r1.element.rPr.rFonts.set(qn('w:eastAsia'), '等线')
        r2 = p.add_run(value)
        r2.font.name = '等线'
        r2.font.size = Pt(9)
        r2.font.color.rgb = GRAY
        r2.element.rPr.rFonts.set(qn('w:eastAsia'), '等线')

    # ── Bottom navy band ──
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(60)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(' ')
    run.font.size = Pt(20)
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0B1D3A" w:val="clear"/>')
    p.paragraph_format.element.get_or_add_pPr().append(shading)

    doc.save(output_path)
    return output_path

def merge_cover_and_body(cover_path, body_path, output_path, meta):
    """Merge cover page with body DOCX, adding headers/footers and proper body formatting."""
    cover_doc = DocxDoc(cover_path)
    body_doc = DocxDoc(body_path)

    # ── Post-process body: apply table borders and font consistency ──
    for table in body_doc.tables:
        # Set table borders
        tbl = table._tbl
        tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            '  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            '</w:tblBorders>'
        )
        # Remove existing borders
        for existing in tblPr.findall(qn('w:tblBorders')):
            tblPr.remove(existing)
        tblPr.append(borders)
        
        # Style header row (first row)
        if len(table.rows) > 0:
            for cell in table.rows[0].cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.name = '黑体'
                        run.font.size = Pt(10.5)
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0, 0, 0)
                        run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
                # Header shading
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="E8E8E8" w:val="clear"/>')
                cell._tc.get_or_add_tcPr().append(shading)
        
        # Style body rows
        for row in table.rows[1:]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.name = '仿宋'
                        run.font.size = Pt(10.5)
                        run.font.color.rgb = RGBColor(0, 0, 0)
                        run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    
    # ── Post-process body paragraphs ──
    for p in body_doc.paragraphs:
        for run in p.runs:
            if run.font.name and 'Heading' in (p.style.name if p.style else ''):
                continue
            # Force body text to 仿宋 16pt (三号)
            if not p.style or p.style.name == 'Normal':
                run.font.name = '仿宋'
                run.font.size = Pt(16)
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')

    # Combine documents
    merged = DocxDoc()
    
    # Copy cover
    for element in cover_doc.element.body:
        merged.element.body.append(element)

    merged.add_page_break()

    # Copy body
    for element in body_doc.element.body:
        merged.element.body.append(element)

    # Set body section margins (cover already has 0 margins)
    for i, section in enumerate(merged.sections):
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        if i > 0:  # body: GB/T 9704-2012
            section.top_margin = Cm(3.7)
            section.bottom_margin = Cm(3.5)
            section.left_margin = Cm(2.8)
            section.right_margin = Cm(2.6)

    # Headers/footers for body sections
    for i, section in enumerate(merged.sections):
        if i == 0:
            continue
        header = section.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = hp.add_run(f'中普咨询 | {meta.get("project_number", "")} | 机密')
        run.font.name = '仿宋'
        run.font.size = Pt(7.5)
        run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
        
        footer = section.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    merged.save(output_path)
    return output_path

def md_to_docx(body_md, dst, meta):
    """Convert markdown body to DOCX via pandoc."""
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w', encoding='utf-8', delete=False) as f:
        f.write(body_md)
        tmp_md = f.name
    
    cmd = [PANDOC, tmp_md, '-o', dst, '--reference-doc', TEMPLATE,
           '--from', 'markdown+pipe_tables+fenced_divs', '--to', 'docx',
           '--metadata', 'lang=zh-CN', '--toc', '--toc-depth=2']
    subprocess.run(cmd, check=True, timeout=60)
    os.unlink(tmp_md)
    return dst

def md_to_html(src, dst):
    """Convert markdown to HTML5 with embedded print CSS."""
    css_path = src.replace('.md', '.css')
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write('''@page { size: A4; margin: 2.54cm 3.17cm; @bottom-center { content: counter(page); } }
body { font-family: "DengXian","Microsoft YaHei","SimHei",sans-serif; font-size:10.5pt; line-height:1.8; color:#222; }
h1 { font-family: "SimHei","黑体",sans-serif; font-size:22pt; text-align:center; border-bottom:2px solid #333; padding-bottom:12pt; }
h2 { font-family: "SimHei","黑体",sans-serif; font-size:15pt; border-bottom:1px solid #ddd; }
h3 { font-family: "SimHei","黑体",sans-serif; font-size:12pt; color:#333; }
table { border-collapse:collapse; width:100%; font-size:9pt; }
th { background:#2d2d2d; color:#fff; padding:5pt 8pt; }
td { border:1px solid #ccc; padding:4pt 8pt; }
tr:nth-child(even) td { background:#fafafa; }
blockquote { font-family:"KaiTi","楷体",serif; font-size:9pt; color:#666; border-left:3px solid #999; padding-left:12pt; }
.cover { page-break-after:always; text-align:center; }
@media print { body { font-size:10pt; } }''')
    cmd = [PANDOC, src, '-o', dst, '--standalone', '--css', css_path,
           '--from', 'markdown+pipe_tables', '--to', 'html5', '--metadata', 'lang=zh-CN']
    subprocess.run(cmd, check=True, timeout=30)
    os.remove(css_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python publish.py <report.md>")
        sys.exit(1)

    src = sys.argv[1]
    base = os.path.splitext(src)[0]
    
    meta, body = parse_frontmatter(src)
    title = meta.get('title', os.path.basename(src)).strip('"').strip("'")

    print(f"[1/4] 封面生成: {title}")
    cover_path = os.path.join(tempfile.gettempdir(), 'zhongpu_cover.docx')
    create_cover(meta, cover_path)

    print("[2/4] → DOCX (WPS/Office)...")
    body_docx = os.path.join(tempfile.gettempdir(), 'zhongpu_body.docx')
    md_to_docx(body, body_docx, meta)
    
    docx_path = base + '.docx'
    merge_cover_and_body(cover_path, body_docx, docx_path, meta)
    print(f"      {docx_path} ({os.path.getsize(docx_path):,} bytes)")

    print("[3/4] → HTML5...")
    html_path = base + '.html'
    md_to_html(src, html_path)
    print(f"      {html_path} ({os.path.getsize(html_path):,} bytes)")

    # Cleanup
    for tmp in [cover_path, body_docx]:
        try:
            os.remove(tmp)
        except:
            pass
    
    print(f"[4/4] ✅ 出版完成")

if __name__ == '__main__':
    main()
