from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from pyexpat.errors import messages
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = "surya-ukg"

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

# Database CLI commands
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('DB Created!')

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('DB Dropped!')

@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='Sun',
                     mass=3.258e23,
                     radius=1516,
                     distance=35.98e6
                     )
    venus = Planet(planet_name='Venus',
                   planet_type='Class E',
                   home_star='Sun',
                   mass=4.867e24,
                   radius=3760,
                   distance=67.24e6
                   )
    earth = Planet(planet_name='Earth',
                   planet_type='Class F',
                   home_star='Sun',
                   mass=5.972e24,
                   radius=3959,
                   distance=92.96e6
                   )

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='Surya',
                     last_name='Mishra',
                     email='abc@test.com',
                     password='1234'
                     )

    db.session.add(test_user)
    db.session.commit()
    print('DB Seeded!')

# Routes
@app.route('/hello')
def hello_world():
    return jsonify(message="Hello World !!!!!!!!"), 200

# User CRUD Operations
@app.route('/users', methods=['GET'])
def get_users():
    users_list = User.query.all()
    result = users_schema.dump(users_list)
    return jsonify(result)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify(user_schema.dump(user))
    else:
        return jsonify(message="User not found"), 404

@app.route('/register', methods=['POST'])
def register():
    data = request.json  # Use request.json to handle JSON data
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(message='Invalid request: email and password are required'), 400

    email = data['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='User already exists!'), 409
    else:
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        password = data['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created'), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Use request.json to handle JSON data
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(message='Invalid request: email and password are required'), 400

    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login succeeded', access_token=access_token), 200
    else:
        return jsonify(message='Bad credentials'), 401

@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        data = request.json
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password)
        db.session.commit()
        return jsonify(message='User updated'), 200
    else:
        return jsonify(message="User not found"), 404

@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify(message='User deleted'), 200
    else:
        return jsonify(message="User not found"), 404

# Planet CRUD Operations
@app.route('/planets', methods=['GET'])
def get_planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)

@app.route('/add_planet', methods=['POST'])
# @jwt_required()
def add_planet():
    data = request.json  # Use request.json to handle JSON data
    if not data or 'planet_name' not in data:
        return jsonify(message="Invalid request: planet_name is required"), 400

    planet_name = data['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify(message="Planet already exists"), 409
    else:
        planet_type = data.get('planet_type', '')
        home_star = data.get('home_star', '')
        mass = float(data.get('mass', 0))
        radius = float(data.get('radius', 0))
        distance = float(data.get('distance', 0))

        new_planet = Planet(
            planet_name=planet_name,
            planet_type=planet_type,
            home_star=home_star,
            mass=mass,
            radius=radius,
            distance=distance
        )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message='Planet added'), 201

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        return jsonify(planet_schema.dump(planet))
    else:
        return jsonify(message="Planet not found"), 404

# @app.route('/add_planet', methods=['POST'])
# @jwt_required()
# def add_planet():
#     data = request.json  # Use request.json to handle JSON data
#     if not data or 'planet_name' not in data:
#         return jsonify(message="Invalid request: planet_name is required"), 400

#     planet_name = data['planet_name']
#     test = Planet.query.filter_by(planet_name=planet_name).first()
#     if test:
#         return jsonify(message="Planet already exists"), 409
#     else:
#         planet_type = data.get('planet_type', '')
#         home_star = data.get('home_star', '')
#         mass = float(data.get('mass', 0))
#         radius = float(data.get('radius', 0))
#         distance = float(data.get('distance', 0))

#         new_planet = Planet(
#             planet_name=planet_name,
#             planet_type=planet_type,
#             home_star=home_star,
#             mass=mass,
#             radius=radius,
#             distance=distance
#         )
#         db.session.add(new_planet)
#         db.session.commit()
#         return jsonify(message='Planet added'), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
@jwt_required()
def update_planet(planet_id):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        data = request.json
        planet.planet_name = data.get('planet_name', planet.planet_name)
        planet.planet_type = data.get('planet_type', planet.planet_type)
        planet.home_star = data.get('home_star', planet.home_star)
        planet.mass = float(data.get('mass', planet.mass))
        planet.radius = float(data.get('radius', planet.radius))
        planet.distance = float(data.get('distance', planet.distance))
        db.session.commit()
        return jsonify(message='Planet updated'), 200
    else:
        return jsonify(message="Planet not found"), 404

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_planet(planet_id):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message='Planet deleted'), 200
    else:
        return jsonify(message="Planet not found"), 404

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

# Marshmallow Schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
