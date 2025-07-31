import os
import subprocess
from datetime import datetime
from flask import Flask, request, render_template, send_file, redirect, url_for
from fpdf import FPDF
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

class CompactPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)
        self.set_font("Courier", size=8)
        self.left_margin = 10
        self.right_margin = 10
        self.top_margin = 10
        self.bottom_margin = 10
        self.column_gap = 5
        self.column_width = (210 - self.left_margin - self.right_margin - self.column_gap) / 2
        self.line_height = 4
        self.current_column = 0
        self.x_positions = [
            self.left_margin,
            self.left_margin + self.column_width + self.column_gap
        ]
        self.y_positions = [self.top_margin, self.top_margin]

    def add_code_block(self, text):
        lines = text.split('\n')
        for line in lines:
            if self.y_positions[self.current_column] + self.line_height > 297 - self.bottom_margin:
                self.current_column += 1
                if self.current_column >= len(self.x_positions):
                    self.add_page()
                    self.current_column = 0
                    self.y_positions = [self.top_margin, self.top_margin]
            x = self.x_positions[self.current_column]
            y = self.y_positions[self.current_column]
            self.set_xy(x, y)
            self.multi_cell(self.column_width, self.line_height, line, border=0)
            self.y_positions[self.current_column] = self.get_y()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        date = request.form.get("date") or datetime.today().strftime("%d-%m-%Y")
        cfile = request.files["cfile"]

        safe_filename = secure_filename(cfile.filename)
        filename = os.path.join(UPLOAD_FOLDER, safe_filename)
        cfile.save(filename)

        with open(filename, "r") as f:
            code = f.read()

        # Use .exe for Windows
        exec_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}.exe")
        compile_proc = subprocess.run(["gcc", "-w", filename, "-o", exec_path]
, capture_output=True, text=True)

        if compile_proc.returncode != 0:
            output = "Compilation Error:\n" + compile_proc.stderr
        else:
            # Use shell=True for Windows
            run_proc = subprocess.run([exec_path], capture_output=True, text=True, shell=True)
            output = run_proc.stdout.strip() if run_proc.returncode == 0 else "Runtime Error:\n" + run_proc.stderr.strip()

        out_txt_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_output.txt")
        with open(out_txt_path, "w") as out_file:
            out_file.write(output)

        pdf = CompactPDF()
        pdf.add_page()
        pdf.add_code_block(f"""/* 
Name: {name}
Roll No: {roll}
Date: {date}
*/""")
        pdf.add_code_block(code)
        pdf.add_code_block(f"""\n/* 
Output:
{output}
*/""")

        pdf_filename = f"{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        pdf.output(pdf_path)

        return redirect(url_for("preview_pdf", filename=pdf_filename))

    return render_template("index.html")

@app.route("/preview/<filename>")
def preview_pdf(filename):
    return render_template("preview.html", filename=filename)

@app.route("/pdfs/<filename>")
def get_pdf(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == "__main__":
    app.run(debug=True)
