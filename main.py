from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cat@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

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