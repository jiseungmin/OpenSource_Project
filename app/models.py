from typing import Union
from pydantic import BaseModel

class ClustertRequest(BaseModel):
    collection_name : str
    date_str : str

class IntegretionNews(BaseModel):
    category : str 
