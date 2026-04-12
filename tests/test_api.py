import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.api.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('src.api.main.cv_worker')
    def test_read_root(self, mock_worker):
        """Tests the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Posture-Sense API is running"})

    @patch('src.api.main.cv_worker')
    def test_health_check(self, mock_worker):
        """Tests the health check endpoint."""
        mock_worker.is_running = True
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    @patch('src.api.main.cv_worker')
    def test_toggle_mirror(self, mock_worker):
        """Tests the toggle-mirror endpoint."""
        mock_worker.toggle_mirror.return_value = True
        response = self.client.post("/api/toggle-mirror")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"mirror_mode": True})

    @patch('src.api.main.cv_worker')
    def test_toggle_auto_align(self, mock_worker):
        """Tests the toggle-auto-align endpoint."""
        mock_worker.toggle_auto_align.return_value = True
        response = self.client.post("/api/toggle-auto-align")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"auto_align": True})

    @patch('src.api.main.cv_worker')
    def test_get_history_empty(self, mock_worker):
        """Tests get_history with no data."""
        mock_worker.stats_manager.db_manager.get_recent_history.return_value = []
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

if __name__ == "__main__":
    unittest.main()
