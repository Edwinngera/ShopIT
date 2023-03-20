from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __table_args__ = {'extend_existing': True}
    userid = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=True)
    lname = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(600), nullable=True)
    address1 = db.Column(db.String(), unique=False, nullable=True)
    address2 = db.Column(db.String(), unique=False, nullable=True)
    city = db.Column(db.String(), unique=False, nullable=True)
    state = db.Column(db.String(), unique=False, nullable=True)
    country = db.Column(db.String(), unique=False, nullable=True)
    zipcode = db.Column(db.String(), unique=False, nullable=True)
    email = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean(),nullable=True,default=True)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')


    def set_password(self, password):
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_id(self):
        return str(self.userid)
    
    def is_authenticated(self):
        return True

    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}'), '{self.password}', " \
               f"'{self.address1}', '{self.address2}', '{self.city}', '{self.state}', '{self.country}'," \
               f"'{self.zipcode}','{self.email}','{self.phone}')"


class Category(db.Model):
    __table_args__ = {'extend_existing': True}
    categoryid = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Category('{self.categoryid}', '{self.category_name}')"


class Product(db.Model):
    __table_args__ = {'extend_existing': True}
    productid = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    regular_price = db.Column(db.DECIMAL)
    discounted_price = db.Column(db.DECIMAL)
    product_rating = db.Column(db.DECIMAL)
    product_review = db.Column(db.String(100), nullable=True)

    

    def __repr__(self):
        return f"Product('{self.productid}','{self.product_name}','{self.description}', '{self.image}',  '{self.quantity}', '{self.regular_price}', '{self.discounted_price}')"


class ProductCategory(db.Model):
    __table_args__ = {'extend_existing': True}
    categoryid = db.Column(db.Integer, db.ForeignKey('category.categoryid'), nullable=False, primary_key=True)
    productid = db.Column(db.Integer, db.ForeignKey('product.productid'), nullable=False, primary_key=True)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Product('{self.categoryid}', '{self.productid}')"


class Cart(db.Model):
    __table_args__ = {'extend_existing': True}
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False, primary_key=True)
    productid = db.Column(db.Integer, db.ForeignKey('product.productid'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Cart('{self.userid}', '{self.productid}, '{self.quantity}')"


class Order(db.Model):
    __table_args__ = {'extend_existing': True}
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.userid'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    order_status = db.Column(db.String(20),nullable=False)
    total_price = db.Column(db.Float,nullable=False)
    order_items=db.Column(db.String(), nullable=False)

    customer = db.relationship('User', backref=db.backref('orders', lazy=True))
    def __repr__(self):
        return f"Order('{self.orderid}', '{self.order_date}','{self.total_price}','{self.userid}'')"


class SaleTransaction(db.Model):
    __table_args__ = {'extend_existing': True}
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.String(20))

    order = db.relationship('Order', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return f"Order('{self.payment_id}', '{self.orderid}','{self.payment_date}','{self.amount}', '{self.payment_status}','{self.methods}')"


