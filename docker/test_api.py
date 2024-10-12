import requests

BASE_URL = "http://localhost:8080"

# 測試 /test 端點
def test_test():
    response = requests.get(f"{BASE_URL}/test")
    assert response.status_code == 200
    assert response.text == "今日は本音とたてまえについてお話をします。"

# 測試 /parse 端點
def test_parse():
    data = { "jpString": "今日は" }
    response = requests.post(f"{BASE_URL}/parse", data=data)
    assert response.status_code == 200

    # 檢查回應的資料型態（應該是 list）
    result = response.json()
    assert isinstance(result, list), "回應資料型態應為列表"
