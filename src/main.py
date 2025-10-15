# file handling 
import os
import shutil

# fastAPI
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

user_video_saving_dir = "data/users"
os.makedirs(user_video_saving_dir, exist_ok=True)
    

templates = Jinja2Templates(directory = "website")
app.mount("/style", StaticFiles(directory="website/style"), name="style")

@app.get("/", response_class=HTMLResponse)
async def mainPage(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.post("/upload")
async def storeVideo(videoFile : UploadFile = File(...)):

    file_path = os.path.join(user_video_saving_dir, videoFile.filename)
    
    try:
        with open(file_path, 'wb') as FILE:
            shutil.copyfileobj(videoFile.file , FILE)
        
        return {
            "status":"video uploaded successfully",
            "filename":videoFile.filename
        }
    except Exception as e:
        return {
            "status":"video uploading is failed",
            "error":f"{e}"
        }
    finally:
        videoFile.file.close()


if __name__ == "__main__":
    uvicorn.run("main:app", port=2025)