import os
from smtplib import SMTPAuthenticationError
from socket import socket, gethostbyname, gaierror

import flask
from sqlalchemy import desc
from flask_mail import Message

from crowdControll.functions import save_profile_picture, save_post_picture, filterPosts, uniquePlaces, getAddress, getAddressPlain
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from werkzeug import exceptions
from werkzeug.utils import secure_filename

from crowdControll import app, db, bcrypt, queue, mail
from crowdControll.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, \
    ResetPasswordForm
from crowdControll.models import User, Post, Announcement
from crowdControll.predictor import Predictor
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

predictor = Predictor(queue, db, app)
db.create_all()

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    paginate = Post.query.order_by(desc('date_posted')).paginate(page=page, per_page=5)
    paginate.items.sort(key=lambda x: x.date_posted, reverse=True)
    for post in paginate.items:
        picture_path = os.path.join(app.root_path, 'static/post_imgs', post.image_file)
        if not os.path.isfile(picture_path):
            post.image_file = 'default.jpg'
    return render_template('home.html', posts=paginate)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/mapview")
def mapview():
    posts = Post.query.all()
    return render_template('map.html', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = save_profile_picture(form.picture.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, number_of_people=0, latitude=form.latitude.data,
                    longitude=form.longitude.data, author=current_user)

        post.image_file = save_post_picture(form.picture.data)
        post.address = getAddress(post.latitude, post.longitude)
        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)
        queue.put(post.id)
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    picture_path = os.path.join(app.root_path, 'static/post_imgs', post.image_file)
    map_path = os.path.join(app.root_path, 'static/maps', post.image_file)
    mapExists = True
    if not os.path.isfile(picture_path):
        post.image_file = 'default.jpg'
    if not os.path.isfile(map_path):
        mapExists = False
    return render_template('post.html', title=post.title, post=post, mapExists=mapExists)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    picture_path = os.path.join(app.root_path, 'static/post_imgs', post.image_file)
    try:
        os.remove(picture_path)
    except Exception:
        pass
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/predict", methods=['POST'])
def predict():
    response = {}
    i = 0

    while True:
        requestFile = 'file' + str(i)
        i += 1
        try:
            file = request.files[requestFile]
            if file:
                filename = secure_filename(file.filename)
                result = predictor.doPredict(Image.open(file))
                response[filename] = result
        except exceptions.BadRequestKeyError:
            break

    return jsonify(response)


@app.route("/calendar/", methods=['GET', 'POST'])
def calendar():
    posts = Post.query.all()
    places = uniquePlaces(posts)
    if flask.request.method == 'POST':
        place = request.form.get('placeSelector')
        if place != "all places":
            posts = filterPosts(posts, place)
    else:
        place = "all places"

    return render_template('calendar.html', posts=posts, places=places, selectedPlace=place)


@app.route("/statistics", methods=['GET', 'POST'])
def statistics():
    dataset = [0, 0, 0, 0, 0, 0, 0]
    posts = Post.query.all()
    places = uniquePlaces(posts)
    if flask.request.method == 'POST':
        place = request.form.get('placeSelector')
        if place != "all places":
            posts = filterPosts(posts, place)
    else:
        place = "all places"

    for post in posts:
        dataset[post.date_posted.weekday()] += 1
    return render_template('statistics.html', dataset=dataset, places=places, selectedPlace=place)


@app.route("/announcements")
def announcements():
    return render_template('announcements.html', announcements=Announcement.query.all())


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)
    try:
        mail.send(msg)
        return 'An email has been sent with instructions to reset your password.'
    except gaierror:
        return 'There was error on sending email. App email server address is INVALID!'
    except SMTPAuthenticationError:
        return 'There was error on sending email. App email server credentials are INVALID!'
    except Exception:
        return 'There was error on sending email.'

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        flash(send_reset_email(user), 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
