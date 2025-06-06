from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://192.168.2.216"}})

@app.route("/api/message", methods=["GET"])
def get_message():
    return jsonify({"message": "Hello from the backend!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)