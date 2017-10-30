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

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

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

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
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
            return redirect('/newpost')
        else:
            flash('User already exists', 'error')
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/blog')
def blog():
    username = request.args.get('user')
    blog_id = request.args.get('id')

    if username:
        posts = db.session.query(Blog, User).join(User).filter(Blog.owner_id == User.id).filter(User.username == username).all()
        return render_template('blog.html', posts=posts)
    elif blog_id:
        posts = db.session.query(Blog, User).join(User).filter(Blog.owner_id == User.id).filter(Blog.id == blog_id).all()
        return render_template('blog.html', posts=posts)
    else:
        posts = db.session.query(Blog, User).join(User).filter(Blog.owner_id == User.id).all()
        return render_template('blog.html', posts=posts)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


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
            username = session['email']
            owner_record = User.query.filter_by(username=username).first()
        
            blog_entry = Blog(title, text, owner_record)
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