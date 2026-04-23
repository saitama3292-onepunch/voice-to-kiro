# -*- coding: utf-8 -*-
"""
Voice-to-Kiro: Hold F2 to talk → auto-paste cleaned text.
Uses Windows low-level keyboard hook to suppress F2 from reaching apps.
"""

import io, os, sys, wave, threading, time, ctypes, ctypes.wintypes
import pyaudio, pyperclip
from groq import Groq

STT_MODEL = "whisper-large-v3-turbo"
LLM_MODEL = "llama-3.3-70b-versatile"
RATE, CHANNELS, CHUNK = 16000, 1, 1024
VK_F2 = 0x71
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

CLEANUP_PROMPT = """You are a speech-to-text cleanup assistant. The user dictated a message via voice.
Clean it up:
- Fix grammar and punctuation
- Remove filler words (um, uh, 呃, 嗯, 那個, 就是)
- Complete obviously unfinished sentences if the intent is clear
- Keep the original meaning and tone exactly
- LANGUAGE RULES (CRITICAL):
  - Chinese parts MUST be Traditional Chinese (繁體中文, Taiwan style). Convert any Simplified Chinese to Traditional.
  - English words/phrases that the user clearly spoke in English MUST stay in English. Do NOT translate them to Chinese.
  - Technical terms, proper nouns, brand names (e.g. GitHub, Kiro, Python, API) MUST stay in their original language.
  - If the user code-switches (混語, e.g. "我要用這個API去call那個endpoint"), preserve the mixed languages exactly.
- Output ONLY the cleaned text, nothing else. No quotes, no explanation."""

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
_held = False
_recording = False

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", ctypes.wintypes.DWORD),
                 ("scanCode", ctypes.wintypes.DWORD),
                 ("flags", ctypes.wintypes.DWORD),
                 ("time", ctypes.wintypes.DWORD),
                 ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

HOOKPROC = ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))

def record():
    global _held
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    while _held:
        frames.append(stream.read(CHUNK, exception_on_overflow=False))
    stream.stop_stream()
    stream.close()
    pa.terminate()
    if len(frames) * CHUNK / RATE < 0.3:
        return None
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    buf.seek(0)
    return buf

def transcribe(audio_buf):
    result = client.audio.transcriptions.create(
        file=("recording.wav", audio_buf, "audio/wav"),
        model=STT_MODEL, response_format="text",
        prompt="繁體中文，台灣用語。Use Traditional Chinese for Chinese, keep other languages as-is.",
    )
    return result.strip() if isinstance(result, str) else result.text.strip()

def cleanup(raw_text):
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": CLEANUP_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.3, max_tokens=1024,
    )
    return resp.choices[0].message.content.strip()

def do_paste(text):
    import subprocess
    pyperclip.copy(text)
    time.sleep(0.1)
    # Use PowerShell to send Ctrl+V via .NET SendKeys
    subprocess.Popen(
        ['powershell', '-Command',
         'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("^v")'],
        creationflags=0x08000000  # CREATE_NO_WINDOW
    )

def process():
    global _recording
    if _recording:
        return
    _recording = True
    try:
        audio = record()
        if not audio:
            return
        raw = transcribe(audio)
        if not raw:
            return
        cleaned = cleanup(raw)
        do_paste(cleaned)
    except Exception:
        pass
    finally:
        _recording = False

def hook_proc(nCode, wParam, lParam):
    global _held
    if nCode >= 0 and lParam.contents.vkCode == VK_F2:
        if wParam == WM_KEYDOWN and not _held:
            _held = True
            threading.Thread(target=process, daemon=True).start()
        elif wParam == WM_KEYUP:
            _held = False
        return 1  # Block F2 from reaching other apps
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

def main():
    # Hide console window
    try:
        ctypes.windll.user32.ShowWindow(kernel32.GetConsoleWindow(), 0)
    except:
        pass

    # Install low-level keyboard hook
    hook_func = HOOKPROC(hook_proc)
    hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, hook_func, 0, 0)
    if not hook:
        sys.exit(1)

    # Message loop (required for hooks to work)
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    user32.UnhookWindowsHookEx(hook)

if __name__ == "__main__":
    main()
