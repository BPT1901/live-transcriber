# 🎙️ Live Transcriber

**Live Transcriber** is a simple Python app that converts live audio into text using OpenAI’s Whisper model. It’s designed for Windows and works perfectly with devices like the Focusrite Scarlett audio interface.

---

## ✨ Features

- Records live audio from your microphone
- Transcribes speech in real-time
- Saves your transcription to a plain text file
- Works entirely offline once the Whisper model is downloaded
- Supports switching between Whisper model sizes for speed vs. accuracy

---

## ✅ Requirements

- Windows 11
- Python 3.10 or newer
- Audio input device (e.g. Focusrite Scarlett)
- ~4 GB RAM minimum (10 GB recommended for large models)
- FFmpeg installed and added to PATH

---

## 🛠 Installation

### 1. Install Python

Download and install Python:

[https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

✅ Make sure you check:
Add Python to PATH


---

### 2. Install FFmpeg

Download FFmpeg from:

[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Extract the zip, and add the `bin` folder to your Windows PATH.

---

### 3. Download This Project

Place the project folder in an easy-to-find location, e.g.: Users\youruser\live-transcriber


---

### 4. Install Python Packages

Open PowerShell or the VS Code terminal and run:

```powershell
cd C:\Users\compu\live-transcriber
pip install -r requirements.txt
```

---

## Test

CD into the directory you created, then run:

```powershell
python main.py
```

You’ll be prompted:

```
Enter the filename for your transcription (e.g. meeting_notes.txt):
```

The app will then begin recording audio. You’ll see:

```
[INFO] Recording started. Press Ctrl+C to stop.
```

Press `Ctrl + C` to stop.

This will stop the transcription and save it to your project folder.

---

## 🔄 Changing the Whisper Model

To use a smaller model for faster transcription:

1. Open `main.py`
2. Find:
    ```python
    MODEL_NAME = "large"
    ```
3. Change it to:
    ```python
    MODEL_NAME = "medium"
    ```
4. Other available models are:
    - `"tiny"`
    - `"base"`
    - `"small"`
    - `"medium"`
    - `"large"`

---

## 💡 How It Works

- The first time you run the app, it automatically downloads the Whisper model (~3 GB for the large version). Future runs do not download it again.
- Transcription is processed in 5-second audio chunks.
- The app removes duplicate text from overlapping audio.
- Your transcription file contains only clean text — no timestamps.
- The app adds blank lines between paragraphs for easier reading.
