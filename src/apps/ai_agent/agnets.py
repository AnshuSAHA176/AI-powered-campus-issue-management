from langgraph.graph import (
    StateGraph,
    START,
    END,
    add_messages,
)

from langgraph.prebuilt import ToolNode, tools_condition

from typing import TypedDict, Annotated

from .llm import get_model
from .tools import agent_tool
from langgraph.checkpoint.memory import InMemorySaver
from .domain import domain
from langchain.messages import AIMessage


cheakpointer=InMemorySaver()

def get_agent(access_token):

    model = get_model()

    class Agent_State(TypedDict):
        messages: Annotated[list, add_messages]
        domain : str

    # Create tool
    (list_my_complaints, get_complaint_details) = agent_tool(
    access_token=access_token
)

    tools = [list_my_complaints, get_complaint_details]

    model_with_tool = model.bind_tools(tools)

    # Graph
    graph_builder = StateGraph(Agent_State)
   
    # Agent node
    def agent(state: Agent_State):

        response = model_with_tool.invoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }



    def domain_classifyer(state:Agent_State):

        human_messages=[
            message
            for message in state['messages']
            if message.type == 'human'
        ]
        recent_human_messages = human_messages[-3:]

        conversation = "\n".join(
            message.content
            for message in recent_human_messages
        )
        result= domain(conversation)
        print(result)
        return {"domain":result}

    def domain_router(state:Agent_State):
        domain=state['domain']
        if domain=='campus':
            return 'campus'
        return "reject"

    
    def reject_off_topic(state: Agent_State):

        return {
            "messages": [
                AIMessage(
                    content=(
                        "I'm here to help with Campus Problems. "
                        
                    )
                )
            ]
        }





    graph_builder.add_node("domain_guard", domain_classifyer)
    graph_builder.add_node("agent", agent)
    graph_builder.add_node("reject", reject_off_topic)
    graph_builder.add_node("tools", ToolNode(tools))

    graph_builder.add_edge(START, "domain_guard")

    graph_builder.add_conditional_edges(
        "domain_guard",
        domain_router,
        {
            "campus": "agent",
            "reject": "reject",
        }
    )

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )


    graph_builder.add_edge("tools", "agent")
    graph_builder.add_edge("reject", END)
        

    return graph_builder.compile(checkpointer=cheakpointer)