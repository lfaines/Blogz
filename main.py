from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root2019*@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y3337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    entry = db.Column(db.String(2500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, entry, owner):
        self.name = name
        self.entry = entry
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(40), unique = True)
    password = db.Column(db.String(40))
    blogs =  db.relationship('Blog', backref='owner')#sqlalchemy should populate the blog list with things from the class blog such that the owner property is equal to the user

    def __init__(self, username, password):
        self.username = username
        self.password = password
   
@app.route('/newpost')
def newpost():
    return render_template('create_blog.html', title = "Blogz")

@app.route('/newpost', methods=['POST'])
def validate_newpost():
    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        name = request.form['name']
        entry = request.form['entry']
        
        new_blog = Blog(name, entry, owner)
        db.session.add(new_blog)
        db.session.commit()
            
    name_error = ""
    entry_error = ""
    blank = ""

    if name == blank or entry == blank:
        name_error = "You cannot leave field blank." 
        name = ""
        entry_error = "You cannot leave field blank." 
        entry =  ""

    while name_error and entry_error:
        return render_template("create_blog.html", name_error=name_error, entry_error=entry_error, name=name, entry=entry)
    else:
        if request.method== 'POST':
            name = request.form['name']
            entry = request.form['entry']
            new_blog = Blog(name, entry, owner)
            blog = new_blog
            return render_template('single_blog.html', blog=blog)

@app.route('/home')
@app.route('/blog', methods = ['GET'])
def index():
    if request.args:
        entry = request.args.get('user')
        users = User.query.get(entry)
        return render_template('singleUser.html', title = "Blogz", user=users)
    users = User.query.all()
    return render_template('index.html', title = "Blogz", users=users)


@app.route('/allpost', methods = ['GET'])
def display_blogs():
    if request.args:
        blog = request.args.get('id')
        blogs = Blog.query.get(blog)
        user = request.args.get('id')
        users = User.query.get(user)
        return render_template('single_blog.html', title = "Blogz", blog=blogs, user = users)
    blogs = Blog.query.all()
    users = User.query.all()  
    return render_template('display_blogs.html', title = "Blogz", blogs=blogs, user = users)

@app.before_request#run this function before you call the request handlers to check for user session in the dictionary runs before #every request
def require_login():
    allowed_routes = ['login', 'signup', 'display_blogs', 'index'] #list of request handler function names that users do not need to be logged in to view
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash("fields were left blank or username and password do not match or user does not exist", 'error')
    return render_template('login.html', title = "Blogz")

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        blank = ""

        if username == blank or password==blank or verify == blank:
            flash('No fields can be left blank', 'error')
            return redirect ('/signup')
        if len(username) < 3 or len(password) < 3 or len(verify) < 3 or len(username) >20 or len(password) > 20 or len(verify) > 20:
            flash('All fields must be between 3-20 characters', 'error')
            return redirect ('/signup')
        if password != verify:
            flash('passwords do not match', 'error')
            return redirect ('/signup')
        elif existing_user and existing_user.username == username:
            flash('username already exists', 'error')
            return redirect ('/signup')    
        else:
            new_user = User(username, 
            password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html', title = "Blogz")

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged out")
    return redirect('/blog')

if __name__ == '__main__':
    app.run()