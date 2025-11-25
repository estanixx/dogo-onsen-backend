from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlmodel import SQLModel
from app.services import FileService
from typing import List, Dict
from fastapi.responses import Response
FileRouter = APIRouter()


# Definimos un modelo de respuesta para claridad
class ImageUploadResponse(SQLModel):
    url: str
    faces: List[Dict[str, int]]  # Lista de diccionarios con x, y, w, h


@FileRouter.post("/upload-image-with-faces") #, response_model=ImageUploadResponse
async def upload_image_with_faces_endpoint(user_file: UploadFile = File(...), template_filename: str = Form(...)):
    """
    Endpoint para subir una imagen, detecta rostros y devuelve la URL de S3
    y las coordenadas de los rostros detectados.
    """

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if user_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Solo se aceptan JPEG, PNG, WebP.",
        )

    # Use the service to upload and detect faces
    result = FileService.create_composite_image(user_file, template_filename)
    return result



class ImageDrawResponse(SQLModel):
    data_url: str
    faces: List[Dict[str, int]]


@FileRouter.post("/draw-faces")
async def draw_faces_endpoint(file: UploadFile = File(...)):
    """
    Endpoint that returns the same image with rectangles drawn around detected faces as a data URL,
    plus the face bounding boxes.
    """

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Solo se aceptan JPEG, PNG, WebP.",
        )

    # Use the service to draw rectangles and return the PNG data URL string
    data_url = FileService.draw_faces_on_image_and_return_data_url(file)
    return Response(content=data_url, media_type="image/jpeg")
