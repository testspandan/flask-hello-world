from flask import Flask, request, jsonify, send_from_directory
from elevenlabs import generate, play
import os

app = Flask(__name__)

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
        
        for i, chunk in enumerate(text_chunks):
            audio_data = generate(text=chunk, voice=voice, model='eleven_multilingual_v1')
            audio_file_path = f"generated_audio_{i}.wav"
            
            with open(audio_file_path, 'wb') as wf:
                wf.write(audio_data)
            
            audio_paths.append(audio_file_path)
        
        # Combine audio paths into a single audio file
        combined_audio_path = "combined_audio.wav"
        
        if len(audio_paths) > 1:
            os.system(f"sox {' '.join(audio_paths)} {combined_audio_path}")
        else:
            combined_audio_path = audio_paths[0]  # Use the single audio path if there's only one chunk
        
        # Return the path to the combined audio file
        return jsonify({'audio_url': f'https://audioapi.spandanpokhrel.com.np/get_audio/{combined_audio_path}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio/<filename>')
def get_audio(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Run the Flask application on host 0.0.0.0 and port 81
    app.run(host='0.0.0.0', port=81, debug=True)
