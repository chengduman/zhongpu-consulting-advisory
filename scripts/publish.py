"""Zhongpu Consulting Document Publisher.
Converts markdown reports to DOCX (WPS/Office compatible) and HTML5."""
import subprocess, os, sys, re

TEMPLATE = r"C:\Users\cheng\zhongpu-consulting-advisory\templates\reference.docx"
PANDOC = r"C:\Users\cheng\AppData\Local\Pandoc\pandoc"

def sanitize_md(text):
    """Remove/escape elements that break pandoc."""
    # Remove \pagebreak (pandoc handles page breaks differently)
    text = text.replace('\\pagebreak', '')
    # Fix YAML frontmatter — remove non-standard keys
    lines = text.split('\n')
    # Keep only title, author, date in frontmatter
    return text

def md_to_docx(src, dst):
    """Convert markdown to professional DOCX."""
    cmd = [
        PANDOC, src,
        '-o', dst,
        '--reference-doc', TEMPLATE,
        '--from', 'markdown+pipe_tables+fenced_divs+bracketed_spans',
        '--to', 'docx',
        '--metadata', 'lang=zh-CN',
        '--toc', '--toc-depth=2',
    ]
    subprocess.run(cmd, check=True, timeout=60)

def md_to_html(src, dst):
    """Convert markdown to HTML5 with embedded CSS for print."""
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

    print(f"[1/3] Sanitizing {os.path.basename(src)}...")
    with open(src, 'r', encoding='utf-8') as f:
        md = f.read()
    # Skip YAML frontmatter for DOCX but keep body
    parts = md.split('---', 2)
    body = parts[2] if len(parts) > 2 else md
    
    tmp = base + '.tmp.md'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(body)

    print("[2/3] → DOCX (WPS/Office)...")
    docx_path = base + '.docx'
    md_to_docx(tmp, docx_path)
    print(f"      {docx_path} ({os.path.getsize(docx_path):,} bytes)")

    print("[3/3] → HTML5...")
    html_path = base + '.html'
    md_to_html(tmp, html_path)
    print(f"      {html_path} ({os.path.getsize(html_path):,} bytes)")

    os.remove(tmp)
    print("Done.")

if __name__ == '__main__':
    main()
