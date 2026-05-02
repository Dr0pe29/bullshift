# Bullshift

Bullshift is a real-time speech fact-checking project. It listens to live transcription, detects verifiable claims, checks them against web sources, and shows the result in the browser with confidence scores, explanations, and sources. The app combines a Python backend, a static frontend, Deepgram for speech-to-text, and Groq-powered AI for claim analysis.

## Main Technologies

- Python + FastAPI for the backend API and websocket stream
- Deepgram for live transcription
- Groq for claim classification and fact-checking analysis
- Tavily and DDGS for web evidence lookup
- HTML, CSS, and JavaScript for the frontend

## Project Structure

- `src/Backend/` contains the FastAPI app, fact-checking logic, and backend tests
- `src/Frontend/` contains the browser UI

## How to Run

### 1. Set up the backend

From the project root:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
.\venv\Scripts\activate
```

Install dependencies:

```bash
cd src/Backend
pip install -r requirements.txt
```

Create a `.env` file inside `src/Backend/` with your API keys:

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
DEEPGRAM_API_KEY=your_deepgram_key
MIC_INDEX=1
DEEPGRAM_LANGUAGE=en
```

### 2. Start the backend server

```bash
uvicorn app:app --reload
```

The backend will run at `http://localhost:8000`.

### 3. Open the frontend

Open `src/Frontend/html/home.html` in a browser, or serve the `src/Frontend` folder with a local static server.

The frontend connects to the websocket at `ws://localhost:8000/ws/transcript`, so the backend must be running first.

## What Happens at Runtime

1. Deepgram transcribes the microphone input in real time.
2. The backend receives transcript chunks through a websocket.
3. The app checks whether each sentence is fact-checkable.
4. Verifiable claims are analyzed against web evidence.
5. The frontend shows the transcript, fact cards, confidence, and sources.

## Evaluation

You can run the local verifiability evaluation script from `src/Backend/`:

```bash
python eval_verifiable.py
```

This prints accuracy, per-label results, and misclassifications for the sample dataset.
