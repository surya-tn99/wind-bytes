import socketio 
import ip
import uvicorn

sio = socketio.AsyncServer(async_mode = "asgi" , cors_allowed_origins='*')


app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid , environ):
    print("client connected : ",sid)

@sio.event
async def disconnect(sid):
    print("client disconnected : ",sid)

@sio.event
async def rcv_client_msg(sid , data):
    print("msg from client \n\t ", sid)
    print("msg : ",data)

    await sio.emit("response_msg" 
        , {'message':f'received data is {data}'}
        , to = sid
    )

def run_socket_server():

    ip_addr = ip.get_ip_addr()
    port = ip.get_port_number()

    if not port[0]:
        print("All port are already binded from range 1100 to 9999")
        return
    
    encoded = ip.encode_ip_port(ip_addr , port[1])
    print(f"\n\n\t IP : {encoded}\n\n")
    uvicorn.run('socketServer:app' 
                , host=ip_addr
                , port=port[1]
                )

if __name__ == '__main__':
    run_socket_server()