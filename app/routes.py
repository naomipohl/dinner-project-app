from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, RegistrationPasswordForm, EditProfileForm, DinnerForm, BringingForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, NewUser, Dinner, Brings
from app.email import send_password_reset_email, send_register_user_email
from datetime import datetime
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from app import app, db

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = DinnerForm()
    if form.validate_on_submit():
        dinner = Dinner(body=form.dinner.data, address=form.address.data, 
            date=form.date.data, author=current_user,
            max_attendees=form.max_attendees.data)
        db.session.add(dinner)
        current_user.attend(dinner)
        db.session.commit()
        flash('Your dinner is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    dinners = Dinner.query.filter_by(user_id=current_user.id).order_by(Dinner.timestamp.desc()).paginate(
        page, app.config['DINNERS_PER_PAGE'], False)
    next_url = url_for('index', page=dinners.next_num) \
        if dinners.has_next else None
    prev_url = url_for('index', page=dinners.prev_num) \
        if dinners.has_prev else None
    return render_template('index.html', title='Home', form=form, 
        dinners=dinners.items, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register_request', methods=['GET', 'POST'])
def register_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        if (email[-10:] != '.upenn.edu'):
            flash('Sorry, this service is currently only available\
                to UPenn community members.')
            return redirect(url_for('login'))
        user = NewUser(username=form.username.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        send_register_user_email(user)
        flash('Check your email to complete registration. Don\'t forget \
            to check your spam folder!')
        return redirect(url_for('login'))
    return render_template('register.html',
        title='Register', form=form)

@app.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    temp_user = NewUser.verify_register_token(token)
    form = RegistrationPasswordForm()
    if form.validate_on_submit():
        user = User(username=temp_user.username, email=temp_user.email)
        user.set_password(form.password.data)
        db.session.add(user)
        #db.session.delete(temp_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    dinners = user.dinners.order_by(Dinner.timestamp.desc()).paginate(
        page, app.config['DINNERS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=dinners.next_num) \
        if dinners.has_next else None
    prev_url = url_for('user', username=user.username, page=dinners.prev_num) \
        if dinners.has_prev else None
    return render_template('user.html', user=user, dinners=dinners.items,
        next_url=next_url, prev_url=prev_url)

@app.route('/delete/<id>', methods=['GET'])
@login_required
def delete(id):
    dinner = Dinner.query.filter_by(id=id).first_or_404()
    db.session.delete(dinner)
    db.session.commit()
    flash('Dinner deleted!')
    return redirect(url_for('index'))


@app.route('/dinner/<id>', methods=['GET', 'POST'])
@login_required
def dinner(id):
    dinner = Dinner.query.filter_by(id=id).first_or_404()
    foods = Brings.query.filter_by(dinner_id=id)
    form = BringingForm()
    if form.validate_on_submit():
        bringing = Brings(user_id=current_user.id, dinner_id=dinner.id, item=form.bringing.data)
        db.session.add(bringing)
        db.session.commit()
        flash('You are bringing something!')
        return redirect(url_for('dinner', id=id, foods=foods))
    return render_template('dinner.html', title='Dinner', form=form, dinner=dinner, foods=foods)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.dietary_restrictions = form.dietary_restrictions.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        return render_template('edit_profile.html', title='Edit Profile', form=form)
    else:
        flash('An error has occurred.')
        return redirect(url_for('edit_profile'))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    dinners = Dinner.query.order_by(Dinner.timestamp.desc()).paginate(
        page, app.config['DINNERS_PER_PAGE'], False)
    next_url = url_for('explore', page=dinners.next_num) \
        if dinners.has_next else None
    prev_url = url_for('explore', page=dinners.prev_num) \
        if dinners.has_prev else None
    return render_template('index.html', title='Explore', 
        dinners=dinners.items, next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
        title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/attend/<dinner_id>')
@login_required
def attend(dinner_id):
    dinner = Dinner.query.filter_by(id=dinner_id).first()
    if dinner is None:
        flash('Dinner {} not found.'.format(dinner))
        return redirect(url_for('index'))
    if dinner.author.id == current_user.id:
        flash('You are already attending your own dinner!')
        return redirect(url_for('dinner', id=dinner_id))
    current_user.attend(dinner)
    db.session.commit()
    flash('You are attending dinner number {}!'.format(dinner_id))
    return redirect(url_for('dinner', id=dinner_id))

@app.route('/unattend/<dinner_id>')
@login_required
def unattend(dinner_id):
    dinner = Dinner.query.filter_by(id=dinner_id).first()
    if dinner is None:
        flash('Dinner {} not found.'.format(dinner))
        return redirect(url_for('index'))
    if dinner.author.id == current_user.id:
        flash('You cannot attend your own dinner!')
        return redirect(url_for('dinner', id=dinner_id))
    current_user.unattend(dinner)
    db.session.commit()
    flash('You are no longer attending dinner number {}!'.format(dinner_id))
    return redirect(url_for('dinner', id=dinner_id))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    upload_result = None
    thumbnail_url1 = None
    thumbnail_url2 = None
    if request.method == 'POST':
        file_to_upload = request.files['file']
        if file_to_upload:
            upload_result = upload(file_to_upload)
            thumbnail_url2, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=90,
                                                     height=90, radius=20, gravity="east")
            current_user.set_picture(thumbnail_url2)
            flash('Successfully set profile picture!')
            return redirect(url_for('user', username=current_user.username))

    return render_template('upload_form.html')

@app.route('/upload_dinner/<dinner_id>', methods=['GET', 'POST'])
@login_required
def upload_dinner_file(dinner_id):
    dinner = Dinner.query.filter_by(id=dinner_id).first()
    upload_result = None
    thumbnail_url2 = None
    if request.method == 'POST':
        file_to_upload = request.files['file']
        if file_to_upload:
            upload_result = upload(file_to_upload)
            thumbnail_url2, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=400,
                                                     height=200, gravity="east")
            dinner.set_picture(thumbnail_url2)
            flash('Successfully set dinner picture!')
            return redirect(url_for('dinner', id=dinner_id))
            
    return render_template('upload_dinner_form.html')

if __name__ == '__main__':
    app.run(debug=True)



