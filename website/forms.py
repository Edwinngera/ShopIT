from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, validators,DateField,FileField,DecimalField,IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import datetime



class SignupForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Register")



class LoginForm(FlaskForm):
    email = StringField(
        "Email"
    )
    password = PasswordField("Password")
    submit = SubmitField("Log In")


class uploadProduct(FlaskForm):
    
    product_name = StringField("Product Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    image = FileField('Select Image', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    regular_price = DecimalField('Price', validators=[DataRequired()])
    discounted_price = DecimalField('Regular_Price', validators=[DataRequired()])
    product_rating = DecimalField('Product_Rating', validators=[DataRequired()])
    product_review = StringField('Product_Review', validators=[DataRequired()])

class orderForm(FlaskForm):
    items=StringField('Test')


class CheckoutForm(FlaskForm):
    shipping_address = StringField('Shipping Address', validators=[DataRequired()])
    billing_address = StringField('Billing Address', validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[DataRequired()])
    card_cvv = IntegerField('Card CVV', validators=[DataRequired()])
    submit = SubmitField('Submit Order')





