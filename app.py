from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask import Flask, render_template, session, redirect, url_for

# Flask app configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Arjun2003%23%40@127.0.0.1/stockroom_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Arjun2003' 

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# User model definition
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# Signup route for user registration
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if username or email already exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or Email already exists"}), 400

    # Create a new user instance
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = user.username  # Store the username in session
        session['user_id'] = user.user_id  # Store the user_id in session
        return jsonify({"message": "Login successful", "redirect": "/myStockroom"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/debug-session', methods=['GET'])
def debug_session():
    return jsonify(dict(session))

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Foreign key to the users table
    customer_name = db.Column(db.String(100), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())  # Auto-set current timestamp
    total_value = db.Column(db.Numeric(10, 2), nullable=False)

    user = db.relationship('User', backref=db.backref('orders', lazy=True))  # Link orders to users


@app.route('/myStockroom', methods=['GET', 'POST'])
def my_stockroom():
    if 'username' not in session:
        return redirect(url_for('index'))  # Redirect to login page if not logged in

    # Fetch the logged-in user
    username = session['username']
    user = User.query.filter_by(username=username).first()

    if not user:
        return redirect(url_for('index'))  # Redirect to login if user not found

    if request.method == 'POST':
        # Get form data
        customer_name = request.form.get('customer_name')
        total_value = request.form.get('total_value')

        # Create a new order and associate it with the user
        new_order = Order(
            user_id=user.user_id,
            customer_name=customer_name,
            total_value=float(total_value)  # Ensure value is converted to float
        )
        db.session.add(new_order)
        db.session.commit()

    # Fetch all orders for the logged-in user
    orders = Order.query.filter_by(user_id=user.user_id).all()

    # Render the myStockroom page with fetched orders
    return render_template('myStockroom.html', username=username, orders=orders)


class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Foreign key to the users table
    product_name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('inventory', lazy=True))  # Relationship to User model


@app.route('/NewInventory', methods=['GET', 'POST'])
def new_inventory():
    if 'username' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in
    
    # Fetch the logged-in user
    username = session['username']
    user = User.query.filter_by(username=username).first()

    if not user:
        return redirect(url_for('index'))  # Redirect if user not found

    if request.method == 'POST':
        # Get form data
        product_name = request.form.get('product_name')
        sku = request.form.get('sku')
        price = request.form.get('price')
        quantity = request.form.get('quantity')

        # Add new product to the inventory
        new_product = Inventory(
            user_id=user.user_id,
            product_name=product_name,
            sku=sku,
            price=price,
            quantity=quantity
        )
        db.session.add(new_product)
        db.session.commit()

    # Fetch inventory products for the logged-in user
    inventory = Inventory.query.filter_by(user_id=user.user_id).all()

    # Render the inventory page with fetched products
    return render_template('NewInventory.html', username=username, inventory=inventory)


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)  # Auto-increment primary key
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)  # Foreign key to orders table
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'), nullable=False)  # Foreign key to inventory table
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship('Order', backref=db.backref('order_items', lazy=True))  # Link order items to orders
    inventory = db.relationship('Inventory', backref=db.backref('order_items', lazy=True))  # Link order items to inventory


@app.route('/newOrder', methods=['GET', 'POST'])
def new_order():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login page if not logged in

    user_id = session['user_id']  # Retrieve user_id from session

    # Fetch all inventory items for the logged-in user
    inventory_items = Inventory.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        customer_name = request.json.get('customerName')
        order_items = request.json.get('orderItems')

        # Create a new order
        new_order = Order(user_id=user_id, customer_name=customer_name)
        db.session.add(new_order)
        db.session.commit()  # Commit the order to generate order_id

        # Add order items
        for item in order_items:
            inventory_item = Inventory.query.get(item['inventory_id'])
            if not inventory_item:
                continue  # Skip invalid inventory items

            quantity = int(item['quantity'])
            total_price = inventory_item.price * quantity

            new_order_item = OrderItem(
                order_id=new_order.order_id,
                inventory_id=inventory_item.inventory_id,
                quantity=quantity,
                price_per_unit=inventory_item.price,
                total_price=total_price
            )
            db.session.add(new_order_item)

        db.session.commit()  # Commit all order items
        return jsonify({"message": "Order created successfully!"}), 200

    return render_template('NewOrder.html', inventory=inventory_items)




@app.route('/')
def index():
    return render_template('FrontPage1.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(host="127.0.0.1", port=5555, debug=True)
