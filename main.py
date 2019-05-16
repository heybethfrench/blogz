from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hello@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    email = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password = password
    
class Blog(db.Model):
    blog_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present


@app.before_request
def require_login():
    allowed_routes = ['signup', 'login', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route("/")
def index():
    users = User.query.all()
    user = request.args.get('id')
    if not user:
        return render_template('blogusers.html', users=users)
    if user:
        return redirect('/blog')
  


@app.route("/signup", methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        verify = request.form['verify']
        username_error = ''
        password_error = ''
        verify_error = ''
        email_error = ''
        existing_user = User.query.filter_by(username=username).first()

        if len(username) < 3 or len(username) > 20:
            username_error = "Please enter a username between 3 and 20 characters in length"

        if not email == '' and not is_email(email):
            email_error = "this is not an email"

        if len(password) < 3 or len(password) > 20:
            password_error = "Please enter a password between 3 and 20 characters in length"

        if password == '':
            password_error = "Please enter a valid password"

        if username == '':
            username_error = "Please enter a valid username"

        if verify != password:
            verify_error = "Passwords do not match"

        if existing_user:
            username_error = "Duplicate User"

        if not username_error and not password_error and not verify_error and not email_error and not existing_user:
            new_user = User(username, password, email)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
            
    return render_template('signup.html', username=username, email=email, username_error=username_error, password_error=password_error, verify_error=verify_error, email_error=email_error)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        login_error = ""

        if user and user.password == password:
            session['username'] = username
            
            return redirect('/')
        else:
            login_error = "Invalid Username or Password"
            return render_template('login.html', login_error=login_error)


@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')


@app.route("/blog")
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if blog_id:
        blog = Blog.query.get(int(blog_id))
        return render_template('allblogs.html', blogs=[blog])

    if user_id is None:
        blogs = Blog.query.all()
        return render_template('allblogs.html', blogs=blogs)

    else:
        blogs = Blog.query.filter_by(owner_id=int(user_id)).all()
        return render_template('allblogs.html', blogs=blogs)


@app.route('/newpost', methods = ['POST', 'GET'])    
def new_post():

    owner = User.query.filter_by(username=session['username']).first()
    

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
            body_error = 'Please enter a blog'

        if not body_error and not title_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
        
            return redirect('/blog?id={}'.format(new_blog.blog_id))
    
    return render_template('newpost.html', title_error=title_error, body_error=body_error, owner=owner)
        

   

if __name__ == '__main__':
    app.run()
