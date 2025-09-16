import os
import uuid
import subprocess
import pty
import select
from flask import send_from_directory, after_this_request, request, render_template, request, jsonify
from generate_pdf import generate_pdf
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')


sessions = {}

@app.route("/")
def index():
    return render_template("index.html")


def limit_resources():
    """Apply CPU, memory, and process limits inside child process."""
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))  # max 2 sec CPU
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))  # 256 MB RAM
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))  # max 10 processes
    resource.setrlimit(resource.RLIMIT_FSIZE, (10*1024*1024, 10*1024*1024))  # 10 MB file output

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("cfile")
    if not file:
        return jsonify({"success": False, "error": "no file uploaded"}), 400
    
    # validate file size (max 1MB)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 1 * 1024 * 1024:
        return jsonify({"success": False, "error": "file too large"}), 400
    
    # save file
    filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.c")
    file.save(filename)

    exec_name = filename.replace(".c", ".out")

    # compile safely
    try:
        compile_proc = subprocess.run(
            ["gcc", "-w", filename, "-o", exec_name],
            capture_output=True,
            text=False,         # don’t force UTF-8
            timeout=10          # prevent long compilation
        )
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "compilation timed out"}), 504

    stderr = compile_proc.stderr.decode(errors="replace")
    stdout = compile_proc.stdout.decode(errors="replace")

    if compile_proc.returncode != 0:
        return jsonify({"success": False, "output": stderr}), 200

    # register session
    session_id = uuid.uuid4().hex
    sessions[session_id] = {"exec": exec_name}

    return jsonify({
        "success": True,
        "session": session_id,
        "compile_stdout": stdout,
        "compile_stderr": stderr
    })
# @app.route("/upload", methods=["POST"])
# def upload():

#     file = request.files["cfile"]
#     filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.c")
#     file.save(filename)

#     exec_name = filename.replace(".c", ".out")
#     compile_proc = subprocess.run(["gcc", "-w", filename, "-o", exec_name], capture_output=True, text=True)

#     if compile_proc.returncode != 0:
#         return {"success": False, "output": compile_proc.stderr}

#     session_id = uuid.uuid4().hex
#     sessions[session_id] = {"exec": exec_name}
#     return {"success": True, "session": session_id}

@socketio.on("start_execution")
def handle_execution(data):
    session_id = data.get("session")
    exec_path = sessions.get(session_id, {}).get("exec")
    if not exec_path:
        emit("terminal_output", "Executable not found.\n", to=request.sid)
        return

    pid, fd = pty.fork()
    if pid == 0:
        os.execv(exec_path, [exec_path])
    else:
        sessions[session_id]["fd"] = fd
        sessions[session_id]["pid"] = pid
        sessions[session_id]["sid"] = request.sid   

        while True:
            r, _, _ = select.select([fd], [], [], 0.1)
            if fd in r:
                try:
                    output = os.read(fd, 1024).decode()
                    socketio.emit("terminal_output", output, to=request.sid)  
                except:
                    break

@socketio.on("send_input")
def handle_input(data):
    session_id = data.get("session")
    user_input = data.get("input", "")
    fd = sessions.get(session_id, {}).get("fd")
    if fd:
        os.write(fd, user_input.encode())

@app.route("/download/<filename>")
def download_pdf(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}", flush=True)
        except Exception as e:
            print(f"Error deleting file: {e}", flush=True)
        return response

    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@socketio.on("generate_pdf")
def handle_generate_pdf(data):
    session_id = data.get("session")
    name = data.get("name")
    expname = data.get("expname")
    rollno = data.get("rollno")
    date = data.get("date")
    output = data.get("output", "")

    session = sessions.get(session_id)
    if not session:
        emit("pdf_generated", {"success": False, "error": "Invalid session"}, to=request.sid)
        return

    c_file_path = session["exec"].replace(".out", ".c")
    pdf_name = f"{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_name)

    try:
        generate_pdf(c_file_path, name, expname, rollno, date, output, pdf_path)
        emit("pdf_generated", {"success": True, "pdf_url": f"/download/{pdf_name}"}, to=request.sid)
    except Exception as e:
        emit("pdf_generated", {"success": False, "error": str(e)}, to=request.sid)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000)
