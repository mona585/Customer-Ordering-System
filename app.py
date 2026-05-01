"""
app.py — Flask application entry point for the Customer Ordering System.
Each team member registers their Blueprint here.
"""

from flask import Flask, session, redirect, render_template
from database import init_db
from controllers.cart_controller import cart_bp

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-production"

# ── Register Blueprints ────────────────────────────────────────
app.register_blueprint(cart_bp)

# ── Initialize Database ────────────────────────────────────────
with app.app_context():
    init_db()

# ── Dev login (temporary — sets user_id = 1 in session) ───────
@app.route("/dev-login")
def dev_login():
    session["user_id"] = 1
    return redirect("/products")

# ── Products page ──────────────────────────────────────────────
@app.route("/products")
def products():
    if "user_id" not in session:
        return redirect("/dev-login")
    return render_template("products.html")

# ── Home redirect ──────────────────────────────────────────────
@app.route("/")
def home():
    return redirect("/dev-login")

if __name__ == "__main__":
    app.run(debug=True)
