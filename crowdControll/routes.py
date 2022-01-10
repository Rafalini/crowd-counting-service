import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from werkzeug import exceptions
from werkzeug.utils import secure_filename

from crowdControll import app, db, bcrypt, queue
from crowdControll.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from crowdControll.models import User, Post
from crowdControll.predictor import Predictor
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

predictor = Predictor(queue, db, app)


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    posts.sort(key=lambda x: x.date_posted, reverse=True)
    for post in posts:
        picture_path = os.path.join(app.root_path, 'static/post_imgs', post.image_file)
        if not os.path.isfile(picture_path):
            post.image_file = 'default.jpg'
    return render_template('home.html', posts=posts)


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


def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_imgs', picture_fn)
    i = Image.open(form_picture)
    # output_size = (500, 500)
    # i.thumbnail(output_size)
    i.save(picture_path, quality=100)
    return picture_fn


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
        post.number_of_people = -1
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
    if not os.path.isfile(picture_path):
        post.image_file = 'default.jpg'
    return render_template('post.html', title=post.title, post=post)


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