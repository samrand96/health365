import socketio
from fastapi import FastAPI
from app.database.database import init_db
from app.routers import users, utilities, patients, doctors, websocket

app = FastAPI()


app.include_router(users.router)
app.include_router(utilities.router)
app.include_router(patients.router)
app.include_router(doctors.router)

app.include_router(websocket.router)



@app.on_event("startup")
async def startup_event():
    """
        A function that handles the startup event by initializing the database.
        No parameters are required. Does not return anything.
    """
    print("INITIALISING DATABASE")
    init_db(app)
