from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField

from wtforms import validators, ValidationError


class ContactForm(Form):
    name = TextField("Name Of Student", [validators.Required("Please enter your name.")])
    Gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    Address = TextAreaField("Address")

    email = TextField("Email", [validators.Required("Please enter your email address."),
                                validators.Email("Please enter your email address.")])

    Age = IntegerField("age")
    language = SelectField('Languages', choices=[('cpp', 'C++'),
                                                 ('py', 'Python')])
    submit = SubmitField("Send")