from flask import Flask, request, jsonify
import re
import threading
import uuid
from scrapper import scrape, scrape_status

app = Flask(__name__)

conversations = {}

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    return re.match(r"^\+?\d{10,15}$", phone)

def is_valid_url(url):
    return re.match(r"https?://www\.finn\.no/realestate/.*", url)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    message = data.get('message')

    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        conversations[conversation_id] = {"step": "hello", "user_info": {}}
    
    conversation = conversations[conversation_id]
    user_info = conversation["user_info"]

    print(f"Current step: {conversation['step']}")  # Debugging statement
    print(f"Message: {message}")  # Debugging statement
    
    if conversation["step"] == "hello":
        conversation["step"] = "ask_name"
        return jsonify(conversation_id=conversation_id, response="Hello! Please provide your name:")

    if conversation["step"] == "ask_name":
        user_info['name'] = message
        conversation["step"] = "ask_phone"
        return jsonify(conversation_id=conversation_id, response="Please provide your phone number:")

    if conversation["step"] == "ask_phone":
        if is_valid_phone(message):
            user_info['phone'] = message
            conversation["step"] = "ask_house_link"
            return jsonify(conversation_id=conversation_id, response="Please provide the house link:")
        else:
            return jsonify(conversation_id=conversation_id, response="Invalid phone number format. Please provide a valid phone number:")

    if conversation["step"] == "ask_house_link":
        if is_valid_url(message):
            user_info['house_link'] = message
            conversation["step"] = "ask_email"
            return jsonify(conversation_id=conversation_id, response="Please provide your email:")
        else:
            return jsonify(conversation_id=conversation_id, response="I only work with finn.no links. Please provide a valid house link:")

    if conversation["step"] == "ask_email":
        if is_valid_email(message):
            user_info['email'] = message
            response_message = f"Thank you, {user_info['name']}! Here is the information you provided:\n" \
                               f"Email: {user_info['email']}\n" \
                               f"Phone: {user_info['phone']}\n" \
                               f"House Link: {user_info['house_link']}\n" \
                               f"Please wait while I scan the info....."
            response = jsonify(conversation_id=conversation_id, response=response_message)
            threading.Thread(target=scrape, args=(user_info['house_link'], conversation_id)).start()
            return response
        else:
            return jsonify(conversation_id=conversation_id, response="Invalid email format. Please provide a valid email:")

    return jsonify(conversation_id=conversation_id, response="Hello! Please provide your name:")

@app.route('/chatbot/status', methods=['GET'])
def check_status():
    conversation_id = request.args.get('conversation_id')
    status = scrape_status.get(conversation_id, "pending")
    if status == "completed":
        return jsonify(conversation_id=conversation_id, response="Scraping completed. You can now ask your questions.")
    elif status == "error":
        return jsonify(conversation_id=conversation_id, response="Scraping encountered an error. Please try again.")
    else:
        return jsonify(conversation_id=conversation_id, response="Scraping is still in progress. Please wait.")

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
