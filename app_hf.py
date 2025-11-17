"""
Flask app for HuggingFace Spaces
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.create.CreateController import CreateController
from src.job.JobController import JobController
from src.info.InfoController import InfoController
from src.arag.AragController import AragController

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# Initialize controllers
print("🚀 Initializing controllers...")
infoController = InfoController()
jobController = JobController()
createController = CreateController()
aragController = AragController(infoController=infoController, jobController=jobController)
print("✅ Controllers initialized!")

# --------------------------------------------------------------

@app.route("/", methods=['GET'])
def home():
    return jsonify({
        "message": "GoodJob API - Powered by Gemini 2.5 Flash",
        "status": "running",
        "platform": "HuggingFace Spaces",
        "endpoints": {
            "POST /api/job-embedding": "Upload job embedding",
            "GET /api/create-sample": "Create sample data",
            "POST /api/job/search": "Search jobs",
            "POST /api/info/answer": "Get info answers",
            "POST /api/chatbot": "Chat with ARAG bot"
        }
    })

# --------------------------------------------------------------

@app.route("/api/job-embedding", methods=['POST'])
def job_embed():
    job = request.get_json()
    if not job:
        return jsonify({
            "success": False,
            "error": "Phải là JSON."
        })
    
    result = createController.job_embed_controller(job)

    if result:
        return jsonify({
            "success": True,
            "message": "Thành công"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Không thành công"
        })
    
# --------------------------------------------------------------

@app.route("/api/create-sample", methods=['GET'])
def create_sample():
    result = createController.create_sample_data()
    return result
    
# --------------------------------------------------------------

@app.route("/api/update-metadata/status", methods=['PUT'])
def update_status():
    data = request.get_json()
    jobID = data['uid']
    status = data['status']

    result = createController.update_status_controller(jobID, status)

    if result:
        return jsonify({
            "success": True,
            "message": "Thành công"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Không thành công"
        })

# --------------------------------------------------------------

@app.route("/api/update-metadata/location", methods=['PUT'])
def update_location():
    data = request.get_json()
    jobID = data['uid']
    location = data['location']

    result = createController.update_location_controller(jobID, location)

    if result:
        return jsonify({
            "success": True,
            "message": "Thành công"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Không thành công"
        })

# --------------------------------------------------------------
    
@app.route("/api/job/<jobID>", methods=['DELETE'])
def delete_embed(jobID):
    result = createController.delete_job_embed(jobID)
    return result

# --------------------------------------------------------------

@app.route("/api/job/search", methods=['POST'])
def search_job():
    data = request.get_json()
    result = jobController.search(data['query'], data['reference'])
    return result

# --------------------------------------------------------------

@app.route("/api/info/answer", methods=['POST'])
def answer_info():
    data = request.get_json()
    result = infoController.answer(data['query'], data['reference'])
    return result

# --------------------------------------------------------------

@app.route("/api/chatbot", methods=['POST'])
def chat_box():
    data = request.get_json(force=True)
    print(f"📝 Query: {data['query']}")
    result = aragController.agent_search(data['query'], data['reference'])
    return result

# --------------------------------------------------------------

if __name__ == '__main__':
    print("🌟 Starting GoodJob API on HuggingFace Spaces...")
    app.run(host='0.0.0.0', port=7860, debug=False)
