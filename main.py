from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hello@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class Blog(db.Model):
    blog_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route("/")
def index():
    return redirect ('/blog')


@app.route("/blog", methods = ['GET', 'POST'])
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods = ['POST', 'GET'])    
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = 'Please enter a blog title'
        if not blog_body:
            body_error = 'Please enter a blog title'

        if not body_error and not title_error:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')
    
    return render_template('newpost.html', title_error=title_error, body_error=body_error)
        

   

if __name__ == '__main__':
    app.run()
