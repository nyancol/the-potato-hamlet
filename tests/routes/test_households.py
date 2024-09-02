from potato_pyserver.main import app
from potato_pyserver.database import engine, get_db, SessionLocal
from potato_pyserver.models import User, reset_tables
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
def access_request(client_authenticated, household, user):
    res = client_authenticated.post(f"/households/{household['id']}/accessRequests",
                                    json={"household_id": household["id"],
                                          "user_id": user["id"],
                                          "content": "PLEASE"})
    return res.json()


def test_list_household(client_authenticated, user):
    res = client_authenticated.get("/households")
    assert res.status_code == 200
    assert len(res.json()) > 0


def test_rename_household(client_authenticated, user):
    res = client_authenticated.put("/households/1", json={"id": 1, "name": "asdf"})
    res = client_authenticated.get("/households/1")
    assert res.status_code == 200
    assert res.json()["name"] == "asdf"


def test_fetch_my_household(client_authenticated, user):
    res = client_authenticated.get("/households/me")
    assert res.status_code == 200
    assert res.json()["name"] != ""


def test_fetch_household_users(client_authenticated, user):
    res = client_authenticated.get("/households/1/users")
    assert res.status_code == 200
    assert len(res.json()) > 0
    assert res.json()[0]["id"] == user["id"]
    assert res.json()[0]["first_name"] == user["first_name"]
    

def test_create_household(client_authenticated, db, user):
    res = client_authenticated.post("/households", json={"name": "my family"})
    assert res.status_code == 200
    assert res.json()["name"] == "my family"
    assert res.json()["id"] > 0

    household = db.query(User).filter(User.id == user["id"]).first().user_household_access.household
    assert household.name == "my family"
    assert household.id == res.json()["id"]

# def test_delete_household(client_authenticated, household)
# def test_update_household(client_authenticated, household)

def test_create_household_access_request(client_authenticated, household, user):
    access_request = {"household_id": household["id"], "user_id": user["id"], "content": "PLEASE"}
    res = client_authenticated.post(f"/households/{household['id']}/accessRequests",
                                    json=access_request)
    assert res.status_code == 200


def test_list_household_access_requests(client_authenticated, access_request):
    req = client_authenticated.get(f"/households/{access_request['household_id']}/accessRequests")
    assert req.status_code == 200
    assert len(req.json()) == 1
    assert req.json()[0]["user_id"] == access_request["user_id"]
    assert req.json()[0]["household_id"] == access_request["household_id"]


def test_get_household_access_request(client_authenticated, access_request):
    r_id = access_request["id"]
    req = client_authenticated.get(f"/households/{access_request['household_id']}/accessRequests/{r_id}")
    assert req.status_code == 200
    assert req.json()["user_id"] == access_request["user_id"]
    assert req.json()["household_id"] == access_request["household_id"]


def test_approve_household_access_request(client_authenticated, access_request, db):
    r_id = access_request["id"]
    req = client_authenticated.put(
            f"/households/{access_request['household_id']}/accessRequests/{r_id}",
            json={"id": r_id, "household_id": access_request["household_id"],
                  "user_id": access_request["user_id"], "status": "Approved",
                  "content": "asdf"})

    assert req.status_code == 200

    user = db.query(User).filter(User.id == access_request["user_id"]).first()
    assert user.user_household_access is not None
    assert user.user_household_access.household_id == access_request["household_id"]

    assert req.json()["status"] == "Approved"


def test_reject_household_access_request(client_authenticated, access_request, db):
    r_id = access_request["id"]
    req = client_authenticated.put(
            f"/households/{access_request['household_id']}/accessRequests/{r_id}",
            json={"id": r_id, "household_id": access_request["household_id"],
                  "user_id": access_request["user_id"], "status": "Rejected",
                  "content": "asdf"})

    assert req.status_code == 200

    user = db.query(User).filter(User.id == access_request["user_id"]).first()
    assert req.json()["status"] == "Rejected"

# def test_users_in_household(client_authenticated)

# def test_get_my_household(client_authenticated, household, user):
#     res = client_authenticated.get(f"/households/{household['id']}/me",
#                                     json=access_request)
#     assert res.status_code == 200
