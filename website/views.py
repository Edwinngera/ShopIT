from flask import Flask, render_template, redirect, request, flash, url_for, jsonify, Blueprint, abort, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from .forms import uploadProduct
import os
from werkzeug.utils import secure_filename
from .models import Product
from . import db
from . import create_app


views = Blueprint('views', __name__)


@views.route('/')
def home():
    latest_products =Product.query.limit(6).all()
    product=Product.query.all()
    print("Edwin")
    print(latest_products)
    return render_template('index.html', latest_products=latest_products)


@views.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    print(page)
    products = Product.query.paginate(page=page, per_page=5)
    # products = Product.query.all()
    return render_template('products.html', products=products)



@views.route('/products_details/<int:productid>', methods=['GET', 'POST'])
def products_details(productid):
    product = Product.query.get(productid)
    return render_template('product-details.html', product=product)



@views.route('/cart')
def cart():
    cart=session.get('cart',[])
    # total = sum(item['price'] * item['quantity'] for item in cart)

    return render_template('cart.html')



@views.route('/account')
def account():
    return render_template('account.html')







@views.route('/admin_users')
def admin_users():
    return render_template('adminUsers.html')

# @views.route('/upload_products')
# def upload_products():
#     return render_template('upload.html')


@views.route('/upload_products')
def test():
    form = uploadProduct()
    return render_template('admin/add_products.html', form=form)


@views.route('/add-product', methods=['POST', 'GET'])
def add_product():
    app = create_app()
    form = uploadProduct()
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        description = request.form.get('description')
        image = request.files['image']
        quantity = request.form.get('quantity')
        regular_price = request.form.get('regular_price')
        discounted_price = request.form.get('discounted_price')
        product_rating = request.form.get('product_rating')
        product_review = request.form.get('product_review')

        # Save image to file system
        filename = secure_filename(image.filename)
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
        return redirect(url_for('views.view'))

    return render_template('admin/add_products.html', form=form)


@views.route("/delete/<int:productid>", methods=["GET", "POST"])
def delete_product(productid):
    try:
        product = Product.query.get(productid)
        db.session.delete(product)
        db.session.commit()
        return jsonify({
            'success': True,
            'deleted': productid
        })

    except Exception as e:
        abort(422)

    return redirect()


@views.route("/add_to_cart/<int:productid>")
def add_to_cart(productid):
    product = Product.query.get_or_404(productid)

    cart_item = {
        'id': product.productid,
        'name': product.product_name,
        'price': product.regular_price if product.discounted_price is None else product.discounted_price,
        'quantity': 1,
        'link': product.image
    }

    cart = session.get('cart', [])

    for item in cart:
        if item['id'] == cart_item['id']:
            item['quantity'] += 1
            break
    else:
        cart.append(cart_item)

    session['cart'] = cart


    flash('Item added to cart', 'success')

    return redirect(url_for('views.cart'))

    # retrieve the current cart from the session or create a new if it doesnt exist




@views.route('/view')
def view():
    products = Product.query.all()
    return render_template('admin/view_products.html', products=products)


@views.route('/admin/')
def dashboard():
    return render_template('admin/dashboard.html')
