import asyncio
import edge_tts
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import threading
import time
import tempfile
import os

VOICE = "hi-IN-SwaraNeural"

# Text to Speech function
async def generate_tts(text, speed, output_path, progress_var):
    try:
        rate_map = {"Slow": "-20%", "Normal": "0%", "Fast": "+20%"}
        communicate = edge_tts.Communicate(text, VOICE, rate=rate_map[speed])

        with open(output_path, "wb") as f:
            total_chunks = 0
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                    total_chunks += 1
                    progress_var.set(f"Processing... {total_chunks*5} KB approx.")
            progress_var.set("✅ Done!")
    except Exception as e:
        progress_var.set("❌ Error!")
        messagebox.showerror("Error", str(e))

# Play audio safely with pygame
def play_audio(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

def pause_audio():
    pygame.mixer.music.pause()

def resume_audio():
    pygame.mixer.music.unpause()

def stop_audio():
    pygame.mixer.music.stop()

# Main GUI
def start_tts():
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("No text", "Please paste some text.")
        return

    speed = speed_var.get()
    progress_var.set("Starting...")
    temp_path = os.path.join(tempfile.gettempdir(), "tts_output.mp3")

    threading.Thread(target=lambda: asyncio.run(generate_tts(text, speed, temp_path, progress_var))).start()
    play_path.set(temp_path)

def download_file():
    save_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
    if save_path and os.path.exists(play_path.get()):
        with open(play_path.get(), "rb") as src, open(save_path, "wb") as dst:
            dst.write(src.read())
        messagebox.showinfo("Saved", f"Audio saved to {save_path}")

# GUI setup
root = tk.Tk()
root.title("TTS TOOL BY UTKARSHCSE2026")
root.geometry("600x500")
root.configure(bg="#222")

# Text box
text_box = tk.Text(root, wrap="word", font=("Arial", 12), height=12, width=60)
text_box.pack(pady=10)

# Speed select
speed_var = tk.StringVar(value="Normal")
tk.Label(root, text="Select Speed:", fg="white", bg="#222", font=("Arial", 12)).pack()
tk.OptionMenu(root, speed_var, "Slow", "Normal", "Fast").pack(pady=5)

# Buttons
tk.Button(root, text="Generate Speech", font=("Arial", 12), command=start_tts, bg="green", fg="white").pack(pady=5)

btn_frame = tk.Frame(root, bg="#222")
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Play", command=lambda: play_audio(play_path.get()), bg="blue", fg="white", width=8).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Pause", command=pause_audio, bg="orange", fg="black", width=8).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Resume", command=resume_audio, bg="purple", fg="white", width=8).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Stop", command=stop_audio, bg="red", fg="white", width=8).grid(row=0, column=3, padx=5)

tk.Button(root, text="Download", command=download_file, bg="gray", fg="white", font=("Arial", 12)).pack(pady=5)

# Progress label
progress_var = tk.StringVar(value="Idle...")
tk.Label(root, textvariable=progress_var, fg="yellow", bg="#222", font=("Arial", 12)).pack(pady=5)

# Store current file path
play_path = tk.StringVar()

root.mainloop()
