from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_analytics_endpoint():
  response = client.get("/api/analytics")
  assert response.status_code == 200
  data = response.json()
  assert "categories" in data
  assert "trend_labels" in data