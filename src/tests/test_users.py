import requests


def test_register():
    response = requests.post(
        "http://0.0.0.0:8000/user/register",
        json={"username": "testu", "password": "testp"},
    )

    assert response.status_code == 200
    assert response.cookies["token"] != ""
    assert response.cookies["token"] != None

    response = requests.post(
        "http://0.0.0.0:8000/user/register",
        json={"username": "testu", "password": "testp"},
    )

    assert response.status_code == 400


def test_login():
    response = requests.post(
        "http://0.0.0.0:8000/user/login",
        json={"username": "testu", "password": "testp"},
    )

    assert response.status_code == 200
    assert response.cookies["token"] != ""
    assert response.cookies["token"] != None

    response = requests.post(
        "http://0.0.0.0:8000/user/login",
        json={"username": "testu", "password": "testp"},
    )

    assert response.status_code == 200
