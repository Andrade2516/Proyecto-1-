def test_summary_empty(client):
    response = client.get("/stats/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_games": 0,
        "total_hours": 0.0,
        "average_rating": None,
    }


def test_summary_with_data(client, create_game):
    create_game(title="Hades", hours_played=50, rating=9)
    create_game(title="Celeste", hours_played=20, rating=10)
    create_game(title="Doom", hours_played=0)

    response = client.get("/stats/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_games": 3,
        "total_hours": 70.0,
        "average_rating": 9.5,
    }


def test_summary_without_ratings(client, create_game):
    create_game(title="Hades", hours_played=5)

    response = client.get("/stats/summary")

    assert response.status_code == 200
    assert response.json()["average_rating"] is None


def test_by_genre_empty(client):
    response = client.get("/stats/by-genre")

    assert response.status_code == 200
    assert response.json() == []


def test_by_genre(client, create_game):
    create_game(title="Hades", genre="Roguelike", hours_played=50)
    create_game(title="Hades II", genre="Roguelike", hours_played=40)
    create_game(title="Celeste", genre="Platformer", hours_played=20)
    create_game(title="Doom", genre="FPS", hours_played=15)
    create_game(title="Stardew Valley", genre="Simulation", hours_played=100)
    create_game(title="Hollow Knight", hours_played=30)

    response = client.get("/stats/by-genre")

    assert response.status_code == 200
    assert response.json() == [
        {"genre": "Roguelike", "total_games": 2, "total_hours": 90.0},
        {"genre": "FPS", "total_games": 1, "total_hours": 15.0},
        {"genre": "Platformer", "total_games": 1, "total_hours": 20.0},
        {"genre": "Simulation", "total_games": 1, "total_hours": 100.0},
        {"genre": "Unknown", "total_games": 1, "total_hours": 30.0},
    ]


def test_linux_compat_empty(client):
    response = client.get("/stats/linux-compat")

    assert response.status_code == 200
    assert response.json() == [
        {"linux_compat": "native", "total_games": 0, "percentage": 0.0},
        {"linux_compat": "proton", "total_games": 0, "percentage": 0.0},
        {"linux_compat": "unknown", "total_games": 0, "percentage": 0.0},
        {"linux_compat": "windows_only", "total_games": 0, "percentage": 0.0},
    ]


def test_linux_compat(client, create_game):
    create_game(title="Hades", linux_compat="proton")
    create_game(title="Celeste", linux_compat="native")
    create_game(title="Stardew Valley", linux_compat="native")
    create_game(title="Doom", linux_compat="windows_only")
    create_game(title="Hollow Knight", linux_compat="unknown")

    response = client.get("/stats/linux-compat")

    assert response.status_code == 200
    assert response.json() == [
        {"linux_compat": "native", "total_games": 2, "percentage": 40.0},
        {"linux_compat": "proton", "total_games": 1, "percentage": 20.0},
        {"linux_compat": "unknown", "total_games": 1, "percentage": 20.0},
        {"linux_compat": "windows_only", "total_games": 1, "percentage": 20.0},
    ]
