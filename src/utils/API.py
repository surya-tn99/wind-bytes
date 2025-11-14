from fastapi import FastAPI , WebSocket

api = FastAPI()

# host websocket 
host_ws = None

# WEBSOCKET COMMUNICATION TYPE 
# 1 - normal chat msg 

@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global host_ws

    await websocket.accept()
    host_ws = websocket
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()  
    except:
        host_ws = None

async def send_msg_2_host(peer_code , msg):

    global host_ws 

    if host_ws:
        try:
            await host_ws.send_json(
                {
                    "peer_code":peer_code,
                    "msg":msg,
                    "type":"1"
                }
            )
        except:
            host_ws = None 
            raise Exception("host websocket is not connected")
    else:
        raise Exception("host websocket is not connected")
