from flask import Flask, render_template, redirect, request, flash, url_for, jsonify, Blueprint, abort, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from .forms import uploadProduct, CheckoutForm,EditUserForm
import os
from werkzeug.utils import secure_filename
from .models import Product, Order,User
from . import db
from . import create_app
from .auth import role_required
from datetime import datetime



views = Blueprint('views', __name__)

#Customer views
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
    products = Product.query.paginate(page=page, per_page=7)
    # products = Product.query.all()
    return render_template('products.html', products=products)


@views.route('/products_details/<int:productid>', methods=['GET', 'POST'])
def products_details(productid):
    product = Product.query.get(productid)
    return render_template('product-details.html', product=product)


@views.route('/cart')
def cart():
    cart = session.get('cart', [])
    subtotal = sum(float(item['price']) *
                   float(item['quantity']) for item in cart)
    vat = (16/100)*subtotal
    total = subtotal+vat
    return render_template('cart.html', subtotal=subtotal, total=total, vat=vat)


@views.route('/account')
def account():
    return render_template('account.html')



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

#remove item from the cart
@views.route('/remove_item/<int:id>', methods=['GET'])
def remove_item(id):
    cart=session["cart"]
    for i in cart:
        if int(i['id']) == id:
            print("Edwin")
            cart.remove(i)
            session['cart'] = cart
    return redirect(url_for('views.cart'))



@views.route('/view')
def view():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=8)
    return render_template('admin/view_products.html', products=products)


@views.route('/orders/')
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.paginate(page=page, per_page=8)
    print(orders.items)
    return render_template('admin/orders.html',orders=orders)

@views.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    cart = session.get('cart', [])
    subtotal = sum(float(item['price']) *
                   float(item['quantity']) for item in cart)
    vat = (16/100)*subtotal
    total = subtotal+vat
    if form.validate_on_submit():
        shipping_address = form.shipping_address.data
        billing_address = form.billing_address.data
        card_number = form.card_number.data
        card_cvv = form.card_cvv.data
        items = session.get('cart')
        order = Order(customer_id=current_user.userid,
                    order_status='Pending', total_price=total, order_items=str(items))
        
        db.session.add(order)
        db.session.commit()

        # Clear the cart after the order has been placed
        session['cart'] = []
        print('Edwin')

        flash('Your order has been placed!', 'success')
        return redirect(url_for('views.view_orders'))
    return render_template('checkout.html', title='Checkout', form=form, total=total, vat=vat, subtotal=subtotal)


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


# Admin

@login_required
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


@login_required
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


@login_required
@views.route('/product/<int:productid>/edit', methods=['POST'])
def edit_product_submission(productid):
    form = uploadProduct()
    if form.validate():
        try:
            app = create_app()
            product = Product.query.get(productid)
            image = form.image.data
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
        return  redirect(url_for('views.view'))
      

    except Exception as e:
        abort(422)

    return redirect()

@login_required
@views.route('/view_order', methods=['GET', 'POST'])
def view_orders():
    order_reponse=[]
    orders = Order.query.filter(Order.customer_id == current_user.userid).all()
    for order in orders:
        print(order.customer_id)
    return render_template('view_orders.html',orders=orders)
 


@views.route('/users', methods=['GET', 'POST'])
@login_required
# @role_required('Admin')
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=8)
    return render_template('admin/staff.html',users=users)

@login_required
@views.route('/edit/users/<int:userid>', methods=['GET', 'POST'])
def edit_user(userid):
    user=User.query.get(userid)
    form = EditUserForm(
        name=user.fname,
        role=user.role,
        email=user.email,
    )
    return render_template('admin/edit_user.html', form=form)


@login_required
@views.route('/admin/')
def dashboard():
    orders=Order.query.all()
    products=Product.query.all()

    dates=[]
    total_sales=0
    num_orders=[]
    
    for order in orders:
        total_sales+=order.total_price
        date=order.order_date
        dates.append(date.strftime("%d-%m-%y"))
    dates=set(dates)
    dates=list(dates)
    dates.sort(key = lambda date: datetime.strptime(date, "%d-%m-%y"))
    for  date in dates:
        count=0
        for order in orders:
            if order.order_date.strftime("%d-%m-%y")==date:
                count+=1
        num_orders.append(count)
    print(dates)
    return render_template('admin/dashboard.html', orders=len(orders), products=len(products),total_sales=total_sales, num_orders=num_orders, dates=dates)



