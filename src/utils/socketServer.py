import socketio 
from fastapi import FastAPI

from utils import API

sio = socketio.AsyncServer(async_mode = "asgi" , cors_allowed_origins='*')

def wrap_fastapi_socketServer(fastapi):
    return socketio.ASGIApp(sio ,other_asgi_app=fastapi )

@sio.event
async def connect(sid , environ , auth):
    print("client connected : ",sid)
    
    await API.send_msg_2_host(
        peer_code = auth["request_from_peer"] 
        ,msg = f"CONNECT REQUEST FROM PEER {auth["request_from_peer"]}"
        )
    
    print("connect client code : "+auth["request_from_peer"])

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
