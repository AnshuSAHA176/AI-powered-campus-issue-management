from langchain.tools import tool
from .service import Services




def agent_tool(access_token):
    

    services=Services(url='http://127.0.0.1:8000/',token=access_token)


    @tool
    def complain_list():
         """
    Return complaints created by the current student.
    
        Optionally filter complaints by status.
        Valid statuses include:
        pending, assigned, accepted, inspection,
        in_progress, resolved, closed, rejected, reopened.
        """
         return services.complain_list()

    return complain_list