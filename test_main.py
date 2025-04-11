import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

# LLMの返答モック（OpenAIへの実際の呼び出しを避ける）
mock_llm_response = {
    "記録日時": "2025-04-11T20:00:00",
    "分類": "生活",
    "タイトル": "買い物と読書",
    "内容": "今日は近所のスーパーで買い物をした後、読書をしてゆっくり過ごした。"
}

@pytest.fixture
def mock_chatcompletion(mocker):
    mock = mocker.patch("main.client.chat.completions.create")
    mock.return_value.choices = [
        type("Choice", (), {"message": type("Message", (), {"content": str(mock_llm_response)})})()
    ]
    return mock

@pytest.fixture
def mock_append_to_sheet(mocker):
    return mocker.patch("main.append_to_sheet")

def test_chat_endpoint_success(mock_chatcompletion, mock_append_to_sheet):
    response = client.post("/chat", json={"message": "今日は読書してゆっくり過ごした"})
    assert response.status_code == 200
    data = response.json()
    assert "記録日時" in data
    assert "分類" in data
    assert "タイトル" in data
    assert "内容" in data
    mock_append_to_sheet.assert_called_once()

def test_chat_endpoint_invalid_json():
    # message フィールドがない
    response = client.post("/chat", json={"msg": "データが不正"})
    assert response.status_code == 422
