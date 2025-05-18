from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import subprocess

app = Flask(__name__)
app.secret_key = 'secretkey'  # Use a secure key in production

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html', username=session.get("username"))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    session['username'] = username
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = username
        return redirect(url_for('home'))
    return 'Invalid credentials. <a href="/">Try again</a>.'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Dashboard features (protected)
@app.route('/collect')
def collect_images():
    if 'username' not in session:
        return redirect(url_for('home'))
    subprocess.run(['python', 'collect_imgs.py'])
    return 'Image Collection Completed! <a href="/">Back to Dashboard</a>'

@app.route('/create_dataset')
def create_dataset():
    if 'username' not in session:
        return redirect(url_for('home'))
    subprocess.run(['python', 'create_dataset.py'])
    return 'Dataset Created! <a href="/">Back to Dashboard</a>'

@app.route('/train_model')
def train_model():
    if 'username' not in session:
        return redirect(url_for('home'))
    subprocess.run(['python', 'train_classifier.py'])
    return 'Model Trained! <a href="/">Back to Dashboard</a>'

@app.route('/inference')
def run_inference():
    if 'username' not in session:
        return redirect(url_for('home'))
    subprocess.run(['python', 'inference_classifier.py'])
    return 'Inference Started! Close the webcam window to end it.'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
