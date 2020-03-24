import datetime
import os

from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired

users = [
    {'username': 'makcimbx', 'password': '123'}
]
lastEnter = []
posts = []
userPosts = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

@app.route('/')
@app.route('/index')
def hello_world():
    someUserName = 'Неизвестный'
    if len(lastEnter) > 0:
        someUserName = lastEnter[len(lastEnter) - 1]['username']
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
    form = LoginForm()
    if form.validate_on_submit():
        somePosts = [
            {
                'author': {'username': form.username.data},
                'body': form.password.data
            }
        ]
        for i in users:
            if i['username'] == form.username.data and i['password'] == form.password.data:
                posts.extend(somePosts)
                someEnter = [{'username': form.username.data, 'enter_data': datetime.datetime.now()}]
                lastEnter.extend(someEnter)
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html',  title='Sign In', form=form)

@app.route('/message', methods=['GET', 'POST'])
def message():
    form = SubmitPostForm()
    if form.validate_on_submit():
        somePosts = [
            {
                'author': {'username': form.username.data},
                'body': form.message.data
            }
        ]
        userPosts.extend(somePosts)
        return redirect('/index')
    return render_template('message.html',  title='Message', form=form)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SubmitPostForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Post this message')

if __name__ == '__main__':
    app.run()
