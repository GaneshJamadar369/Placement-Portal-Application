from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired

class CreateDriveForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Job Description')
    salary = FloatField('Salary (CTC)', validators=[DataRequired()])
    positions = IntegerField('Number of Positions', validators=[DataRequired()])
    eligibility = StringField('Eligibility (e.g. CSE, ECE, CGPA>7)', validators=[DataRequired()])
    location = StringField('Location (e.g. Bangalore, Remote)', validators=[DataRequired()])
    job_type = StringField('Job Type (e.g. Full-time, Internship)', validators=[DataRequired()])
    min_cgpa = FloatField('Minimum CGPA Required', default=0.0)
    deadline = DateField('Application Deadline (YYYY-MM-DD)', validators=[DataRequired()])
    submit = SubmitField('Create Drive')
