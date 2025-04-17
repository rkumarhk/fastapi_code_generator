
from langgraph.graph import StateGraph
from typing import TypedDict

from components.nodes2 import (
    end_point,
    buisness_logic,
    db_schema,
    auth,
)


class MyState(TypedDict):
    input: str
    output: str
    end_point: str
    buisness_logic: str
    db_schema: str
    auth: str

def run_langgraph_workflow(processed_data):
    graph = StateGraph(state_schema=MyState)

    graph.add_node("ep_node", end_point)
    graph.add_node("bl_node", buisness_logic)
    graph.add_node("db_node", db_schema)
    graph.add_node("auth_node", auth)

    graph.set_entry_point("ep_node")

    graph.add_edge("ep_node", "bl_node")
    graph.add_edge("bl_node", "db_node")
    graph.add_edge("db_node", "auth_node")

    graph.set_finish_point("auth_node")

    # result = graph.run(initial_input=processed_data)
    compiled_graph = graph.compile()
    result = compiled_graph.invoke(processed_data)
    return result
