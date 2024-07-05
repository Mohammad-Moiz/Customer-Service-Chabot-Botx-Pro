from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.chatbot import reply


app = Flask(__name__)

CORS(app)


@app.route('/')
def hello():
    return 'Every thing is OK'


@app.route('/name_relation', methods=['POST'])
def get_name_relation():

    data = request.get_json()
    if data:
        name = data.get('name') 
        relation = data.get("relation")
    else: None

    return {"name":name,"relation":relation}



@app.route('/data', methods=['POST'])
def chat():

    data = request.get_json()
    
    human_input = data.get('message') if data else None
    output_text = reply(human_input)
    print(output_text)
    return {'message': output_text}



if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)