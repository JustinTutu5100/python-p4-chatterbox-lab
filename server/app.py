from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Ensure tables exist
with app.app_context():
    db.create_all()

# Root route to avoid 404
@app.route('/')
def home():
    return "Flask API is running! Use /messages to see data."

# GET /messages – all messages ordered by created_at asc
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages])

# POST /messages – create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or 'body' not in data or 'username' not in data:
        return jsonify({"error": "body and username are required"}), 400

    new_message = Message(body=data['body'], username=data['username'])
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

# PATCH /messages/<id> – update message body
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    if not message:
        abort(404)

    data = request.get_json()
    if 'body' in data:
        message.body = data['body']
    db.session.commit()

    return jsonify(message.to_dict())

# DELETE /messages/<id> – delete a message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    if not message:
        abort(404)

    db.session.delete(message)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(port=5555)
