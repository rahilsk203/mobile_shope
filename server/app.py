import uuid
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Flask app initialization
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database initialization
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    auth_key = db.Column(db.String(100), unique=True, nullable=False)

class RepairingProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class SellingProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), unique=True, nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    is_new = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Available or Sold Out
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # New field for date
    

class RepairingDevice(db.Model):
    __tablename__ = 'repairingdevice'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)  # Mandatory field
    phone_number = db.Column(db.String(15), nullable=True, default='N/A')  # Optional with default 'N/A'
    received_by = db.Column(db.String(50), nullable=True, default='N/A')  # Optional
    company = db.Column(db.String(100), nullable=True, default='N/A')  # Optional
    model = db.Column(db.String(100), nullable=True, default='N/A')  # Optional
    device_condition = db.Column(db.String(100), nullable=True, default='N/A')  # Optional
    repairing_status = db.Column(db.String(100), nullable=True, default='Pending')  # Optional, default 'Pending'
    repairing_cost = db.Column(db.Float, nullable=True, default=0.0)  # Optional, default 0.0
    estimated_delivery_date = db.Column(db.Date, nullable=True)  # Optional
    parts_replaced = db.Column(db.String(255), nullable=True, default='N/A')  # Optional
    bill_status = db.Column(db.String(50), nullable=True, default='Unpaid')  # Optional, default 'Unpaid'
    due_price = db.Column(db.Float, nullable=True, default=0.0)  # Optional, default 0.0
    advance_payment = db.Column(db.Float, nullable=True, default=0.0)  # Optional, default 0.0
    payment_method = db.Column(db.String(50), nullable=True, default='N/A')  # Optional
    delivery_status = db.Column(db.String(50), nullable=True, default='Pending')  # Optional, default 'Pending'
    technician_name = db.Column(db.String(100), nullable=True, default='N/A')  # Optional
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Auto-filled timestamp
    
    def update_status(self, is_available):
        self.status = "Available" if is_available else "Sold Out"

# Utility function to verify auth key
def verify_auth_key(auth_key):
    user = User.query.filter_by(auth_key=auth_key).first()
    return user is not None

# Manually create tables
with app.app_context():
    db.create_all()

# User Management APIs
@app.route('/register', methods=['GET'])
def register():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    auth_key = str(uuid.uuid4())
    new_user = User(username=username, password=hashed_password, auth_key=auth_key)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "auth_key": auth_key}), 201

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"message": f"User '{username}' logged in successfully", "auth_key": user.auth_key}), 200

# Repairing Product Management APIs
@app.route('/repairing/add', methods=['GET'])
def add_repairing_product():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    name = request.args.get('name')
    type = request.args.get('type')
    company = request.args.get('company')
    model = request.args.get('model')
    quantity = request.args.get('quantity')

    if not name or not type or not company or not model or not quantity:
        return jsonify({"message": "All fields are required"}), 400

    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message": "Quantity must be an integer"}), 400

    product = RepairingProduct(name=name, type=type, company=company, model=model, quantity=quantity)
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": f"Repairing product '{name}' added successfully"}), 201

@app.route('/repairing/view', methods=['GET'])
def view_repairing_products():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    products = RepairingProduct.query.all()
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "type": product.type,
            "company": product.company,
            "model": product.model,
            "quantity": product.quantity
        }
        for product in products
    ]
    return jsonify({"repairing_products": product_list}), 200

# Selling Product Management APIs
@app.route('/selling/add', methods=['GET'])
def add_selling_product():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    name = request.args.get('name')
    type = request.args.get('type')
    price = request.args.get('price')
    quantity = request.args.get('quantity')

    if not name or not type or not price or not quantity: 
        return jsonify({"message": "All fields are required"}), 400

    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message": "Price must be a float and quantity an integer"}), 400

    product = SellingProduct(name=name, type=type, price=price, quantity=quantity)
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": f"Selling product '{name}' added successfully"}), 201

