import os
import requests
import json
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

class PineconeService:
    
    def __init__(self):

        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.PINECONE_HOST = os.getenv("PINECONE_HOST")

        # Debug: In ra giá trị để kiểm tra
        print(f"[DEBUG] PINECONE_API_KEY: {self.PINECONE_API_KEY[:10]}..." if self.PINECONE_API_KEY else "[DEBUG] PINECONE_API_KEY: None")
        print(f"[DEBUG] PINECONE_HOST (raw): '{self.PINECONE_HOST}'")

        # Loại bỏ https:// nếu có trong host và strip khoảng trắng
        if self.PINECONE_HOST:
            self.PINECONE_HOST = self.PINECONE_HOST.strip()
            if self.PINECONE_HOST.startswith("https://"):
                self.PINECONE_HOST = self.PINECONE_HOST.replace("https://", "")
            if self.PINECONE_HOST.startswith("http://"):
                self.PINECONE_HOST = self.PINECONE_HOST.replace("http://", "")
        
        print(f"[DEBUG] PINECONE_HOST (cleaned): '{self.PINECONE_HOST}'")
        
        self.pc = Pinecone(api_key=self.PINECONE_API_KEY)
        self.index = self.pc.Index(name="demo-pinecone", host=self.PINECONE_HOST)

        self.namespace = "jobs-area"

    # --------------------------------------------------------------

    def pinecone_upsert_all_datas(self, datas):
        self.index.upsert_records(
            self.namespace,
            datas
        ) 

    # --------------------------------------------------------------

    def pinecone_upsert_one_data(self, job, embed, context):

        self.index.upsert(
            namespace=self.namespace,
            vectors=[
                {
                    "id": job['uid'],
                    "values": embed,
                    "metadata": {
                        "jobID": job['uid'],
                        "userID": job['user']['uid'],
                        "price": job['price'],
                        "startTime": job['startTime'],
                        "listDays": job['listDays'],
                        "serviceType": job['serviceType'],
                        "location": job['location'],
                        "createdAt": job['createdAt'],
                        "context": context,
                        "lat": job['lat'],
                        "lon": job['lon']
                    }
                }
            ]
        )
        return True

    # --------------------------------------------------------------

    def pinecone_search_data(self, embed, query):

        cleaning = [
            "dọn dẹp vệ sinh",
            "vệ sinh",
            "dọn dẹp",
            "lau dọn"
        ]

        healthcare = [
            "chăm sóc sức khỏe",
            "chăm sóc",
            "trông nom",
        ]

        maintenance = [
            "bảo trì thiết bị",
            "bảo trì",
            "bảo dưỡng",
            "sửa chữa",
            "sửa"
        ]

        try:

            def getServiceTypeFilter():
                serviceTypeFilter = "CLEANING" if any(map(lambda i: i.lower() in query.lower(), cleaning)) else None
                
                if not serviceTypeFilter: 
                    serviceTypeFilter = "HEALTHCARE" if any(map(lambda i: i.lower() in query.lower(), healthcare)) else None
                
                if not serviceTypeFilter: 
                    serviceTypeFilter = "MAINTENANCE" if any(map(lambda i: i.lower() in query.lower(), maintenance)) else None

                return serviceTypeFilter

            # -------------------------------------------------------------------------------------------

            pineconeFilter = {}

            serviceTypeFilter = getServiceTypeFilter()

            # Search ------------------------------------------------------------------------------------

            if serviceTypeFilter:
                pineconeFilter["serviceType"] = { "$eq": serviceTypeFilter }

            result = self.index.query(
                namespace = self.namespace,
                vector=embed,
                top_k=5,
                include_metadata=True,
                include_values=False,
                filter=pineconeFilter
            )

            data = []
            for match in result['matches']:
                item = match["metadata"]
                item["similarity_score"] = match.get("score", None)
                data.append(item)

            if len(data)==0:
                return {
                    "success": False,
                    "error": "Không tìm thấy công việc phù hợp"
                }

            return {
                "success": True,
                "message": "Thành công",
                "type": "Job",
                "data": data
            }
        except Exception as e:
            print(f"Lỗi tìm kiếm: {e}")
            return {
                "success": False,
                "error": "Không tìm thấy công việc phù hợp"
            }

    # --------------------------------------------------------------

    def pinecone_delete(self, jobID):
        try: 
            self.index.delete(ids=[jobID], namespace=self.namespace)

            return {
                "success": True,
                "message": "Thành công"
            }
        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": "Xoá embed không thành công"
            }

    # --------------------------------------------------------------

    def pinecone_update_metadata_status(self, jobID, status):
        
        try:
            url = f"{self.PINECONE_HOST}/vectors/update"

            headers = {
                "Api-Key": self.PINECONE_API_KEY,
                "Content-Type": "application/json",
                "X-Pinecone-API-Version": "unstable"
            }

            data = {
                "dry_run": False,
                "namespace": self.namespace,
                "filter": {
                    "jobID": {"$eq": f"{jobID}"}
                },
                "setMetadata": {
                    "status": f"{status}"
                }
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(response.json())
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"Lỗi cập nhật metadata Pinecone: {e}")
            return False
    
    # --------------------------------------------------------------

    def pinecone_update_metadata_location(self, jobID, location):
        
        try:
            url = f"{self.PINECONE_HOST}/vectors/update"

            headers = {
                "Api-Key": self.PINECONE_API_KEY,
                "Content-Type": "application/json",
                "X-Pinecone-API-Version": "unstable"
            }

            data = {
                "dry_run": False,
                "namespace": self.namespace,
                "filter": {
                    "jobID": {"$eq": f"{jobID}"}
                },
                "setMetadata": {
                    "location": f"{location}"
                }
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))
            print(response.json())
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"Lỗi cập nhật metadata Pinecone: {e}")
            return False
    
    # --------------------------------------------------------------