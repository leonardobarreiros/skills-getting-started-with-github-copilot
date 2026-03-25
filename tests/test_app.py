import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Teste: Listagem de atividades (GET /activities)
def test_get_activities():
    # Arrange
    # (Nada a preparar, pois o banco é in-memory e já inicializado)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

# Teste: Inscrição em atividade (POST /activities/{activity_name}/signup)
def test_signup_for_activity():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email} for {activity}" in data["message"]
    # Verifica se o participante foi adicionado
    get_resp = client.get("/activities")
    assert email in get_resp.json()[activity]["participants"]

# Teste: Não permite inscrição duplicada
def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = "duplicatetest@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

# Teste: Remoção de participante (DELETE /activities/{activity_name}/participants/{email})
def test_remove_participant():
    # Arrange
    activity = "Chess Club"
    email = "removeuser@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}?email={email}")

    # Assert
    assert response.status_code == 200
    assert f"Removed {email} from {activity}" in response.json()["message"]
    # Verifica se o participante foi removido
    get_resp = client.get("/activities")
    assert email not in get_resp.json()[activity]["participants"]

# Teste: Erro ao remover participante inexistente
def test_remove_nonexistent_participant():
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

# Teste: Erro ao inscrever em atividade inexistente
def test_signup_nonexistent_activity():
    # Arrange
    activity = "Nonexistent Club"
    email = "user@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