@app.route('/selling/view', methods=['GET'])
def view_selling_products():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    products = SellingProduct.query.all()
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "type": product.type,
            "price": product.price,
            "quantity": product.quantity
        }
        for product in products
    ]
    return jsonify({"selling_products": product_list}), 200

@app.route('/phone/add', methods=['GET'])
def add_phone():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    imei = request.args.get('imei')
    model_name = request.args.get('model_name')
    company = request.args.get('company')
    is_new = request.args.get('is_new')
    price = request.args.get('price')
    is_available = request.args.get('is_available')  # This will replace stock

    if not imei or not model_name or not company or is_new is None or not price or is_available is None:
        return jsonify({"message": "All fields are required (IMEI, model_name, company, is_new, price, is_available)"}), 400

    try:
        is_new = bool(int(is_new))
        price = float(price)
        is_available = bool(int(is_available))  # 1 for available, 0 for sold out
    except ValueError:
        return jsonify({"message": "Invalid input values"}), 400

    if Phone.query.filter_by(imei=imei).first():
        return jsonify({"message": "Phone with this IMEI already exists"}), 400

    # Set status based on availability
    status = "Available" if is_available else "Sold Out"
    
    phone = Phone(imei=imei, model_name=model_name, company=company, is_new=is_new, price=price, status=status)
    db.session.add(phone)
    db.session.commit()

    phone_type = "New" if is_new else "Old"
    return jsonify({"message": f"{phone_type} phone '{model_name}' by {company} added successfully"}), 201



@app.route('/phone/view', methods=['GET'])
def view_phones():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    phones = Phone.query.all()
    phone_list = [
        {
            "id": phone.id,
            "imei": phone.imei,
            "model_name": phone.model_name,
            "company": phone.company,
            "is_new": "New" if phone.is_new else "Old",
            "price": phone.price,
            "status": phone.status,  # Showing status (Available or Sold Out)
            "date_added": phone.date_added
        }
        for phone in phones
    ]
    return jsonify({"phones": phone_list}), 200

    
# ----- Repairing Product Management -----
@app.route('/repairing/edit', methods=['GET'])
def edit_repairing_product():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    product_id = request.args.get('id')
    name = request.args.get('name')
    type = request.args.get('type')
    company = request.args.get('company')
    model = request.args.get('model')
    quantity = request.args.get('quantity')

    product = RepairingProduct.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if name: product.name = name
    if type: product.type = type
    if company: product.company = company
    if model: product.model = model
    if quantity:
        try:
            product.quantity = int(quantity)
        except ValueError:
            return jsonify({"message": "Quantity must be an integer"}), 400

    db.session.commit()
    return jsonify({"message": f"Repairing product '{product.name}' updated successfully"}), 200

@app.route('/repairing/delete', methods=['GET'])
def delete_repairing_product():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    product_id = request.args.get('id')
    product = RepairingProduct.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Repairing product '{product.name}' deleted successfully"}), 200

# ----- Selling Product Management -----
@app.route('/selling/edit', methods=['GET'])
def edit_selling_product():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    product_id = request.args.get('id')
    name = request.args.get('name')
    type = request.args.get('type')
    price = request.args.get('price')
    quantity = request.args.get('quantity')

    product = SellingProduct.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if name: product.name = name
    if type: product.type = type
    if price:
        try:
            product.price = float(price)
        except ValueError:
            return jsonify({"message": "Price must be a float"}), 400
    if quantity:
        try:
            product.quantity = int(quantity)
        except ValueError:
            return jsonify({"message": "Quantity must be an integer"}), 400

    db.session.commit()
    return jsonify({"message": f"Selling product '{product.name}' updated successfully"}), 200

@app.route('/selling/delete', methods=['GET'])
def delete_selling_product():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    product_id = request.args.get('id')
    product = SellingProduct.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Selling product '{product.name}' deleted successfully"}), 200

