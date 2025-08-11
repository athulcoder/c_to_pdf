import os
import uuid
import subprocess
import pty
import select
import shlex
from flask import send_from_directory, after_this_request
from generate_pdf import generate_pdf
import eventlet
eventlet.monkey_patch()  

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

sessions = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["cfile"]
    filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.c")
    file.save(filename)

    exec_name = filename.replace(".c", ".out")
    compile_proc = subprocess.run(["gcc", "-w", filename, "-o", exec_name], capture_output=True, text=True)

    if compile_proc.returncode != 0:
        return {"success": False, "output": compile_proc.stderr}

    session_id = uuid.uuid4().hex
    sessions[session_id] = {"exec": exec_name}
    return {"success": True, "session": session_id}

@socketio.on("start_execution")
def handle_execution(data):
    session_id = data.get("session")
    exec_path = sessions.get(session_id, {}).get("exec")
    if not exec_path:
        emit("terminal_output", "Executable not found.\n")
        return

    pid, fd = pty.fork()
    if pid == 0:
        os.execv(exec_path, [exec_path])
    else:
        sessions[session_id]["fd"] = fd
        sessions[session_id]["pid"] = pid

        while True:
            r, _, _ = select.select([fd], [], [], 0.1)
            if fd in r:
                try:
                    output = os.read(fd, 1024).decode()
                    socketio.emit("terminal_output", output)
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
            print(f"Deleted file: {file_path}",flush=True)
        except Exception as e:
            print(f"Error deleting file: {e}",flush=True)
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
        emit("pdf_generated", {"success": False, "error": "Invalid session"})
        return
    

    c_file_path = session["exec"].replace(".out", ".c")
    pdf_name = f"{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_name)

    try:
        generate_pdf(c_file_path, name, expname,rollno, date, output, pdf_path)
        emit("pdf_generated", {"success": True, "pdf_url": f"/download/{pdf_name}"})
    except Exception as e:
        emit("pdf_generated", {"success": False, "error": str(e)})


if __name__ == "__main__":
    socketio.run(app,host="0.0.0.0", port=8000)
