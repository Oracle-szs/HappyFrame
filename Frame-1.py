#!/usr/bin/env python3

import os
import tkinter as tk
from PIL import Image, ImageTk
import threading
import random
import pygame
import pyaudio
from vosk import Model, KaldiRecognizer
import json
import urllib.request
import zipfile
import shutil
from config import ConfigManager
from setup import run_setup

# ------------------------
# Paths
# ------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
MODELS_DIR = os.path.join(BASE_DIR, "models")

VOSK_MODEL_PATH = os.path.join(MODELS_DIR, "vosk-model-nl-spraakherkenning-0.6")

# Initialize config manager
CONFIG_MANAGER = ConfigManager(BASE_DIR)

# Load triggers from config
def load_triggers():
    """Load triggers from config file"""
    config = CONFIG_MANAGER.load_config()
    if not config or not config.get("triggers"):
        return {}
    
    # Convert config format to legacy format for compatibility
    triggers = {}
    for trigger_data in config["triggers"]:
        triggers[trigger_data["id"]] = {
            "images": trigger_data.get("images", []),
            "sounds": trigger_data.get("sounds", []),
            "phrases": trigger_data.get("phrases", [])
        }
    
    return triggers

TRIGGERS = load_triggers()

DEFAULT_CYCLE_INTERVAL = 5000
RESET_DELAY = 10000
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

# ------------------------
# Main class
# ------------------------

