from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '\x9d*\x0e\x008\xb5\xde\xdd\x86\xbb\xa8{\xdf2)o\xa4L\xe1\x88\x95\xf6\xc0\xca'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

#@app.before_request
#def require_login():
#    allowed_routes = ['login', 'signup']
#    if request.endpoint not in allowed_routes and 'username' not in session:
#        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['email'] = username
            flash("Logged in")
            return redirect('/')
        
        elif not user:
            flash('User does not exist', 'error')
        
        elif not user.password == password:
            flash('User password incorrect', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if not (username and password and verify):
            flash('User must supply username, password and verify', 'error')
            return render_template('signup.html') 
        
        if not (password == verify):
            flash('Error: passwords do not match', 'error')
            return render_template('signup.html') 

        if len(password) < 3:
            flash('Error: passwords must be more than 3 charaters long', 'error')
            return render_template('signup.html') 

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:

            if len(username) < 3:
                flash('Error: Username must be more than 3 charaters long', 'error')
                return render_template('signup.html') 

            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = username
            return redirect('/')
        else:
            flash('User already exists', 'error')
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/blog')
def blog():
    post_id = request.args.get('id')

    if post_id:
        post = Blog.query.filter_by(id=post_id).first()
        return render_template('onepage.html', post=post)
    else:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts)

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/newpost', methods=['POST', "GET"])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        
        title_error = ''
        text_error = ''

        if not title:
            title_error = 'Must supply a title'
        if not text:
            text_error = 'Must supply blog text'

        if not text_error and not title_error:
            blog_entry = Blog(title, text)
            db.session.add(blog_entry)
            db.session.commit()
            post_id = str(blog_entry.id)
            return redirect("/blog?id=" + post_id)
        else:
            return render_template('newpost.html', title_error=title_error, text_error=text_error, title=title, text=text)
    
    if request.method == 'GET':
    
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()