
from reportlab.platypus import SimpleDocTemplate, Frame, PageTemplate, Paragraph
from reportlab.platypus import FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from xml.sax.saxutils import escape
from reportlab.lib.enums import TA_LEFT
def generate_pdf(c_file_path, student_name, roll_no, date_str, output_text, output_pdf):
    
    header_lines = [
        "/*****************************",
        f"{student_name}",
        f"{roll_no}",
        f"{date_str}",
        "**************************/",
        ""
    ]


    with open(c_file_path, "r") as f:
        code_lines = [line.rstrip() for line in f.readlines()]

    footer_lines = ["", "/************OUTPUT*****************"] + \
                   [f" {line}" for line in output_text.strip().splitlines()] + \
                   ["*/"]


    full_lines = header_lines + code_lines + footer_lines


    style = ParagraphStyle(
        name='Code',
        fontName='Courier',
        fontSize=10,
        leading=12,
        spaceBefore=0,
        spaceAfter=0,
        alignment=TA_LEFT
    )


    def format_line(line):
        html_safe = escape(line).replace(" ", "&nbsp;")
        return Paragraph(html_safe, style)

    paragraphs = [format_line(line) for line in full_lines]

  
    page_width, page_height = A4
    margin = 10 * mm
    col_gap = 5 * mm
    col_width = (page_width - 2 * margin - col_gap) / 2
    col_height = page_height - 2 * margin

    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                            leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=margin)

    left_frame = Frame(margin, margin, col_width, col_height, id='left')
    right_frame = Frame(margin + col_width + col_gap, margin, col_width, col_height, id='right')

    template = PageTemplate(id='TwoCol', frames=[left_frame, right_frame])
    doc.addPageTemplates([template])

    
    flow = []
    for i, para in enumerate(paragraphs):
        flow.append(para)
       
        if (i + 1) % 1000 == 0:  
            flow.append(FrameBreak())

    doc.build(flow)
