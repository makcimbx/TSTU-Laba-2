import datetime
import hashlib
import os

from flask import Flask, render_template, flash, redirect, url_for, json
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import current_user, login_user, logout_user, UserMixin, LoginManager

lastEnter = []
posts = []
userPosts = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

loginManager = LoginManager(app)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'



class User(UserMixin):
    KEY_LOGIN = 'login'
    KEY_PASSW = 'passw'

    userList = None

    login = ''
    passw = ''
    is_external = False

    def __init__(self, data):
        self.login = data[User.KEY_LOGIN]
        self.passw = data[User.KEY_PASSW]

    def get_id(self):
        return self.login

    def get_full_name(self):
        try:
            return self.info['first_name'] + ' ' + self.info['last_name']
        except AttributeError:
            return self.login

    def avatar_url(self):
        try:
            return self.info['photo_50']
        except AttributeError:
            return ''

    def check_password(self, password):
        return hashlib.md5(password.encode('utf-8')).hexdigest() == self.passw

    def __repr__(self):
        return F'User: {self.login}'

    @staticmethod
    @loginManager.user_loader
    def load_user(_login):
        if _login not in User.userList:
            return None
        else:
            return User.userList[_login]

    @staticmethod
    def load(_context):
        if not User.userList:
            filename = os.path.join(_context.root_path, 'data', 'userdata.json')
            file = open(filename, 'r')
            data = json.load(file)
            file.close()

            User.userList = {}
            for item in data:
                User.userList[item['login']] = User(item)

User.load(app)

@app.route('/')
@app.route('/index')
def hello_world():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    someUserName = current_user.login
    user = {'username': someUserName}
    somePosts = [
        {
            'author': {'username': 'Привет'},
            'body': 'Сообщение добавляется каждый раз при заходе на index'
        }
    ]
    #posts.extend(somePosts)
    return render_template('index.html', title='Home', user=user, posts=posts, userPosts=userPosts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/index")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.load_user(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user)
        somePosts = [
            {
                'author': {'username': form.username.data},
                'body': form.password.data
            }
        ]
        posts.extend(somePosts)
        return redirect("/index")
    return render_template('login.html',  title='Sign In', form=form)

@app.route('/message', methods=['GET', 'POST'])
def message():
    if not current_user.is_authenticated:
        return redirect("/index")
    form = SubmitPostForm()
    if form.validate_on_submit():
        somePosts = [
            {
                'author': {'username': current_user.login},
                'body': form.message.data
            }
        ]
        userPosts.extend(somePosts)
        return redirect("/index")
    return render_template('message.html',  title='Message', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/index")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SubmitPostForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Post this message')

if __name__ == '__main__':
    app.run()
