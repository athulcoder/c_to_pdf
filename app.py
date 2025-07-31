from flask import Flask, Request, Response

app = Flask()

@app.route
def home():
    return Response