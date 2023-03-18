from flask import Flask, render_template, redirect, request, flash, url_for, jsonify, Blueprint, abort, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from .forms import uploadProduct
import os
from werkzeug.utils import secure_filename
from .models import Product, Order
from . import db
from . import create_app


views = Blueprint('views', __name__)


@views.route('/')
def home():
    latest_products = Product.query.limit(6).all()
    product = Product.query.all()
    print("Edwin")
    print(latest_products)
    return render_template('index.html', latest_products=latest_products)


@views.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    print(page)
    products = Product.query.paginate(page=page, per_page=8)
    # products = Product.query.all()
    return render_template('products.html', products=products)


@views.route('/products_details/<int:productid>', methods=['GET', 'POST'])
def products_details(productid):
    product = Product.query.get(productid)
    return render_template('product-details.html', product=product)


@views.route('/cart')
def cart():
    cart = session.get('cart', [])
    subtotal = sum(int(item['price']) * int(item['quantity']) for item in cart)
    vat=(16/100)*subtotal
    total=subtotal+vat
    return render_template('cart.html' ,subtotal=subtotal, total=total, vat=vat)


@views.route('/account')
def account():
    return render_template('account.html')


@views.route('/admin_users')
def admin_users():
    return render_template('adminUsers.html')


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


@views.route('/product/<int:productid>/edit', methods=['GET'])
def edit_product(productid):
    form = uploadProduct()
    product = Product.query.get(productid)
    form = uploadProduct(
        product_name=product.product_name,
        description=product.description,
        image=product.image,
        quantity=product.quantity,
        regular_price=product.regular_price,
        discounted_price=product.discounted_price,
        product_rating=product.product_rating,
        product_review=product.product_review
    )
    return render_template('admin/edit_product.html', form=form)


@views.route('/product/<int:productid>/edit', methods=['POST'])
def edit_product_submission(productid):
    form = uploadProduct()
    if form.validate():
        try:
            app = create_app()
            product = Product.query.get(productid)
            image=form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.product_name = form.product_name.data,
            product.description = form.description.data,
            product.image = filename,
            product.quantity = form.quantity.data,
            product.regular_price = form.regular_price.data,
            product.discounted_price = form.discounted_price.data,
            product.product_rating = form.product_rating.data,
            product.product_review = form.product_review.data
            db.session.add(product)
            db.session.commit()
            flash("Product updated successfully")
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("Venue not updated successfully")
        finally:
            db.session.close()
    return redirect(url_for('views.view'))

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
        'description': product.description,
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
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=8)
    return render_template('admin/view_products.html', products=products)


@views.route('/admin/')
def dashboard():
    return render_template('admin/dashboard.html')


@views.route('/checkout')
def checkout():
    if current_user.is_authenticated:
        # user is logged in, show checkout page

        return render_template('checkout.html')
    else:
        # user is not logged in, redirect to login page
        return redirect(url_for('login'))


@views.route('/place_order', methods=['GET', 'POST'])
def place_order():
    items = session.get('cart')
    total = sum(item['price'] * item['quantity'] for item in items)
    order = Order(user_id=current_user.id, items=str(items), total=total)
    db.session.add(order)
    db.session.commit()
    session['cart'] = []  # clear cart after order is placed
    flash('Your order has been placed.', 'success')
    return redirect(url_for('index'))
