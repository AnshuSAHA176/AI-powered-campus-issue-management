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
     @tool
     def get_similar_complaints(complaint_id: str):
          """
          Find complaints that are semantically similar to the specified complaint.

          Use this tool when the user asks to:
          - find similar complaints
          - find duplicate complaints
          - check for duplicate or related complaints
          - see complaints similar to a specific complaint

          The result already contains all information needed to present the
          similar complaints:
          - complaint_id
          - complaint_title
          - similarity_score

          IMPORTANT:
          After using this tool, do NOT call get_complaint_details for the
          returned complaints unless the user explicitly asks for the details
          of a specific returned complaint.

          Args:
               complaint_id: The ID of the complaint for which similar complaints
                    should be found.

          Returns:
               A list of similar complaints containing only their complaint ID,
               title, and similarity score.
          """
          print("similar complaints")
          return services.get_similar_complaints(complaint_id)

     return list_my_complaints, get_complaint_details,get_similar_complaints