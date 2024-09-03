from potato_pyserver.main import app
from potato_pyserver.database import engine, get_db, SessionLocal
from potato_pyserver.models import User, reset_tables, House, Position
from potato_pyserver.dependencies import get_current_user

from pytest import fixture

from fastapi.testclient import TestClient
from fastapi import Header, HTTPException



@fixture
def client():
    app.dependency_overrides = {}
    return TestClient(app)


@fixture
def user(client):
    user_details = {"username": "toto", "password": "password", "first_name": "asdf",
                    "last_name": "asdf", "email": "asdfasdf@example.com"}
    return client.post("/users", json=user_details).json()


@fixture
def client_authenticated(user):
    def skip_auth():
        return User(**user)

    app.dependency_overrides[get_current_user] = skip_auth
    return TestClient(app)


@fixture(autouse=True)
def db():
    reset_tables(engine)
    db = SessionLocal()
    yield db
    db.close()
    reset_tables(engine)


@fixture
def household(client_authenticated):
    return client_authenticated.post("/households", json={"name": "family test"}).json()


@fixture
def house(client_authenticated, household):
    payload = {"household_id": household["id"], "hamlet_id": 1, "name": "My house"}
    return client_authenticated.post("/worldItems/1/houses", json=payload).json()


def test_create_house(client_authenticated, household, db):
    payload = {"household_id": household["id"], "hamlet_id": 1, "name": "My house"}
    res = client_authenticated.post("/worldItems/1/houses", json=payload)
    assert res.status_code == 200, str(vars(res))

    house = db.query(House).first()
    assert house.name == "My house"
    assert house.household_id == household["id"]
    assert house.household is not None

    assert house.item is not None
    assert house.item.position == Position(0, 0, 0)

    assert house.item.item_type is not None
    assert house.item.item_type.name == "house"


def test_list_houses(client_authenticated, household, house, db):
    res = client_authenticated.get("/worldItems/1/houses")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == house["id"], res.json()[0]
    assert res.json()[0]["item"]["position"]["x"] == 0.0
    assert res.json()[0]["item"]["position"]["y"] == 0.0
    assert res.json()[0]["item"]["position"]["z"] == 0.0


def test_fetch_house(client_authenticated, household, house, db):
    res = client_authenticated.get(f"/worldItems/1/houses/{house['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == house["id"], res.json()
    assert isinstance(res.json()["item"]["position"]["x"], float)
    assert isinstance(res.json()["item"]["position"]["y"], float)
    assert isinstance(res.json()["item"]["position"]["z"], float)
