import pytest


def test_create_game(client):
    response = client.post(
        "/games",
        json={"title": "Hades", "platform": "Steam"},
    )

    assert response.status_code == 201
    game = response.json()
    assert game["id"] == 1
    assert game["title"] == "Hades"
    assert game["status"] == "backlog"
    assert game["hours_played"] == 0.0
    assert game["rating"] is None
    assert game["linux_compat"] == "unknown"
    assert game["created_at"] is not None


def test_create_game_trims_whitespace(client):
    response = client.post(
        "/games",
        json={"title": "  Hades  ", "platform": "  Steam  "},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Hades"
    assert response.json()["platform"] == "Steam"


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "platform": "Steam"},
        {"title": "   ", "platform": "Steam"},
        {"title": "Hades"},
        {"title": "Hades", "platform": "Steam", "rating": 11},
        {"title": "Hades", "platform": "Steam", "rating": 0},
        {"title": "Hades", "platform": "Steam", "hours_played": -1},
        {"title": "Hades", "platform": "Steam", "status": "invalid"},
        {"title": "Hades", "platform": "Steam", "linux_compat": "invalid"},
    ],
)
def test_create_game_validation_errors(client, payload):
    response = client.post("/games", json=payload)
    assert response.status_code == 422


def test_list_games_with_pagination(client, create_game):
    create_game(title="Hades")
    create_game(title="Celeste")
    create_game(title="Doom")

    response = client.get("/games")
    assert response.status_code == 200
    assert [game["title"] for game in response.json()] == [
        "Hades",
        "Celeste",
        "Doom",
    ]

    response = client.get("/games", params={"limit": 2})
    assert [game["title"] for game in response.json()] == ["Hades", "Celeste"]

    response = client.get("/games", params={"skip": 1, "limit": 1})
    assert [game["title"] for game in response.json()] == ["Celeste"]

    assert client.get("/games", params={"skip": -1}).status_code == 422
    assert client.get("/games", params={"limit": 0}).status_code == 422
    assert client.get("/games", params={"limit": 101}).status_code == 422


def test_list_games_filters(client, create_game):
    create_game(
        title="Hades",
        genre="Roguelike",
        status="completed",
        linux_compat="proton",
    )
    create_game(
        title="Celeste",
        genre="Platformer",
        status="playing",
        linux_compat="native",
    )
    create_game(
        title="Doom",
        genre="FPS",
        status="backlog",
        linux_compat="windows_only",
    )
    create_game(
        title="Stardew Valley",
        genre="Simulation",
        status="playing",
        linux_compat="native",
    )

    response = client.get("/games", params={"status": "playing"})
    assert [game["title"] for game in response.json()] == [
        "Celeste",
        "Stardew Valley",
    ]

    response = client.get("/games", params={"genre": "FPS"})
    assert [game["title"] for game in response.json()] == ["Doom"]

    response = client.get("/games", params={"linux_compat": "native"})
    assert [game["title"] for game in response.json()] == [
        "Celeste",
        "Stardew Valley",
    ]

    response = client.get(
        "/games",
        params={"status": "playing", "linux_compat": "native"},
    )
    assert [game["title"] for game in response.json()] == [
        "Celeste",
        "Stardew Valley",
    ]

    response = client.get(
        "/games",
        params={"status": "playing", "genre": "FPS"},
    )
    assert response.json() == []

    assert client.get("/games", params={"status": "invalid"}).status_code == 422
    assert (
        client.get("/games", params={"linux_compat": "invalid"}).status_code
        == 422
    )
    assert client.get("/games", params={"genre": ""}).status_code == 422


def test_get_game(client, create_game):
    created = create_game(title="Hades")

    response = client.get(f"/games/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Hades"

    response = client.get("/games/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"


def test_update_game(client, create_game):
    created = create_game(title="Hades", hours_played=1)
    game_id = created["id"]

    response = client.put(
        f"/games/{game_id}",
        json={
            "title": "Hades II",
            "status": "playing",
            "hours_played": 12.5,
            "rating": 9,
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Hades II"
    assert updated["status"] == "playing"
    assert updated["hours_played"] == 12.5
    assert updated["rating"] == 9

    response = client.put(f"/games/{game_id}", json={"rating": None})
    assert response.status_code == 200
    assert response.json()["rating"] is None

    response = client.put(f"/games/{game_id}", json={"title": None})
    assert response.status_code == 200
    assert response.json()["title"] == "Hades II"

    response = client.put("/games/999", json={"hours_played": 1})
    assert response.status_code == 404


def test_delete_game(client, create_game):
    created = create_game(title="Hades")
    game_id = created["id"]

    response = client.delete(f"/games/{game_id}")
    assert response.status_code == 204
    assert response.text == ""

    assert client.get(f"/games/{game_id}").status_code == 404
    assert client.delete(f"/games/{game_id}").status_code == 404
