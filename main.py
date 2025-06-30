import os
import whisper
import pyaudio
import wave
import threading
import time
from datetime import datetime
import torch

# ===== CONFIGURATION =====
CHUNK_DURATION = 30              # seconds
OVERLAP_DURATION = 0            # seconds
SAMPLE_RATE = 16000             # Hz
CHANNELS = 1
FORMAT = pyaudio.paInt16
MODEL_NAME = "large-v3"

# Prompt for output filename
TRANSCRIPT_FILE = input("Enter the filename for your transcription (e.g meeting_notes.txt): ").strip()
if TRANSCRIPT_FILE == "":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    TRANSCRIPT_FILE = f"transcription_{timestamp}.txt"

TEMP_AUDIO_FILE = "temp_chunk.wav"
FOCUSRITE_KEYWORD = "Focusrite"  # Keyword to identify your device

# ===== GLOBALS =====
audio_buffer = bytearray()
stop_flag = False


def detect_focusrite_device(p):
    """
    Search all audio devices for one matching the Focusrite keyword.
    Returns the device index if found.
    """
    print("[INFO] Searching for Focusrite device...")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if FOCUSRITE_KEYWORD.lower() in info["name"].lower() and info["maxInputChannels"] > 0:
            print(f"[INFO] Found Focusrite device: {info['name']} (Index {i})")
            return i
    print("[WARN] Focusrite device not found. Using default input.")
    return None


def record_audio_loop(stream, chunk_size):
    global audio_buffer, stop_flag
    print("[INFO] Recording started. Press Ctrl+C to stop.")
    while not stop_flag:
        data = stream.read(chunk_size, exception_on_overflow=False)
        audio_buffer.extend(data)


def spinner(stop_event):
    while not stop_event.is_set():
        for ch in "|/-\\":
            print(f"\rTranscribing... {ch}", end="", flush=True)
            if stop_event.wait(0.1):
                break


def save_chunk(filename, data, sample_rate=SAMPLE_RATE):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
        wf.setframerate(sample_rate)
        wf.writeframes(data)


def main():
    global stop_flag, audio_buffer

    # Check device availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Torch device detected: {device}")

    print(f"[INFO] Loading Whisper model '{MODEL_NAME}'...")
    model = whisper.load_model(MODEL_NAME, device=device)

    # Set up audio stream
    p = pyaudio.PyAudio()
    focusrite_index = detect_focusrite_device(p)

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=focusrite_index,
        frames_per_buffer=int(SAMPLE_RATE * CHUNK_DURATION)
    )

    # Start audio recording thread
    chunk_size = int(SAMPLE_RATE * CHUNK_DURATION)
    record_thread = threading.Thread(target=record_audio_loop, args=(stream, chunk_size))
    record_thread.start()

    # Processing loop
    try:
        chunk_stride = int(SAMPLE_RATE * (CHUNK_DURATION - OVERLAP_DURATION))
        transcript = []

        while not stop_flag:
            if len(audio_buffer) >= chunk_size:
                current_chunk = audio_buffer[:chunk_size]
                save_chunk(TEMP_AUDIO_FILE, current_chunk)

                # Start spinner
                stop_event = threading.Event()
                t = threading.Thread(target=spinner, args=(stop_event,))
                t.start()

                # Run transcription
                result = model.transcribe(
                    TEMP_AUDIO_FILE,
                    language='en'
                )

                # Stop spinner
                stop_event.set()
                t.join()
                print("\rTranscribing... done!        ")

                text = result['text'].strip()

                if text:
                    text = text[0].upper() + text[1:]  # Capitalize first letter
                if text and not text.endswith(('.', '!', '?')):
                    text += '.'

                if transcript:
                    last_text = transcript[-1].strip().lower()
                
                    if last_text:
                        overlap_len = min(30, len(last_text))
                        overlap = last_text[-overlap_len:]

                        if overlap and text.lower().startswith(overlap):
                            text = text[len(overlap):].lstrip()
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(text)
                transcript.append(text)

                # Slide buffer forward
                audio_buffer = audio_buffer[chunk_stride:]
            else:
                time.sleep(0.25)

    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")
        stop_flag = True

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)

        with open(TRANSCRIPT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(transcript))
        print(f"[INFO] Transcription saved to {TRANSCRIPT_FILE}")


if __name__ == '__main__':
    main()