class HappyFrame:

    def __init__(self, root):

        print("[INIT] Starting HappyFrame")

        self.root = root
        root.attributes("-fullscreen", True)
        root.configure(bg="black")

        self.label = tk.Label(root, bg="black")
        self.label.pack(expand=True, fill="both")

        self.current_image = None

        print("[INIT] Initializing pygame mixer")
        pygame.mixer.init()

        print("[INIT] Loading trigger sounds")
        self.sounds = {}

        for trigger in TRIGGERS:
            self.sounds[trigger] = []

            for soundfile in TRIGGERS[trigger]["sounds"]:

                path = os.path.join(SOUND_DIR, soundfile)

                if os.path.exists(path):

                    print("[INIT] Loaded sound:", path)

                    self.sounds[trigger].append(
                        pygame.mixer.Sound(path)
                    )

                else:

                    print("[ERROR] Missing sound:", path)

        print("[INIT] Loading idle images")

        self.all_images = [

            f for f in os.listdir(IMAGE_DIR)

            if f.lower().endswith(VALID_EXTENSIONS)

        ]

        print("[INIT] Idle image count:", len(self.all_images))

        self.trigger_active = False
        self.reset_job = None
        self.cycle_job = None

        if self.all_images:
            self.start_default_cycle()
        else:
            print("[WARN] No idle images found - idle cycle disabled")

        print("[INIT] Starting Vosk thread")

        threading.Thread(
            target=self.vosk_loop,
            daemon=True
        ).start()

    # ------------------------
    # Image display
    # ------------------------

    def show_image(self, filename):

        try:

            path = os.path.join(IMAGE_DIR, filename)

            print("[IMAGE] Showing:", path)

            if not os.path.exists(path):

                print("[ERROR] Image missing:", path)
                return

            img = Image.open(path)

            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()

            img_w, img_h = img.size

            scale = min(
                1,
                screen_w / img_w,
                screen_h / img_h
            )

            if scale < 1:

                img = img.resize(
                    (
                        int(img_w * scale),
                        int(img_h * scale)
                    ),
                    Image.LANCZOS
                )

            self.current_image = ImageTk.PhotoImage(img)

            self.label.config(
                image=self.current_image
            )

        except Exception as e:

            print("[ERROR] show_image failed:", e)

    # ------------------------
    # Idle cycle
    # ------------------------

    def start_default_cycle(self):

        print("[STATE] Returning to idle cycle")

        self.trigger_active = False

        self.schedule_cycle()

    def schedule_cycle(self):

        if self.trigger_active:
            return

        if not self.all_images:
            print("[WARN] No idle images available, idle cycle disabled")
            return

        img = random.choice(self.all_images)

        self.show_image(img)

        self.cycle_job = self.root.after(
            DEFAULT_CYCLE_INTERVAL,
            self.schedule_cycle
        )

    # ------------------------
    # Trigger handler
    # ------------------------

    def handle_trigger(self, trigger):

        print("[TRIGGER] Activated:", trigger)

        try:

            self.trigger_active = True

            if self.cycle_job:

                self.root.after_cancel(
                    self.cycle_job
                )

            image = random.choice(
                TRIGGERS[trigger]["images"]
            )

            print("[TRIGGER] Selected image:", image)

            self.show_image(image)

            sounds = self.sounds.get(trigger, [])

            if sounds:

                snd = random.choice(sounds)

                print("[TRIGGER] Playing sound")

                snd.play()

            else:

                print("[WARNING] No sounds loaded")

            if self.reset_job:

                self.root.after_cancel(
                    self.reset_job
                )

            self.reset_job = self.root.after(
                RESET_DELAY,
                self.start_default_cycle
            )

        except Exception as e:

            print("[ERROR] Trigger failed:", e)

    # ------------------------
    # Find USB mic
    # ------------------------

    def find_mic(self, p):

        print("[AUDIO] Searching microphones")

        for i in range(p.get_device_count()):

            info = p.get_device_info_by_index(i)

            print(
                "[AUDIO]",
                i,
                info["name"]
            )

            if (
                info["maxInputChannels"] > 0
                and
                "MICROPHONE" in info["name"].upper()
            ):
                print(
                    "[AUDIO] Selected mic:",
                    info["name"]
                )
                return i

        return None

    # ------------------------
    # Model download
    # ------------------------

    def download_vosk_model(self):
        """Download and extract Vosk model if it doesn't exist"""
        model_dir = VOSK_MODEL_PATH
        model_zip = os.path.join(MODELS_DIR, "vosk-model-nl-spraakherkenning-0.6.zip")
        model_url = "https://alphacephei.com/vosk/models/vosk-model-nl-spraakherkenning-0.6.zip"

        if os.path.exists(model_dir):
            print("[VOSK] Model already exists")
            return True

        print("[VOSK] Model not found, downloading...")

        try:
            # Create models directory if it doesn't exist
            os.makedirs(MODELS_DIR, exist_ok=True)

            # Download the model
            print("[VOSK] Downloading model from alphacephei.com...")
            with urllib.request.urlopen(model_url) as response:
                with open(model_zip, 'wb') as f:
                    shutil.copyfileobj(response, f)

            # Extract the model
            print("[VOSK] Extracting model...")
            with zipfile.ZipFile(model_zip, 'r') as zip_ref:
                zip_ref.extractall(MODELS_DIR)

            # Clean up zip file
            os.remove(model_zip)

            print("[VOSK] Model downloaded and extracted successfully")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to download model: {e}")
            return False

    # ------------------------
    # Vosk loop
    # ------------------------

    def vosk_loop(self):

        print("[VOSK] Loading model")

        # Download model if it doesn't exist
        if not self.download_vosk_model():
            print("[ERROR] Could not load or download Vosk model")
            return

        model = Model(VOSK_MODEL_PATH)

        p = pyaudio.PyAudio()

        mic_index = self.find_mic(p)

        if mic_index is None:

            print("[ERROR] No microphone found")
            return

        info = p.get_device_info_by_index(mic_index)

        rate = int(info["defaultSampleRate"])

        print("[VOSK] Sample rate:", rate)

        rec = KaldiRecognizer(
            model,
            rate
        )

        stream = p.open(

            format=pyaudio.paInt16,

            channels=1,

            rate=rate,

            input=True,

            input_device_index=mic_index,

            frames_per_buffer=8192

        )

        stream.start_stream()

        print("[VOSK] Listening...")

        while True:

            data = stream.read(
                4096,
                exception_on_overflow=False
            )

            if rec.AcceptWaveform(data):

                result = json.loads(
                    rec.Result()
                )

                text = result.get(
                    "text",
                    ""
                ).lower()

                if text:

                    print(
                        "[HEARD]",
                        text
                    )

                    for trigger in TRIGGERS:

                        # Check if the trigger word is in the heard text
                        if trigger in text:

                            print(
                                "[MATCH]",
                                trigger
                            )

                            self.root.after(
                                0,
                                self.handle_trigger,
                                trigger
                            )

            else:

                partial = json.loads(
                    rec.PartialResult()
                )

                ptxt = partial.get(
                    "partial",
                    ""
                )

                if ptxt:

                    print(
                        "[PARTIAL]",
                        ptxt
                    )


# ------------------------
# Main
# ------------------------

if __name__ == "__main__":
    # Check if setup is needed
    if not TRIGGERS:
        print("[SETUP] No configuration found, launching setup wizard")
        run_setup(BASE_DIR)
        # Reload triggers after setup
        TRIGGERS = load_triggers()
        if not TRIGGERS:
            print("[ERROR] No triggers configured, exiting")
            exit(1)
    
    root = tk.Tk()
    app = HappyFrame(root)
    root.mainloop()