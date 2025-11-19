import os
import uuid
import io
from typing import List, Dict

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
import cv2
import numpy as np
import base64
from fastapi import UploadFile, HTTPException

# Load environment
load_dotenv()

# S3 config from env
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")

# Haar cascade path: same relative location as before (app/data/...)
FACE_CASCADE_PATH = os.path.join(
    os.path.dirname(__file__), "../data/haarcascade_frontalface_default.xml"
)

if not os.path.exists(FACE_CASCADE_PATH):
    raise FileNotFoundError(
        f"Error: No se encontró el archivo del clasificador Haar Cascade en '{FACE_CASCADE_PATH}'. "
        "Por favor, descárgalo de https://github.com/opencv/opencv/raw/4.x/data/haarcascades/haarcascade_frontalface_default.xml "
        "y colócalo en la ruta correcta."
    )

face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION,
)


class FileService:
    @staticmethod
    def detect_faces(image_bytes: bytes) -> List[Dict[str, int]]:
        """Detect faces in image bytes and return list of dicts {x,y,w,h}."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(
                status_code=400, detail="No se pudo decodificar la imagen."
            )
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        min_neighbors = 7
        min_size = (30, 30)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1, 
            minNeighbors=min_neighbors,
            minSize=min_size 
        )
        return [
            {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
            for (x, y, w, h) in faces
        ]

    @staticmethod
    def upload_file_to_s3_with_face_detection(file: UploadFile) -> Dict:
        """Upload file to S3 and return public URL + detected faces."""
        # Read bytes once
        image_bytes = file.file.read()
        # Reset pointer for any other consumer
        file.file.seek(0)

        file_extension = os.path.splitext(file.filename)[1]
        file_key = f"{uuid.uuid4()}{file_extension}"

        try:
            s3_client.upload_fileobj(
                io.BytesIO(image_bytes),
                AWS_S3_BUCKET_NAME,
                file_key,
                ExtraArgs={
                    "ContentType": file.content_type,
                    # 'ACL': 'public-read'
                },
            )

            file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION}.amazonaws.com/{file_key}"
            faces = FileService.detect_faces(image_bytes)
            return {"url": file_url, "faces": faces}

        except NoCredentialsError:
            raise HTTPException(
                status_code=500, detail="Credenciales de AWS no encontradas."
            )
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error al subir a S3: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")

    @staticmethod
    def draw_faces_on_image_and_return_data_url(file: UploadFile) -> str:
        """Draw rectangles around detected faces and return a PNG data URL string."""
        # Read bytes once
        image_bytes = file.file.read()
        # Reset pointer if other consumers expect it
        try:
            file.file.seek(0)
        except Exception:
            # Not critical if seek fails for some file-like objects
            pass

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(
                status_code=400, detail="No se pudo decodificar la imagen."
            )

        # Use the existing detect_faces helper to get face boxes
        faces_list = FileService.detect_faces(image_bytes)

        # Draw rectangles (green, thickness 2) using the boxes from detect_faces
        for face in faces_list:
            x = face["x"]
            y = face["y"]
            w = face["w"]
            h = face["h"]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Encode to PNG in memory
        success, encoded = cv2.imencode(".png", img)
        if not success:
            raise HTTPException(
                status_code=500, detail="Error al codificar la imagen con rectángulos."
            )

        png_bytes = encoded.tobytes()
        b64 = base64.b64encode(png_bytes).decode("ascii")
        data_url = f"data:image/png;base64,{b64}"

        # Return only the data URL (caller can call detect_faces separately if they need boxes)
        return png_bytes
