import socketio
from fastapi import WebSocket, APIRouter
from fastapi.security import OAuth2PasswordBearer
from app.database.models.user import User
from app.helpers.security import verify_token


router = APIRouter()


sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

user_sockets = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def send_notification_to_user(user_id: int, message: str):
    """
    Send notification message to user through WebSocket connection.
    """
    print(user_id)
    print(user_sockets)
    if user_id in user_sockets:
        await user_sockets[user_id].send_text(message)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    jwt_token = websocket.headers.get("sec-websocket-protocol")
    if jwt_token is None:
        await websocket.close()
        return
    user = verify_token(jwt_token)
    current_user = await User.get_or_none(id=user.get("id"))
    if current_user is None:
        await websocket.close()
        return
    user_sockets[int(current_user.id)] = websocket
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)
