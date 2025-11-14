import asyncio
import uvicorn
from utils import ip , socketClient
from utils.API import api
from utils.socketServer import wrap_fastapi_socketServer

from fastapi import Request 
from fastapi.templating import Jinja2Templates 
from fastapi.responses import HTMLResponse , JSONResponse
from fastapi.staticfiles import StaticFiles

app = wrap_fastapi_socketServer(api)

servers_lock = asyncio.Lock()


ip_addr = ip.get_ip_addr()
port_info = ip.get_port_number()

if not port_info[0]:
    print("All ports are already binded from range 1100 to 9999")
    exit(404)

port_number = port_info[1]
host_encoded_code = ip.encode_ip_port(ip_addr, port_number)


templates = Jinja2Templates(directory = "website")
# css
api.mount("/style", StaticFiles(directory="website/style"), name="style")
api.mount("/u/style", StaticFiles(directory="website/style"), name="style")
# js
api.mount("/script", StaticFiles(directory="website/script"), name="script")
api.mount("/u/script", StaticFiles(directory="website/script"), name="script")
# assert
api.mount("/assert", StaticFiles(directory="website/assert"), name="assert")
api.mount("/u/assert", StaticFiles(directory="website/assert"), name="assert")


@api.get("/", response_class=HTMLResponse)
def indexPage(request:Request):
    return templates.TemplateResponse("index.html"
            , 
            {
                "request":request,
                "host_code":host_encoded_code
            } 
    )

@api.get("/peer/connect/{peer_code}" , response_class=JSONResponse)
async def connect_peer(peer_code: str):

    #----------------
    #   TODO:
    #    check whether the peer_code is not same as host_code
    #---------------- 

    async with servers_lock:
        connection_flag , connetion_status= await socketClient.create_connection(peer_code ,host_encoded_code)

    return JSONResponse({"is_connection_success": connection_flag 
                         ,"status":connetion_status
                         })


@api.get("/exit" , response_class=JSONResponse)
async def end_conn():
    async with servers_lock:
        await socketClient.disconnect_all()
    return JSONResponse({"status": "all disconnected"})


@api.get("/host_ip", response_class=JSONResponse)
def show_host_ip():
    return {"ip": ip_addr , "port":port_number , "code":ip.encode_ip_port(ip_addr , port_number)} 

def run_app():

    print(f"\n\tIP : {ip_addr} \n\tPORT : {port_number} \n\tCODE : {host_encoded_code}\n")

    uvicorn.run("sio:app", host=ip_addr, port=port_number)


if __name__ == "__main__":
    run_app()
