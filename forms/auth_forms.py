from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class StudentRegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    roll_number = StringField('Roll Number', validators=[DataRequired()])
    branch = StringField('Branch', validators=[DataRequired()])
    cgpa = StringField('CGPA', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register Student')

class CompanyRegistrationForm(FlaskForm):
    full_name = StringField('Company Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cin = StringField('CIN', validators=[DataRequired()])
    sector = StringField('Sector', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register Company')
