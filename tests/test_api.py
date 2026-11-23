from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["model_r2"] > 0.85


def test_predict_bathinda_wheat() -> None:
    res = client.post(
        "/predict",
        json={
            "district": "Bathinda",
            "crop": "Wheat",
            "season": "Rabi",
            "area_ekad": 4.0,
            "variety": "PBW 826",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["district"] == "Bathinda"
    assert data["prediction"]["expected_yield_q_ekad"] > 10.0
    assert data["pau_advisory"]["selected_variety"] == "PBW 826"
    # PBW 826 recommends 2.0 Urea bags/ekad -> 8.0 bags for 4 ekad
    assert data["pau_advisory"]["total_fertilizer_bags_for_area"]["Urea"] == 8.0
