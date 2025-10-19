# file handling 
import os
import shutil

# fastAPI
from fastapi import FastAPI, File, UploadFile, Request ,Header, HTTPException
from fastapi.responses import HTMLResponse , StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

# file ID preparation
from datetime import datetime
import random
import csv

app = FastAPI()

user_video_saving_dir = "data/videos"
os.makedirs(user_video_saving_dir, exist_ok=True)

# file to store the video file name
csv_file_path = "data/users/videoName.csv"
os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

# Ensure CSV file exists with header
if not os.path.exists(csv_file_path):
    with open(csv_file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "filename"]) 

# chunk
KB = 1024
MB = 1024 * KB
CHUNK_SIZE = 1 * MB 

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

# user interaction page hosting
@app.get("/u/upload", response_class=HTMLResponse)
async def uploadVideoPage(request:Request):
    return templates.TemplateResponse("uploadVideo.html",{"request":request})

@app.get("/u/watch", response_class=HTMLResponse)
async def watchVideoPage(request: Request):
    video_list = []

    # Read videos from CSV
    try:
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                video_list.append(row)
    except FileNotFoundError:
        video_list = []

    return templates.TemplateResponse(
        "watchVideo.html",
        {
            "request": request,
            "videos": video_list  # Pass the video list to Jinja
        }
    )

# host the player page
@app.get("/source/{videoId}")
async def videoPlayerPage(request: Request , videoId:str):
    return templates.TemplateResponse("videoPlayer.html",{
        "request":request,
        "videoId":videoId
    })

# backend related routes
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

# streaming video
@app.get("/stream/{videoId}")
async def streamVideo(videoId:str , range:str = Header(None)):

    video_path = os.path.join(user_video_saving_dir, videoId)
    if not os.path.isfile(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = os.path.getsize(video_path)
    start = 0
    end = file_size - 1
    status_code = 200

    if range is not None:
        range_value = range.strip().replace("bytes=", "")
        start_str, end_str = range_value.split("-") if "-" in range_value else (range_value, "")
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1  # don’t enforce CHUNK_SIZE
        status_code = 206


    content_length = (end - start) + 1

    # chunk_size = 4 * KB # repeated send 16KB to client
    chunk_size = 64 * KB
    def file_iterator(path , offset , bytes_to_read):
        with open(path , "rb") as file:
            file.seek(offset)
            while bytes_to_read > 0 :
                chunk = file.read(min(chunk_size , bytes_to_read))
                if not chunk:
                    break
                bytes_to_read -= len(chunk)
                yield chunk

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type":  "video/mp4",
    }

    return StreamingResponse(
        file_iterator(video_path , start , content_length),
        status_code = status_code,
        headers = headers
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=2025 , reload=True , host="0.0.0.0")


# 200 - full content
# 206 - partial content
# 404 - not found


