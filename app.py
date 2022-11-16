import os
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask import send_from_directory
from init import app, db
from models import User
from forms import LoginForm, RegistrationForm
from flask_socketio import SocketIO

###upload test###
UPLOAD_FOLDER = './upload'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
###upload test###

socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            flash("您已經成功的登入系統")
            next = request.args.get('next')
            if next == None or not next[0]=='/':
                next = url_for('welcome_user')
                return redirect(next)
    return render_template('login.html',form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("您已經登出系統")
    return redirect(url_for('home'))


@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
        username=form.username.data, password=form.password.data)
        
        # add to db table
        db.session.add(user)
        db.session.commit()
        flash("感謝註冊本系統成為會員")
        return redirect(url_for('login'))
    return render_template('register.html',form=form)


@app.route('/welcome', methods=['GET', 'POST'])
@login_required
# def welcome_user():
#     return render_template('welcome_user.html',user=current_user)


def welcome_user():  #upload_file
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                                   filename))
            return render_template('welcome_user.html',user=current_user, filename=filename)
    return render_template('welcome_user.html', user=current_user)

@app.route('/welcome/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    
@socketio.on('send')
def chat(message):
    socketio.emit('get', { "message": message, "name": current_user.username})

@socketio.on('text')
def test():
    socketio.send("test")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
    # app.run(debug=True)