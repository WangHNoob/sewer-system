from langgraph.graph import StateGraph
from langgraph.constants import END
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    BaseMessage,
)
from typing import TypedDict, Annotated, Sequence
import operator
import os


class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    session_id: str
    detection_cache: dict
    uploaded_image_path: str


class ChatEngine:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.image_path = None
        self.detection_cache = {}
        self.graph = self._build_graph()

    def _build_graph(self):
        from services.tools import get_all_tools
        from services.prompts import SYSTEM_PROMPT
        from services.llm_provider import LLMProvider

        llm = LLMProvider().get_langchain_llm()
        tools = get_all_tools()
        tool_map = {t.name: t for t in tools}
        llm_with_tools = llm.bind_tools([t.get_schema() for t in tools])

        def model_reasoning(state: ChatState) -> dict:
            messages = list(state["messages"])
            if not any(isinstance(m, SystemMessage) for m in messages):
                messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        def tool_execution(state: ChatState) -> dict:
            last = state["messages"][-1]
            tool_messages = []
            for tc in last.tool_calls:
                tool = tool_map.get(tc["name"])
                try:
                    validation = (
                        tool.validate_params(tc["args"])
                        if tool
                        else {"valid": False, "error": f"Unknown tool: {tc['name']}"}
                    )
                    if not validation["valid"]:
                        result = f"参数校验失败：{validation['error']}。请修正参数后重试。"
                    else:
                        result = tool.execute(**tc["args"])
                except Exception as e:
                    result = f"工具执行异常：{str(e)}"
                tool_messages.append(
                    ToolMessage(content=str(result), tool_call_id=tc["id"])
                )
            return {"messages": tool_messages}

        def should_continue(state: ChatState) -> str:
            last = state["messages"][-1]
            if hasattr(last, "tool_calls") and last.tool_calls:
                return "call_tool"
            return "finish"

        graph = StateGraph(ChatState)
        graph.add_node("model_reasoning", model_reasoning)
        graph.add_node("tool_execution", tool_execution)
        graph.set_entry_point("model_reasoning")
        graph.add_conditional_edges(
            "model_reasoning",
            should_continue,
            {"call_tool": "tool_execution", "finish": END},
        )
        graph.add_edge("tool_execution", "model_reasoning")

        return graph.compile()

    async def handle_text_message(self, text: str):
        initial_state = {
            "messages": [HumanMessage(content=text)],
            "session_id": self.session_id,
            "detection_cache": self.detection_cache,
            "uploaded_image_path": self.image_path,
        }

        async for event in self.graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                if node_name == "model_reasoning":
                    msg = node_output["messages"][-1]
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            yield {
                                "type": "tool_call",
                                "data": {"tool": tc["name"], "args": tc["args"]},
                            }
                    else:
                        yield {"type": "token", "data": msg.content}
                elif node_name == "tool_execution":
                    for msg in node_output["messages"]:
                        yield {"type": "tool_result", "data": msg.content[:500]}

    async def handle_image_message(self, image_bytes: bytes, text: str):
        from services.detector import PipelineDefectDetector
        from services.prior_converter import StructuredPriorConverter

        tmp_path = os.path.join("uploads", f"{self.session_id}.jpg")
        os.makedirs("uploads", exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(image_bytes)
        self.image_path = tmp_path

        detector = PipelineDefectDetector(model_path="models/detector/best.pt")
        detection_result = detector.detect_from_bytes(image_bytes)
        self.detection_cache = detection_result

        converter = StructuredPriorConverter()
        prior_text = converter.convert(detection_result)

        full_message = f"{text}\n\n## 检测先验信息\n{prior_text}"

        initial_state = {
            "messages": [HumanMessage(content=full_message)],
            "session_id": self.session_id,
            "detection_cache": detection_result,
            "uploaded_image_path": tmp_path,
        }

        yield {"type": "detection_result", "data": detection_result}

        async for event in self.graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                if node_name == "model_reasoning":
                    msg = node_output["messages"][-1]
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            yield {
                                "type": "tool_call",
                                "data": {"tool": tc["name"], "args": tc["args"]},
                            }
                    else:
                        yield {"type": "token", "data": msg.content}

    def run_detection_only(self, image_bytes: bytes) -> dict:
        from services.detector import PipelineDefectDetector

        detector = PipelineDefectDetector(model_path="models/detector/best.pt")
        return detector.detect_from_bytes(image_bytes)
