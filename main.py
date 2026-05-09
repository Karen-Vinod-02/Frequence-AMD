from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

vllm_url = os.getenv("NGROK_URL")

client = AsyncOpenAI(
    base_url=vllm_url,
    api_key="empty" 
)

class VisualizerRequest(BaseModel):
    user_prompt: str
    current_state: dict

@app.post("/generate_visuals")
async def generate_visuals(payload: VisualizerRequest):
    state_str = json.dumps(payload.current_state)
    system_prompt = f"""
    You are an AI visual DJ controlling a music visualizer. 
    The user describes a vibe, and you output the parameters to match it.
    
    Current state of the visualizer: {state_str}
    
    You MUST respond with ONLY a raw JSON object. Do not use markdown formatting, do not use json wrappers, and do not add any conversational text.
    
    Output Schema:
    {{
      "style": "abstract",
      "colorA": "#hexcode",
      "colorB": "#hexcode",
      "speed": 1.0,
      "intensity": 1.0,
      "complexity": 0.5,
      "smoothing": 0.8,
      "particleCount": 120,
      "barCount": 64,
      "mirror": false,
      "rotation": false,
      "glow": false,
      "message": "A short, punchy confirmation of what you changed."
    }}
    """

    try:
        response = await client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.user_prompt}
            ],
            temperature=0.7
        )
        
        raw_output = response.choices[0].message.content
        clean_json = raw_output.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_json)
        
    except Exception as e:
        return {
            "style": "waveform",
            "colorA": "#ff0000",
            "colorB": "#0000ff",
            "speed": 1.0,
            "intensity": 1.0,
            "complexity": 0.5,
            "smoothing": 0.8,
            "particleCount": 120,
            "barCount": 64,
            "mirror": False,
            "rotation": False,
            "glow": False,
            "message": f"AI Parsing Error. Try again. Error: {str(e)}"
        }

@app.get("/health")
async def health():
    return {"status": "Backend is alive", "ai_model": "Phase 2 - AMD MI300X Qwen"}

app.mount("/", StaticFiles(directory="build", html=True), name="static")