import socketio , asyncio , uvicorn
import  ip
from fastapi import FastAPI

servers = {}

server_count = 0

async def create_connection(ip_addr):
    global server_count

    sio = socketio.AsyncClient()
    server_count += 1
    name = f"server_{server_count}"

    url = ip.buildup_url_from_ip_addr(ip_addr)

    print(f"\n\n\t URL : {url}\n\n")

    @sio.event
    async def connect():
        print(f"{name} connected - {ip_addr}")
        await sio.emit("rcv_client_msg" , {"message" : "message from CLIENT"})


    @sio.event
    async def disconnect():
        print(f"{name} disconnected - {ip_addr}")

    @sio.event
    async def response_msg(data):
        print(f"response from {name} - {ip_addr}")
        print("response is " + data["message"])

    await sio.connect(url)
    

    servers[name] = sio

async def disconnect_all():
    """Disconnect all clients."""
    for name, sio in servers.items():
        if sio.connected:
            await sio.disconnect()
            print(f"[{name}] Connection closed.")


app = FastAPI()

@app.get("/add/{ip_addr}")
async def add_con(ip_addr: str):
    decoded = ip.decode_ip_port(ip_addr)
    url = decoded[2]

    print(f"\n\n\t {ip_addr} : {url}\n\n")
    
    await create_connection(url)
    
    return {"connected_servers": list(servers.keys())}

@app.get("/exit")
async def end_conn():
    await disconnect_all()
    return {"status": "all disconnected"}


def run_socket_client():

    port = ip.get_port_number()

    if not port[0]:
        print("All port are already binded from range 1100 to 9999")
        return
    
    uvicorn.run('socketClient:app' 
                , host=ip.get_ip_addr() 
                , port = port[1]
                )

if __name__ == '__main__':
    run_socket_client()