# ----- Phone Management -----
@app.route('/phone/edit', methods=['GET'])
def edit_phone():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    phone_id = request.args.get('id')
    imei = request.args.get('imei')
    model_name = request.args.get('model_name')
    company = request.args.get('company')
    is_new = request.args.get('is_new')
    price = request.args.get('price')
    is_available = request.args.get('is_available')  # New availability field

    phone = Phone.query.filter_by(id=phone_id).first()
    if not phone:
        return jsonify({"message": "Phone not found"}), 404

    if imei: phone.imei = imei
    if model_name: phone.model_name = model_name
    if company: phone.company = company
    if is_new is not None:
        try:
            phone.is_new = bool(int(is_new))
        except ValueError:
            return jsonify({"message": "is_new must be 0 (old) or 1 (new)"}), 400
    if price: 
        try:
            phone.price = float(price)
        except ValueError:
            return jsonify({"message": "Price must be a float"}), 400
    if is_available is not None:
        try:
            is_available = bool(int(is_available))  # 1 for available, 0 for sold out
            phone.update_status(is_available)
        except ValueError:
            return jsonify({"message": "is_available must be 0 (sold out) or 1 (available)"}), 400

    db.session.commit()
    return jsonify({"message": f"Phone '{phone.model_name}' updated successfully"}), 200


@app.route('/phone/delete', methods=['GET'])
def delete_phone():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    phone_id = request.args.get('id')
    phone = Phone.query.filter_by(id=phone_id).first()
    if not phone:
        return jsonify({"message": "Phone not found"}), 404

    db.session.delete(phone)
    db.session.commit()
    return jsonify({"message": f"Phone '{phone.model_name}' deleted successfully"}), 200
    


