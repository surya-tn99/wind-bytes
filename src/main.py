# file handling 
import os
import shutil

# fastAPI
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

# file ID preparation
from datetime import datetime
import random
import csv

app = FastAPI()

user_video_saving_dir = "data/users"
os.makedirs(user_video_saving_dir, exist_ok=True)

# file to store the video file name
csv_file_path = "data/videos/videoName.csv"
os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

# Ensure CSV file exists with header
if not os.path.exists(csv_file_path):
    with open(csv_file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "filename"]) 


templates = Jinja2Templates(directory = "website")
# css
app.mount("/style", StaticFiles(directory="website/style"), name="style")
app.mount("/u/style", StaticFiles(directory="website/style"), name="style")
# js
app.mount("/script", StaticFiles(directory="website/script"), name="script")
app.mount("/u/script", StaticFiles(directory="website/script"), name="script")

@app.get("/", response_class=HTMLResponse)
async def indexPage(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/u/upload", response_class=HTMLResponse)
async def uploadVideoPage(request:Request):
    return templates.TemplateResponse("uploadVideo.html",{"request":request})

# route : /u/watch <- user can view the videos

@app.post("/file/upload")
async def storeVideo(videoFile : UploadFile = File(...)):

    def prepare_file_id():
        
        timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        uuid4 = f"{random.randint(1000, 9999)}"
        extension = os.path.splitext(videoFile.filename)[1]
        return  f"{timestamp}-{uuid4}{extension}"
        
    try:
        
        ID = prepare_file_id()

        file_path = os.path.join(user_video_saving_dir, ID )
    
        with open(file_path, 'wb') as FILE:
            shutil.copyfileobj(videoFile.file , FILE)
        

        with open(csv_file_path,"a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([ID, videoFile.filename])
        
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
    uvicorn.run("main:app", port=2025 , reload=True)