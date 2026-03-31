"""
LangGraph graph node definitions — exact replica of Phase 3 Cells 15-16.
"""
from __future__ import annotations

import re

from langchain_core.messages import SystemMessage

from agent.state import AgentState
from agent.tools import TOOLS
from rag.intent import classify_intent


SYSTEM_PROMPT = '''You are an expert Olist e-commerce customer support agent.
You have access to tools to look up orders, search knowledge base, and analyse sellers.

DECISION FRAMEWORK:
1. If the customer mentions an order ID → call order_lookup FIRST
2. If the question involves policy/refunds/returns → call rag_search
3. If seller is mentioned → call seller_analysis
4. If you have all information needed → generate final response WITHOUT tool calls
5. If issue cannot be resolved after 2 tool calls → call escalate_to_human

Always be empathetic, cite your sources, and give a concrete next step.'''


def build_agent_node(llm_with_tools):
    """Create the agent_node closure with the bound LLM."""

    def agent_node(state: AgentState) -> dict:
        """Main reasoning node — decides what tools to call or generates
        final answer."""
        messages = ([SystemMessage(content=SYSTEM_PROMPT)]
                    + list(state['messages']))
        response = llm_with_tools.invoke(messages)
        return {
            'messages': [response],
            'tool_call_count': state.get('tool_call_count', 0),
        }

    return agent_node


def extract_metadata_node(state: AgentState) -> dict:
    """Extract order ID and intent from the latest user message."""
    last_msg = (state['messages'][-1].content
                if state['messages'] else '')

    # Extract order ID (simple regex — works for Olist UUID-like IDs)
    order_match = re.search(r'\b([a-f0-9]{32})\b', last_msg)
    order_id = order_match.group(1) if order_match else ''

    intent = classify_intent(last_msg).value

    return {'order_id': order_id, 'intent': intent}


def build_tools_node():
    """Create the tools execution node."""
    from langgraph.prebuilt import ToolNode

    tool_executor = ToolNode(TOOLS)

    def tools_node(state: AgentState) -> dict:
        """Execute tool calls, increment counter, check escalation."""
        result = tool_executor.invoke(state)
        count = state.get('tool_call_count', 0) + 1
        # Check if escalation was triggered
        last_msg = result.get('messages', [{}])[-1]
        escalated = 'ESCALATED' in str(getattr(last_msg, 'content', ''))
        return {**result, 'tool_call_count': count, 'escalated': escalated}

    return tools_node


# ── Routing functions (conditional edges) ─────────────────────


def should_continue(state: AgentState) -> str:
    """
    After the agent node, decide:
    - 'tools'    → agent wants to call a tool
    - 'end'      → agent is done, return answer
    """
    last_msg = state['messages'][-1]
    count = state.get('tool_call_count', 0)

    # Guard: max 3 tool calls per query to prevent infinite loops
    if count >= 3:
        return 'end'

    # If escalated, stop
    if state.get('escalated', False):
        return 'end'

    # Check if the LLM made tool calls
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return 'tools'

    return 'end'


def after_tools(state: AgentState) -> str:
    """After tools execute, always return to agent for synthesis."""
    if state.get('escalated', False):
        return 'end'
    return 'agent'
