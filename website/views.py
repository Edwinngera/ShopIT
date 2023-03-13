from flask import Flask, render_template, redirect, request, flash,url_for,jsonify,Blueprint
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required, current_user
from .forms import uploadProduct
import os
from werkzeug.utils import secure_filename
from .models import Product
from . import db
from . import create_app



views=Blueprint('views',__name__)


@views.route('/')
def home():
    return render_template('index.html')


@views.route('/products')
def products():
    return render_template('products.html')


@views.route('/account')
def account():
    return render_template('products.html')


@views.route('/products_details', methods=['GET', 'POST'])
def products_details():
    return render_template('product-details.html')

@views.route('/cart')
def cart():
    return render_template('cart.html')

@views.route('/admin_users')
def admin_users():
    return render_template('adminUsers.html')

@views.route('/upload_products')
def upload_products():
    return render_template('upload.html')


@views.route('/test')
def test():
    form=uploadProduct()
    return render_template('admin/add_products.html', form=form)


@views.route('/add-product',methods=['POST','GET'])
def add_product():
    app=create_app()
    form=uploadProduct()
    if request.method == 'POST':
        product_name=request.form.get('product_name')
        description=request.form.get('description')
        image=request.files['image']
        quantity=request.form.get('quantity')
        regular_price = request.form.get('regular_price')
        discounted_price = request.form.get('discounted_price')
        product_rating = request.form.get('product_rating')
        product_review = request.form.get('product_review')

        #Save image to file system
        filename=secure_filename(image.filename);
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product = Product(
            product_name=product_name,
            description=description,
            image=filename,
            quantity=quantity,
            regular_price=regular_price,
            discounted_price=discounted_price,
            product_rating=product_rating,
            product_review=product_review
        )
        db.session.add(product)
        db.session.commit()
        return 'Product added successfully'
    return render_template('admin/add_products.html',form=form)


@views.route('/view')
def view(): 
    products=Product.query.all()
    return render_template('admin/view_products.html', products=products)





