from flask import Flask, send_from_directory, request, abort
from flask_sock import Sock
import os, sys, subprocess, threading, uuid, atexit

BASE = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=None)
sock = Sock(app)

SESS = {}

@app.after_request
def headers(r):
    r.headers["Cache-Control"] = "no-store"
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r

@app.route("/")
def index():
    return send_from_directory(BASE, "index.html")

@app.route("/<path:p>")
def static_files(p):
    p = p.strip("/").replace("..", "")
    full = os.path.join(BASE, p)
    if os.path.isfile(full):
        return send_from_directory(BASE, p)
    abort(404)

def spawn(cmd):
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    exe = sys.executable
    args = [exe, "-u"] + cmd[1:]
    return subprocess.Popen(
        args, cwd=BASE,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=0, universal_newlines=True, encoding="utf-8", env=env
    )

def reader(proc, ws):
    buf = []
    try:
        while True:
            ch = proc.stdout.read(1)
            if ch == '' or ch is None:
                if buf: 
                    try: ws.send(''.join(buf))
                    except: pass
                break
            buf.append(ch)
            s = ''.join(buf)
            if ch == '\n' or s.endswith(': ') or s.endswith('? ') or len(s) >= 256:
                try: ws.send(s.rstrip('\r'))
                except: break
                buf = []
    finally:
        try: proc.stdout.close()
        except: pass

@sock.route("/ws")
def ws_run(ws):
    cmd = request.args.get("cmd", "/python/echo.py").lstrip("/")
    full = os.path.join(BASE, cmd)
    if not os.path.isfile(full):
        ws.send(f"[ERRORE] File non trovato: /{cmd}")
        ws.close(); return
    ws.send("Connesso. Avvio processo…")
    proc = spawn([sys.executable, full])
    t = threading.Thread(target=reader, args=(proc, ws), daemon=True)
    t.start()
    sid = str(uuid.uuid4())
    SESS[sid] = proc
    try:
        while True:
            msg = ws.receive()
            if msg is None: break
            if msg.strip() == "!stop":
                break
            try:
                proc.stdin.write(msg + "\n"); proc.stdin.flush()
            except: break
    finally:
        try: proc.terminate()
        except: pass
        try: proc.wait(timeout=2)
        except: pass
        SESS.pop(sid, None)
        try: ws.close()
        except: pass

def _cleanup():
    for p in list(SESS.values()):
        try: p.terminate()
        except: pass
atexit.register(_cleanup)

if __name__ == "__main__":
    print("http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)
