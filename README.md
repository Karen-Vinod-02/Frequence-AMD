---
title: Frequence
emoji: 🎵
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
---

# Frequence: AI-Powered Music Visualizer
Frequence is an AI-driven music visualizer that transforms audio into interactive generative art using natural-language controls. By bridging a modern React frontend with a high-performance AMD GPU backend, it allows users to control visual aesthetics through natural language prompts.

It uses a FastAPI backend to route user prompts to a Qwen 2.5 7B model running on AMD MI300X hardware (or equivalent), which dynamically updates the visualizer's mathematical parameters in real-time.

## Features
- Agentic Control: Type commands like "make it aggressive" or "warm sunset palette" to change visuals via AI.
- Multi-Style Engine: Support for Abstract, Waveform, Frequency Bars, and Particle styles.
- Real-time Audio Analysis: Processes uploaded audio files with real-time visual response.

## Tech Stack
- **GPU Infrastructure**: AMD Instinct MI300X (AMD Developer Cloud)
- **AI Model**: Qwen 2.5 7B Instruct
- **Inference Engine**: vLLM 
- **Backend**: FastAPI, Python
- **API Layer**: OpenAI-compatible endpoint
- **Frontend**: React, Tailwind CSS, Lucide React
- **Deployment**: Docker 

## Infrastructure Requirements
To run the generative inference engine:
- **Compute**: AMD Instinct™ MI300X or equivalent ROCm-capable instance.
- **Server**: OpenAI-compatible inference server (vLLM/Ollama) hosting Qwen 2.5.
- **Bridge**: Ngrok (if connecting a local dev environment to the GPU cloud). 

## Setup Instructions
### 1. Clone the Repository
```
git clone https://github.com/Karen-Vinod-02/Frequence-AMD.git
cd Frequence-AMD
```
### 2. Configure Environment Variables
The backend requires a connection to your GPU inference server.
Create a .env file in the root directory. Add your GPU endpoint::
```
NGROK_URL=https://your-ngrok-or-gpu-endpoint.dev
```
### 3. Docker Deployment (Recommended)
This project is containerized for easy deployment to services like Hugging Face Spaces.
Build the image:
```
docker build -t frequence-app .
```
Run the container:
```
docker run -p 7860:7860 --env NGROK_URL=your_url frequence-app
```
### 4. Local Python Setup
If running without Docker:
```
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

## How it Works
1. **Static Serving**: The FastAPI server mounts the build/ directory to serve the React frontend on the root (/) path.
2. **AI Handshake**: User prompts are sent to /generate_visuals.
3. **Parameter Injection**: The Qwen model analyzes the "current state" of the visualizer and returns a JSON object containing new colors, speeds, and complexities.
4. **Canvas Update**: The React frontend receives the JSON and instantly updates the HTML5 Canvas draw loop.

## Acknowledgements
- AMD – For the MI300X hardware acceleration.
- Alibaba Cloud – For the Qwen 2.5 7B model.

## License
This project is licensed under the [MIT License](LICENSE).
