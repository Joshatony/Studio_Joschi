from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from rng import SecureRNG
import time
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Userdaten speichern in Datei
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

symbols = ["🍒", "🍋", "🔔", "🍀", "💎"]

@app.route('/')
def index():
    if "username" not in session:
        return redirect(url_for('login'))

    balance = session.get("balance", 100)
    return render_template('index.html', username=session["username"], balance=balance)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if username in users:
            return "Benutzer existiert bereits"
        users[username] = {"password": password}
        save_users(users)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form["username"]
        password = request.form["password"]
        if username in users and check_password_hash(users[username]["password"], password):
            session["username"] = username
            session["balance"] = 100
            return redirect(url_for("index"))
        return "Login fehlgeschlagen"
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/spin')
def spin():
    if "username" not in session:
        return jsonify({"error": "Nicht eingeloggt"})

    balance = session.get("balance", 100)
    bet = 10
    if balance < bet:
        return jsonify({"error": "Nicht genug Guthaben"})

    balance -= bet
    seed = str(time.time())
    rng = SecureRNG(seed)
    result = [rng.get_symbol(symbols) for _ in range(3)]

    if result[0] == result[1] == result[2]:
        winnings = 50
        balance += winnings
        message = f"Jackpot mit {result[0]}! Seed: {rng.get_seed_hash()}"
    else:
        message = f"Leider nichts – Seed: {rng.get_seed_hash()}"

    session["balance"] = balance
    return jsonify({
        "symbols": result,
        "message": message,
        "balance": balance,
        "seed": rng.get_seed_hash(),
        "original_seed": seed
    })

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/verify_result', methods=['POST'])
def verify_result():
    seed = request.form['seed']
    rng = SecureRNG(seed)
    result = [rng.get_symbol(symbols) for _ in range(3)]
    return render_template('verify_result.html', result=result, seed=seed, seed_hash=rng.get_seed_hash())

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/reload')
def reload():
    if "username" not in session:
        return jsonify({"error": "Nicht eingeloggt"})
    session["balance"] = 100
    return jsonify({"balance": session["balance"]})
@app.route('/slot/<name>')
def slot(name):
    if "username" not in session:
        return redirect(url_for('login'))

    if name == "classic":
        symbols = ["🍒", "🍋", "🔔"]
    elif name == "fancy":
        symbols = ["🦄", "👑", "💰", "💎", "🔥"]
    else:
        return "Unbekannter Slot"

    return render_template(f"slot_{name}.html", username=session["username"], balance=session["balance"])

@app.route('/book')
def book_slot():
    if "username" not in session:
        return redirect(url_for('login'))
    return render_template("book_josch.html", balance=session.get("balance", 100))

@app.route('/book_spin')
def book_spin():
    if "username" not in session:
        return jsonify({"error": "Nicht eingeloggt"})

    balance = session.get("balance", 100)
    bet = 10
    if balance < bet:
        return jsonify({"error": "Nicht genug Guthaben"})

    balance -= bet
    seed = str(time.time())
    rng = SecureRNG(seed)
    result = [rng.get_symbol(["symbol_1", "symbol_2", "symbol_3", "symbol_4", "symbol_5"]) for _ in range(5)]

    if result[0] == result[1] == result[2]:
        winnings = 100
        balance += winnings
        message = f"JACKPOT! Symbol: {result[0]} | Seed: {rng.get_seed_hash()}"
    else:
        message = f"Verloren – Seed: {rng.get_seed_hash()}"

    session["balance"] = balance
    return jsonify({
        "symbols": result,
        "message": message,
        "balance": balance
    })

@app.route('/slot_select')
def slot_select():
    if "username" not in session:
        return redirect('/login')
    return render_template("slot_select.html", balance=session.get("balance", 100))


