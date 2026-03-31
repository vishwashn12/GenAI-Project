"""
LangGraph graph compilation — exact replica of Phase 3 Cell 17.
Builds and compiles the StateGraph with conditional edges.
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import (
    build_agent_node,
    build_tools_node,
    extract_metadata_node,
    should_continue,
    after_tools,
)


def compile_agent(llm_with_tools):
    """Build and compile the full LangGraph agent."""

    agent_node = build_agent_node(llm_with_tools)
    tools_node = build_tools_node()

    # ── Build graph ───────────────────────────────────────────
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node('extract_metadata', extract_metadata_node)
    workflow.add_node('agent', agent_node)
    workflow.add_node('tools', tools_node)

    # Entry point
    workflow.set_entry_point('extract_metadata')

    # Static edges
    workflow.add_edge('extract_metadata', 'agent')

    # Conditional edges — routing logic
    workflow.add_conditional_edges(
        'agent',
        should_continue,
        {
            'tools': 'tools',
            'end': END,
        },
    )

    workflow.add_conditional_edges(
        'tools',
        after_tools,
        {
            'agent': 'agent',
            'end': END,
        },
    )

    # Compile
    agent_app = workflow.compile()
    print("✓ LangGraph agent compiled")
    return agent_app
