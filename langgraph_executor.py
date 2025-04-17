
from langgraph.graph import StateGraph
from typing import TypedDict

from nodes import (
    analysis_node,
    setup_node,
    coding_node,
    iteration_node,
    deployment_node,
    documentation_node,
    logging_node,
)


class MyState(TypedDict):
    input: str
    output: str
    analysis: str
    setup: str
    coding: str
    iteration: str
    deployment: str
    documentation: str

def run_langgraph_workflow(processed_data):
    graph = StateGraph(state_schema=MyState)

    graph.add_node("analysis_node", analysis_node)
    graph.add_node("setup_node", setup_node)
    graph.add_node("coding_node", coding_node)
    graph.add_node("iteration_node", iteration_node)
    graph.add_node("deployment_node", deployment_node)
    graph.add_node("documentation_node", documentation_node)
    graph.add_node("logging_node", logging_node)

    graph.set_entry_point("analysis_node")

    graph.add_edge("analysis_node", "setup_node")
    graph.add_edge("setup_node", "coding_node")
    graph.add_edge("coding_node", "iteration_node")
    graph.add_edge("iteration_node", "deployment_node")
    graph.add_edge("deployment_node", "documentation_node")
    graph.add_edge("documentation_node", "logging_node")

    graph.set_finish_point("logging_node")

    # result = graph.run(initial_input=processed_data)
    compiled_graph = graph.compile()
    result = compiled_graph.invoke(processed_data)
    # print(result)
    print(121)
    return result
