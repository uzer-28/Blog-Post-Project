import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ResetPasswordForm, RequestResetForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required                            #login_user is the function from flask-login used to login the user if the credentials are correct
from flask_mail import Message

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)                  #this code displays only specified 'per_page' no. of blog posts on the 1 page
    return render_template('home.html', posts=posts)                                    #the oredr_by(Post.date_posted.desc()) displays the newest/latest posts on the top


@app.route('/about')
def about():
    return render_template("about.html", title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')                   #encrypts the password entered by the user
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)             #instance of User class
        db.session.add(user)
        db.session.commit()                                                                                   #adding the user tothe database
        flash(f'Your account has been created. Please Login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:                                    #if the user is logged in the after clicking on register/login page will redirect to home page
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
           login_user(user, remember=form.remember.data)                 #this fun will login the user if all the info is crrt & remember parameter is usedto remember the user if checked at tym of login
           next_page = request.args.get('next')
           if next_page:                                                 #this conditional part will redirect us to the next page(route) if available, which we are trying to access being logged out
               return redirect(next_page)                                #or else logs us directly home page
           else:
              flash('Login Successful!','success')
              return redirect(url_for('home'))
        else:
           flash('Login failed. Enter valid credentials!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()                                                     #logout_user fn is used to log the user out
    return redirect(url_for('home'))

def save_picture(form_picture):                                      #save_picture() encodes the name of given file and extracts the extension of img
    random_hex = secrets.token_hex(8)                                #and returns the new name for the image with same extension
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    form_picture.save(picture_path)
    #output_size = (125, 125)
    #i = Image.open(form_picture)
    #i.thumbnail(output_size)                   #this comment lines are to reduce the size of image
    #i.save(picture_path)
    return picture_filename

@app.route('/account', methods=['GET', 'POST'])
@login_required                                                     #used to protect about route in our Flask application, ensuring that only authenticated users can access them.
def account():                                                      #If a user is not authenticated, they will be redirected to the login view (as specified by login_manager.login_view).
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data                  #if current username/email is not available in database as checked in forms.py-UpdateAccountForm
        current_user.email = form.email.data                        #then the username/email will be updated.
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':                                   #this condition displays the username and email on the Accountform
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods = ['GET','POST'])
@login_required
def new_post():                                                                                   #route to add new posts
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)          #instance of class Post and passing it the title, content & author
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='New Post', form=form, legend='Add New Post')


@app.route('/post/<int:post_id>', methods = ['GET','POST'])
def post(post_id):                                                                                 #this route display the individual post when click on the title of the post
    post = Post.query.get_or_404(post_id)                                                          #get_or_404(post_id) gets the post with post_id or throws the error if post doesn't exist
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET','POST'])                                   #route for updating the post
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if post.author != current_user:                                                                #posts can be updated only by it author, so if someone else other than author
        abort(403)                                                                                 #tries to update then the error will be thrown
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':                                                                  #this condition displays the post on the postform
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', title='Update Post', form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_post(username):                                                                            # when clicked on the username on the post then this route will display
    page = request.args.get('page', 1, type=int)                                                    #the posts of that user only in latest-oldest pattern
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_post.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset the password, click the following link:
{url_for('reset_token', token=token, _external=True, _scheme='http')}
If you did not made this request then simply ignore this. 
    '''
    mail.send(msg)

@app.route('/reset_password', methods = ['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Reset token has been sent to your email.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods = ['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')                   #encrypts the password entered by the user
        user.password = hashed_password
        db.session.commit()                                                                                   #adding the user tothe database
        flash(f'Your password has been reset! Please Login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)