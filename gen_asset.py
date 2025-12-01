import json
import os
import requests
import asyncio
import edge_tts

INPUT_FILE = "video_plan.json"
OUTPUT_DIR = "assets"
HF_TOKEN = "Key"

HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

VOICE = "en-US-ChristopherNeural"

async def generate_audio(text, filename):
    """Generates AI speech using Microsoft Edge's Neural TTS."""
    print(f"Generating Audio: {filename}...")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

def generate_image(prompt, filename):
    """Generates an image using Hugging Face API."""
    print(f"Generating Image: {filename}...")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    for i in range(3):
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return True
        elif "loading" in response.text:
            print("Model is loading, waiting 5s...")
            import time
            time.sleep(5)
        else:
            print(f"Error generating image: {response.text}")
            return False

async def main():
    if not os.path.exists(INPUT_FILE):
        print("Error: video_plan.json not found.")
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    for segment in data['segments']:
        seg_id = segment['id']
        narration = segment['narration']
        image_prompt = segment['image_prompt']

        audio_path = os.path.join(OUTPUT_DIR, f"audio_{seg_id}.mp3")
        image_path = os.path.join(OUTPUT_DIR, f"image_{seg_id}.jpg")

        await generate_audio(narration, audio_path)

        final_prompt = f"{image_prompt}, historical documentary style, 8k resolution, cinematic lighting"
        generate_image(final_prompt, image_path)

    print(f"Success! All assets saved in '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    asyncio.run(main())