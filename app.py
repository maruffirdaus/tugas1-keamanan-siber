from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import bleach

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
is_logged_in = False

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    global is_logged_in
    is_logged_in = False
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    global is_logged_in
    if is_logged_in:
        # RAW Query
        students = db.session.execute(text('SELECT * FROM student')).fetchall()
        return render_template('index.html', students=students)
    else:
        return 'You are not authorized'
    
@app.route('/login', methods=['POST'])
def login():
    passkey = request.form['passkey']
    if passkey == 'Admin123':
        global is_logged_in
        is_logged_in = True
        return redirect('/dashboard')
    else:
        return redirect('/')

@app.route('/add', methods=['POST'])
def add_student():
    global is_logged_in
    if (is_logged_in):
        name = bleach.clean(request.form['name'])
        age = bleach.clean(request.form['age'])
        grade = bleach.clean(request.form['grade'])
        

        connection = sqlite3.connect('instance/students.db')
        cursor = connection.cursor()

        # RAW Query
        # db.session.execute(
        #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
        #     {'name': name, 'age': age, 'grade': grade}
        # )
        # db.session.commit()
        query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
        cursor.execute(query)
        connection.commit()
        connection.close()
        return redirect('/dashboard')
    else:
        return 'You are not authorized'


@app.route('/delete/<string:id>') 
def delete_student(id):
    global is_logged_in
    if (is_logged_in):
        # RAW Query
        db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
        db.session.commit()
        return redirect('/dashboard')
    else:
        return 'You are not authorized'


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    global is_logged_in
    if (is_logged_in):
        if request.method == 'POST':
            name = bleach.clean(request.form['name'])
            age = bleach.clean(request.form['age'])
            grade = bleach.clean(request.form['grade'])
            
            # RAW Query
            db.session.execute(text(f"UPDATE student SET\n name='{name}',\n age={age},\n grade='{grade}'\n WHERE id={id}"))
            db.session.commit()
            return redirect('/dashboard')
        else:
            # RAW Query
            student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
            return render_template('edit.html', student=student)
    else:
        return 'You are not authorized'

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

