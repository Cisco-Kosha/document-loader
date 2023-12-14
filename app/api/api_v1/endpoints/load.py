import os
from typing import Any, List

import requests
from fastapi import APIRouter, UploadFile, File
from starlette.responses import Response

from app.helper.url_loader import URLLoader
from app.helper.utility import web_crawl_RecursiveUrlLoader, web_crawl_AsyncHtmlLoader, web_crawl_AsyncChromiumLoader, web_crawl_SimpleWebPageLoader, load_file, fetch_contents_from_api_endpoint
from app.schemas.loader import BaseLoader


router = APIRouter()

@router.post("/crawl", status_code=200)
def crawl_website(document: BaseLoader) -> Any:
    """
       This endpoint is used to load any type of document by crawling a website url
    """
    try:
        #content, err = web_crawl_RecursiveUrlLoader(document)
        #content, err = web_crawl_AsyncHtmlLoader(document)
        content, err = web_crawl_AsyncChromiumLoader(document)
        #content, err = web_crawl_SimpleWebPageLoader(document)
        if err != "":
            return Response(status_code=400, content=str(err))
    except Exception as e:
        return Response(status_code=400, content=str(e))
    if not content:
        return Response(status_code=400, content="could not crawl provided url")
    else:
        return content    


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
        content, err = load_file(document)
        if err != "":
            return Response(status_code=400, content=err)
    except Exception as e:
        return Response(status_code=400, content=str(e))
    # delete the temporary file
    os.remove(file.filename)
    if not content:
        return Response(status_code=400, content="File type not supported")
    else:
        return content


@router.post("/remote", status_code=200)
def load_remote_document(document: BaseLoader) -> Any:
    """
       This endpoint is used to load any type of document (including REST APIs) from a remote location
    """
    try:
        content, err = load_file(document)
        if err != "":
            return Response(status_code=400, content=str(err))
        if len(content) == 0:
            # could be an API endpoint
            try:
                content = fetch_contents_from_api_endpoint(document)
            except Exception as e:
                return Response(status_code=400, content=e)
    except Exception as e:
        return Response(status_code=400, content=str(e))
    if not content:
        return Response(status_code=400, content="Data type not supported")
    else:
        return content



