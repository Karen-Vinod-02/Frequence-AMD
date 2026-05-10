from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
import json
import os
import re

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

def clean_json_response(raw_text: str) -> str:
    """Clean and extract JSON from AI response"""
    text = re.sub(r'```json\s*', '', raw_text)
    text = re.sub(r'```\s*', '', text)
    
    # Try to find JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return text.strip()

@app.post("/generate_visuals")
async def generate_visuals(payload: VisualizerRequest):
    current = payload.current_state
    
    system_prompt = f"""You are an AI visual DJ controlling a music visualizer.
The user describes a vibe or gives a command, and you output JSON parameters to match it.

CRITICAL: Respond with ONLY a valid JSON object. No markdown, no explanations, no extra text.

Available styles: "abstract", "waveform", "bars", "particles"

Current state:
{json.dumps(current, indent=2)}

Output JSON must include ALL these fields (modify only what the user requested, keep others from current state):
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
  "message": "Short confirmation of what changed"
}}

Examples:
- "make it aggressive" → increase speed to 2.5, intensity to 2.8, use reds/oranges
- "warm sunset palette" → colorA: "#ff6b35", colorB: "#f7931e"
- "switch to particles" → style: "particles"
- "mirror mode on" → mirror: true
- "slow it down" → speed: 0.5"""

    try:
        response = await client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        raw_output = response.choices[0].message.content
        clean_json = clean_json_response(raw_output)
        
        ai_response = json.loads(clean_json)
        
        # Extract style and message
        style = ai_response.get("style", current.get("style", "bars"))
        message = ai_response.get("message", "Updated!")
        
        # Build params dict with all required fields
        params = {
            "colorA": ai_response.get("colorA", current.get("colorA", "#7f77dd")),
            "colorB": ai_response.get("colorB", current.get("colorB", "#1d9e75")),
            "speed": float(ai_response.get("speed", current.get("speed", 1.0))),
            "intensity": float(ai_response.get("intensity", current.get("intensity", 1.0))),
            "complexity": float(ai_response.get("complexity", current.get("complexity", 0.5))),
            "smoothing": float(ai_response.get("smoothing", current.get("smoothing", 0.8))),
            "particleCount": int(ai_response.get("particleCount", current.get("particleCount", 120))),
            "barCount": int(ai_response.get("barCount", current.get("barCount", 64))),
            "mirror": bool(ai_response.get("mirror", current.get("mirror", False))),
            "rotation": bool(ai_response.get("rotation", current.get("rotation", False))),
            "glow": bool(ai_response.get("glow", current.get("glow", False))),
        }
        
        # Return in format expected by frontend
        return {
            "style": style,
            "params": params,
            "message": message
        }
        
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "style": current.get("style", "bars"),
            "params": current,
            "message": f"AI error: {str(e)[:50]}. Try rephrasing?"
        }

@app.get("/health")
async def health():
    return {"status": "Backend is alive", "ai_model": "Phase 2 - AMD MI300X Qwen"}

app.mount("/", StaticFiles(directory="build", html=True), name="static")