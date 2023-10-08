#app\controllers\auth_controller.py
from flask import jsonify

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

from app.models.user_model import User
from app.forms.login_form import LoginForm
from app.forms.signup_form import SignupForm



def login(email, password):
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            token = user.generate_token()
            return jsonify({'token': token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'message': 'Invalid form submission'}), 400

def signup(email, password, meross_password):
    form = SignupForm()  # Create an instance of the SignupForm

    if form.validate_on_submit():
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Hash the password
        meross_password = form.meross_password.data

        user = User(email=email, password=password, meross_password=meross_password)
        user.save()
        token = user.generate_token()
        return jsonify({'token': token}), 201

    return jsonify({'message': 'Invalid form submission'}), 400

def logout():
    return jsonify({'message': 'Logout successful'}), 200
