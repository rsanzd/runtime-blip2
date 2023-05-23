from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import requests
import json

app = FastAPI()


class ImageURL (BaseModel):
    image_url: str


class ImageQuestion (BaseModel):
    image_url: str
    question: str


@app.post("/describe-image")
async def describe_image(image_data: ImageURL):
    response = requests.post(
        "http://1689-34-143-171-130.ngrok-free.app",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"image_url": image_data.image_url},
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error")

    return JSONResponse(content=response.json())


@app.post("/blip2_question")
async def blip2_question(image_question: ImageQuestion):
    image_url = image_question.image_url
    question = image_question.question

    if not image_url:
        return JSONResponse(content={"error": "No se proporcionó ninguna URL"})

    if not question:
        return JSONResponse(content={"error": "No se proporcionó ninguna pregunta"})

    response = requests.post(
        "http://1689-34-143-171-130.ngrok-free.app/blip2_question",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"image_url": image_url, "question": question},
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error")

    return JSONResponse(content=response.json())


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def serve_manifest():
    try:
        with open("manifest.json", "r") as manifest_file:
            manifest_data = manifest_file.read()
        return JSONResponse(content=json.loads(manifest_data))

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Manifest file not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)