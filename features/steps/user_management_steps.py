# -- FILE: features/steps/example_steps.py
import csv

from potato_pyserver.models import User, Household, House, Hamlet

from fastapi.exceptions import HTTPException
from behave import given, when, then, step
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def populate_test_users(engine):
    session = Session(engine)
    with open('users.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            session.add(User(first_name=row["first_name"], last_name=row["last_name"]))
    session.commit()


def populate_test_hamlets(engine):
    session = Session(engine)
    with open('hamlets.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            session.add(Hamlet(name=row["name"]))
    session.commit()


def populate_test_households(engine):
    session = Session(engine)
    with open('households.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            session.add(Household(name=row["name"]))
    session.commit()


def populate_test_user_households(engine):
    session = Session(engine)
    with open('household_users.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            user = session.query(User).filter_by(id=int(row["user_id"])).first()
            user.household_id = row["household_id"]
    session.commit()


def populate_test_world_item_types(engine):
    session = Session(engine)
    with open('world_items.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            session.add(WorldItemType(name=row["name"]))
    session.commit()


def populate_test_world_items(engine):
    session = Session(engine)
    with open('world_items.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            session.add(WorldItem(name=row["name"], item_type_id=row["item_type_id"],
                                  hamlet_id=row["hamlet_id"]))
    session.commit()


def populate_test_houses(engine):
    session = Session(engine)
    with open('houses.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            session.add(House(item_id=row["world_item_id"], household_id=row["household_id"]))
    session.commit()



def populate_test_tables(engine):
    populate_test_hamlets(engine)
    populate_test_users(engine)
    populate_test_households(engine)
    populate_test_user_households(engine)
    populate_test_world_item_types(engine)
    populate_test_world_items(engine)
    populate_test_houses(engine)


@given('I am logging in the registration page')
def step_impl(context):
    pass


@when('I provide a {username}, {email}, {password}, {first_name} and {last_name}')
def step_impl(context, username, email, password, first_name, last_name):
    user = {"username": username, "email": email,
            "password": password, "first_name": first_name, "last_name": last_name}
    context.response = context.client.post("/users", json=user)


@then('I should receive a confirmation of a sucessful registration')
def step_impl(context):
    assert context.response.status_code == 200


@then('I should receive an error "{code}" message')
def step_impl(context, code):
    assert context.response.status_code == int(code), context.response


@when('I provide registration values "{username}" and "{email}"')
def step_impl(context, username, email):
    user = {"username": username, "email": email,
            "password": "asdfasdf", "first_name": "asdfasdf",
            "last_name": "asdfasdf"}
    context.response = context.client.post("/users", json=user)


@given('There is an existing user "{username}" and "{email}"')
def step_impl(context, username, email):
    context.db.add(User(username=username, email=email,
                        hashed_password="asdfasdfasdf",
                        first_name="asdf", last_name="asdf"))
    context.db.commit()


@given('I am a new user with a username "{username}"')
def step_impl(context, username):
    user = {"username": username, "email": "yann@gmail.com",
            "password": "asdfasdf", "first_name": "first_name", "last_name": "last_name"}
    context.user = context.client.post("/users", json=user).json()


@when('I delete my user with a username "{username}"')
def step_impl(context, username):
    context.response = context.client.delete("/users/" + str(context.user["id"]),
                                             headers={"Authorization": f"Bearer {username}"})


@then('My user "{username}" should not exist anymore')
def step_impl(context, username):
    assert context.db.query(User).filter(User.username == username).first() is None


@given('I am connected with the "{username}"')
def step_impl(context, username):
    context.token = f"Bearer {username}"


@when('I update the user "{username}" email to "{email}"')
def step_impl(context, username, email):
    user = context.db.query(User).filter(User.username == username).first()
    assert user is not None
    new_user = {"username": user.username, "email": email,
                "first_name": user.first_name, "last_name": user.last_name}
    context.response = context.client.put(f"/users/{user.id}", json=new_user,
                       headers={"Authorization": context.token})


@then('I should get a permission error')
def step_impl(context):
    assert context.response.status_code == 409


@when('I update my email to "{email}"')
def step_impl(context, email):
    user = context.user
    new_user = {"username": user["username"], "first_name": user["first_name"],
                "last_name": user["last_name"], "email": email}
    context.response = context.client.put("/users/" + str(context.user["id"]),
                                         json=new_user,
                                         headers={"Authorization": f"Bearer {user['username']}"})


@then('My user should have "{email}" as email')
def step_impl(context, email):
    assert context.response.json()["email"] == email, context.response.content


@when('I fetch my user details')
def step_impl(context):
    context.response = context.client.get("/users/me/", headers={"Authorization": "Bearer mocked_token"})


@then('I should receive a status code of 200 and a payload with my user id')
def step_impl(context):
    assert context.response.status_code == 200
    assert "id" in context.response.json(), context.response.content
    assert context.response.json()["username"] == "mocked_token", context.response.content
    assert context.response.json()["id"] > 0


@given('There are "{num:d}" users')
def step_impl(context, num):
    user = {"password": "asdfasdf", "first_name": "first_name", "last_name": "last_name"}
    for i in range(num):
        user["username"] = f"aaau{i}"
        user["email"] = f"u{i}@gmail.com"
        context.client.post("/users", json=user).json()


@when('I fetch the list of users')
def step_impl(context):
    context.users = context.client.get("/users", headers={"Authorization": "Bearer toto"}).json()


@then('I should get a list of "{num:d}" users, with valid ids and usernames')
def step_impl(context, num):
    assert len(context.users) == num, len(context.users)
    assert all([u["id"] > 0 for u in context.users])
    assert all([len(u["username"]) > 0 for u in context.users])
    assert "hashed_password" not in context.users[0]


@given('I am a registered user "{username}" with a password "{password}"')
def step_impl(context, username, password):
    context.client.post("/users", json={"username": username, "password": password,
                                        "first_name": "fasdf", "last_name": "asdf",
                                        "email": "aucun@gmail.com"})


@when('I login with my "{user}" and "{password}"')
def step_impl(context, user, password):
    context.token = context.client.post("/token",
                                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                                        data={"grant_type": "password",
                                              "username": user,
                                              "password": password})

@then('I should get a valid token and username "{username}"')
def step_impl(context, username):
    assert "access_token" in context.token.json()
    assert "token_type" in context.token.json()
