# Norwegian Chatbot

This project provides a Norwegian Chatbot that answers questions based on the content of a provided PDF file.

## How It Works

1. **Launch the Flask API**: 
   - Run the `app.py` script to start the Flask API.
   
2. **Send Requests**:
   - Use a tool like Postman to send a POST request to the API.
   - The request should include a PDF file and a list of questions in JSON format.
   
3. **Receive Responses**:
   - The API will respond with a JSON file containing the questions and their respective answers extracted from the PDF.

## Request Format

Here is the format for sending questions to the API:

```json
{
  "pdf": "4",
  "questions": [
        "Skal det bygges noe nytt i nabolaget?",
        "hvor gamle er vinduene?",
        "Hva er takhøyden?",
        "hvor gammelt er bygget?",
        "hva inngår i felleskostnadene?",
        "Hva slags sluk er det på badet?",
        "Hvor gammelt er badet?",
        "Når er kjøkkenet fra?",
        "er det bod? hvor stor er den?",
        "er det planlagt større påkostninger i borettslaget?",
        "har det vært noe feil på våtrom?",
        "er det utført arbeid på el-anlegg?",
        "er det samsvarserklæring?",
        "er borettslaget i tvister av noe slag?"
    ]
}
