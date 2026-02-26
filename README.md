# Talking with Real-Time Audio LLM

This project demonstrates how to interact with a Large Language Model (LLM) using real-time audio streaming. It connects your microphone to an Azure OpenAI model, streams your voice, and plays back the model's audio responses in real time.

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [How It Works](#how-it-works)
5. [Step-by-Step Tutorial](#step-by-step-tutorial)
6. [Troubleshooting](#troubleshooting)
7. [License](#license)

---

## Overview
This script enables a real-time, voice-based conversation with an LLM hosted on Azure OpenAI. It captures your microphone input, streams it to the model, and plays back the model's spoken responses.

---

## Prerequisites

- Python 3.8+
- [Azure OpenAI Service](https://learn.microsoft.com/azure/cognitive-services/openai/)
- An Azure OpenAI deployment with real-time audio support
- API Key and endpoint for your Azure OpenAI resource
- A working microphone and speakers

---

## Setup

1. **Clone the repository**
	```bash
	git clone <this-repo-url>
	cd talking-with-realtime-audio-llm
	```

2. **Create and activate a virtual environment (optional but recommended):**
	```bash
	python -m venv .venv
	# On Windows:
	.venv\Scripts\activate
	# On macOS/Linux:
	source .venv/bin/activate
	```

3. **Install dependencies:**
	```bash
	pip install pyaudio openai
	```

4. **Set environment variables:**
	- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL (e.g., `https://your-resource.openai.azure.com`)
	- `AZURE_OPENAI_DEPLOYMENT_NAME`: The name of your Azure OpenAI deployment
	- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key

	You can set these in your terminal:
	```bash
	set AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
	set AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
	set AZURE_OPENAI_API_KEY=your-api-key
	```

---

## How It Works

1. **Audio Streams:**
	- Uses `pyaudio` to capture microphone input and play audio output.
2. **WebSocket Connection:**
	- Connects to Azure OpenAI using the `openai` Python SDK with real-time audio support.
3. **Session Configuration:**
	- Sets up the session for real-time, voice-only interaction.
4. **Async Tasks:**
	- Streams microphone audio to the model and plays back responses concurrently.

---

## Step-by-Step Tutorial

### 1. Prepare Your Environment
Follow the [Setup](#setup) steps above to install dependencies and set environment variables.

### 2. Run the Script
```bash
python talking-with-realtime-audio-llm.py
```

### 3. Speak and Listen
- After running, you'll see:
	```
	Connection established. Speak into your microphone. Press Ctrl+C to stop.
	```
- Speak into your microphone. The model will respond with synthesized audio.

### 4. Stop the Program
- Press `Ctrl+C` to terminate.

---

## Troubleshooting

- **Missing environment variables:**
	- The script will raise an error if any required variable is missing.
- **Audio device errors:**
	- Ensure your microphone and speakers are connected and not in use by other applications.
- **API errors:**
	- Check your Azure OpenAI deployment and API key.

---

## License

See [LICENSE](LICENSE) for details.
