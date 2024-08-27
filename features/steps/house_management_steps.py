from potato_pyserver.models import House, WorldItem

from behave import given, when, then, step


DEFAULT_USER = {"username": "nyancol", "email": "yanncolina@test.com",
               "first_name": "toto", "last_name": "tata"}


@given('A user named "{user}" exists')
def step_impl(context, user):
    user = {**DEFAULT_USER, **{"username": user}}
    context.client.post("/users", json=user)


@given('The "{user}" belongs to a household named "{hh_name}"')
def step_impl(context, username, hh_name):
    household = context.client.post("/households", json={"name": hh_name}).json()
    user = context.client.get("/users/my", headers={"Authorization": f"Bearer {username}"}).json()
    user = {**DEFAULT_USER, **{"household_id": household["id"]}}
    user = context.client.put(f"/users/{user['id']}", json=user,
                              headers={"Authorization": f"Bearer {user}"}).json()
    context.user = user
    context.household = household


@when('I create a house named "{h_name}" belonging to the household in the hamlet')
def step_impl(context, h_name):
    hh_id = context.household["id"]
    hl_id = context.hamlet["id"]
    response = context.client.post("/worldItems/houses", json={"name": h_name,
                                                               "household_id": hh_id,
                                                               "hamlet_id": hl_id})
    context.response = response


@then("I should receive a confirmation of a successful creation")
def step_impl(context):
    context.response.status_code == 201


@then('A house named "{house_name}" should exist')
def step_impl(context, house_name):
    house = context.db.query(House).where(House.name == house_name).first()
    assert house is not None, house


@then('A world item linked to a house "{house_name}" should exist')
def step_impl(context, house_name):
    item_id = context.db.query(House).where(House.name == house_name).first().item_id
    item = context.db.query(WorldItem).where(WorldItem.id == item_id).first()
    assert item is not None


@given('A house named "{name}" belonging to the household "{hh_id:d}" in the hamlet "{hl_id:d}" exists')
def step_impl(context, name, hh_id, hl_id):
    context.client.post("/households", json={"name": "asdf"})
    context.client.post("/hamlets", json={"name": "asdfasdf"})
    context.client.post("/worldItems/houses", json={"household_id": hh_id, "hamlet_id": hl_id,
                                                   "name": name})


@when('I fetch the house of id "{house_id:d}"')
def step_impl(context, house_id):
    context.house = context.client.get(f"/worldItems/houses/{house_id}").json()
    

@then('I should receive a house id, item_id, household_id and hamlet_id')
def step_impl(context):
    assert context.house["id"] > 0
    assert context.house["item_id"] > 0
    assert context.house["household_id"] > 0
    assert context.house["hamlet_id"] > 0

