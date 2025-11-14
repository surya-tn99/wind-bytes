import asyncio
from fastapi import FastAPI
import uvicorn
import ip  
import socketClient  
import socketServer

api = FastAPI()

api.mount("/" ,socketServer.app)

# Ensure thread-safe access to servers dict
servers_lock = asyncio.Lock()

@api.get("/add/{ip_addr}")
async def add_con(ip_addr: str):
    decoded = ip.decode_ip_port(ip_addr)
    url = decoded[2] 

    print(f"\n\n\tAdding connection to {ip_addr} : {url}\n\n")

    async with servers_lock:
        await socketClient.create_connection(url)
        connected = list(socketClient.servers.keys())

    return {"connected_servers": connected}


@api.get("/exit")
async def end_conn():
    async with servers_lock:
        await socketClient.disconnect_all()
    return {"status": "all disconnected"}


def run_api():
    ip_addr = ip.get_ip_addr()
    port_info = ip.get_port_number()  # should return (bool, port_number)

    if not port_info[0]:
        print("All ports are already binded from range 1100 to 9999")
        return

    port_number = port_info[1]
    encoded = ip.encode_ip_port(ip_addr, port_number)
    print(f"\n\tIP : {ip_addr} \n\tPORT : {port_number} \n\tCODE : {encoded}\n")

    uvicorn.run("sio:api", host=ip_addr, port=port_number , reload=True)


if __name__ == "__main__":
    run_api()
