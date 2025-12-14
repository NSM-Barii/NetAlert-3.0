import sounddevice as sd
import queue
import json
import numpy as np
import samplerate
from vosk import Model, KaldiRecognizer

# === CONFIG ===
MODEL_PATH = "models/vosk-model-small-en-us-0.15"
TARGET_RATE = 16000
WAKE_PHRASE = "yoda"
LISTEN_SECONDS = 5

# === INIT ===
print("[Yoda] Loading model...")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, TARGET_RATE)

# === MIC SETUP ===
def find_mic():
    for i, dev in enumerate(sd.query_devices()):
        if dev['max_input_channels'] > 0:
            try:
                sd.check_input_settings(device=2, samplerate=48000)
                print(f"[Mic] Using: {dev['name']} (index {i})")
                return i, int(dev['default_samplerate'])
            except Exception:
                continue
    raise RuntimeError("❌ No usable mic found.")

print(find_mic())
device_index, native_rate = 0, 48000

# === RECORDING ===
def record_block(seconds):
    audio = []

    def callback(indata, frames, time, status):
        if status:
            pass; print("Mic status:", status)
        audio.extend(indata[:, 0])

    with sd.InputStream(samplerate=native_rate, channels=1, dtype='float32',
                        callback=callback, device=device_index):
        print(f"[Yoda] Recording for {seconds} seconds...")
        sd.sleep(int(seconds * 1000))

    return np.array(audio)

# === RESAMPLE ===
def resample_audio(audio):
    resampler = samplerate.Resampler(converter_type='sinc_fastest')
    return resampler.process(audio, TARGET_RATE / native_rate)

# === TRANSCRIBE ===
def transcribe(audio):
    audio_int16 = (audio * 32767).astype(np.int16).tobytes()
    if rec.AcceptWaveform(audio_int16):
        result = json.loads(rec.Result())
    else:
        result = json.loads(rec.FinalResult())
    return result.get("text", "")

# === MAIN ===
def run_yoda():
    from nsm_modules.nsm_main import Main
    Main.run()
    print("[Yoda] Say 'Hey Yoda' to wake me up...\n")
    while True:
        wake_audio = record_block(LISTEN_SECONDS)
        wake_resampled = resample_audio(wake_audio)
        transcript = transcribe(wake_resampled)

        if not transcript:
            continue

       # print(f"[STT] Heard: '{transcript}'")

        if WAKE_PHRASE in transcript.lower():
            print("[Yoda] Wake word detected.")
            cmd_audio = record_block(LISTEN_SECONDS)
            cmd_resampled = resample_audio(cmd_audio)
            command = transcribe(cmd_resampled)
            print(f"[Yoda] Command: '{command}'\n")
            if "attack" in command:
                from yoda_controller import ARP_Poison
                ARP_Poison.main(router_ip="192.168.1.1", iface="wlan0")

if __name__ == "__main__":
    run_yoda()
