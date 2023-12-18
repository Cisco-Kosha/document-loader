import os
from typing import List

from langchain.document_loaders import TextLoader, CSVLoader, JSONLoader, Docx2txtLoader, PyPDFLoader, BSHTMLLoader
from langchain.schema import Document

from app.core.config import logger
from app.helper.url_loader import URLLoader
from app.schemas.loader import BaseLoader

from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader
from bs4 import BeautifulSoup as Soup
from fake_useragent import UserAgent

from langchain.document_loaders import AsyncHtmlLoader

from langchain.document_loaders import AsyncChromiumLoader

from llama_index import download_loader

import requests
from bs4 import BeautifulSoup
import pandas

from urllib.parse import urljoin, urlparse

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


def web_crawl_MediumUrlLoader(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to crawl a single medium article per url provided
    :param document: url of medium article to crawl
    :return:  List of documents and metadata related to the medium article url input
    """  

    # The below uses 
    # 1. BeautifulSoup to parse the metadata from the medium article url. 
    # (other frameworks like scrapy work as well for more advanced usecases)
    # 2. RecursiveUrlLoader to parse the page_content for the medium article url. 
    # (can use vanilla Beautiful Soup or another Loader type as well)
    # 3. How to combine metadata obtained from the 2 methods as required.
    
    response = requests.get(document.url)

    post = {}
    response = requests.get(document.url)
    article = BeautifulSoup(response.content, 'html.parser')
    #title
    if article.find('h1',attrs={'class':'a8db'}):
        h1 = article.find('h1',attrs={'class':'a8db'})
    else:
        h1 = article.find('h1')
    article_title = h1.text
 
    post = {
    'title':article_title,
    'link':document.url
    }

    print("Additional metadata :", post)
    loader = RecursiveUrlLoader(url=document.url, max_depth=2, extractor=lambda x: Soup(x, "html.parser").text)
    docs = loader.load()

    # if we want to combine metadata obtained by Beautiful soup parsing + obtained from loader, that can be done here
    # Additional metadata can be added to the metadata field of langchain document
    # The merge it with the docs to return
    # https://js.langchain.com/docs/modules/data_connection/document_loaders/how_to/creating_documents
    
    #print(docs)

    return docs, ""
    

def web_crawl_MediumPubUrlLoader(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to crawl a medium publication url provided
    :param document: url of medium publication to crawl
    :return:  List of documents and metadata related to each document in the publication
    """  

    # todo - get all articles under a publication
    # currently limited articles are returned, when input publication url as https://medium.com/cisco-fpie
    # Medium Apis do not offer functionality to get all articles under a publication
    # https://github.com/Medium/medium-api-docs#32-publications
    # Alternative use inputs that can be considered - publication archives for medium archive url ?

    # This example demonstrates - How to get specific metadata about medium article (that is not provided by other default loaders), 
    # The medium article can be scraped to get that metadata + merge with metadata provided by the Langchain Loaders as required.
 
    response = requests.get(document.url)
    content = BeautifulSoup(response.content, 'html.parser')
    container = content.find('div', attrs={'class':'js-collectionStream'})
    a = container.findAll('a')

    links = []
    for link in a:
        link = link['href']
        links.append(link)
    
    cleaned_links = []

    # scrape link metadata only for required medium pub (Eg. medium.com/cisco-fpie if input url=https://medium.com/cisco-fpie)
    url_pub_path = document.url.split('/')[2] + "/" + document.url.split('/')[3]
    for link in links:
        if url_pub_path in link:
            cleaned_links.append(link)
    cleaned_links = list(dict.fromkeys(cleaned_links))

    print(cleaned_links)

    archive = []
    docs = [] #List[Document]

    for article_link in cleaned_links:
        post = {}
        response = requests.get(article_link)
        article = BeautifulSoup(response.content, 'html.parser')
        #title
        if article.find('h1',attrs={'class':'a8db'}):
                h1 = article.find('h1',attrs={'class':'a8db'})
        else:
                h1 = article.find('h1')
        article_title = h1.text
        #subtitle
        #if article.find('h2', attrs={'class':'3dfe'}):
        #               h2 = article.find('h2', attrs={'class':'3dfe'})
        #else:
        #       subh = article.findAll('h2')
        #               h2 = subh[1]
        #article_subtitle=h2.text
        #img
        '''
        #fig = article.find('figure')
        #print(fig)
        '''
        #img = article.find('img',attrs={'class':'s'})
        #article_img = img['src']
        post = {
        'title':article_title,
        #'subtitle':article_subtitle,
        #'img': article_img,
        'link':article_link
        }
        archive.append(post)

        url_path_noquery = article_link.split('?')[0]
        print(url_path_noquery)

        # use any appropriate/chosen loader/ vanilla beautiful soup to extract contents of each article wihin the provided medium publication
        loader = RecursiveUrlLoader(url=article_link, max_depth=2, extractor=lambda x: Soup(x, "html.parser").text)
        docs_for_link = loader.load()
        print(docs_for_link)

        # todo
        # if we want to combine metadata obtained by Beautiful soup parsing + obtained from loader, that can be done here
        # Additional metadata can be added to the metadata field of langchain document
        # The merge it with the docs to return
        # https://js.langchain.com/docs/modules/data_connection/document_loaders/how_to/creating_documents
        docs.extend(docs_for_link)

    print("********************************************************************************************")
    print(docs)

    return docs, ""

def web_crawl_RecursiveUrlLoader(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to crawl a website url provided
    :param document: url of website to crawl
    :return:  List of documents
    """  

    #https://github.com/langchain-ai/langchain/issues/11540 -> 403 errors for website
    header_template = {}
    header_template["User-Agent"] = UserAgent().random

    loader = RecursiveUrlLoader(url=document.url, max_depth=2, extractor=lambda x: Soup(x, "html.parser").text)
    docs = loader.load()

    print(docs)

    return docs, ""

def web_crawl_AsyncHtmlLoader(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to crawl a website url provided
    :param document: url of website to crawl
    :return:  List of documents
    """  
    urls = []
    urls.append(document.url)
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()

    print(docs)

    return docs, ""

def web_crawl_AsyncChromiumLoader(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to crawl a website url provided
    :param document: url of website to crawl
    :return:  List of documents
    """  
    urls = []
    urls.append(document.url) 
    loader = AsyncChromiumLoader(urls)
    docs = loader.load()

    #print(docs)
    #print(docs[0].page_content[0:])

    return docs, ""

def web_crawl_SimpleWebPageLoader(document: BaseLoader) -> (List[Document], str):
    """
         This endpoint is used to crawl a website url provided
    :param document: url of website to crawl
    :return:  List of documents
    """  
    urls = []
    urls.append(document.url)
 
    SimpleWebPageReader = download_loader("SimpleWebPageReader")
    loader = SimpleWebPageReader()
    docs = loader.load_data(urls)

    print(docs)

    return docs, ""
