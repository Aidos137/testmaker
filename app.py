from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Замени на свой ключ

# 🔧 База данных
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT,
        correct TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# 🔐 Логин
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        data = c.fetchone()
        conn.close()
        if data:
            session['username'] = data[1]
            session['role'] = data[3]
            return redirect(url_for('dashboard'))
        else:
            return "Неверный логин или пароль"
    return render_template('login.html')

# 🏠 Панель
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    role = session['role']
    if role == 'teacher':
        return render_template('dashboard_teacher.html')
    else:
        return render_template('dashboard_student.html')

# ➕ Добавить тест
@app.route('/add_test', methods=['GET', 'POST'])
def add_test():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    if request.method == 'POST':
        q = request.form['question']
        o1 = request.form['option1']
        o2 = request.form['option2']
        o3 = request.form['option3']
        o4 = request.form['option4']
        correct = request.form['correct']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO tests (question, option1, option2, option3, option4, correct) VALUES (?, ?, ?, ?, ?, ?)",
                  (q, o1, o2, o3, o4, correct))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_test.html')

# 📋 Пройти тест
@app.route('/take_test', methods=['GET', 'POST'])
def take_test():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tests")
    questions = c.fetchall()
    conn.close()

    if request.method == 'POST':
        score = 0
        for q in questions:
            qid = str(q[0])
            answer = request.form.get(qid)
            if answer == q[6]:
                score += 1
        return render_template('result.html', score=score, total=len(questions))

    return render_template('test.html', questions=questions)

# 🚪 Выход
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
