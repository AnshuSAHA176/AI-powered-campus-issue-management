from langchain.tools import tool
from .service import Services

aut_token=''

services=Services(url='http://127.0.0.1:8000/',token=aut_token)


@tool
def complain_list():
    '''Return all the complaints create by the student'''
    return services.complain_list()

