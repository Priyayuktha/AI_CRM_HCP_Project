from langgraph.graph import StateGraph, END

from app.langgraph.state import AgentState

from app.langgraph.nodes import (
    extract_node,
    decide_tool,
    execute_tool,
)

from app.langgraph.response_node import response_node


workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("extract", extract_node)
workflow.add_node("decide", decide_tool)
workflow.add_node("execute", execute_tool)
workflow.add_node("response", response_node)

# Entry Point
workflow.set_entry_point("extract")

# Edges
workflow.add_edge("extract", "decide")
workflow.add_edge("decide", "execute")
workflow.add_edge("execute", "response")
workflow.add_edge("response", END)

# Finish Point
workflow.set_finish_point("response")

# Compile Graph
graph = workflow.compile()