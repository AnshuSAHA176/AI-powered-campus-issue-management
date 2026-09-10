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

def get_agent(access_token):

    model = get_model()

    class Agent_State(TypedDict):
        messages: Annotated[list, add_messages]

    # Create tool
    complaint_list = agent_tool(
        access_token=access_token
    )

    # Bind tool to LLM
    model_with_tool = model.bind_tools(
        [complaint_list]
    )

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



    def domain(state:Agent_State):
        ...




    graph_builder.add_node(
        "agent",
        agent
    )

    # Tool node
    graph_builder.add_node(
        "tools",
        ToolNode([complaint_list])
    )

    # START → agent
    graph_builder.add_edge(
        START,
        "agent"
    )

    # agent → tools OR END
    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )

    # tools → agent
    graph_builder.add_edge(
        "tools",
        "agent"
    )
    

    return graph_builder.compile()