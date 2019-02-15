from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root2019*@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    entry = db.Column(db.String(2500))

    def __init__(self, name, entry):
        self.name = name
        self.entry = entry

@app.route('/newpost')
def display_newpost_page():
    return render_template('create_blog.html')

@app.route('/newpost', methods=['POST'])
def validate_newpost():
    if request.method == 'POST':
        name = request.form['name']
        entry = request.form['entry']
        new_blog = Blog(name, entry)
        db.session.add(new_blog)
        db.session.commit()
    blogs = Blog.query.all() 
            
    name_error = ""
    entry_error = ""
    blank = ""

    if name == blank or entry == blank:
        name_error = "You cannot leave field blank." 
        name = ""
        entry_error = "You cannot leave field blank." 
        entry =  ""
    
    if not name_error and not entry_error:
        request.args == True
        entry = request.args.get('id')
        blogs = Blog.query.get(entry)
        return render_template('single_blog.html', blog=blogs)
        #return redirect('/blog
    
    else:
        return render_template("create_blog.html", name_error=name_error, entry_error=entry_error, name=name, entry=entry)

    return render_template('display_blogs.html', blogs=blogs)


@app.route('/blog', methods = ['POST', 'GET'])
def display_blogs_individually():
    if request.args:
        entry = request.args.get('id')
        blogs = Blog.query.get(entry)
        return render_template('single_blog.html', blog=blogs)
    blogs = Blog.query.all()  
    return render_template('display_blogs.html', blogs=blogs)

if __name__ == '__main__':
    app.run()