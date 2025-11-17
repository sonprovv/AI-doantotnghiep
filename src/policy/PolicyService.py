from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class PolicyService:

    def __init__(self):
        self.modelName = "models/text-embedding-004"
        self.persistDir = "chroma_db_policy"
        self.llmModel = "models/gemini-2.5-flash"

        self.llm = ChatGoogleGenerativeAI(model=self.llmModel, google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.modelName, google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.vs = Chroma(
            persist_directory=self.persistDir,
            embedding_function=self.embeddings
        )

        self.promptTemplate = """
            Bạn là trợ lý AI về ứng dụng GoodJob.
            
            QUY TẮC:
            - Trả lời bằng TIẾNG VIỆT rõ ràng, ngắn gọn
            - CHỈ dùng thông tin từ ngữ cảnh
            - KHÔNG bịa đặt thông tin
            - Trả lời trực tiếp, không thêm "Theo tài liệu"
            - Nếu không có thông tin: "Không có thông tin"
            
            GỢI Ý:
            - "Ứng dụng do ai làm ra?" → Tìm thông tin tập đoàn, thành viên
            - "Có những loại công việc nào?" → Tìm danh mục dịch vụ
            - "Liên hệ?" → Tìm email, số điện thoại
            
            Ngữ cảnh:
            {context}

            Câu hỏi: {question}

            Trả lời:
        """

        self.customPrompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.promptTemplate
        )

    def searchVectorDB(self, query):
        q = query.lower()
        expanded_queries = [query]
        
        if any(kw in q for kw in ["ai làm ra", "ai tạo ra", "do ai", "người làm", "nhà phát triển"]):
            expanded_queries.extend(["thông tin tập đoàn", "thành viên", "nhà sáng tạo"])
        
        all_docs = []
        seen_content = set()
        
        for eq in expanded_queries:
            queryVector = self.embeddings.embed_query(eq)
            docs = self.vs.similarity_search_by_vector(queryVector, k=3)
            for d in docs:
                content = d.page_content
                if content not in seen_content:
                    all_docs.append(d)
                    seen_content.add(content)
        
        context = "\n\n".join([d.page_content for d in all_docs[:5]])
        return context

    def sendToLLM(self, context, question):
        prompt = self.customPrompt.format(context=context, question=question)
        response = self.llm.invoke(prompt)
        return response

    def policy_answer(self, query):
        try:
            print(f"[Policy] Câu hỏi: {query}")
            context = self.searchVectorDB(query=query)
            answer = self.sendToLLM(context=context, question=query)
            print(f"[Policy] Trả lời: {answer.content}")
            print("=================================================================\n")
            return {
                "success": True,
                "message": "Thành công",
                "type": "Policy",
                "data": answer.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Không tìm thấy thông tin"
            }
