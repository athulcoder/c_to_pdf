# C to PDF Converter

A web-based tool that allows users to compile and execute C programs, interact with them via a terminal-like interface, and export the code along with the output to a well-formatted PDF.

## Live Site

[https://c-to-pdf.onrender.com](https://c-to-pdf.onrender.com)

---

## Features

- Upload `.c` files via a simple web interface.
- Compile C code using `gcc` with error feedback if compilation fails.
- Terminal-like interface for runtime input and real-time output.
- Export a PDF that includes:
  - Student name, roll number, and date
  - The original C source code
  - The output of the program
  - Proper formatting with a two-column layout
  - Page numbers on each page
- Automatic deletion of temporary files after usage.

---

## How It Works

1. Upload a `.c` file.
2. The server compiles the file using GCC.
3. If compilation is successful, a terminal session is created using a pseudo-terminal.
4. Input is sent from the browser to the process, and output is streamed back.
5. Once the output is ready, a PDF can be generated with all the content.
6. PDF is served for download and deleted after delivery.
7. All `.c` and `.out` files are removed after PDF generation to ensure cleanup.

---

## Technology Stack

- **Backend**: Python, Flask, Flask-SocketIO, Eventlet
- **Frontend**: HTML, JavaScript, Socket.IO
- **PDF Generator**: ReportLab
- **Compiler**: GCC
- **Hosting**: Render.com
