# -- FILE: features/environment.py
from potato_pyserver.main import app
from potato_pyserver.models import reset_tables, User
from potato_pyserver.database import engine, SessionLocal
from potato_pyserver.dependencies import get_current_user, UserDataResponse


from fastapi import Header, HTTPException
from fastapi.testclient import TestClient



def before_all(context):
    context.client = TestClient(app)
    context.db = SessionLocal()
    app.dependency_overrides[get_current_user]  = override_current_user


def after_all(context):
    context.db.close()
    app.dependency_overrides.clear()


def before_scenario(context, scenario):
    context.db.close()
    reset_tables(engine)


def override_current_user(authorization: str = Header(None)):
    token = authorization.split(" ")[1]
    return User(id=1, username=token, email="toto@example.com", first_name="toto", last_name="tata", role="user")


