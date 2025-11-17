from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class InfoService:

    def __init__(self):
        self.modelName = "models/text-embedding-004"
        self.persistDir = "chroma_db"
        self.llmModel = "models/gemini-2.5-flash"

        self.llm = ChatGoogleGenerativeAI(model=self.llmModel, google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.modelName, google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.vs = Chroma(
            persist_directory=self.persistDir,
            embedding_function=self.embeddings
        )


        self.promptTemplate = """
            Bạn là trợ lý AI về ứng dụng GoodJob - ứng dụng dịch vụ việc làm.
            
            QUY TẮC QUAN TRỌNG:
            - Luôn trả lời bằng TIẾNG VIỆT rõ ràng, tự nhiên, ngắn gọn
            - CHỈ sử dụng thông tin từ ngữ cảnh được cung cấp
            - KHÔNG bịa đặt hoặc suy luận thông tin không có trong ngữ cảnh
            - Trả lời trực tiếp, không thêm "Theo tài liệu" hay "Dựa vào ngữ cảnh"
            - Nếu ngữ cảnh không chứa thông tin liên quan, trả lời: "Không có thông tin"
            
            GỢI Ý HIỂU CÂU HỎI:
            - "Ứng dụng do ai làm ra?" / "Ai tạo ra ứng dụng?" → Tìm thông tin về tập đoàn, nhà phát triển, thành viên
            - "Có những loại công việc nào?" → Tìm danh mục dịch vụ
            - "Thông tin liên hệ?" → Tìm email, số điện thoại
            
            Ngữ cảnh từ tài liệu:
            {context}

            Câu hỏi: {question}

            Trả lời:
        """

        self.customPrompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.promptTemplate
        )
    
    # --------------------------------------------------------------

    def searchVectorDB(self, query):
        # Expand query để tăng khả năng tìm thấy context liên quan
        q = query.lower()
        expanded_queries = [query]
        
        # Nếu hỏi về người tạo/làm ứng dụng, thêm query về tập đoàn
        if any(kw in q for kw in ["ai làm ra", "ai tạo ra", "do ai", "người làm", "nhà phát triển"]):
            expanded_queries.extend([
                "thông tin tập đoàn",
                "thành viên",
                "nhà sáng tạo"
            ])
        
        # Search với multiple queries và merge results
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
        
        # Limit to top 5 unique docs
        context = "\n\n".join([d.page_content for d in all_docs[:5]])
        return context
    
    # --------------------------------------------------------------

    def sendToLLM(self, context, question):
        prompt = self.customPrompt.format(context=context, question=question)
        response = self.llm.invoke(prompt)
        return response
    
    # --------------------------------------------------------------
    
    def info_answer(self, query):
        try:
            print(f"Câu hỏi: {query}")
            
            # Regular RAG flow
            context = self.searchVectorDB(query=query)
            answer = self.sendToLLM(context=context, question=query)
            print(f"\nTrả lời:\n\t{answer.content}")
            print("\n=================================================================\n")
            return {
                "success": True,
                "message": "Thành công",
                "type": "Info",
                "data": answer.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Không tìm thấy thông tin"
            }
    
    # --------------------------------------------------------------