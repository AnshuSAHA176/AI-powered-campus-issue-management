from rest_framework.views import APIView
from rest_framework.response import Response
from .agnets import get_agent
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from langchain.messages import HumanMessage

class AgentView(APIView):
    permission_classes=[AllowAny]
    # authentication_classes=[JWTAuthentication]
    def post(self,request):
        agent = get_agent()
        user_message=request.data['message']
        
        message=agent.invoke({"messages":[HumanMessage(content=user_message)]})
        return Response({"status":message["messages"][-1].content})