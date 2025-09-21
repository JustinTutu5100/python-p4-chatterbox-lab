from datetime import datetime

from app import app
from models import db, Message

class TestApp:
    """Flask application in app.py"""

    def setup_method(self):
        """Runs before each test to ensure the DB has at least one message"""
        with app.app_context():
            # Clean database
            Message.query.delete()
            db.session.commit()
            # Add a default message
            self.default_message = Message(body="Hello 👋", username="Liza")
            db.session.add(self.default_message)
            db.session.commit()

    def teardown_method(self):
        """Runs after each test to clean up DB"""
        with app.app_context():
            Message.query.delete()
            db.session.commit()

    def test_has_correct_columns(self):
        with app.app_context():
            m = Message.query.first()
            assert m.body == "Hello 👋"
            assert m.username == "Liza"
            assert isinstance(m.created_at, datetime)
            assert isinstance(m.updated_at, datetime)

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        with app.app_context():
            response = app.test_client().get('/messages')
            records = Message.query.all()

            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

    def test_creates_new_message_in_the_database(self):
        with app.app_context():
            app.test_client().post(
                '/messages',
                json={"body": "Hi there!", "username": "John"}
            )
            h = Message.query.filter_by(body="Hi there!").first()
            assert h

    def test_returns_data_for_newly_created_message_as_json(self):
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={"body": "Hey!", "username": "Jane"}
            )
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Hey!"
            assert response.json["username"] == "Jane"

    def test_updates_body_of_message_in_database(self):
        with app.app_context():
            m = Message.query.first()
            id = m.id
            old_body = m.body

            app.test_client().patch(
                f'/messages/{id}',
                json={"body": "Goodbye 👋"}
            )

            g = Message.query.filter_by(body="Goodbye 👋").first()
            assert g is not None

            # Restore old value
            g.body = old_body
            db.session.commit()

    def test_returns_data_for_updated_message_as_json(self):
        with app.app_context():
            m = Message.query.first()
            id = m.id
            old_body = m.body

            response = app.test_client().patch(
                f'/messages/{id}',
                json={"body": "Farewell 👋"}
            )

            assert response.content_type == 'application/json'
            assert response.json["body"] == "Farewell 👋"

            # Restore old value
            g = Message.query.filter_by(body="Farewell 👋").first()
            g.body = old_body
            db.session.commit()

    def test_deletes_message_from_database(self):
        with app.app_context():
            m = Message.query.first()
            id = m.id

            app.test_client().delete(f'/messages/{id}')

            h = Message.query.filter_by(id=id).first()
            assert h is None
