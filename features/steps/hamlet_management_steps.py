from behave import given, when, then, step

DEFAULT_USER = {"username": "nyancol", "email": "yanncolina@test.com",
               "first_name": "toto", "last_name": "tata"}


@given('A hamlet named "{hl_name}" exists')
def step_impl(context, hl_name):
    context.hamlet = context.client.post("/hamlets", json={"name": hl_name},
                                         headers={"Authorization": f"Bearer {context.token}"}).json()


# @given('I am a registered user "{username}"')
# def step_impl(context, username):
#     context.response = context.client.post("/users", json={**DEFAULT_USER, **{"username": username}})


@given('I am logged in with the user "{username}')
def step_impl(context, username):
    context.token = username
    context.me = context.client.get("/users/me/",
                                    headers={"Authorization": f"Bearer {context.token}"}).json()


@when('I fetch the list of Hamlets')
def step_impl(context):
    context.response = context.client.get("/hamlets",
                                    headers={"Authorization": f"Bearer {context.token}"})


@then('I should get at least one hamlet')
def step_impl(context):
    assert len(context.response.json()) >= 1, context.response.content
    assert context.response.json()[0]["id"] > 0, context.response.content


@when('I request access to the hamlet "{hl_name}"')
def step_impl(context, hl_name):
    hamlets = context.client.get("/hamlets",
                                 headers={"Authorization": f"Bearer {context.token}"}).json()

    hl_id = [h["id"] for h in hamlets if h["name"] == hl_name][0]
    request = {"hamlet_id": hl_id, "user_id": context.me["id"], "content": "Please"}
    context.response = context.client.post(f"/hamlets/{hl_id}/naturalisations",
                                    json=request,
                                    headers={"Authorization": f"Bearer {context.token}"})


@then('I should see my request being created with a status "{status}"')
def step_impl(context, status):
    assert "id" in context.response.json()
    assert "user_id" in context.response.json()
    assert context.response.json()["user_id"] == context.me["id"]
    assert context.response.json()["status"] == status
    assert context.response.status_code == 200


@given('A hamlet access request exists from "{username}" to "{hamlet_name}"')
def step_impl(context, username, hamlet_name):
    users = context.client.get("/users", headers={"Authorization": f"Bearer {context.token}"}).json()
    user_id = [u["id"] for u in users if u["username"] == username][0]

    hamlet_id = context.hamlet["id"]
    request = {"hamlet_id": hamlet_id, "user_id": user_id, "content": "Please"}
    context.access_request = context.client.post(f"/hamlets/{hamlet_id}/naturalisations",
                                                 json=request,
                                          headers={"Authorization": f"Bearer {context.token}"}) \
                                           .json()


@when('I approve the access request')
def step_impl(context):
    hamlet_id = context.hamlet["id"]
    request_id = context.access_request["id"]

    request = context.client.get(f"/hamlets/{hamlet_id}/naturalisations/{request_id}",
                                 headers={"Authorization": f"Bearer {context.token}"}).json()
    status_update = {"hamlet_id": hamlet_id, "id": request["id"], "status": "Approved"}
    context.response = context.client.put(f"/hamlets/{hamlet_id}/naturalisations/{request_id}/status",
                                 json=status_update,
                                 headers={"Authorization": f"Bearer {context.token}"}).json()


@then('The user "{username}" should have access to hamlet "{hamlet_name}"')
def step_impl(context, username, hamlet_name):
    hamlet_id = context.hamlet["id"]
    assert context.response["status"] == "Approved", context.response
    hamlet_details = context.client.get(f"/hamlets/{hamlet_id}",
                                        headers={"Authorization": f"Bearer {context.token}"}).json()
    assert hamlet_details["access"] == True, hamlet_details

