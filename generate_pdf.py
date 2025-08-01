from reportlab.platypus import SimpleDocTemplate, Frame, PageTemplate, Paragraph
from reportlab.platypus.flowables import FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from xml.sax.saxutils import escape

def generate_pdf(c_file_path, student_name, roll_no, date_str, output_text, output_pdf):
    # Prepare C comment-style header (top only)
    header_lines = [
        "/*****************************",
        f"{student_name}",
        f"{roll_no}",
        f"{date_str}",
        "**************************/",
        ""
    ]

    # Read original C code
    with open(c_file_path, "r") as f:
        code_lines = [line.rstrip() for line in f.readlines()]

    # Prepare output comment for the bottom
    footer_lines = ["", "/************OUTPUT*****************"] + \
                   [f" {line}" for line in output_text.strip().splitlines()] + \
                   ["*/"]

    # Combine all lines: header + code + footer
    full_lines = header_lines + code_lines + footer_lines

    # Style for the code
    style = ParagraphStyle(
        name='Code',
        fontName='Courier',
        fontSize=11.5,
        leading=13,
        spaceBefore=0,
        spaceAfter=0
    )

    # Convert lines to styled Paragraphs
    def format_line(line):
        html_safe = escape(line).replace(" ", "&nbsp;")
        return Paragraph(html_safe, style)

    paragraphs = [format_line(line) for line in full_lines]

    # Page layout
    page_width, page_height = A4
    margin = 10 * mm
    col_gap = 5 * mm
    col_width = (page_width - 2 * margin - col_gap) / 2
    col_height = page_height - 2 * margin

    # Create document and two-column frames
    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                            leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=margin)

    left_frame = Frame(margin, margin, col_width, col_height, id='left')
    right_frame = Frame(margin + col_width + col_gap, margin, col_width, col_height, id='right')

    template = PageTemplate(id='TwoCol', frames=[left_frame, right_frame])
    doc.addPageTemplates([template])

    # Let ReportLab handle text flow: no manual chunking
    flow = []
    for i, para in enumerate(paragraphs):
        flow.append(para)
        # Switch to right column after first column is filled
        if (i + 1) % 1000 == 0:  # optional large batch — safe fallback
            flow.append(FrameBreak())

    doc.build(flow)
