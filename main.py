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


@app.post("/blip2")
async def blip2(image_data: ImageURL):
    # Verifica si se proporcionó la URL de la imagen
    if not image_data.image_url:
        return JSONResponse(content={"error": "No se proporcionó ninguna URL de imagen."})

    try:
        # Intenta hacer una solicitud POST a tu servidor local
        response = requests.post(
            "http://fc6a-35-243-150-66.ngrok-free.app/blip2",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"image_url": image_data.image_url},
        )

        # Verifica si la respuesta tiene un código de estado 200
        if response.status_code != 200:
            return JSONResponse(content={"error": f"El servidor local devolvió un código de estado {response.status_code}."})

        # Intenta decodificar la respuesta como JSON
        response_data = response.json()

    except requests.RequestException as e:
        # Si hay un error en la solicitud, devuelve un mensaje de error
        return JSONResponse(content={"error": f"Hubo un error en la solicitud: {str(e)}."})

    except json.JSONDecodeError as e:
        # Si hay un error al decodificar la respuesta como JSON, devuelve un mensaje de error
        return JSONResponse(content={"error": f"Hubo un error al decodificar la respuesta como JSON: {str(e)}."})

    # Si todo va bien, devuelve la respuesta del servidor local
    return JSONResponse(content=response_data)




@app.post("/blip2_question")
async def blip2_question(image_question: ImageQuestion):
    image_url = image_question.image_url
    question = image_question.question

    if not image_url:
        return JSONResponse(content={"error": "No se proporcionó ninguna URL"})

    if not question:
        return JSONResponse(content={"error": "No se proporcionó ninguna pregunta"})

    response = requests.post(
        "http://fc6a-35-243-150-66.ngrok-free.app/blip2_question",
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