# Voice-to-Kiro 🎤

Hold F2 to talk, release to auto-paste cleaned text. Works anywhere — Kiro CLI, browser, any app.

**Free** — powered by Groq's Whisper (STT) + Llama (text cleanup).

## How it works

```
Hold F2 → Record → Groq Whisper (speech-to-text) → Groq LLM (cleanup) → Auto-paste
```

- Removes filler words (呃、嗯、那個)
- Fixes grammar and punctuation
- Completes unfinished sentences
- Forces Traditional Chinese (繁體中文) output
- Runs silently in background, starts on boot

## One-click Install (Windows)

Open PowerShell and run:

```powershell
irm https://raw.githubusercontent.com/islandcodestudios2026418/voice-to-kiro/main/install.ps1 | iex
```

It will ask for your Groq API key (get one free at [console.groq.com](https://console.groq.com)).

## Manual Install

1. Install Python 3.10+
2. Clone this repo
3. `pip install -r requirements.txt`
4. Set your Groq API key:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_yourkey", "User")
   ```
5. Run: `python voice-to-kiro.py`

## Usage

- **Hold F2** — start recording
- **Release F2** — processes and auto-pastes text at cursor
- Runs in background, no window needed
- Auto-starts on boot after install

## Get a Groq API Key (free)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with Google
3. Go to API Keys → Create API Key
4. Copy the `gsk_...` key

## License

MIT
