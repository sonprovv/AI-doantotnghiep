from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
import json
import os
from dotenv import load_dotenv

load_dotenv()

from src.info.InfoController import InfoController
from src.job.JobController import JobController
from src.policy.PolicyController import PolicyController

# Define state structure
class AgentState(TypedDict):
    query: str
    reference: dict
    topic: str
    result: str

class AragController:
    
    def __init__(self, infoController, jobController):

        self.llmModel = "models/gemini-2.5-flash"
        self.llm = ChatGoogleGenerativeAI(model=self.llmModel, temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"))

        self.infoController = InfoController()
        self.jobController = JobController()
        self.policyController = PolicyController()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

    def _build_workflow(self):
        """Build StateGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_topic", self._classify_topic)
        workflow.add_node("policy_search", self._policy_search)
        workflow.add_node("info_search", self._info_search)
        workflow.add_node("job_search", self._job_search)
        
        # Add edges
        workflow.set_entry_point("classify_topic")
        
        # Conditional routing from classify_topic
        workflow.add_conditional_edges(
            "classify_topic",
            self._route_by_topic,
            {
                "policy": "policy_search",
                "info": "info_search",
                "job": "job_search"
            }
        )
        
        # End edges
        workflow.add_edge("policy_search", END)
        workflow.add_edge("info_search", END)
        workflow.add_edge("job_search", END)
        
        return workflow

    def _classify_topic(self, state: AgentState) -> AgentState:
        """Node: Phân loại chủ đề của câu hỏi"""
        query = state["query"]
        
        print("============================================================")
        print(f"[Classify] Query: {query}")
        
        # Prompt-based classification using LLM
        prompt = f"""
            Phân loại câu hỏi sau vào MỘT trong ba nhóm: job, info, policy

            NHÓM 1 - job (TÌM công việc CỤ THỂ để ứng tuyển):
            - Tìm công việc dọn dẹp
            - Công việc gần tôi nhất
            - Công việc phù hợp chuyên môn của tôi
            - Công việc giá/lương cao nhất

            NHÓM 2 - info (MÔ TẢ cách làm dịch vụ):
            - Trông trẻ/chăm sóc người già/người khuyết tật cần làm gì
            - Dọn phòng/vệ sinh như thế nào
            - Giá dịch vụ bao nhiêu

            NHÓM 3 - policy (Thông tin CHUNG về ứng dụng):
            - Ứng dụng do ai làm, tính năng
            - Có những LOẠI/DANH MỤC công việc nào (hỏi về danh sách loại)
            - Liên hệ, email, chính sách

            Câu hỏi: "{query}"

            CHỈ TRẢ LỜI MỘT TỪ DUY NHẤT (job hoặc info hoặc policy), KHÔNG GIẢI THÍCH:
            """
        
        response = self.llm.invoke(prompt)
        topic = response.content.strip().lower()
        
        # Extract first word if LLM returns multiple words
        if " " in topic or "\n" in topic:
            topic = topic.split()[0].strip()
        
        # Validate response
        if topic not in ["policy", "info", "job"]:
            topic = "policy"  # fallback
            print(f"[Classify] Topic: POLICY (fallback - invalid LLM response: {response.content})")
        else:
            print(f"[Classify] Topic: {topic.upper()} (by LLM)")
        
        state["topic"] = topic
        return state

    def _route_by_topic(self, state: AgentState) -> Literal["policy", "info", "job"]:
        """Routing function based on classified topic"""
        return state["topic"]

    def _policy_search(self, state: AgentState) -> AgentState:
        """Node: Tìm kiếm thông tin chính sách ứng dụng"""
        print("[Policy Search] Processing...")
        result = self.policyController.answer(state["query"], state["reference"])
        state["result"] = result
        return state

    def _info_search(self, state: AgentState) -> AgentState:
        """Node: Tìm kiếm thông tin dịch vụ (cleaning, healthcare)"""
        print("[Info Search] Processing...")
        result = self.infoController.answer(state["query"], state["reference"])
        state["result"] = result
        return state

    def _job_search(self, state: AgentState) -> AgentState:
        """Node: Tìm kiếm công việc"""
        print("[Job Search] Processing...")
        result = self.jobController.search(state["query"], state["reference"])
        state["result"] = result
        return state

    def agent_search(self, query, reference):
        """Main entry point - executes the workflow"""
        initial_state = {
            "query": query,
            "reference": reference,
            "topic": "",
            "result": ""
        }
        
        # Run the workflow
        final_state = self.app.invoke(initial_state)
        
        return final_state["result"]


