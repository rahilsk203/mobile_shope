import uuid
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone,timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from pytz import timezone

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
    


class Accessory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accessory_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    initial_stock = db.Column(db.Integer, default=0)
    added_stock = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float, default=0.0)
    minimum_stock = db.Column(db.Integer, default=0)
    last_purchase_quantity = db.Column(db.Integer, default=0)
    times_sold = db.Column(db.Integer, default=0)
    stock_out = db.Column(db.Integer, default=0)
    add_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_purchase_date = db.Column(db.DateTime, nullable=True)

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "accessory_name": self.accessory_name,
            "type": self.type,
            "company": self.company,
            "category": self.category,
            "initial_stock": self.initial_stock,
            "added_stock": self.added_stock,
            "unit_price": self.unit_price,
            "minimum_stock": self.minimum_stock,
            "last_purchase_quantity": self.last_purchase_quantity,
            "times_sold": self.times_sold,
            "stock_out": self.stock_out,
            "add_date": self.add_date.isoformat(),
            "last_purchase_date": self.last_purchase_date.isoformat() if self.last_purchase_date else None,
        }



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
    
    

# Route to manage accessories
@app.route('/accessory', methods=['GET'])
def manage_accessory():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    action = request.args.get('action')
    try:
        # Set Indian timezone
        india_tz = timezone('Asia/Kolkata')
        current_time_ist = datetime.now(india_tz)

        if action == "add":
            new_accessory = Accessory(
                accessory_name=request.args.get('accessory_name'),
                type=request.args.get('type'),
                company=request.args.get('company'),
                category=request.args.get('category'),
                initial_stock=int(request.args.get('initial_stock', 0)),
                added_stock=int(request.args.get('added_stock', 0)),
                unit_price=float(request.args.get('unit_price', 0.0)),
                minimum_stock=int(request.args.get('minimum_stock', 0)),
                add_date=current_time_ist
            )
            db.session.add(new_accessory)
            db.session.commit()
            return jsonify({"message": "Accessory added successfully", "add_date": current_time_ist.isoformat()}), 201

        elif action == "update":
            accessory_id = request.args.get('id')
            accessory = Accessory.query.get(accessory_id)
            if not accessory:
                return jsonify({"message": "Accessory not found"}), 404

            update_fields = {
                "added_stock": int(request.args.get('added_stock', 0)),
                "last_purchase_quantity": int(request.args.get('last_purchase_quantity', 0)),
                "unit_price": float(request.args.get('unit_price', accessory.unit_price)),
                "minimum_stock": int(request.args.get('minimum_stock', accessory.minimum_stock)),
                "times_sold": int(request.args.get('times_sold', accessory.times_sold)),
            }

            # Handle stock adjustments
            if update_fields["last_purchase_quantity"] > 0:
                accessory.added_stock -= update_fields["last_purchase_quantity"]
                accessory.stock_out += update_fields["last_purchase_quantity"]
                accessory.last_purchase_quantity = update_fields["last_purchase_quantity"]
                accessory.last_purchase_date = current_time_ist

            if update_fields["added_stock"] > 0:
                accessory.added_stock += update_fields["added_stock"]

            # Update fields dynamically
            for field, value in update_fields.items():
                if field not in ["added_stock", "last_purchase_quantity"] and request.args.get(field) is not None:
                    setattr(accessory, field, value)

            alert = accessory.added_stock < accessory.minimum_stock
            db.session.commit()

            return jsonify({
                "message": f"Accessory '{accessory.accessory_name}' updated successfully",
                "current_stock": accessory.added_stock,
                "stock_out": accessory.stock_out,
                "last_purchase_quantity": accessory.last_purchase_quantity,
                "last_purchase_date": current_time_ist.isoformat(),
                "alert": alert
            }), 200

        elif action == "delete":
            accessory_id = request.args.get('id')
            accessory = Accessory.query.get(accessory_id)
            if not accessory:
                return jsonify({"message": "Accessory not found"}), 404

            db.session.delete(accessory)
            db.session.commit()
            return jsonify({"message": f"Accessory with ID {accessory_id} deleted successfully"}), 200

        elif action == "view":
            accessory_id = request.args.get('id')
            if accessory_id:
                accessory = Accessory.query.get(accessory_id)
                if not accessory:
                    return jsonify({"message": "Accessory not found"}), 404

                current_stock = accessory.added_stock
                alert = current_stock < accessory.minimum_stock

                return jsonify({
                    "id": accessory.id,
                    "accessory_name": accessory.accessory_name,
                    "type": accessory.type,
                    "company": accessory.company,
                    "category": accessory.category,
                    "initial_stock": accessory.initial_stock,
                    "current_stock": current_stock,
                    "unit_price": accessory.unit_price,
                    "minimum_stock": accessory.minimum_stock,
                    "last_purchase_quantity": accessory.last_purchase_quantity,
                    "times_sold": accessory.times_sold,
                    "stock_out": accessory.stock_out,
                    "add_date": accessory.add_date.isoformat(),
                    "last_purchase_date": accessory.last_purchase_date.isoformat() if accessory.last_purchase_date else None,
                    "alert": alert
                }), 200
            else:
                accessories = Accessory.query.all()
                results = []
                for accessory in accessories:
                    current_stock = accessory.added_stock
                    alert = current_stock < accessory.minimum_stock

                    results.append({
                        "id": accessory.id,
                        "accessory_name": accessory.accessory_name,
                        "type": accessory.type,
                        "company": accessory.company,
                        "category": accessory.category,
                        "initial_stock": accessory.initial_stock,
                        "current_stock": current_stock,
                        "unit_price": accessory.unit_price,
                        "minimum_stock": accessory.minimum_stock,
                        "last_purchase_quantity": accessory.last_purchase_quantity,
                        "times_sold": accessory.times_sold,
                        "stock_out": accessory.stock_out,
                        "add_date": accessory.add_date.isoformat(),
                        "last_purchase_date": accessory.last_purchase_date.isoformat() if accessory.last_purchase_date else None,
                        "alert": alert
                    })

                return jsonify({"accessories": results}), 200

        else:
            return jsonify({"message": "Invalid action specified"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error occurred: {str(e)}"}), 500

    
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
    