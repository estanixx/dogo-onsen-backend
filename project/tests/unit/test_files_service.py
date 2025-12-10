import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


def test_files_module_import_and_draw_faces_error(monkeypatch):
    # Prevent FileNotFoundError on import by making os.path.exists True
    import os

    monkeypatch.setattr(os.path, "exists", lambda p: True)

    # Patch cv2.CascadeClassifier to a dummy that has detectMultiScale
    class DummyCascade:
        def detectMultiScale(
            self, img, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30)
        ):
            return []

    import importlib

    # Ensure boto3 client creation is safe: patch boto3.client to a dummy
    monkeypatch.setattr("boto3.client", lambda *args, **kwargs: MagicMock())

    # Patch cv2.imdecode to return None to trigger HTTPException in draw function
    monkeypatch.setattr("cv2.imdecode", lambda *args, **kwargs: None)
    monkeypatch.setattr("cv2.CascadeClassifier", lambda *args, **kwargs: DummyCascade())

    # Now import the module under test
    mod = importlib.import_module("app.services.files")
    FileService = mod.FileService

    # Create a fake UploadFile-like object with a file attribute
    class FakeFile:
        def __init__(self, data: bytes):
            self.file = MagicMock()
            self.file.read.return_value = data

    fake = FakeFile(b"not-an-image")

    with pytest.raises(HTTPException):
        FileService.draw_faces_on_image_and_return_data_url(fake)
