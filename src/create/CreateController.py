from src.utils.GeminiService import GeminiService
from src.utils.PineconeService import PineconeService
import json

class CreateController:

    def __init__(self):
        self.geminiService = GeminiService()
        self.pineconeService = PineconeService()

    # --------------------------------------------------------------

    def getTextCleaning(self, text, job): 

        text += f"Công việc kéo dài {job['duration']['workingHour']} giờ."

        other = ""
        if job['isCooking']: other += "Công việc thêm bao gồm: Nấu ăn"
        
        if job['isIroning']:
            if other=="": other += "Công việc thêm bao gồm: Ủi đồ"
            else: other += ", Ủi đồ"
        
        if other!="": text += " " + other + "."

        return text   
    
    # --------------------------------------------------------------

    def getTextHealthcare(self, text, job):

        text += f"Công việc kéo dài {job['shift']['workingHour']} giờ."

        other = "Số lượng chăm sóc: "

        services = job['services']
        for i in range(len(services)):
            other += f"{str(services[i]['quantity'])} {services[i]['serviceName']}"   # VD: 3 người khuyết tật, 2 người lớn tuổi, 5 trẻ em
            
            if i<len(services)-1: other += ', '
        
        text += " " + other + "."
        return text

    # --------------------------------------------------------------

    '''
        Bảo trì bao gồm: 12 Máy giặt, 10 Điều hòa. Thay lồng giặt 3 và bơm gas 4
    '''

    def getTextMaintenance(self, text, job):

        other = "Bảo trì bao gồm: "

        serviceName = []
        maintenanceName = []

        services = job['services']
        for i in range(len(services)):
            powers = services[i]['powers']
            quantity = 0
            quantityAction = 0
            for j in range(len(powers)):
                print(powers[j])
                quantity += powers[j]['quantity']
                quantityAction += powers[j]['quantityAction']
            
            print(services[i])
            serviceName.append(f"{str(quantity)} {services[i]['serviceName']}")
            maintenanceName.append(f"{services[i]['maintenance']} {str(quantityAction)}")

        for i in range(len(serviceName)):
            other += serviceName[i]
            if i<len(serviceName)-1: other += ", "
            else: other += ". "

        other += "Trong đó: "
        for i in range(len(maintenanceName)):
            other += maintenanceName[i]
            if i<len(maintenanceName)-1: other += ", "
            else: other += "."

        text += other
        return text

    # --------------------------------------------------------------

    def job_embed_controller(self, job):
        print('=========================================================')
        print(job)

        listDays = ""
        for i in range(len(job['listDays'])):
            listDays += job['listDays'][i]
            if i<len(job['listDays'])-1: listDays += ", "
        
        text = f"Công việc {job['uid']} của khách hàng {job['user']['uid']} sẽ bắt đầu vào lúc {job['startTime']} các ngày {listDays} ở địa chỉ {job['location']}. "

        if job['serviceType']=='CLEANING': text = self.getTextCleaning(text, job)
        elif job['serviceType']=='HEALTHCARE': text = self.getTextHealthcare(text, job)
        elif job['serviceType']=='MAINTENANCE': text = self.getTextMaintenance(text, job)

        print(text)
        print('=========================================================')

        embed = self.geminiService.gemini_get_embedding(text.lower())

        if not embed: return False

        return self.pineconeService.pinecone_upsert_one_data(job, embed, text)

    # --------------------------------------------------------------

    def update_status_controller(self, jobID, status):
        return self.pineconeService.pinecone_update_metadata_status(jobID, status)

    # --------------------------------------------------------------

    def update_location_controller(self, jobID, location):
        return self.pineconeService.pinecone_update_metadata_location(jobID, location)

    # --------------------------------------------------------------

    def delete_job_embed(self, jobID):
        return self.pineconeService.pinecone_delete(jobID)

    # --------------------------------------------------------------

    def create_sample_data(self):
        try:
            with open("src/create/data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for i in data:
                self.job_embed_controller(i)

            return {
                "success": True,
                "error": "Create sample successfully"
            }
        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": "Create sample failed"
            }