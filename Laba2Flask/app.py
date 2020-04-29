import datetime
import hashlib
import os

from flask import Flask, render_template, flash, redirect, url_for, json
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import current_user, login_user, logout_user, UserMixin, LoginManager
from google import google, images

lastEnter = []
posts = []
userPosts = []

userSearch = []
userCalculate = []
userImageSearch = []
userCurrencyConvert = []
lastQuery = []

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

@app.route('/websearch', methods=['GET', 'POST'])
def websearch():
    if not current_user.is_authenticated:
        return redirect("/index")
    form = WebSearchPostForm()
    if form.validate_on_submit():
        lastQuery.clear()
        lastQuery.append(form.query.data)
        search_results = google.search(form.query.data, int(form.pages.data))
        userSearch.clear()
        for result in search_results:
            somePosts = [
                {
                    'name': result.name,
                    'link': result.link,
                    'google_link': result.google_link,
                    'description': result.description,
                    'thumb': result.thumb,
                    'cached': result.cached,
                    'page': result.page,
                    'index': result.index,
                    'number_of_results': result.number_of_results
                }
            ]
            userSearch.extend(somePosts)
        return redirect("/websearch")
    return render_template('websearch.html',  title='Websearch', form=form, userSearch=userSearch, current_user=current_user, lastQuery=lastQuery)

@app.route('/webcalculate', methods=['GET', 'POST'])
def webcalculate():
    if not current_user.is_authenticated:
        return redirect("/index")
    form = WebCalculatePostForm()
    if form.validate_on_submit():
        lastQuery.clear()
        lastQuery.append(form.query.data)
        search_results = google.calculate(form.query.data)
        userCalculate.clear()
        for result in search_results:
            somePosts = [
                {
                    'value': result.value,
                    'from_value': result.from_value,
                    'unit': result.unit,
                    'from_unit': result.from_unit,
                    'expr': result.expr,
                    'result': result.result,
                    'fullstring': result.fullstring
                }
            ]
            userCalculate.extend(somePosts)
        return redirect("/webcalculate")
    return render_template('webcalculate.html',  title='Webcalculate', form=form, userCalculate=userCalculate, current_user=current_user, lastQuery=lastQuery)

@app.route('/webimagesearch', methods=['GET', 'POST'])
def webimagesearch():
    if not current_user.is_authenticated:
        return redirect("/index")
    form = WebImageSearchPostForm()
    if form.validate_on_submit():
        lastQuery.clear()
        lastQuery.append(form.query.data)
        options = images.ImageOptions()
        options.image_type = form.imageType.data
        options.size_category = form.sizeCategory.data
        options.larger_than = form.largerThan.data
        options.exact_width = form.exactWidth.data
        options.exact_height = form.exactHeight.data
        options.color_type = form.colorType.data
        options.color = form.color.data
        search_results = google.search_images(form.query.data, options)
        userImageSearch.clear()
        for result in search_results:
            somePosts = [
                {
                    'domain': result.domain,
                    'filesize': result.filesize,
                    'format': result.format,
                    'height': result.height,
                    'index': result.index,
                    'link': result.link,
                    'name': result.name,
                    'page': result.page,
                    'site': result.site,
                    'thumb': result.thumb,
                    'thumb_height': result.thumb_height,
                    'thumb_width': result.thumb_width,
                    'width': result.width
                }
            ]
            userImageSearch.extend(somePosts)
        return redirect("/webimagesearch")
    return render_template('webimagesearch.html',  title='Websearch', form=form, userImageSearch=userImageSearch, current_user=current_user, lastQuery=lastQuery)


@app.route('/webconvert', methods=['GET', 'POST'])
def webconvert():
    if not current_user.is_authenticated:
        return redirect("/index")
    form = WebConvertPostForm()
    if form.validate_on_submit():
        lastQuery.clear()
        lastQuery.append(form.value.data)
        print(float(form.value.data))
        print(form.fromQuery.data)
        print(form.afterQuery.data)

        search_results = google.convert_currency(float(form.value.data), form.fromQuery.data, form.afterQuery.data)
        userCurrencyConvert.clear()
        somePosts = [
            {'value': form.value.data,
             'beforeQuery': form.fromQuery.data,
             'afterQuery': form.afterQuery.data,
             'result': search_results
            }
        ]
        userCalculate.extend(somePosts)
        return redirect("/webconvert")
    return render_template('webconvert.html',  title='Webconvert', form=form, userCurrencyConvert=userCurrencyConvert, current_user=current_user, lastQuery=lastQuery)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SubmitPostForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Post this message')

class WebSearchPostForm(FlaskForm):
    query = StringField('Search Query', validators=[DataRequired()])
    pages = StringField('Pages Count', validators=[DataRequired()], default="1")
    submit = SubmitField('Search')

class WebCalculatePostForm(FlaskForm):
    query = StringField('Calculate Query', validators=[DataRequired()], default="157.3kg in grams")
    submit = SubmitField('Search')

class WebImageSearchPostForm(FlaskForm):
    query = StringField('Search Query', validators=[DataRequired()], default="яблоко")
    imageType = StringField('Image type', validators=[DataRequired()], default="photo")
    sizeCategory = StringField('Size category', validators=[DataRequired()], default="m")
    largerThan = StringField('Larger than', validators=[DataRequired()], default="8mp")
    exactWidth = StringField('Exact width', validators=[DataRequired()], default="10000")
    exactHeight = StringField('Exact height', validators=[DataRequired()], default="10000")
    colorType = StringField('Color type', validators=[DataRequired()], default="specific")
    color = StringField('Color', validators=[DataRequired()], default="green")
    submit = SubmitField('Search')

class WebConvertPostForm(FlaskForm):
    value = StringField('Value', validators=[DataRequired()], default="100")
    fromQuery = StringField('From Currency', validators=[DataRequired()], default="RUB")
    afterQuery = StringField('After Currency', validators=[DataRequired()], default="dollars")
    submit = SubmitField('Search')

if __name__ == '__main__':
    app.run()
