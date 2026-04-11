from fastapi.testclient import TestClient
from app.main import app # Ajuste aqui se o seu arquivo principal tiver outro nome

client = TestClient(app)

def test_read_main():
    """Verifica se a API está online"""
    response = client.get("/")
    assert response.status_code == 200

def test_prediction_schema():
    """Verifica se o endpoint de predição existe"""
    # Enviamos um payload vazio apenas para ver se a rota responde (mesmo que com erro 422)
    response = client.post("/predict", json={})
    assert response.status_code != 404 # Garante que a rota existe