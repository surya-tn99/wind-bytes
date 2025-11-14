import socketio 
from fastapi import FastAPI

sio = socketio.AsyncServer(async_mode = "asgi" , cors_allowed_origins='*')
# api = FastAPI()
# app = socketio.ASGIApp(sio, other_asgi_app=api)

def wrap_fastapi_socketServer(fastapi):
    return socketio.ASGIApp(sio ,other_asgi_app=fastapi )

@sio.event
async def connect(sid , environ):
    print("client connected : ",sid)

@sio.event
async def disconnect(sid):
    print("client disconnected : ",sid)

@sio.event
async def rcv_client_msg(sid , data):
    print("msg from client \n\t ", sid)
    print("msg : ",data["message"])

    await sio.emit("response_msg" 
        , {'message':f'received data is {data}'}
        , to = sid
    )

