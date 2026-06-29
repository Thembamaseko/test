
from tokenize import String

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,BooleanField,RadioField,IntegerField,DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError,length,Regexp,NumberRange

from .models import User

class LoginForm(FlaskForm):
    email = StringField('Enter E-mail', validators=[DataRequired()],render_kw={"class":"login-input"})
    password = PasswordField('Enter Passwoed', validators=[DataRequired()],render_kw={"class":"login-input"})
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),length(max=125) ],render_kw={"class":"reg-input"})
    username = StringField('Username', validators=[DataRequired()],render_kw={"class":"reg-input"})
    password = PasswordField('Password', validators=[DataRequired(), length(min=6)],render_kw={"class":"reg-input"})
    age = StringField('Age', validators=[DataRequired()],render_kw={"class":"reg-input"})
    id_number = StringField('ID Number', validators=[DataRequired(), length(min=13, max=13,message="ID nust be 13 digits"),Regexp(r'^\d{13}$',message="ID number must contain only digits")],render_kw={"class":"reg-input"})
    cellphone = StringField('Cellphone', validators=[DataRequired(), length(min=10, max=10,message="Enter a valid 10 digit Cell number")],render_kw={"class":"reg-input"})
    gender = RadioField('Gender', choices=[("male","Male"),("female","Female")],validators=[DataRequired()],render_kw={"class":"reg-input"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],render_kw={"class":"reg-input"})
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please choose a different one.')
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    submit = SubmitField('send Reset Link')

class BankForm(FlaskForm):
    phone = IntegerField('Phone',validators={DataRequired()})
    amount = IntegerField('Amount of Coins')
    search = SubmitField('Search')
    add = SubmitField('Add')
    deduct = SubmitField('Deduct')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
class BetForm(FlaskForm):
    spin_id = IntegerField('Spin_Id', id="current_spin_id",validators=[DataRequired()])
    choice = StringField('Choice', validators=[DataRequired()])
    amount = IntegerField('Amount',id='bet-input', validators=[DataRequired()])
    submit = SubmitField('Place Bet')

class DepositForm(FlaskForm):
    deposit_amount = IntegerField('Amount',id="deposit_amount",validators=[DataRequired()])
    submit = SubmitField('Add Amount')

class WithdrawForm(FlaskForm):
    amount = DecimalField(
        "Amount",
        validators=[
            DataRequired(),
            NumberRange(min=200, message='minimum withdrawal amount is R200')
        ],places=2
    )
    submit = SubmitField('Send Withdrawal Request')