from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/images'


# Ensure the image folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# File paths
BOOKS_FILE = "books.json"
STUDENTS_FILE = "students.json"
TEACHERS_FILE = "teachers.json"

# ------------------ Utility Functions ------------------
def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# ------------------ Routes ------------------
@app.route('/')
def home():
    if 'student_id' in session:
        return redirect(url_for('student_dashboard'))
    elif 'teacher_id' in session:
        return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        student_id = request.form['student_id']
        contact = request.form['contact']
        email = request.form['email']
        course = request.form['course']
        address = request.form['address']

        students = load_data(STUDENTS_FILE)
        if any(s['student_id'] == student_id for s in students):
            flash("Student ID already exists.", "danger")
            return redirect(url_for('register'))

        students.append({
            'name': name,
            'student_id': student_id,
            'contact': contact,
            'email': email,
            'course': course,
            'address' : address
        })
        save_data(STUDENTS_FILE, students)
        flash("Registered successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        students = load_data(STUDENTS_FILE)
        if any(s['student_id'] == student_id for s in students):
            session['student_id'] = student_id
            return redirect(url_for('student_dashboard'))
        flash("Invalid ID.", "danger")
    return render_template('login.html')

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        teachers = load_data(TEACHERS_FILE)
        if any(t['teacher_id'] == teacher_id for t in teachers):
            session['teacher_id'] = teacher_id
            return redirect(url_for('teacher_dashboard'))
        flash("Invalid ID.", "danger")
    return render_template('teacher_login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    students = load_data(STUDENTS_FILE)
    books = load_data(BOOKS_FILE)
    student = next((s for s in students if s['student_id'] == session['student_id']), None)
    issued_books = [book for book in books if book.get('issued_to') and book['issued_to']['id'] == session['student_id']]
    return render_template('student_dashboard.html', student=student, issued_books=issued_books)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    books = load_data(BOOKS_FILE)
    students = load_data(STUDENTS_FILE)
    return render_template('teacher_dashboard.html', books=books, students=students)





@app.route('/add_book', methods=['POST'])
def add_book():
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    books = load_data(BOOKS_FILE)
    books.append({
        'title': request.form['title'],
        'author': request.form['author'],
        'genre': request.form['genre'],
        'image': request.form.get('image', ''),
        'issued_to': None
    })
    save_data(BOOKS_FILE, books)
    return redirect(url_for('teacher_dashboard'))

@app.route('/issue_book/<int:index>', methods=['POST'])
def issue_book(index):
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    books = load_data(BOOKS_FILE)
    id_ = request.form['id']
    role = request.form.get('role' , 'student')
    if books[index]['issued_to'] is None:
        books[index]['issued_to'] = {'id': id_, 'role': role}
    save_data(BOOKS_FILE, books)
    return redirect(url_for('teacher_dashboard'))

@app.route('/return_book/<int:index>', methods=['POST'])
def return_book(index):
    if 'teacher_id' not in session:
        return redirect(url_for('teacher_login'))
    books = load_data(BOOKS_FILE)
    books[index]['issued_to'] = None
    save_data(BOOKS_FILE, books)
    return redirect(url_for('teacher_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
