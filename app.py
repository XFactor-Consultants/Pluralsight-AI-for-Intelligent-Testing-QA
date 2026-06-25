#m1
from flask import Flask, request, redirect

app = Flask(__name__)

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<body>
  <form method="POST" action="/login">
    <input id="user-email"    name="email"    type="text"     placeholder="Email" /><br>
    <input id="user-password" name="password" type="password" placeholder="Password" /><br>
    <button id="submit-btn"   type="submit">Login</button>
  </form>
</body>
</html>
"""

@app.route("/login", methods=["GET"])
def login():
    return LOGIN_PAGE

@app.route("/login", methods=["POST"])
def do_login():
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    return "<h5>Dashboard</h5 >"

if __name__ == "__main__":
    app.run(port=3000)