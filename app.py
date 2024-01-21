from flask import Flask, request, jsonify, send_from_directory
from elevenlabs import generate, play
import os
from pydub import AudioSegment 
from elevenlabs import set_api_key
app = Flask(__name__)


set_api_key("c0da0b329321126f382ba5d2d430649f")

def split_text(text, chunk_size):
    chunks = []
    while len(text) > chunk_size:
        nearest_period = text.rfind('.', 0, chunk_size)
        nearest_purna_biram = text.rfind('।', 0, chunk_size)  # "purna biram" in Nepali
        nearest_split = max(nearest_period, nearest_purna_biram)

        if nearest_split == -1:
            nearest_split = chunk_size

        chunks.append(text[:nearest_split + 1].strip())
        text = text[nearest_split + 1:]

    if text:
        chunks.append(text.strip())

    return chunks if chunks else [text]  # If the text is shorter than chunk_size, return the entire text as a single chunk

@app.route('/')
def index():
    return 'Hello from Flask!'

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        text = request.json.get('text')
        voice = request.json.get('voice')
        chunk_size = 250

        text_chunks = split_text(text, chunk_size)
        audio_paths = []
        chunk_audio_urls = []

        for i, chunk in enumerate(text_chunks):
            audio_data = generate(text=chunk, voice=voice, model='eleven_multilingual_v1')
            audio_file_path = f"generated_audio_{i}.wav"

            with open(audio_file_path, 'wb') as wf:
                wf.write(audio_data)

            audio_paths.append(audio_file_path)
            chunk_audio_urls.append(f'https://2cbeb26d-4f0c-4513-a4a6-d72a5a837f0d-00-1kxlnxhjad91f.sisko.replit.dev/get_audio/{audio_file_path}')

        # Combine audio paths into a single audio file using pydub
        combined_audio_path = "combined_audio.wav"

        if len(audio_paths) > 1:
            combined_audio = AudioSegment.silent()
            for path in audio_paths:
                combined_audio += AudioSegment.from_wav(path)
            combined_audio.export(combined_audio_path, format="wav")
        else:
            combined_audio_path = audio_paths[0]  # Use the single audio path if there's only one chunk

        # Return the paths to individual and combined audio files
        response = {
            'chunk_audio_urls': chunk_audio_urls,
            'combined_audio_url': f'https://2cbeb26d-4f0c-4513-a4a6-d72a5a837f0d-00-1kxlnxhjad91f.sisko.replit.dev/get_audio/{combined_audio_path}'
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio/<filename>')
def get_audio(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Run the Flask application on host 0.0.0.0 and port 81
    app.run(host='0.0.0.0', port=81, debug=True)
