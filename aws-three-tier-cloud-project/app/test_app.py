import unittest
from unittest.mock import patch
from app import app

class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    @patch("app.record_visit", return_value=7)
    def test_home_page_shows_database_counter(self, mocked_record_visit):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"7", response.data)
        mocked_record_visit.assert_called_once()

if __name__ == "__main__":
    unittest.main()
