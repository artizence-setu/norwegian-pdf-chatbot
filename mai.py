from flask import Flask, request, jsonify
import classifier
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    if request.headers['Content-Type'] == 'application/json':
        # Handle JSON data sent from Postman or API clients
        data = request.get_json()
        pdf = data.get('pdf')
        pdf_ch = pdf + '.pdf'
        filename = os.path.join('files', pdf_ch) 
        questions = data.get('questions')  

        if pdf is None or questions is None:
            return jsonify({'error': 'Missing data in request'}), 400

        if not isinstance(questions, list):
            return jsonify({'error': 'Questions should be provided as a list'}), 400

        results = []
        for question in questions:
            # Process each question, for example using a classifier
            result = classifier.classify(filename, question)
            results.append({'question': question, 'result': result})

        # Return JSON response with results for each question
        return jsonify({'results': results}), 200
    else:
        return jsonify({'error': 'Unsupported Media Type'}), 415

if __name__ == '__main__':
    app.run(debug=True)
