# test_mailbox.py
# This file contains unit tests for the Mailbox feature, including message sharing
# and management functionality (e.g., /share, /messages, marking messages as read).

import unittest
from datetime import datetime, timezone
from app import create_app, db
from config import TestConfig
from app.models import User, Message
from werkzeug.security import generate_password_hash
from markupsafe import Markup

class MailboxUnitTests(unittest.TestCase):
    """Unit tests for Mailbox feature, covering message sharing, viewing, and marking."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.user1 = User(email="user1@example.com", password=generate_password_hash("pass1"))
        self.user2 = User(email="user2@example.com", password=generate_password_hash("pass2"))
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        """Tear down the test environment after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_user(self, user_id):
        """Helper method to log in a user by setting user_id in session."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id

    def test_share_page_requires_login(self):
        """Test that unauthenticated users are redirected to login from /share."""
        response = self.client.get("/share", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_messages_page_requires_login(self):
        """Test that unauthenticated users are redirected to login from /messages."""
        response = self.client.get("/messages", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_share_page_loads_for_logged_in_user(self):
        """Test that /share page loads successfully for a logged-in user."""
        self.login_user(self.user1.id)
        response = self.client.get("/share")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Share Your Progress", response.data)

    def test_messages_page_loads_for_logged_in_user(self):
        """Test that /messages page loads successfully for a logged-in user."""
        self.login_user(self.user1.id)
        response = self.client.get("/messages")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Messages", response.data)

    def test_send_message_via_share(self):
        """Test sending a message via /share, verifying message content and status."""
        self.login_user(self.user1.id)
        response = self.client.post("/share", data={
            "receiver_email": "user2@example.com"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Health information shared successfully!", response.data)

        message = Message.query.filter_by(sender_id=self.user1.id, receiver_id=self.user2.id).first()
        self.assertIsNotNone(message)
        self.assertTrue(message.content.startswith("Sharing the recording! View my health information: "))
        self.assertFalse(message.is_read)

    def test_share_prevents_sending_to_self(self):
        """Test that /share prevents a user from sending a message to themselves."""
        self.login_user(self.user1.id)
        response = self.client.post("/share", data={
            "receiver_email": "user1@example.com"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You cannot share with yourself.", response.data)

    def test_share_with_invalid_recipient(self):
        """Test that /share fails when the recipient email is invalid."""
        self.login_user(self.user1.id)
        response = self.client.post("/share", data={
            "receiver_email": "nonexistent@example.com"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User with this email not found.", response.data)

    def test_messages_page_displays_messages(self):
        """Test that /messages page displays sent and received messages correctly."""
        sent_message = Message(sender_id=self.user1.id, receiver_id=self.user2.id,
                               content="Test message: http://localhost:5000/health_info/testtoken",
                               is_read=False, timestamp=datetime(2025, 5, 15, tzinfo=timezone.utc))
        received_message = Message(sender_id=self.user2.id, receiver_id=self.user1.id,
                                   content="Reply message: http://localhost:5000/health_info/testtoken2",
                                   is_read=True, timestamp=datetime(2025, 5, 15, tzinfo=timezone.utc))
        db.session.add_all([sent_message, received_message])
        db.session.commit()

        self.login_user(self.user1.id)
        response = self.client.get("/messages")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test message", response.data)  # Sent message
        self.assertIn(b"Reply message", response.data)  # Received message
        self.assertIn(b"Unread", response.data)  # Sent message is unread
        self.assertIn(b"Read", response.data)  # Received message is read

    def test_mark_message_as_read(self):
        """Test marking a single message as read via /messages."""
        message = Message(sender_id=self.user2.id, receiver_id=self.user1.id,
                          content="Test message: http://localhost:5000/health_info/testtoken",
                          is_read=False, timestamp=datetime(2025, 5, 15, tzinfo=timezone.utc))
        db.session.add(message)
        db.session.commit()

        self.login_user(self.user1.id)
        response = self.client.post("/messages", data={
            "action": "mark_read",
            "message_id": message.id
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Message marked as read.", response.data)

        updated_message = Message.query.get(message.id)
        self.assertTrue(updated_message.is_read)

    def test_mark_all_messages_as_read(self):
        """Test marking all messages as read via /messages."""
        db.session.add_all([
            Message(sender_id=self.user2.id, receiver_id=self.user1.id,
                    content="Message 1: http://localhost:5000/health_info/testtoken",
                    is_read=False, timestamp=datetime(2025, 5, 15, tzinfo=timezone.utc)),
            Message(sender_id=self.user2.id, receiver_id=self.user1.id,
                    content="Message 2: http://localhost:5000/health_info/testtoken2",
                    is_read=False, timestamp=datetime(2025, 5, 15, tzinfo=timezone.utc))
        ])
        db.session.commit()

        self.login_user(self.user1.id)
        response = self.client.post("/messages", data={
            "action": "mark_all_read"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"All messages have been marked as read.", response.data)

        messages = Message.query.filter_by(receiver_id=self.user1.id).all()
        for msg in messages:
            self.assertTrue(msg.is_read)

if __name__ == '__main__':
    unittest.main()