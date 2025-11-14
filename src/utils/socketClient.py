import socketio 
from utils import  ip

servers = {}
server_count = 0

async def create_connection(peer_code , host_code):
    global server_count


    decoded = ip.decode_ip_port(peer_code)
    ip_addr = decoded[2] 
    
    sio = socketio.AsyncClient()
    server_count += 1
    name = f"server_{server_count}"

    url = ip.buildup_url_from_ip_addr(ip_addr)

    @sio.event
    async def connect():
        print(f"{name} connected - {ip_addr}")
        
        await sio.emit("rcv_client_msg" , {"message" : "message from CLIENT"})

    @sio.event
    async def disconnect():
        host_ws = None
        print(f"{name} disconnected - {ip_addr}")

    @sio.event
    async def response_msg(data):
        print(f"response from {name} - {ip_addr}")
        print("response is " + data["message"])
    

    try:
        await sio.connect(url , auth={
            "request_from_peer":host_code
        })
    except Exception as e:
        print(f"failed to connect\n {name} - {ip_addr}\nReason :  {e}")
        return False , f"failed to connect {ip_addr} \n Reason : {e}"
    
    servers[name] = {
        "sio":sio,
        "ip_addr":ip_addr,
        "peer_code":peer_code
    }

    return True , "Peer Connected Successfully"


async def disconnect_all():
    """Disconnect all clients."""
    for name, server in servers.items():
        sio = server["sio"]
        if sio.connected:
            await sio.disconnect()
            print(f"[{name}] Connection closed.")

