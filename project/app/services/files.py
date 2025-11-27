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
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1, 
            minNeighbors=7,
            minSize=(30, 30)
        )
        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No se detectó ningún rostro claro. Por favor, tome la foto una vez más.")

        candidates = []
        for (x, y, w, h) in faces:
            candidates.append({
                "x": int(x), "y": int(y), 
                "w": int(w), "h": int(h),
                "area": w * h # Calculamos área para saber cuál es más grande
            })

        # CASO: SE DETECTA 1 O MÁS -> ELEGIR EL MÁS GRANDE
        # Ordenamos de mayor a menor según el 'area'
        candidates.sort(key=lambda f: f["area"], reverse=True)

        # Tomamos el primero (el ganador)
        best_face = candidates[0]

        return [best_face]

    @staticmethod
    def _download_image_from_s3(key: str) -> np.ndarray:
        """Helper para descargar imagen de S3 y convertirla a OpenCV format"""
        try:
            response = s3_client.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=key, )
            image_bytes = response['Body'].read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise Exception("No se pudo decodificar la imagen del template")
            return img
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error descargando template {key}: {str(e)}")

    @staticmethod
    def create_composite_image(user_file: UploadFile, template_filename: str) -> Dict:
        # 1. Leer imagen del usuario
        user_bytes = user_file.file.read()
        user_file.file.seek(0)
        
        # 2. Detectar rostro
        faces = FileService.detect_faces(user_bytes)
        if not faces:
            # IMPORTANTE: Validar esto para no procesar sin cara
            raise HTTPException(status_code=400, detail="No se detectó rostro en la foto del usuario.")
        
        face_data = faces[0]
        nparr = np.frombuffer(user_bytes, np.uint8)
        user_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        x, y, w, h = face_data['x'], face_data['y'], face_data['w'], face_data['h']
        face_roi = user_img[y:y+h, x:x+w]

        # 3. Descargar Template (Manejo de errores mejorado)
        if not template_filename.endswith(('.png', '.jpg', '.jpeg')):
             # Aseguramos extensión si viene sin ella
             template_filename += ".png"
        
        template_end = template_filename.split('/')[-1]
        template_key = f"spirit_types/{template_end}"
        print(f"DEBUG: Intentando descargar {template_key}") # <--- LOG ÚTIL
        
        try:
            template_img = FileService._download_image_from_s3(template_key)
        except Exception as e:
            print(f"ERROR S3: {str(e)}")
            raise HTTPException(status_code=404, detail=f"No se encontró el template '{template_end}'")

        # 4. Procesamiento de Color (HSV)
        hsv_template = cv2.cvtColor(template_img, cv2.COLOR_BGR2HSV)

        # Rango VERDE (Ajustado)
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([85, 255, 255])
        mask_green_raw = cv2.inRange(hsv_template, lower_green, upper_green)

        # Rango AZUL (Ajustado)
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])
        mask_blue_raw = cv2.inRange(hsv_template, lower_blue, upper_blue)

        # --- LIMPIEZA DE MÁSCARAS (NUEVO) ---
        
        # Función auxiliar para quedarse solo con el contorno más grande
        def get_largest_contour_mask(raw_mask, color_name):
            # 1. Eliminar ruido tipo "sal y pimienta"
            kernel = np.ones((3,3), np.uint8)
            clean_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel, iterations=2)
            
            # 2. Encontrar contornos
            contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None, None, None
            
            # 3. Ordenar por área y tomar el más grande
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Filtro de tamaño mínimo: Si lo que encontró es un puntito de ruido (<100px), ignóralo
            if cv2.contourArea(largest_contour) < 100:
                print(f"ADVERTENCIA: El {color_name} encontrado es demasiado pequeño (posible ruido).")
                return None, None, None

            # 4. Crear una máscara NUEVA negra y dibujar solo el ganador (blanco)
            final_mask = np.zeros_like(raw_mask)
            cv2.drawContours(final_mask, [largest_contour], -1, 255, -1) # -1 rellena el interior
            
            return final_mask, largest_contour, cv2.boundingRect(largest_contour)

        try:
        # 5. Obtener Máscara Verde Limpia
            mask_green, green_contour, green_rect = get_largest_contour_mask(mask_green_raw, "VERDE")
            
            if mask_green is None:
                raise HTTPException(status_code=422, detail="No se encontró un área verde clara (o era muy pequeña).")
            
            gx, gy, gw, gh = green_rect

            # 6. Obtener Máscara Azul Limpia y su Centro
            mask_blue, blue_contour, _ = get_largest_contour_mask(mask_blue_raw, "AZUL")
            cx_blue, cy_blue = 0, 0
            if mask_blue is not None:
                # Usamos momentos SOLO sobre la máscara azul limpia
                M = cv2.moments(mask_blue)
                if M["m00"] != 0:
                    cx_blue = int(M["m10"] / M["m00"])
                    cy_blue = int(M["m01"] / M["m00"])
                else:
                    cx_blue = gx + gw // 2
                    cy_blue = gy + gh // 2
            else:
                print("WARN: No se encontró punto azul limpio. Usando centro del verde.")
                mask_blue = np.zeros_like(mask_green)
                cx_blue = gx + gw // 2
                cy_blue = gy + gh // 2

        except Exception as e:
            # Si ocurre cualquier error matemático raro, lo atrapamos aquí
            print(f"ERROR CRÍTICO EN OPENCV: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error procesando la imagen del template: {str(e)}")


        # 7. Redimensionar Rostro (Aspect Fill)
        face_h, face_w = face_roi.shape[:2]
        scale_w = gw / face_w
        scale_h = gh / face_h
        scale = max(scale_w, scale_h) * 1.05 # 5% extra

        new_w = int(face_w * scale)
        new_h = int(face_h * scale)
        face_resized = cv2.resize(face_roi, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # 8. Composición
        template_h, template_w = template_img.shape[:2]
        face_layer = np.zeros((template_h, template_w, 3), dtype=np.uint8)

        face_center_x = new_w // 2
        face_center_y = new_h // 2
        top_left_x = cx_blue - face_center_x
        top_left_y = cy_blue - face_center_y

        # Clipping seguro
        x1 = max(top_left_x, 0)
        y1 = max(top_left_y, 0)
        x2 = min(top_left_x + new_w, template_w)
        y2 = min(top_left_y + new_h, template_h)

        fx1 = max(0, -top_left_x)
        fy1 = max(0, -top_left_y)
        fx2 = fx1 + (x2 - x1)
        fy2 = fy1 + (y2 - y1)

        if x2 > x1 and y2 > y1:
            face_layer[y1:y2, x1:x2] = face_resized[fy1:fy2, fx1:fx2]

        # 9. Fusión Final
        # Borramos azul y verde del fondo
        mask_to_remove = cv2.bitwise_or(mask_green, mask_blue)
        # Invertimos para conservar el fondo
        mask_bg = cv2.bitwise_not(mask_to_remove)
        
        bg_part = cv2.bitwise_and(template_img, template_img, mask=mask_bg)
        fg_part = cv2.bitwise_and(face_layer, face_layer, mask=mask_green)

        final_output = cv2.add(bg_part, fg_part)

        # 10. Subir y Retornar
        success, encoded_jpg = cv2.imencode(".jpg", final_output)
        if not success:
             raise HTTPException(status_code=500, detail="Error codificando imagen final.")
        
        result_bytes = io.BytesIO(encoded_jpg.tobytes())
        final_filename = f"users/composite_{uuid.uuid4()}.jpg"
        
        try:
            s3_client.upload_fileobj(
                result_bytes,
                AWS_S3_BUCKET_NAME,
                final_filename,
                ExtraArgs={"ContentType": "image/jpeg"}
            )
            file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION}.amazonaws.com/{final_filename}"
            
            # RETORNO CORREGIDO (Incluye faces vacío para evitar error de validación)
            return {
                "url": file_url, 
                "status": "success",
                "faces": [] 
            }
            
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error subiendo a S3: {e}")

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
