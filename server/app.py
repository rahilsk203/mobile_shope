import uuid
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from pytz import timezone
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

    def __repr__(self):
        return f"<User {self.username}>"

class RepairingProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<RepairingProduct {self.name}, Type: {self.type}>"
        
        
class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), unique=True, nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    is_new = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # "Available" or "Sold Out"
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Auto-filled timestamp

    def __repr__(self):
        return f"<Phone {self.model_name}, IMEI: {self.imei}>"

    # Method to update phone status
    def update_status(self, is_available):
        self.status = "Available" if is_available else "Sold Out"
        

        
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
    add_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_purchase_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Accessory {self.accessory_name}, Stock: {self.added_stock}>"

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
        
        
class RepairingAccessory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Change to Integer with autoincrement
    name = db.Column(db.String(100))
    type = db.Column(db.String(100))
    repairing_cost = db.Column(db.Float)
    selling_cost = db.Column(db.Float)
    current_stock = db.Column(db.Integer)
    add_stock = db.Column(db.Integer, default=0)
    last_purchase_quantity = db.Column(db.Integer, default=0)
    last_repairing_quantity = db.Column(db.Integer, default=0)
    total_out_stock = db.Column(db.Integer, default=0)
    last_purchase_date = db.Column(db.DateTime)
    last_repairing_date = db.Column(db.DateTime)
    minimum_stock = db.Column(db.Integer, default=0)
    alert = db.Column(db.Boolean, default=False)
    company = db.Column(db.String(100))
    model = db.Column(db.String(100))
    
    
    def __repr__(self):
        return f"<RepairingAccessory {self.name}, Stock: {self.current_stock}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "repairing_cost": self.repairing_cost,
            "selling_cost": self.selling_cost,
            "current_stock": self.current_stock,
            "add_stock": self.add_stock,
            "last_purchase_quantity": self.last_purchase_quantity,
            "last_repairing_quantity": self.last_repairing_quantity,
            "total_out_stock": self.total_out_stock,
            "last_purchase_date": self.last_purchase_date.isoformat() if self.last_purchase_date else None,
            "minimum_stock": self.minimum_stock,
            "last_repairing_date": self.last_repairing_date.isoformat() if self.last_repairing_date else None,
            "alert": self.alert,
            "company": self.company,
            "model": self.model
        }        
        
        
        
class RepairingDevice(db.Model):
    __tablename__ = 'repairing_device'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), default='N/A')
    received_by = db.Column(db.String(50), default='N/A')
    company = db.Column(db.String(100), default='N/A')
    model = db.Column(db.String(100), default='N/A')
    device_condition = db.Column(db.String(100), default='N/A')
    repairing_status = db.Column(db.String(100), default='Pending')
    repairing_cost = db.Column(db.Float, default=0.0)
    estimated_delivery_date = db.Column(db.Date, nullable=True)
    parts_replaced = db.Column(db.String(255), default='N/A')
    bill_status = db.Column(db.String(50), default='Unpaid')
    due_price = db.Column(db.Float, default=0.0)
    advance_payment = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(50), default='N/A')
    delivery_status = db.Column(db.String(50), default='Pending')
    technician_name = db.Column(db.String(100), default='N/A')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RepairingDevice {self.customer_name}, Status: {self.repairing_status}>"


class RepairingInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(100), nullable=False, unique=True)
    repairing_device_id = db.Column(db.Integer, db.ForeignKey('repairing_device.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    repairing_cost = db.Column(db.Float, default=0.0)
    advance_payment = db.Column(db.Float, default=0.0)
    due_price = db.Column(db.Float, default=0.0)
    bill_status = db.Column(db.String(50), default='Unpaid')
    payment_method = db.Column(db.String(50), default='N/A')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    repairing_device = db.relationship('RepairingDevice', backref='repairing_invoices', lazy=True)
    shop = db.relationship('Shop', backref='repairing_invoice_history', lazy=True)

    def __repr__(self):
        return f"<RepairingInvoice {self.invoice_id}>"
    

# Models
class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Shop {self.name}>"
        
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False)
    customer_location = db.Column(db.String(200), nullable=False)
    phone_id = db.Column(db.Integer, db.ForeignKey('phone.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    shop = db.relationship('Shop', backref='invoices')
    phone = db.relationship('Phone', backref='invoices')

    def __repr__(self):
        return f"<Invoice {self.id} - {self.customer_name}>"

    @property
    def due_amount(self):
        # Calculate due amount dynamically
        return self.total_amount - self.paid_amount

    def update_paid_amount(self, payment):
        """Update the paid amount and reflect changes in due_amount."""
        self.paid_amount += payment
        db.session.commit()

class Due(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    phone_model = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    paid_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with the Invoice
    invoice = db.relationship('Invoice', backref='dues')

    def __repr__(self):
        return f"<Due {self.id} - {self.phone_model}>"

    def add_payment(self, payment):
        # Update the paid_amount for the Due record
        self.paid_amount += payment
        self.payment_date = datetime.utcnow()  # Set the payment date to the current time
        db.session.commit()

        # Update the corresponding Invoice's due amount
        invoice = Invoice.query.get(self.invoice_id)
        invoice.update_due(payment)

class InvoiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False)
    customer_location = db.Column(db.String(200), nullable=False)
    total_paid = db.Column(db.Float, nullable=False)
    total_due = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with Invoice
    invoice = db.relationship('Invoice', backref='history')

    def __repr__(self):
        return f"<InvoiceHistory {self.id} - {self.invoice_id}>"
 



    
    def __repr__(self):
        return f"<RepairingAccessory {self.name}, Stock: {self.current_stock}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "repairing_cost": self.repairing_cost,
            "selling_cost": self.selling_cost,
            "current_stock": self.current_stock,
            "add_stock": self.add_stock,
            "last_purchase_quantity": self.last_purchase_quantity,
            "last_repairing_quantity": self.last_repairing_quantity,
            "total_out_stock": self.total_out_stock,
            "last_purchase_date": self.last_purchase_date.isoformat() if self.last_purchase_date else None,
            "minimum_stock": self.minimum_stock,
            "last_repairing_date": self.last_repairing_date.isoformat() if self.last_repairing_date else None,
            "alert": self.alert,
            "company": self.company,
            "model": self.model
        }
        
        
class AccessorieInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(36), nullable=False, unique=True)  # UUID
    user_name = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(15), nullable=False)
    accessory_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    shop_name = db.Column(db.String(100), nullable=False)
    shop_address = db.Column(db.String(200), nullable=False)
    shop_phone = db.Column(db.String(15), nullable=False)
    shop_email = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Invoice {self.invoice_id}>"

# Utility function to verify auth key
def verify_auth_key(auth_key):
    return User.query.filter_by(auth_key=auth_key).first() is not None

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

