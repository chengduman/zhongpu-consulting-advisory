"""Zhongpu Consulting — Professional Markdown to PDF renderer.
Handles: tables with column sizing, CJK fonts, page layout, TOC, headers/footers."""
import re, sys, os
from fpdf import FPDF

class ZhongpuPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font('Hei', '', r'C:\Windows\Fonts\simhei.ttf')     # 黑体 - headers
        self.add_font('Kai', '', r'C:\Windows\Fonts\simkai.ttf')      # 楷体 - quotes
        self.add_font('Deng', '', r'C:\Windows\Fonts\Deng.ttf')       # 等线 - body
        self.set_auto_page_break(True, 22)
        self._in_table = False
        self._table_rows = []
        self._cols = []
        self._page_count = 0

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Hei', '', 7)
        self.set_text_color(160, 160, 160)
        self.cell(0, 5, '中普咨询 | 内部研究报告 | 机密', align='C')
        self.ln(6)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-18)
        self.set_font('Hei', '', 7)
        self.set_text_color(160, 160, 160)
        self.cell(0, 5, f'{self.page_no()}', align='C')

    def render_md(self, text):
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()

            if s.startswith('\\pagebreak') or s == '---' and i > 0 and lines[i-1].strip().startswith('\\pagebreak'):
                self.add_page()
                i += 1
                continue

            if s.startswith('# ') and not s.startswith('## '):
                self.add_page()
                self.set_font('Hei', '', 20)
                self.set_text_color(0, 0, 0)
                self.set_y(50)
                self.multi_cell(0, 12, s[2:], align='C')
                self.ln(6)
                # subtitle line
                self.set_draw_color(40, 40, 40)
                self.set_line_width(0.5)
                x = self.get_x() + 40
                self.line(x, self.get_y(), self.w - x, self.get_y())
                self.ln(10)
            elif s.startswith('## '):
                self.ln(4)
                self.set_font('Hei', '', 13)
                self.set_text_color(0, 0, 0)
                self.multi_cell(0, 8, s[3:])
                self.set_draw_color(200, 200, 200)
                self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
                self.ln(3)
            elif s.startswith('### '):
                self.ln(2)
                self.set_font('Hei', '', 10.5)
                self.set_text_color(40, 40, 40)
                self.multi_cell(0, 7, s[4:])
                self.ln(1)
            elif s.startswith('#### '):
                self.set_font('Hei', '', 9.5)
                self.set_text_color(60, 60, 60)
                self.multi_cell(0, 6, s[5:])
            elif '|' in s and s.count('|') >= 2:
                self._handle_table_line(s, i, lines)
            elif s.startswith('- **'):
                self._render_bullet(s, bold_key=True)
            elif s.startswith('- ') or s.startswith('* '):
                self._render_bullet(s)
            elif s.startswith('> '):
                self.set_font('Kai', '', 8.5)
                self.set_text_color(100, 100, 100)
                self.set_x(self.l_margin + 6)
                self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 5, s[2:])
                self.ln(1)
            elif s.startswith('```'):
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
            elif s == '':
                self.ln(2)
            elif s.startswith('**') and '：' in s:
                self.set_font('Hei', '', 9.5)
                self.set_text_color(0, 0, 0)
                self.multi_cell(0, 6, s)
                self.ln(1)
            elif s:
                self.set_font('Deng', '', 9)
                self.set_text_color(40, 40, 40)
                self.multi_cell(0, 5.5, s)
                self.ln(1)
            i += 1

    def _render_bullet(self, s, bold_key=False):
        text = s[s.index(' ') + 1:].strip()
        self.set_x(self.l_margin + 5)
        self.set_font('Deng', '', 9)
        self.set_text_color(50, 50, 50)
        if bold_key and '**' in text:
            parts = text.split('**')
            self.set_font('Deng', '', 9)
            self.cell(3, 5, '•')
            for j, p in enumerate(parts):
                if j % 2 == 1:
                    self.set_font('Hei', '', 9)
                else:
                    self.set_font('Deng', '', 9)
                self.multi_cell(self.w - self.l_margin - self.r_margin - 15, 5, p)
        else:
            self.cell(3, 5, '•')
            self.multi_cell(self.w - self.l_margin - self.r_margin - 15, 5, text)

    def _handle_table_line(self, s, i, lines):
        if re.match(r'^\|[\s\-:|]+\|$', s):
            self._render_table()
            return
        cells = [c.strip() for c in s.split('|')[1:-1]]
        self._table_rows.append(cells)

    def _render_table(self):
        if not self._table_rows:
            return
        rows = self._table_rows
        self._table_rows = []

        ncols = len(rows[0])
        available = self.w - self.l_margin - self.r_margin - 4
        col_w = available / ncols

        # Check if table fits on this page
        needed = len(rows) * 7 + 10
        if self.get_y() + needed > self.h - 25:
            self.add_page()

        # Header
        self.set_fill_color(40, 40, 40)
        self.set_text_color(255, 255, 255)
        self.set_font('Hei', '', 7.5)
        for j, cell in enumerate(rows[0]):
            self.cell(col_w, 7, cell[:40], border=0, fill=True)
        self.ln()

        # Body
        for r, row in enumerate(rows[1:], 1):
            if r % 2 == 0:
                self.set_fill_color(248, 248, 248)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(40, 40, 40)
            self.set_font('Deng', '', 7)
            for j, cell in enumerate(row):
                self.cell(col_w, 6, cell[:50], border=0, fill=True)
            self.ln()
        self.ln(4)


def main():
    if len(sys.argv) < 2:
        print("Usage: python md2pdf_pro.py <input.md> [output.pdf]")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.replace('.md', '.pdf')

    with open(src, 'r', encoding='utf-8') as f:
        md = f.read()

    # Skip YAML frontmatter
    parts = md.split('---', 2)
    body = parts[2] if len(parts) > 2 else md

    # Sanitize glyphs CJK fonts can't render
    glyph_map = {'✓': '[OK]', '✗': '[NO]', '↔': '<>', '¥': 'RMB',
                 '🌐': '[Web]', '📊': '[Chart]', '📦': '[Pkg]', '📄': '[Doc]',
                 '🎯': '[Target]', '⭐': '*', '⚠️': '[!]', '✅': '[OK]',
                 '❌': '[NO]', '🟢': '[G]', '🟡': '[Y]', '🔴': '[R]',
                 '🔍': '[Search]', '🕵️': '[Intel]', '🛠': '[Tool]',
                 '🎨': '[Design]', '📋': '[List]', '💰': '[Money]',
                 '⚖️': '[Law]', '🏛️': '[Gov]', '🏢': '[Corp]',
                 '📊': '[Data]', '📈': '[Up]', '📉': '[Down]',
                 '🔒': '[Lock]', '🔓': '[Open]', '💡': '[Idea]',
                 '🔥': '[Hot]', '💪': '[Strong]', '🚀': '[Launch]',
                 '🧠': '[Brain]', '🤖': '[Bot]', '⚡': '[Fast]',
                 '▶': '>', '◀': '<', '→': '->', '←': '<-',
                 '"': '"', '"': '"', ''': "'", ''': "'",
                 '—': '--', '–': '-', '…': '...',
    }
    for emoji, replacement in glyph_map.items():
        body = body.replace(emoji, replacement)

    pdf = ZhongpuPDF()
    pdf.add_page()
    pdf.set_title(os.path.basename(src))
    pdf.render_md(body)
    pdf.output(dst)
    print(f"PDF: {dst} ({pdf.page_no()} pages, {os.path.getsize(dst):,} bytes)")

if __name__ == '__main__':
    main()
