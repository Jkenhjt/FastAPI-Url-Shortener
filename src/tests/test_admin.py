import requests


link: str


def test_create_url():
    response = requests.post("http://0.0.0.0:8000/admin/add", json={"link": "https://youtube.com"})

    assert response.status_code == 403

    session = requests.Session()
    response = session.post(
        "http://0.0.0.0:8000/user/register",
        json={"username": "admin", "password": "admin"},
    )
    response = session.post("http://0.0.0.0:8000/admin/add", json={"link": "https://youtube.com"})

    assert response.status_code == 200

    global link
    link = response.json()["shortened_url"]


def test_get_data_one_url():
    response = requests.post("http://0.0.0.0:8000/admin/get_link", json={"link": link})

    assert response.status_code == 403

    session = requests.Session()
    response = session.post(
        "http://0.0.0.0:8000/user/login",
        json={"username": "admin", "password": "admin"},
    )
    response = session.post("http://0.0.0.0:8000/admin/get_link", json={"link": link})

    assert response.status_code == 200

    j_data = response.json()

    assert j_data["original_url"] == "https://youtube.com"
    assert j_data["shortened_url"] != ""
    assert j_data["clicks"] == 0


def test_get_data_all_urls():
    response = requests.get("http://0.0.0.0:8000/admin/get_all")

    assert response.status_code == 403

    session = requests.Session()
    response = session.post(
        "http://0.0.0.0:8000/user/login",
        json={"username": "admin", "password": "admin"},
    )
    response = session.get("http://0.0.0.0:8000/admin/get_all")

    assert response.status_code == 200

    j_data = response.json()

    assert j_data[0]["original_url"] == "https://youtube.com"
    assert j_data[0]["shortened_url"] != ""
    assert j_data[0]["clicks"] == 0


def test_delete_url():
    response = requests.delete("http://0.0.0.0:8000/admin/delete", json={"link": link})

    assert response.status_code == 403

    session = requests.Session()
    response = session.post(
        "http://0.0.0.0:8000/user/login",
        json={"username": "admin", "password": "admin"},
    )
    response = session.delete("http://0.0.0.0:8000/admin/delete", json={"link": link})

    assert response.status_code == 200

    response = session.delete("http://0.0.0.0:8000/admin/delete", json={"link": link})

    assert response.status_code == 400
