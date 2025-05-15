import unittest
from app import create_app, db
from config import TestConfig

class IndexPageUnitTests(unittest.TestCase):
    def setUp(self):
        # Set up test app and client.
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        #  Clean up after tests.
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page_loads(self):
        # check index page loads with site name.
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"FitTracker", response.data)

    def test_team_names_present(self):
        # check team names are on the page.
        response = self.client.get("/")
        self.assertIn(b"Xu Li", response.data)
        self.assertIn(b"Fei Han", response.data)
        self.assertIn(b"Arthur Zhang", response.data)
        self.assertIn(b"Harshit Gadhiya", response.data)

    def test_index_static_assets(self):
        # check page includes JS and CSS.
        response = self.client.get("/")
        self.assertIn(b"/static/js/index.js", response.data)
        self.assertIn(b"/static/css/index.css", response.data)
