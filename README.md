# AI Interview Assistant

## About
AI Interview Assistant is an interactive web application designed to help users practice and prepare for interviews using AI-powered question-answering features. The app leverages a Python backend and front-end technologies including JavaScript, CSS, and HTML to deliver a smooth user experience.

## Features
- Voice interaction for asking and answering interview questions
- Text-to-Speech support for AI-generated answers
- Real-time speech recognition and response
- User-friendly interface with light/dark mode toggling
- API integration with Google Gemini AI for intelligent responses

## Technologies Used
- Python (Backend and AI processing)
- JavaScript (Frontend interactivity)
- HTML & CSS (UI design and layout)
- SpeechRecognition and PyAudio for voice input
- Eel for Python-JavaScript communication

## Installation

1. Clone the repository:
git clone https://github.com/ps982182/AI_Interview.git
cd AI_Interview

text

2. Create and activate a Python virtual environment:
- On Windows:
  ```
  python -m venv ai_interview_env
  ai_interview_env\Scripts\activate
  ```
- On Linux/macOS:
  ```
  python3 -m venv ai_interview_env
  source ai_interview_env/bin/activate
  ```

3. Install dependencies:
pip install -r requirements.txt

text

4. Run the application:
python assist.py

text

## Usage
- Start the app and use the microphone to ask interview questions.
- Answers will appear in the interface and can be heard via text-to-speech.
- Securely save your Google Gemini API Key for backend AI calls.
- Use on-screen control buttons to start/stop listening, change API key, and clear conversation history.

## Contribution
Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests.

## License
This project is open-source under the MIT License.

## Contact
Created and maintained by Prajakta Singhal.  
For questions or collaboration, reach out via email:  
[singhal.riya2018@gmail.com](mailto:singhal.riya2018@gmail.com)
