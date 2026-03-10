from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class StudentProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    branch = StringField('Branch', validators=[DataRequired()])
    cgpa = FloatField('CGPA', validators=[DataRequired()])
    phone = StringField('Phone')
    resume = FileField('Upload Resume (PDF)', validators=[FileAllowed(['pdf', 'doc', 'docx'])])
    cover_letter = TextAreaField('Cover Letter Template')
    submit = SubmitField('Save Profile')
