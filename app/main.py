from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/send-prompt")
async def send_prompt(prompt: str):
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    url = "http://10.12.1.31:8086/api/generate"
    payload = {"model":"llama3:latest", "prompt":"answer in one single word. You should answer pong. Ping?"}
    
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to send prompt")
    
    return {"response": response}