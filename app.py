import os
import subprocess
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/run", methods=["POST"])
def run_c_code():
    cfile = request.files["cfile"]
    user_input = request.form.get("input", "")

    # Save uploaded file
    filename = secure_filename(cfile.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    cfile.save(filepath)

    # Prepare executable path
    exec_name = f"{uuid.uuid4().hex}.exe"
    exec_path = os.path.join(UPLOAD_FOLDER, exec_name)

    # Compile the C file
    compile_proc = subprocess.run(
        ["gcc", filepath, "-o", exec_path],
        capture_output=True,
        text=True
    )

    if compile_proc.returncode != 0:
        return jsonify({
            "status": "error",
            "output": compile_proc.stderr
        })

    # Run the executable and feed user input (stdin)
    try:
        run_proc = subprocess.run(
            [exec_path],
            input=user_input,
            capture_output=True,
            text=True,
            timeout=10,  # prevent infinite loops
            shell=True  # required for Windows
        )

        if run_proc.returncode != 0:
            output = f"Runtime Error:\n{run_proc.stderr}"
        else:
            output = run_proc.stdout

        return jsonify({
            "status": "success",
            "output": output
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "output": "Error: Program timed out. (Possible infinite loop)"
        })


if __name__ == "__main__":
    app.run(debug=True)
