from rest_framework.views import APIView
from rest_framework.response import Response
from .agnets import get_agent
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from langchain.messages import HumanMessage,SystemMessage

class AgentView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self,request):
        config={"configurable": {"thread_id": request.user.id}}
        access=self._get_token(request)
        agent = get_agent(access_token=access)
        user_message=request.data['message']
        
        result = agent.invoke(
            {
    "messages": [
        SystemMessage(
            content="""
                You are CivicAI, an AI assistant for a campus complaint
                management system.

                Formatting rules:
                - Give concise and clear answers.
                - Use Markdown headings when useful.
                - Use bullet points for lists.
                - Use Markdown tables only when comparing multiple complaints.
                - Never use unnecessary explanations.
                - Do not invent information.
                - When showing complaints, include:
                Complaint ID, Title, Status, Priority and Category.
                """
                        ),
                        HumanMessage(content=user_message)
                    ]
                },config=config
                )
                        
        return Response({"status":result["messages"][-1].content})

    
    def _get_token(self, request):
        auth_header = request.headers.get("Authorization", "")
        return auth_header.replace("Bearer ", "")