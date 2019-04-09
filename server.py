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
    return render_template("signin.html")

@app.route('/signin')
def signin():
    mysql = connectToMySQL("photobomb")
    query = "SELECT * FROM users WHERE id = %(user_id)s;"
    data = { "user_id": session['user_id'] }
    user_list = mysql.query_db(query, data)
    return render_template('signin.html', current_user = user_list[0])

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

#     mysql = connectToMySQL("quote_beltexam")
#     query = "SELECT users.first_name, users.last_name, quotes.author, quotes.quote, quotes.id, quotes.user_id, count(*) as likes FROM quotes JOIN users ON users.id = quotes.user_id LEFT JOIN likes on quotes.id = likes.quote_id GROUP BY users.first_name, users.last_name, quotes.author, quotes.quote, quotes.id, quotes.user_id;"
#     # data = {'user_id': session['user_id']}
#     user_quotes = mysql.query_db(query)

#     return render_template('quotes.html',
#         one_user = logged_user[0],
#         all_quotes = user_quotes,
#         loggedin_userid = session['user_id']
#     )

# @app.route("/addquotes", methods=['POST'])
# def add_quotes():
#     valid = True
#     if len(request.form['author']) < 3:
#     	valid = False
#     	flash("Please enter a valid author.")

#     if len(request.form['quote']) < 10:
#     	valid = False
#     	flash("Please enter a valid quote.")
    
#     if not valid:
#         return redirect('/quotes')

#     mysql = connectToMySQL("quote_beltexam")
#     query = "INSERT INTO quotes (author, quote, created_at, updated_at, user_id) VALUES (%(au)s, %(qu)s, NOW(), NOW(), %(user_id)s);"
#     data = {
#         "au": request.form["author"],
#         "qu": request.form["quote"],
#         "user_id": session['user_id']
#     }
#     mysql.query_db(query, data)
#     return redirect('/quotes')

# @app.route("/user/<user_id>")
# def user_page(user_id):
#     mysql = connectToMySQL("quote_beltexam")
#     query = "SELECT * FROM quotes WHERE user_id = %(user_id)s;"
#     data = {'user_id': user_id}
#     user_quotes = mysql.query_db(query, data)

#     mysql = connectToMySQL("quote_beltexam")
#     query = "SELECT first_name, last_name FROM users WHERE id = %(user_id)s;"
#     data = {'user_id': user_id}
#     selected_user = mysql.query_db(query, data)

#     return render_template('user.html', 
#         all_quotes = user_quotes,
#         one_user = selected_user[0]
#     )

# @app.route('/newuser', methods=['POST'])
# def users_new():
#     valid = True		
#     if len(request.form['fname']) < 1:
#     	valid = False
#     	flash("Please enter a first name")
#     if len(request.form['lname']) < 1:
#     	valid = False
#     	flash("Please enter a last name")
    
#     if not EMAIL_REGEX.match(request.form['email']):    # test whether a field matches the pattern
#         valid = False
#         flash("Invalid email address!")

#     if len(request.form['password']) < 8:
#         flash("Password must be at least 8 characters")
#         valid = False

#     if request.form['password'] != request.form['confirm']:
#         flash("Passwords must match")
#         valid = False

#     mysql = connectToMySQL('quote_beltexam')
#     validate_email_query = 'SELECT id FROM users WHERE email=%(email)s;'
#     form_data = {
#         'email': request.form['email']
#     }
#     existing_users = mysql.query_db(validate_email_query, form_data)

#     if existing_users:
#         flash("Email already in use")
#         valid = False

#     if not valid:
#         # redirect to the form page, don't create user
#         return redirect('/')

#     pw_hash = bcrypt.generate_password_hash(request.form['password'])
#     mysql = connectToMySQL("quote_beltexam")
#     query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(email)s, %(password_hash)s, NOW(), NOW());"
#     data = {
#         "fn": request.form["fname"],
#         "ln": request.form["lname"],
#         "email": request.form["email"],
#         "password_hash": pw_hash
#     }
#     user_id = mysql.query_db(query, data)  
#     session['user_id'] = user_id
#     return redirect('/quotes') 

# @app.route("/addlike/<quote_id>", methods=['POST'])
# def add_like(quote_id):

#     mysql = connectToMySQL("quote_beltexam")
#     query = "SELECT * FROM likes WHERE quote_id = %(quote_id)s and user_id = %(user_id)s;"
#     data = {
#         "user_id": session["user_id"],
#         "quote_id": quote_id
#     }
#     likes = mysql.query_db(query, data)

#     if len(likes) > 0:
#         flash("This has already been liked.")
#         return redirect('/quotes')

#     mysql = connectToMySQL("quote_beltexam")
#     query = "INSERT INTO likes (user_id, quote_id, created_at, updated_at) VALUES (%(u_id)s, %(q_id)s, NOW(), NOW());"
#     data = {
#         "u_id": session["user_id"],
#         "q_id": quote_id
#     }
#     mysql.query_db(query, data)
#     return redirect('/quotes')

# @app.route("/delete/<quote_id>", methods=['POST'])
# def delete(quote_id):
#     mysql = connectToMySQL("quote_beltexam")
#     query = "DELETE FROM likes WHERE quote_id = %(quote_id)s;"
#     data = {
#         "quote_id": quote_id
#     }
#     mysql.query_db(query, data)

#     mysql = connectToMySQL("quote_beltexam")
#     query = "DELETE FROM quotes WHERE id = %(quote_id)s;"
#     data = {
#         "quote_id": quote_id
#     }
#     mysql.query_db(query, data)
#     return redirect('/quotes')

# @app.route('/login', methods=['POST'])
# def login():
#     mysql = connectToMySQL("quote_beltexam")
#     query = "SELECT id, password FROM users WHERE email = %(email)s;"
#     data = { "email": request.form['email'] }
#     user_list = mysql.query_db(query, data)
#     if user_list:
#         user = user_list[0]
#         if bcrypt.check_password_hash(user['password'], request.form['password']):
#             session['user_id'] = user['id']
#             return redirect('/quotes')

#     flash("Email or password incorrect")
#     return redirect('/')

# @app.route('/myaccount')
# def account():
#     mysql = connectToMySQL("quote_beltexam")
#     query = "SELECT * FROM users WHERE id = %(user_id)s;"
#     data = { "user_id": session['user_id'] }
#     user_list = mysql.query_db(query, data)
#     return render_template('myaccount.html', current_user = user_list[0])

# @app.route('/myaccount', methods=['POST'])
# def change_account():
#     valid = True
#     if len(request.form['fname']) < 2:
#         flash("First name must be at least 2 characters")
#         valid = False

#     if len(request.form['lname']) < 2:
#         flash("Last name must be at least 2 characters")
#         valid = False

#     if not EMAIL_REGEX.match(request.form['email']):
#         flash("Email must be valid")
#         valid = False

#     mysql = connectToMySQL('quote_beltexam')
#     validate_email_query = 'SELECT id FROM users WHERE email=%(email)s;'
#     form_data = {
#         'email': request.form['email']
#     }
#     existing_users = mysql.query_db(validate_email_query, form_data)

#     if existing_users:
#         flash("Email already in use")
#         valid = False
    
#     if not valid:
#         return redirect('/myaccount')
    
#     mysql = connectToMySQL("quote_beltexam")
#     query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s WHERE id = %(id)s;"
#     data = { 
#         "first_name": request.form['fname'], 
#         "last_name": request.form['lname'],
#         "email": request.form['email'],
#         "id": session['user_id'],
#     }
#     mysql.query_db(query, data)
#     return redirect('/quotes')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)