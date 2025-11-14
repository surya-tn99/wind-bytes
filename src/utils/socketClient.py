import socketio 
from utils import  ip

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

    try:
        await sio.connect(url)
    except Exception as e:
        print(f"failed to connect\n {name} - {ip_addr}\nReason :  {e}")
        return
    
    servers[name] = sio

async def disconnect_all():
    """Disconnect all clients."""
    for name, sio in servers.items():
        if sio.connected:
            await sio.disconnect()
            print(f"[{name}] Connection closed.")
