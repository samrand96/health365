from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.helpers.constant import DB_URL

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["app.database.models.user","app.database.models.patient", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI) -> None:
    """
        Initializes the database by registering Tortoise ORM with the provided FastAPI 'app'.

        Parameters:
            app: FastAPI - The FastAPI instance to register Tortoise ORM with.

        Returns:
            None
    """
    register_tortoise(
        app,
        db_url=DB_URL,
        modules={"models": ["app.database.models.user", "app.database.models.patient"]},
        generate_schemas=True,
        add_exception_handlers=False
    )