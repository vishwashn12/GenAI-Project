"""
AgentState TypedDict — shared memory that flows through every graph node.
Exact replica of Phase 3 Cell 14.
"""
from __future__ import annotations

import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    # Conversation history — accumulates across turns
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # Extracted from query if present
    order_id: str
    # Classified intent for routing decisions
    intent: str
    # Number of tool calls made this turn (prevents infinite loops)
    tool_call_count: int
    # Flag set by escalation tool
    escalated: bool
    # Final answer accumulated
    final_answer: str
