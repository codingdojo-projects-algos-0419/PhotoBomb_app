import re
from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL    # import the function that will return an instance of a connection

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "keep it secret, keep it safe"

@app.route("/")
def index():
    return render_template("photobomb.html")

@app.route('/signin')
def signin():
    return render_template("signin.html")

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("photobomb")
    query = "SELECT id, password FROM users WHERE email = %(email)s;"
    data = { "email": request.form['email'] }
    user_list = mysql.query_db(query, data)
    if user_list:
        user = user_list[0]
        if bcrypt.check_password_hash(user['password'], request.form['password']):
            session['user_id'] = user['id']
            return redirect('/dashboard')

    flash("Email or password incorrect")
    return redirect('/signin')

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/newuser', methods=['POST'])
def users_new():
    valid = True		
    if len(request.form['fname']) < 1:
    	valid = False
    	flash("Please enter a first name")
    if len(request.form['lname']) < 1:
    	valid = False
    	flash("Please enter a last name")
    
    if not EMAIL_REGEX.match(request.form['email']):    # test whether a field matches the pattern
        valid = False
        flash("Invalid email address!")

    if len(request.form['password']) < 8:
        flash("Password must be at least 8 characters")
        valid = False

    if request.form['password'] != request.form['confirm']:
        flash("Passwords must match")
        valid = False

    mysql = connectToMySQL('photobomb')
    validate_email_query = 'SELECT id FROM users WHERE email=%(email)s;'
    form_data = {
        'email': request.form['email']
    }
    existing_users = mysql.query_db(validate_email_query, form_data)

    if existing_users:
        flash("Email already in use")
        valid = False

    if not valid:
        # redirect to the form page, don't create user
        return redirect('/signin')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    mysql = connectToMySQL("photobomb")
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(email)s, %(password_hash)s, NOW(), NOW());"
    data = {
        "fn": request.form["fname"],
        "ln": request.form["lname"],
        "email": request.form["email"],
        "password_hash": pw_hash
    }
    user_id = mysql.query_db(query, data)  
    session['user_id'] = user_id
    return redirect('/dashboard') 

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/signin')
    mysql = connectToMySQL("photobomb")
    query = "SELECT first_name FROM users WHERE id = %(user_id)s;"
    data = {'user_id': session['user_id']}
    logged_user = mysql.query_db(query, data)

    mysql = connectToMySQL("photobomb")
    query = "SELECT users.first_name, users.last_name, photos.title, photos.keywords, photos.id, photos.user_id;"
    user_photo = mysql.query_db(query)

    return render_template('dashboard.html',
        one_user = logged_user[0],
        all_photos = user_photo,
        loggedin_userid = session['user_id']
    )

@app.route("/addimage", methods=['POST'])
def add_images():
    valid = True
    if len(request.form['photo']) < 3:
    	valid = False
    	flash("Please upload a valid image file.")

    if not valid:
        return redirect('/dashboard')

    mysql = connectToMySQL("photobomb")
    query = "INSERT INTO photos (photo, created_at, updated_at, user_id) VALUES (%(ph)s, NOW(), NOW(), %(user_id)s);"
    data = {
        "ph": request.form["photo"],
        "user_id": session['user_id']
    }
    mysql.query_db(query, data)
    return redirect('/dashboard')

@app.route('/profile')
def profile():
    mysql = connectToMySQL("photobomb")
    query = "SELECT * FROM users WHERE id = %(user_id)s;"
    data = { "user_id": session['user_id'] }
    user_list = mysql.query_db(query, data)
    return render_template('profile.html', current_user = user_list[0])

@app.route('/profile', methods=['POST'])
def change_profile():
    valid = True
    if len(request.form['fname']) < 2:
        flash("First name must be at least 2 characters")
        valid = False

    if len(request.form['lname']) < 2:
        flash("Last name must be at least 2 characters")
        valid = False

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email must be valid")
        valid = False

    mysql = connectToMySQL('photobomb')
    validate_email_query = 'SELECT id FROM users WHERE email=%(email)s;'
    form_data = {
        'email': request.form['email']
    }
    existing_users = mysql.query_db(validate_email_query, form_data)

    if existing_users:
        flash("Email already in use")
        valid = False
    
    if not valid:
        return redirect('/profile')
    
    mysql = connectToMySQL("photobomb")
    query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s WHERE id = %(id)s;"
    data = { 
        "first_name": request.form['fname'], 
        "last_name": request.form['lname'],
        "email": request.form['email'],
        "id": session['user_id'],
    }
    mysql.query_db(query, data)
    return redirect('/dashboard')

@app.route('/photo_1')
def photo1():
    return render_template("photo1.html")

@app.route('/photo_2')
def photo2():
    return render_template("photo2.html")

@app.route('/photo_3')
def photo3():
    return render_template("photo3.html")

@app.route('/photo_4')
def photo4():
    return render_template("photo4.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)