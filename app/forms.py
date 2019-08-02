from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, InputRequired

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[Email(), InputRequired()])
    