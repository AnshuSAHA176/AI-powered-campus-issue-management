from langgraph.graph import StateGraph,START,END,add_messages
from typing import TypedDict,Annotated,Literal
from .llm import get_model

def get_agent():
    model = get_model()
    
    class Agent_State(TypedDict):
        messages : Annotated[list,add_messages]





    grape_builder=StateGraph(Agent_State)

    def chat_agent(state:Agent_State):
        responce = model.invoke(state['messages'])
        return {
            'messages':[responce]
        }

    grape_builder.add_node('agnet',chat_agent)
    grape_builder.add_edge(START,'agnet')
    grape_builder.add_edge('agnet',END)
    return  grape_builder.compile()