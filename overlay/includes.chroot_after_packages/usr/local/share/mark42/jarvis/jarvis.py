#!/usr/bin/env python3
"""MARK 42 — JARVIS voice assistant engine.

Fully offline. Listens with Vosk, thinks with the local Ollama model, and
speaks through the system speakers with eSpeak-NG. Driven by the `jarvis`
command; you normally don't run this file directly.
"""
import os, sys, json, subprocess, re, urllib.request

JDIR       = "/opt/mark42/jarvis"
VOSK_MODEL = os.path.join(JDIR, "vosk-model")
LOG        = os.path.join(JDIR, "jarvis.log")
OLLAMA     = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL      = os.environ.get("JARVIS_MODEL", "jarvis")
USER       = os.environ.get("JARVIS_USER") or os.environ.get("SUDO_USER") or os.environ.get("USER") or "sir"
YOLO       = os.environ.get("JARVIS_YOLO") == "1"   # run commands without the safety check

# commands JARVIS will refuse to run unless JARVIS_YOLO=1
DANGEROUS = [r"rm\s+-rf\s+/(?!home|opt|tmp|var/tmp)", r"\bmkfs", r"\bdd\b[^\n]*of=/dev/",
             r">\s*/dev/sd", r"\bwipefs", r":\(\)\s*{\s*:\s*\|", r"\bshred\b", r"/dev/sd[a-z]\b"]

def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(msg.rstrip() + "\n")
    except Exception:
        pass

# ---------------------------------------------------------------- voice out
def speak(text):
    text = re.sub(r"<cmd>.*?</cmd>", "", text, flags=re.S).strip()
    text = re.sub(r"\s+", " ", text)
    if not text:
        return
    print(f"JARVIS: {text}")
    # British-sounding, slightly lower pitch -> closer to the JARVIS feel
    try:
        subprocess.run(["espeak-ng", "-v", "en-gb", "-s", "155", "-p", "22", "-a", "190", text],
                       check=False)
    except FileNotFoundError:
        print("(espeak-ng not installed; run: jarvis setup)")

# ---------------------------------------------------------------- the brain
def ask(messages):
    body = json.dumps({"model": MODEL, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read()).get("message", {}).get("content", "")

# ---------------------------------------------------------------- do things
def is_dangerous(cmd):
    return any(re.search(p, cmd) for p in DANGEROUS)

def run_command(cmd):
    log(f"RUN: {cmd}")
    if is_dangerous(cmd) and not YOLO:
        return "I didn't run that — it looked destructive. Set JARVIS_YOLO=1 if you really mean it."
    try:
        # runs as the logged-in user, in their home directory
        p = subprocess.run(["bash", "-lc", cmd], cwd=os.path.expanduser("~"),
                           capture_output=True, text=True, timeout=120)
        out = (p.stdout or p.stderr).strip()
        log(out[:2000])
        return out
    except subprocess.TimeoutExpired:
        return "That command took too long, so I stopped it."
    except Exception as e:
        return f"That failed: {e}"

def handle(reply):
    """Speak the reply; run any <cmd>..</cmd> the model asked for."""
    cmds = re.findall(r"<cmd>(.*?)</cmd>", reply, flags=re.S)
    speak(reply)
    results = []
    for c in cmds:
        c = c.strip()
        if not c:
            continue
        print(f"  $ {c}")
        out = run_command(c)
        results.append((c, out))
    if results:
        # let JARVIS report the shortest useful bit of output out loud
        last = results[-1][1]
        if last and len(last) < 400:
            speak(last)
        else:
            speak("Done.")
    return results

# ---------------------------------------------------------------- listening
def listen_stream():
    import queue
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
    if not os.path.isdir(VOSK_MODEL):
        speak("My speech model is missing. Please run jarvis setup.")
        sys.exit(1)
    q = queue.Queue()
    def cb(indata, frames, t, status):
        q.put(bytes(indata))
    model = Model(VOSK_MODEL)
    rec = KaldiRecognizer(model, 16000)
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=cb):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                txt = json.loads(rec.Result()).get("text", "").strip()
                if txt:
                    yield txt

def listen_loop():
    speak(f"JARVIS online. Say my name, {USER}, and I'm listening.")
    history = [{"role": "system",
                "content": f"(The operator's name is {USER}. Keep spoken answers short.)"}]
    awake = False
    for text in listen_stream():
        print(f"heard: {text}")
        low = text.lower()
        if "jarvis" in low:
            text = re.sub(r"\bhey\b|\bjarvis\b", "", low).strip()
            awake = True
            if not text:
                speak(f"Yes, {USER}?")
                continue
        elif not awake:
            continue  # ignore chatter until addressed
        if low in ("stop", "quiet", "shut up", "that's all", "goodbye", "bye"):
            speak(f"Goodbye, {USER}.")
            return
        history.append({"role": "user", "content": text})
        try:
            reply = ask(history)
        except Exception as e:
            speak("I can't reach my brain. Is Ultron's engine running?")
            log(f"ollama error: {e}")
            continue
        history.append({"role": "assistant", "content": reply})
        handle(reply)
        history = history[:1] + history[-8:]  # keep context small
        awake = False  # require the name again for the next command

# ---------------------------------------------------------------- entry
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "listen"
    if cmd == "say":
        speak(" ".join(sys.argv[2:]) or "Hello.")
    elif cmd == "ask":
        q = " ".join(sys.argv[2:])
        handle(ask([{"role": "user", "content": q}]))
    elif cmd == "listen":
        try:
            listen_loop()
        except KeyboardInterrupt:
            print()
    else:
        print("usage: jarvis.py {listen|say <text>|ask <text>}")

if __name__ == "__main__":
    main()
