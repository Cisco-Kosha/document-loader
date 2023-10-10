import os
from typing import Any, List

from fastapi import APIRouter, UploadFile, File
from starlette.responses import Response

from app.helper.utility import load_file
from app.schemas.loader import BaseLoader


router = APIRouter()


@router.post("/", status_code=200)
def load_document(file: UploadFile = File(...)) -> Any:
    """
       This endpoint is used to load any type of document from a local filesystem location
    """
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    document = BaseLoader(url=file.filename)
    try:
        content = load_file(document)
    except Exception as e:
        return Response(status_code=400, content=e)
    # delete the temporary file
    os.remove(file.filename)
    if not content:
        return Response(status_code=400, content="File type not supported")
    else:
        return content


@router.post("/remote", status_code=200)
def load_remote_document(document: BaseLoader) -> Any:
    """
       This endpoint is used to load any type of document from a remote location
    """
    try:
        content = load_file(document)
    except Exception as e:
        return Response(status_code=400, content=e)
    if not content:
        return Response(status_code=400, content="File type not supported")
    else:
        return content



