import os
from typing import List

from langchain.document_loaders import TextLoader, CSVLoader, JSONLoader, Docx2txtLoader, PyPDFLoader, BSHTMLLoader
from langchain.schema import Document

from app.core.config import logger
from app.helper.url_loader import URLLoader
from app.schemas.loader import BaseLoader

from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from bs4 import BeautifulSoup as Soup

def load_file(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to load any type of document from a local filesystem or remote location
    :param document: url of the document
    :return: List of documents
    """
    content = []
    try:
        file_extension = os.path.splitext(document.url)[1]
        # load the file using the appropriate loader
        if file_extension is not None:
            if file_extension == ".pdf":
                loader = PyPDFLoader(document.url)
                content = loader.load()
            elif file_extension == ".docx" or file_extension == ".doc":
                loader = Docx2txtLoader(document.url)
                content = loader.load()
            elif file_extension == ".json":
                temp_loader = URLLoader(document.url)
                loader = JSONLoader(file_path=temp_loader.get_file_path(), jq_schema='.', text_content=False)
                content = loader.load()
                # delete the temporary file
                temp_loader.del_file()
            elif file_extension == ".csv":
                temp_loader = URLLoader(document.url)
                loader = CSVLoader(file_path=temp_loader.get_file_path())
                content = loader.load()
                # delete the temporary file
                temp_loader.del_file()
            elif file_extension == ".txt":
                temp_loader = URLLoader(document.url)
                content = TextLoader(file_path=temp_loader.get_file_path())
                content = content.load()
                # delete the temporary file
                temp_loader.del_file()
            elif file_extension == ".html":
                temp_loader = URLLoader(document.url)
                content = BSHTMLLoader(file_path=temp_loader.get_file_path())
                content = content.load()
                # delete the temporary file
                temp_loader.del_file()
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        return [], str(e)
    return content, ""


def fetch_contents_from_api_endpoint(document: BaseLoader):
    temp_loader = URLLoader(document.url)
    loader = JSONLoader(file_path=temp_loader.get_file_path(), jq_schema='.', text_content=False)
    content = loader.load()
    # delete the temporary file
    temp_loader.del_file()
    return content

def web_crawl(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to crawl a website url provided
    :param document: url of website to crawl
    :return:  List of documents
    """  
    #print(document) 
    loader = RecursiveUrlLoader(url=document.url, max_depth=2, extractor=lambda x: Soup(x, "html.parser").text)
    docs = loader.load()

    print(docs)

    return docs, ""
