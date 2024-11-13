import os
import MySQLdb
import requests
import secrets
import json
import re
from PIL import Image
from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
import datetime

conn = MySQLdb.connect(host="localhost", user="******", passwd="*******", db="shopping_db")

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '414di3576tgjkhgvgs45667890/'
bcrypt = Bcrypt(app)
CORS(app)
 
app.config["JWT_SECRET_KEY"] = "564592102u011yt1512ryiahg6111"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=30)

jwt = JWTManager(app)

def validate_registration(username, password):
    """ Validate login """
    if not username or not password:
        return jsonify({"error": "Please fill out all your login credentials"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be atleast 8 characters long"}), 400
    if len(username) < 2:
        return jsonify({'error': 'Name too short'}), 400
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    
    if re.match(pattern, password):
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        cur = conn.cursor()
        cur.execute("""SELECT username FROM users;""")
        users = cur.fetchall()
        if (username,) in users:
            return jsonify({'error': f"{username} is already in use. Choose a different name"}), 400
        cur.execute("""INSERT INTO users(username, password)
                    VALUES(%s, %s );""", (username, hashed))
        conn.commit()
        return jsonify({"message": "User created successfully"}), 200
    else:
        return jsonify({"error": "Password must be with atleast one Capital letter, one small letter,\
                       one or more special characters [@$!%*?&], and of more than length 8."}), 400

def validate_item(item):
    """ Validate login """
    
    for key in item:
        if key != 'image':
            if item[key] == '':
                return jsonify({'error': f'please fillout the item"s {key}'})

    if item['image'] == '':
        item['image'] = 'default.png'

    cur = conn.cursor()
    cur.execute("""INSERT INTO items(name, price, bp, barcode, image) VALUES (%s, %s, %s, %s, %s);""",
                (item['name'], item['price'], item['bp'],
                item['barcode'], item['image'])
               )
    conn.commit()
    return jsonify({'msg': 'Item added'})

def login(username, password):
    """Validate login"""
    if username and password:
        cur = conn.cursor()
        cur.execute("""SELECT username, password FROM users;""")
        users = cur.fetchall()
        for from_db_username, from_db_password in users:
            if username ==  from_db_username and bcrypt.check_password_hash(from_db_password, password):
                access_token = create_access_token(identity=username)
                refresh_token = create_refresh_token(identity=username)
                return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        return jsonify({'error': f"Failed login! Invalid credentials"}), 400
    else:
        return jsonify({"error": "Provide login credetials"}), 400

def all_products():
    cur = conn.cursor()
    cur.execute("""SELECT * FROM items;""")
    items = cur.fetchall()
    return jsonify(items)

@app.route("/create_ac", methods=['POST'])
def create_account():
    """Create account"""
    return validate_registration(request.form.get('username', ''),
                          request.form.get('password', ''))

@app.route("/create_item", methods=['POST'])
@jwt_required()
def make_product():
    """Add product to database"""
    item = {
        'name': request.form.get('name', ''),
        'price': request.form.get('price', ''),
        'bp': request.form.get('bp', ''),
        'barcode': request.form.get('barcode', ''),
        'image': ''
    }

    if request.files.get('file'):
        file = request.files.get('file', '')
        item['image'] = file.filename

        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
    return validate_item(item)

@app.route("/products")
@jwt_required()
def retrieve_all_products():
    """Get every item in database"""
    return all_products()

def allowed_file(filename):
    """Check if Filename has the right extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """Endpoint for uploading a file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file in the request"}), 400

    file = request.files['file']

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return jsonify({'message': "Image Upload successful", "file_path": file_path}), 200

    return jsonify({"error": "invalid file type"}), 400


@app.route("/login", methods=['POST'])
def user_login():
    """login user"""
    if 'username' in session:
        return 'haha'
    print(request.form.get('username', ''), request.form.get('password', ''))
    return login(request.form.get('username', ''),
                 request.form.get('password', ''))

@app.route("/refresh", methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)