@app.route('/repairingdevice/add', methods=['GET'])
def add_repairing_device():
    # Extract parameters from the request, handling empty or missing strings
    def handle_missing_string(value, default="None"):
        return value.strip() if value and value.strip() else default

    auth_key = request.args.get('auth_key')
    customer_name = handle_missing_string(request.args.get('customer_name'), "N/A")
    phone_number = handle_missing_string(request.args.get('phone_number'), "N/A")
    received_by = handle_missing_string(request.args.get('received_by'), "N/A")
    company = handle_missing_string(request.args.get('company'), "N/A")
    model = handle_missing_string(request.args.get('model'), "N/A")
    device_condition = handle_missing_string(request.args.get('device_condition'), "N/A")
    repairing_status = handle_missing_string(request.args.get('repairing_status'), "Pending")
    parts_replaced = handle_missing_string(request.args.get('parts_replaced'), "N/A")
    bill_status = handle_missing_string(request.args.get('bill_status'), "Unpaid")
    payment_method = handle_missing_string(request.args.get('payment_method'), "N/A")
    delivery_status = handle_missing_string(request.args.get('delivery_status'), "Pending")
    technician_name = handle_missing_string(request.args.get('technician_name'), "N/A")

    # Handle numeric fields
    def handle_missing_numeric(value, default=0.0):
        try:
            return float(value) if value and value.strip() else default
        except ValueError:
            return default

    repairing_cost = handle_missing_numeric(request.args.get('repairing_cost'))
    due_price = handle_missing_numeric(request.args.get('due_price'))
    advance_payment = handle_missing_numeric(request.args.get('advance_payment'))

    # Handle date fields
    estimated_delivery_date = request.args.get('estimated_delivery_date')
    if estimated_delivery_date:
        try:
            estimated_delivery_date = datetime.strptime(estimated_delivery_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use 'YYYY-MM-DD'."}), 400

    # Validate if the user is authorized
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    # Creating the new repairing device object
    repairing_device = RepairingDevice(
        customer_name=customer_name,
        phone_number=phone_number,
        received_by=received_by,
        company=company,
        model=model,
        device_condition=device_condition,
        repairing_status=repairing_status,
        repairing_cost=repairing_cost,
        estimated_delivery_date=estimated_delivery_date,
        parts_replaced=parts_replaced,
        bill_status=bill_status,
        due_price=due_price,
        advance_payment=advance_payment,
        payment_method=payment_method,
        delivery_status=delivery_status,
        technician_name=technician_name,
    )

    try:
        db.session.add(repairing_device)
        db.session.commit()
        return jsonify({"message": "Repairing device added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add repairing device. Error: {str(e)}"}), 500
        
@app.route('/repairingdevice/view', methods=['GET'])
def view_repairing_devices():
    # Extract auth key from the request
    auth_key = request.args.get('auth_key')

    # Verify if the user is authorized
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    # Query all repairing devices from the database
    repairing_devices = RepairingDevice.query.all()

    # Prepare the list of repairing devices
    device_list = [
        {
            "id": device.id,
            "customer_name": device.customer_name,
            "phone_number": device.phone_number,
            "received_by": device.received_by,
            "company": device.company,
            "model": device.model,
            "device_condition": device.device_condition,
            "repairing_status": device.repairing_status,
            "repairing_cost": device.repairing_cost,
            "estimated_delivery_date": device.estimated_delivery_date,
            "parts_replaced": device.parts_replaced,
            "bill_status": device.bill_status,
            "due_price": device.due_price,
            "advance_payment": device.advance_payment,
            "payment_method": device.payment_method,
            "delivery_status": device.delivery_status,
            "technician_name": device.technician_name,
            "date_added": device.date_added
        }
        for device in repairing_devices
    ]

    # Return the list of repairing devices in the response
    return jsonify({"repairing_devices": device_list}), 200
    
@app.route('/repairingdevice/delete', methods=['GET'])
def delete_repairing_device():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    device_id = request.args.get('id')
    repairing_device = RepairingDevice.query.filter_by(id=device_id).first()
    if not repairing_device:
        return jsonify({"message": "Repairing device not found"}), 404

    db.session.delete(repairing_device)
    db.session.commit()
    return jsonify({"message": f"Repairing device with ID {device_id} deleted successfully"}), 200
    
    
@app.route('/repairingdevice/edit', methods=['GET'])
def edit_repairing_device():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    device_id = request.args.get('id')
    repairing_device = RepairingDevice.query.filter_by(id=device_id).first()
    if not repairing_device:
        return jsonify({"message": "Repairing device not found"}), 404

    # Optional fields for editing
    customer_name = request.args.get('customer_name')
    phone_number = request.args.get('phone_number')
    received_by = request.args.get('received_by')
    company = request.args.get('company')
    model = request.args.get('model')
    device_condition = request.args.get('device_condition')
    repairing_status = request.args.get('repairing_status')
    repairing_cost = request.args.get('repairing_cost')
    estimated_delivery_date = request.args.get('estimated_delivery_date')
    parts_replaced = request.args.get('parts_replaced')
    bill_status = request.args.get('bill_status')
    due_price = request.args.get('due_price')
    advance_payment = request.args.get('advance_payment')
    payment_method = request.args.get('payment_method')
    delivery_status = request.args.get('delivery_status')
    technician_name = request.args.get('technician_name')

    # Update fields if provided
    if customer_name: repairing_device.customer_name = customer_name
    if phone_number: repairing_device.phone_number = phone_number
    if received_by: repairing_device.received_by = received_by
    if company: repairing_device.company = company
    if model: repairing_device.model = model
    if device_condition: repairing_device.device_condition = device_condition
    if repairing_status: repairing_device.repairing_status = repairing_status
    if repairing_cost: repairing_device.repairing_cost = repairing_cost
    if estimated_delivery_date:
        try:
            repairing_device.estimated_delivery_date = datetime.strptime(estimated_delivery_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use 'YYYY-MM-DD'."}), 400
    if parts_replaced: repairing_device.parts_replaced = parts_replaced
    if bill_status: repairing_device.bill_status = bill_status
    if due_price: repairing_device.due_price = due_price
    if advance_payment: repairing_device.advance_payment = advance_payment
    if payment_method: repairing_device.payment_method = payment_method
    if delivery_status: repairing_device.delivery_status = delivery_status
    if technician_name: repairing_device.technician_name = technician_name

    db.session.commit()
    return jsonify({"message": f"Repairing device with ID {device_id} updated successfully"}), 200


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
    