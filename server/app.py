from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message  # import from your models.py

app = Flask(__name__)

# configure db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)


# GET /messages – all messages ordered by created_at asc
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() if hasattr(m, 'to_dict') else m.to_dict() for m in messages]
                   if not hasattr(Message, 'to_dict') else [m.to_dict() for m in messages])
    # If you’re using SerializerMixin, you can just do:
    # return jsonify([m.to_dict() for m in messages])


# POST /messages – create new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or 'body' not in data or 'username' not in data:
        return jsonify({"error": "body and username are required"}), 400

    new_message = Message(
        body=data['body'],
        username=data['username']
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict() if hasattr(new_message, 'to_dict') else new_message.to_dict()), 201


# PATCH /messages/<id> – update body
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get_or_404(id)
    data = request.get_json()

    if 'body' in data:
        message.body = data['body']

    db.session.commit()

    return jsonify(message.to_dict() if hasattr(message, 'to_dict') else message.to_dict())


# DELETE /messages/<id>
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)

    db.session.delete(message)
    db.session.commit()

    return '', 204


if __name__ == '__main__':
    app.run(port=5555)
