from flask import Flask, request, jsonify, send_from_directory
from elevenlabs import generate, play
import os

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello from Flask!'

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        
        text = request.json.get('text')
        voice = request.json.get('voice')
        #voice=Arnold
        audio_data = generate(text=text, voice=voice, model='eleven_multilingual_v1')

        
        audio_file_path = "generated_audio.wav"
        with open(audio_file_path, 'wb') as wf:
            wf.write(audio_data)

        # Return the path to the hosted audio file
        return jsonify({'audio_url': f'https://audioapi.spandanpokhrel.com.np/get_audio/{audio_file_path}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio/<filename>')
def get_audio(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Run the Flask application on host 0.0.0.0 and port 81
    app.run(host='0.0.0.0', port=81, debug=True)
