from langchain.tools import tool
from .service import Services


def agent_tool(access_token):

     services = Services(
        url="http://127.0.0.1:8000/",
        token=access_token
    )

     @tool
     def list_my_complaints():
          """
          List all complaints submitted by the authenticated student.

          Use this only when the user wants to see their collection
          of complaints.

          Do not use this when the user provides a specific complaint ID.
          """
          print("list_my_complaints")
          return services.complain_list()


     @tool
     def get_complaint_details(complaint_id: str):
          """
          Retrieve information about one specific complaint.

          Use this when the user provides a complaint ID such as
          CMP-2026-000068 and asks about that complaint.

          This includes questions about its status, category, priority,
          location, assigned officer, description, resolution, or
          any other information about that specific complaint.

          If a complaint ID is present, use this tool instead of
          list_my_complaints.

          Args:
               complaint_id: Exact complaint ID, e.g. CMP-2026-000068.
          """
          print("get_complaint_details")
          return services.compliant_details(complaint_id)


     return list_my_complaints, get_complaint_details