@app.route('/repairing_accessory', methods=['GET'])
def manage_repairing_accessory():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    action = request.args.get('action')
    try:
        india_tz = timezone('Asia/Kolkata')
        current_time_ist = datetime.now(india_tz)

        if action == "add":
            # Adding a new repairing accessory
            name = request.args.get('name')
            type_ = request.args.get('type')
            company = request.args.get('company')
            model = request.args.get('model')

            existing_accessory = RepairingAccessory.query.filter_by(
                name=name, type=type_, company=company, model=model
            ).first()

            if existing_accessory:
                return jsonify({"message": "Repairing accessory already exists."}), 400

            new_accessory = RepairingAccessory(
                name=name,
                type=type_,
                repairing_cost=float(request.args.get('repairing_cost', 0.0)),
                selling_cost=float(request.args.get('selling_cost', 0.0)),
                current_stock=int(request.args.get('current_stock', 0)),
                add_stock=int(request.args.get('current_stock', 0)),
                minimum_stock=int(request.args.get('minimum_stock', 0)),
                alert=False,
                company=company,
                model=model
            )
            db.session.add(new_accessory)
            db.session.commit()
            return jsonify({
                "message": "Repairing accessory added successfully",
                "add_date": current_time_ist.isoformat()
            }), 201

        elif action == "update":
            # Updating an existing repairing accessory
            accessory_id = request.args.get('id')
            accessory = RepairingAccessory.query.get(accessory_id)
            if not accessory:
                return jsonify({"message": "Repairing accessory not found"}), 404

            add_stock = int(request.args.get('add_stock', 0))
            last_purchase_quantity = int(request.args.get('last_purchase_quantity', 0))
            last_repairing_quantity = int(request.args.get('last_repairing_quantity', 0))

            if add_stock > 0:
                accessory.current_stock += add_stock
                accessory.add_stock += add_stock

            if last_purchase_quantity > 0:
                accessory.last_purchase_quantity = last_purchase_quantity
                accessory.current_stock -= last_purchase_quantity
                accessory.total_out_stock += last_purchase_quantity
                accessory.last_purchase_date = current_time_ist

            if last_repairing_quantity > 0:
                accessory.last_repairing_quantity = last_repairing_quantity
                accessory.current_stock -= last_repairing_quantity
                accessory.total_out_stock += last_repairing_quantity
                accessory.last_repairing_date = current_time_ist

            accessory.repairing_cost = float(request.args.get('repairing_cost', accessory.repairing_cost))
            accessory.selling_cost = float(request.args.get('selling_cost', accessory.selling_cost))

            accessory.alert = accessory.current_stock < accessory.minimum_stock

            db.session.commit()

            return jsonify({
                "message": f"Repairing accessory '{accessory.name}' updated successfully",
                **accessory.to_dict()
            }), 200

        elif action == "delete":
            # Deleting an existing repairing accessory
            accessory_id = request.args.get('id')
            accessory = RepairingAccessory.query.get(accessory_id)
            if not accessory:
                return jsonify({"message": "Repairing accessory not found"}), 404

            db.session.delete(accessory)
            db.session.commit()
            return jsonify({"message": f"Repairing accessory with ID {accessory_id} deleted successfully"}), 200

        elif action == "view":
            # Viewing one or all repairing accessories
            accessory_id = request.args.get('id')
            if accessory_id:
                accessory = RepairingAccessory.query.get(accessory_id)
                if not accessory:
                    return jsonify({"message": "Repairing accessory not found"}), 404

                return jsonify(accessory.to_dict()), 200
            else:
                accessories = RepairingAccessory.query.all()
                return jsonify({
                    "repairing_accessories": [accessory.to_dict() for accessory in accessories]
                }), 200

        else:
            return jsonify({"message": "Invalid action specified"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error occurred: {str(e)}"}), 500
        
        
        
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


@app.route('/add_shop', methods=['GET'])
def add_shop():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    name = request.args.get('name')
    address = request.args.get('address')
    phone = request.args.get('phone')
    email = request.args.get('email')

    if not name or not address or not phone:
        return jsonify({'error': 'Name, address, and phone are required'}), 400

    shop = Shop(name=name, address=address, phone=phone, email=email)
    db.session.add(shop)
    db.session.commit()

    return jsonify({'message': 'Shop added successfully', 'shop_id': shop.id}), 200
    
    
@app.route('/generate_invoice', methods=['GET'])
def generate_invoice():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403
        
    user_name = request.args.get('name')
    user_phone = request.args.get('phone')
    user_location = request.args.get('location')
    imei = request.args.get('imei')
    shop_id = request.args.get('shop_id')  # Shop ID provided by the user
    paid_amount = float(request.args.get('paid_amount', 0.0))

    # Validate shop
    shop = Shop.query.filter_by(id=shop_id).first()
    if not shop:
        return jsonify({'error': 'Shop not found'}), 404

    # Find phone details by IMEI
    phone = Phone.query.filter_by(imei=imei).first()
    if not phone:
        return jsonify({'error': 'Phone with given IMEI not found'}), 404

    # Check if phone is already sold
    if phone.status == "Sold Out":
        return jsonify({'error': 'Phone is already sold out'}), 400

    total_amount = phone.price
    due_amount = total_amount - paid_amount

    # Create Invoice
    invoice = Invoice(
    customer_name=user_name,
    customer_phone=user_phone,
    customer_location=user_location,
    phone_id=phone.id,
    shop_id=shop.id,
    total_amount=total_amount,
    paid_amount=paid_amount,
)
    db.session.add(invoice)
    db.session.commit()  # Commit to get the invoice_id

    # Add Initial Due Record (Make sure invoice_id is available)
    due = Due(
        invoice_id=invoice.id,
        phone_model=phone.model_name,
        customer_name=user_name,
        paid_amount=paid_amount,
        payment_date=datetime.utcnow()  # Set payment_date as current time
    )
    db.session.add(due)

    # Add Invoice History
    invoice_history = InvoiceHistory(
        invoice_id=invoice.id,
        customer_name=user_name,
        customer_phone=user_phone,
        customer_location=user_location,
        total_paid=paid_amount,
        total_due=due_amount,
        total_amount=total_amount
    )
    db.session.add(invoice_history)

    # Update phone status to "Sold Out"
    phone.update_status(False)
    db.session.commit()

    # Fetch the created invoice details
    invoice_details = {
        'invoice_id': invoice.id,
        'customer_name': invoice.customer_name,
        'customer_phone': invoice.customer_phone,
        'customer_location': invoice.customer_location,
        'total_amount': invoice.total_amount,
        'paid_amount': invoice.paid_amount,
        'due_amount': invoice.due_amount,
        'date_created': invoice.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        'phone': {
            'model_name': phone.model_name,
            'company': phone.company,
            'imei': phone.imei,
            'price': phone.price
        },
        'shop': {
            'name': shop.name,
            'address': shop.address,
            'phone': shop.phone,
            'email': shop.email
        },
        'due': {
            'phone_model': due.phone_model,
            'customer_name': due.customer_name,
            'paid_amount': due.paid_amount,
            'payment_date': due.payment_date.strftime('%Y-%m-%d %H:%M:%S')  # Format payment_date
        },
        'invoice_history': {
            'total_paid': invoice_history.total_paid,
            'total_due': invoice_history.total_due,
            'total_amount': invoice_history.total_amount,
            'last_updated': invoice_history.last_updated.strftime('%Y-%m-%d %H:%M:%S')  # Format last_updated
        }
    }

    return jsonify({
        'message': 'Invoice created successfully',
        'invoice_details': invoice_details
    }), 200
 
@app.route('/add_payment', methods=['GET'])
def add_payment():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    invoice_id = request.args.get('invoice_id')
    payment = float(request.args.get('payment', 0.0))

    # Fetch invoice
    invoice = Invoice.query.filter_by(id=invoice_id).first()
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    # Validate payment
    if payment <= 0:
        return jsonify({'error': 'Payment must be greater than 0'}), 400
    if payment > invoice.due_amount:
        return jsonify({'error': 'Payment exceeds due amount'}), 400

    # Update invoice payment
    invoice.update_paid_amount(payment)

    # Log the payment in Due table
    due = Due(
        invoice_id=invoice.id,
        phone_model=invoice.phone.model_name,
        customer_name=invoice.customer_name,
        paid_amount=payment,
        payment_date=datetime.utcnow()
    )
    db.session.add(due)

    # Update InvoiceHistory
    invoice_history = InvoiceHistory.query.filter_by(invoice_id=invoice_id).first()
    if invoice_history:
        invoice_history.total_paid += payment
        invoice_history.total_due = invoice.due_amount

    db.session.commit()

    return jsonify({
        'message': 'Payment added successfully',
        'remaining_due': invoice.due_amount
    }), 200

@app.route('/invoice_history', methods=['GET'])
def invoice_history():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    invoices = Invoice.query.all()  # Fetch all invoices
    result = []
    for invoice in invoices:
        # Fetch the corresponding phone
        phone = Phone.query.filter_by(id=invoice.phone_id).first()
        if not phone:
            continue

        # Fetch the corresponding shop
        shop = Shop.query.filter_by(id=invoice.shop_id).first()
        if not shop:
            continue

        # Fetch the corresponding invoice history
        history = InvoiceHistory.query.filter_by(invoice_id=invoice.id).first()
        if not history:
            continue

        # Fetch all dues for this invoice
        due = Due.query.filter_by(invoice_id=invoice.id).all()

        # Add details to the result
        result.append({
            'invoice_id': invoice.id,
            'customer_name': invoice.customer_name,
            'customer_phone': invoice.customer_phone,
            'customer_location': invoice.customer_location,
            'total_paid': invoice.paid_amount,
            'total_due': invoice.due_amount,
            'total_amount': invoice.total_amount,
            'date_created': invoice.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'phone_details': {
                'model_name': phone.model_name,
                'company': phone.company,
                'imei': phone.imei,
                'price': phone.price,
                'status': phone.status,
                'is_new': phone.is_new,
                'date_added': phone.date_added.strftime('%Y-%m-%d %H:%M:%S')
            },
            'shop_details': {
                'name': shop.name,
                'address': shop.address,
                'phone': shop.phone,
                'email': shop.email
            },
            'invoice_history': {
                'invoice_id': history.invoice_id,
                'customer_name': history.customer_name,
                'customer_phone': history.customer_phone,
                'customer_location': history.customer_location,
                'total_paid': history.total_paid,
                'total_due': history.total_due,
                'total_amount': history.total_amount,
                'last_updated': history.last_updated.strftime('%Y-%m-%d %H:%M:%S')
            },
            'due_details': [
                {
                    'phone_model': due_item.phone_model,
                    'customer_name': due_item.customer_name,
                    'paid_amount': due_item.paid_amount,
                    'payment_date': due_item.payment_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                for due_item in due
            ]
        })

    return jsonify({'invoice_history': result}), 200
    
    


@app.route('/repairingdevice/invoice', methods=['GET'])
def generate_and_save_invoice():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    device_id = request.args.get('id')
    shop_id = request.args.get('shop_id')

    # Get the repairing device
    repairing_device = RepairingDevice.query.filter_by(id=device_id).first()
    if not repairing_device:
        return jsonify({"message": "Repairing device not found"}), 404

    # Get the shop details
    shop = Shop.query.filter_by(id=shop_id).first()
    if not shop:
        return jsonify({"message": "Shop not found"}), 404

    # Generate unique invoice ID
    india_tz = timezone('Asia/Kolkata')
    current_time_ist = datetime.now(india_tz)
    
    invoice_id = f"INV-{device_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Automatically save the invoice to history
    new_invoice = RepairingInvoice(
        invoice_id=invoice_id,
        repairing_device_id=device_id,
        shop_id=shop.id,
        customer_name=repairing_device.customer_name,
        repairing_cost=repairing_device.repairing_cost,
        advance_payment=repairing_device.advance_payment,
        due_price=repairing_device.due_price,
        bill_status=repairing_device.bill_status,
        payment_method=repairing_device.payment_method,
    )

    try:
        # Save the invoice history
        db.session.add(new_invoice)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save invoice history. Error: {str(e)}"}), 500

    # Convert and format date_added field to IST
    date_added_ist = repairing_device.date_added.astimezone(india_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Full invoice details
    invoice_details = {
        "invoice_id": invoice_id,
        "repairing_device_id": repairing_device.id,
        "customer_name": repairing_device.customer_name,
        "phone_number": repairing_device.phone_number,
        "company": repairing_device.company,
        "model": repairing_device.model,
        "device_condition": repairing_device.device_condition,
        "repairing_status": repairing_device.repairing_status,
        "repairing_cost": repairing_device.repairing_cost,
        "advance_payment": repairing_device.advance_payment,
        "due_price": repairing_device.due_price,
        "bill_status": repairing_device.bill_status,
        "payment_method": repairing_device.payment_method,
        "delivery_status": repairing_device.delivery_status,
        "technician_name": repairing_device.technician_name,
        "estimated_delivery_date": repairing_device.estimated_delivery_date.strftime('%Y-%m-%d') if repairing_device.estimated_delivery_date else None,
        "date_added": date_added_ist,  # Date in IST formatted as string
        "shop_details": {
            "shop_id": shop.id,
            "shop_name": shop.name,
            "shop_address": shop.address,
            "shop_phone": shop.phone,
            "shop_email": shop.email,
        }
    }

    # Return the full invoice details as JSON
    return jsonify({"message": "Invoice generated and saved successfully", "invoice_details": invoice_details}), 200
    
    
@app.route('/repairinginvoice/history', methods=['GET'])
def view_repairing_invoice_history():
    auth_key = request.args.get('auth_key')
    if not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    # Fetch all invoices from the database
    invoices = RepairingInvoice.query.all()

    # Prepare the list of invoices with related details
    invoice_history = [
        {
            "invoice_id": invoice.invoice_id,
            "repairing_device_id": invoice.repairing_device.id,
            "customer_name": invoice.customer_name,
            "repairing_cost": invoice.repairing_cost,
            "advance_payment": invoice.advance_payment,
            "due_price": invoice.due_price,
            "bill_status": invoice.bill_status,
            "payment_method": invoice.payment_method,
            "created_at": invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "shop_details": {
                "shop_id": invoice.shop.id,
                "shop_name": invoice.shop.name,
                "shop_address": invoice.shop.address,
                "shop_phone": invoice.shop.phone,
                "shop_email": invoice.shop.email,
            }
        }
        for invoice in invoices
    ]

    # Return the history as JSON
    return jsonify({"message": "Repairing invoice history retrieved successfully", "invoices": invoice_history}), 200
    
import requests

@app.route('/generate_accessorie_invoice', methods=['GET'])
def generate_accessorie_invoice():
    # Check for authorization key
    auth_key = request.args.get('auth_key')
    if not auth_key or not verify_auth_key(auth_key):
        return jsonify({"message": "Unauthorized access"}), 403

    # Extract parameters from the query string
    user_name = request.args.get("user_name")
    user_phone = request.args.get("user_phone")
    accessory_id = request.args.get("accessory_id")
    shop_id = request.args.get("shop_id")
    quantity = request.args.get("quantity")

    # Validation
    if not all([user_name, user_phone, accessory_id, shop_id, quantity]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        # Convert quantity to integer
        quantity = int(quantity)

        # Fetch accessory details from the database
        accessory = Accessory.query.get(accessory_id)
        if not accessory:
            return jsonify({"error": "Accessory not found"}), 404

        # Fetch shop details from the database
        shop = Shop.query.get(shop_id)
        if not shop:
            return jsonify({"error": "Shop not found"}), 404

        # Check stock availability
        if accessory.added_stock < quantity:
            return jsonify({"error": "Insufficient stock available"}), 400

        # Generate unique invoice ID
        invoice_id = str(uuid.uuid4())

        # Calculate total price
        total_price = accessory.unit_price * quantity

        # Update stock and sales details
        accessory.added_stock -= quantity
        accessory.times_sold += quantity
        db.session.commit()

        # Save invoice to the database
        new_invoice = AccessorieInvoice(
            invoice_id=invoice_id,
            user_name=user_name,
            user_phone=user_phone,
            accessory_name=accessory.accessory_name,
            company=accessory.company,
            category=accessory.category,
            unit_price=accessory.unit_price,
            quantity=quantity,
            total_price=total_price,
            shop_name=shop.name,
            shop_address=shop.address,
            shop_phone=shop.phone,
            shop_email=shop.email,
        )
        db.session.add(new_invoice)
        db.session.commit()

        # Prepare invoice data for response
        invoice_data = {
            "invoice_id": invoice_id,
            "user_name": user_name,
            "user_phone": user_phone,
            "accessory_details": {
                "accessory_name": accessory.accessory_name,
                "company": accessory.company,
                "category": accessory.category,
                "unit_price": accessory.unit_price,
                "quantity": quantity,
                "total_price": total_price,
            },
            "shop_details": {
                "shop_name": shop.name,
                "shop_address": shop.address,
                "shop_phone": shop.phone,
                "shop_email": shop.email,
            },
            "date": datetime.utcnow().isoformat(),
        }

        # Make an API call to update the accessory
        update_url = "http://localhost:5000/accessory"
        update_params = {
            "action": "update",
            "auth_key": auth_key,
            "id": accessory_id,
            "last_purchase_quantity": quantity
        }

        try:
            response = requests.get(update_url, params=update_params)
            if response.status_code != 200:
                return jsonify({"error": "Failed to update accessory"}), response.status_code
        except Exception as e:
            return jsonify({"error": f"Failed to update accessory: {str(e)}"}), 500

        return jsonify({"status": "success", "invoice": invoice_data}), 200

    except ValueError:
        return jsonify({"error": "Invalid quantity format"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
    