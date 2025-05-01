from flask import Flask, request, send_from_directory, render_template_string, redirect, make_response
import threading, time, random, os, csv
from datetime import datetime
from deception_logger import log_event

app = Flask(__name__)
CSV_LOG_FILE = "deception_log.csv"
FAKE_DIR = "fake_files"

FAKE_SQL_ERRORS = [
    "You have an error in your SQL syntax near '' at line 1",
    "Warning: mysql_fetch_array() expects parameter 1 to be resource, boolean given",
    "PG::SyntaxError: ERROR:  syntax error at or near \"'\"",
    "sqlsrv_query(): Invalid parameter array",
    "Fatal error: Call to a member function query() on null",
    "Uncaught mysqli_sql_exception: Commands out of sync; you can't run this command now",
    "java.sql.SQLException: ORA-00933: SQL command not properly ended",
    "System.Data.SqlClient.SqlException (0x80131904): Incorrect syntax near 'admin'",
    "Traceback (most recent call last): sqlite3.OperationalError: near \"admin\": syntax error"
]


@app.route("/", methods=["GET", "POST"])
def login():
    # Check if user already "logged in"
    if request.cookies.get("logged_in") == "yes":
        return redirect("/files")

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        ip = request.remote_addr

        try:
            with open("common_passwords.txt", "r") as f:
                valid_passwords = set(p.strip() for p in f.readlines())
        except FileNotFoundError:
            valid_passwords = set()

        if password in valid_passwords:
            log_event("login_success", ip, f"user='{username}' pass='{password}'")
            resp = make_response(redirect("/files"))
            resp.set_cookie("logged_in", "yes")
            return resp
        else:
            log_event("login_fail", ip, f"user='{username}' pass='{password}'")
            return render_template_string("<h3>Login failed</h3><p>Invalid credentials.</p><a href='/'>Try again</a>")

    html = """
    <h2>Internal Portal Login</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button type="submit">Login</button>
    </form>
    """
    return render_template_string(html)

@app.route("/files")
def file_list():
    if request.cookies.get("logged_in") != "yes":
        return redirect("/")

    files = os.listdir(FAKE_DIR)
    html = "<h1>Internal File Repository</h1><ul>"
    for f in files:
        html += f'<li><a href="/download/{f}">{f}</a></li>'
    html += "</ul><p><i>For authorized internal use only.</i></p>"
    return render_template_string(html)

@app.route("/download/<path:filename>")
def download_file(filename):
    if request.cookies.get("logged_in") != "yes":
        return redirect("/")

    log_event("download", request.remote_addr, f"filename='{filename}'")
    return send_from_directory(FAKE_DIR, filename, as_attachment=True)

@app.route("/query", methods=["GET", "POST"])
def sqli_handler():
    input_data = request.args.to_dict()
    input_data.update(request.form.to_dict())
    query = " ".join(input_data.values()).lower()

    if any(keyword in query for keyword in ["' or", "' and", "sleep(", "benchmark(", "--", "'=", "' like"]):
        delay = round(random.uniform(2, 6), 2)
        fake_error = random.choice(FAKE_SQL_ERRORS)
        log_event("sqli", request.remote_addr, f"query='{query}' delay={delay}s error='{fake_error}'")
        time.sleep(delay)
        return f"<html><body><h1>Database Error</h1><pre>{fake_error}</pre></body></html>"

    return "<html><body><h1>Query OK</h1><p>No error detected.</p></body></html>"

def start_sql_honeypot():
    def run():
        print("[+] SQLi/Web honeypot server running on port 8081")
        app.run(host="0.0.0.0", port=8081, debug=False, use_reloader=False)

    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
