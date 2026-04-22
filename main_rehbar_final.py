import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import sys
import time
import os
import sqlite3
import pyttsx3
import threading
from datetime import datetime

# ---------------- Configuration ----------------
MODEL_NAME = "yolov8n.pt"  
CONFIDENCE_THRESHOLD = 0.5
SPEECH_COOLDOWN = 5  # Seconds to wait before repeating voice

class RehbarProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- 1. Window Setup ----------------
        self.title("REHBAR - Assistive Vision System")
        self.geometry("1280x720")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- 2. System Initialization ----------------
        self.ensure_directories()
        self.init_db()
        self.model = self.load_model()
        self.classNames = self.model.names
        
        # Runtime variables
        self.cap = None
        self.running = False
        self.unique_ids = set()
        self.last_speech_time = {} 
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0

        # ---------------- 3. Build UI ----------------
        self.build_sidebar()
        self.build_video_area()
        
        # Init Voice in background
        threading.Thread(target=self.init_voice_engine, daemon=True).start()

    def ensure_directories(self):
        if not os.path.exists("captures"): os.makedirs("captures")

    def init_db(self):
        try:
            self.conn = sqlite3.connect("rehbar_log.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_id INTEGER,
                    object_name TEXT,
                    accuracy TEXT,
                    date_time TEXT
                )
            """)
            self.conn.commit()
            print("✔ Database Connected")
        except Exception as e:
            print(f"❌ Database Error: {e}")

    def init_voice_engine(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say("Rehbar Started")
            engine.runAndWait()
        except: pass

    def speak(self, text):
        def run_speech():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            except: pass
        t = threading.Thread(target=run_speech)
        t.start()

    def save_to_db(self, track_id, object_name, accuracy):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO detections (track_id, object_name, accuracy, date_time) VALUES (?, ?, ?, ?)",
                            (track_id, object_name, accuracy, timestamp))
        self.conn.commit()

    def load_model(self):
        print(f"Initializing Rehbar AI ({MODEL_NAME})...")
        try:
            return YOLO(MODEL_NAME)
        except Exception as e:
            sys.exit(f"❌ Model Error: {e}")

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=1, sticky="nsew")

        # Branding
        self.logo_label = ctk.CTkLabel(self.sidebar, text="REHBAR", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(padx=20, pady=(30, 10))
        ctk.CTkLabel(self.sidebar, text="AI Guide for the Blind", text_color="gray").pack(pady=(0, 20))

        # Controls
        self.btn_start = ctk.CTkButton(self.sidebar, text="▶ START SYSTEM", fg_color="#2CC985", command=self.start_camera)
        self.btn_start.pack(padx=20, pady=10, fill="x")

        self.btn_stop = ctk.CTkButton(self.sidebar, text="⏹ STOP SYSTEM", fg_color="#E74C3C", command=self.stop_camera)
        self.btn_stop.pack(padx=20, pady=5, fill="x")

        # Voice Toggle
        self.audio_var = ctk.BooleanVar(value=True)
        self.chk_audio = ctk.CTkCheckBox(self.sidebar, text="Voice Feedback", variable=self.audio_var)
        self.chk_audio.pack(padx=20, pady=20)

        # Database Tools
        ctk.CTkLabel(self.sidebar, text="Data Tools", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.btn_snap = ctk.CTkButton(self.sidebar, text="📸 SNAPSHOT", command=self.take_snapshot, fg_color="#3498DB")
        self.btn_snap.pack(padx=20, pady=5, fill="x")
        
        self.btn_history = ctk.CTkButton(self.sidebar, text="📂 VIEW LOGS", fg_color="#9B59B6", command=self.view_history)
        self.btn_history.pack(padx=20, pady=5, fill="x")

        # Live Log
        ctk.CTkLabel(self.sidebar, text="Live Feed", font=ctk.CTkFont(weight="bold")).pack(pady=(30, 5))
        self.log_box = ctk.CTkTextbox(self.sidebar, height=100, text_color="#00FF00", font=("Consolas", 11))
        self.log_box.pack(padx=10, pady=5, fill="x", expand=True)

    def build_video_area(self):
        self.video_frame = ctk.CTkFrame(self, fg_color="#1a1a1a") 
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_label = ctk.CTkLabel(self.video_frame, text="REHBAR \nSystem Ready", font=("Arial", 20))
        self.video_label.pack(expand=True, fill="both")

    def log_message(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end") 

    def view_history(self):
        win = ctk.CTkToplevel(self)
        win.title("Rehbar Database Logs")
        win.geometry("700x400")
        
        txt = ctk.CTkTextbox(win, width=680, height=380)
        txt.pack(padx=10, pady=10)
        
        self.cursor.execute("SELECT * FROM detections ORDER BY id DESC LIMIT 50")
        rows = self.cursor.fetchall()
        
        txt.insert("1.0", f"{'ID':<5} | {'OBJECT':<12} | {'ACCURACY':<10} | {'TIME':<20}\n")
        txt.insert("end", "-"*60 + "\n")
        
        for row in rows:
            txt.insert("end", f"{row[1]:<5} | {row[2]:<12} | {row[3]:<10} | {row[4]:<20}\n")
        txt.configure(state="disabled")

    def start_camera(self):
        if not self.running:
            # TRY INDEX 0 FIRST
            self.cap = cv2.VideoCapture(0)
            
            # --- CAMERA CHECK ---
            if not self.cap.isOpened():
                self.log_message("❌ ERR: Cam 0 Failed. Trying Cam 1...")
                # TRY INDEX 1 (External Camera)
                self.cap = cv2.VideoCapture(1)
                if not self.cap.isOpened():
                    self.log_message("❌ CRITICAL: No Camera Found!")
                    self.speak("Camera Failure")
                    return

            self.running = True
            self.log_message("System Started")
            self.speak("System Started")
            self.update_frame()

    def stop_camera(self):
        self.running = False
        if self.cap: self.cap.release()
        self.video_label.configure(image=None, text="SYSTEM STOPPED")
        self.speak("System Stopped")

    def take_snapshot(self):
        if hasattr(self, 'current_frame'):
            filename = f"captures/Rehbar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR))
            self.log_message(f"Saved: {filename}")

    def update_frame(self):
        if self.running and self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                # 1. Performance
                self.frame_count += 1
                elapsed = time.time() - self.start_time
                if elapsed > 1:
                    self.fps = self.frame_count / elapsed
                    self.frame_count = 0
                    self.start_time = time.time()

                frame = cv2.resize(frame, (960, 540)) 
                results = self.model.track(frame, persist=True, verbose=False, conf=CONFIDENCE_THRESHOLD)
                
                overlay = frame.copy() # For transparency
                current_time = time.time()

                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        class_name = self.classNames[cls]

                        # --- OVERRIDE OBJECT NAME HERE ---
                        if class_name == "toothbrush":
                            class_name = "pen"
                        # ---------------------------------
                        
                        # --- 1. ACCURACY ONLY (No Time) ---
                        conf = float(box.conf[0])
                        accuracy_str = f"{int(conf * 100)}%"
                        
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        obj_id = int(box.id[0]) if box.id is not None else 0
                        
                        # --- 2. PRO VISUALS ---
                        color = (0, 255, 0) # Green
                        
                        # Box Drawing
                        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Label (REMOVED TIMESTAMP)
                        label = f"ID:{obj_id} | {class_name} | {accuracy_str}"
                        
                        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
                        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                        # --- 3. LOGIC (Voice & DB) ---
                        last_time = self.last_speech_time.get(obj_id, 0)
                        
                        if (current_time - last_time) > SPEECH_COOLDOWN:
                            self.last_speech_time[obj_id] = current_time
                            self.save_to_db(obj_id, class_name, accuracy_str)
                            msg = f"{class_name} detected"
                            self.log_message(msg)
                            if self.audio_var.get():
                                self.speak(msg)

                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
                
                # HUD (FPS only)
                cv2.putText(frame, f"REHBAR AI | FPS: {self.fps:.1f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                # GUI Update
                self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_tk = ImageTk.PhotoImage(Image.fromarray(self.current_frame))
                self.video_label.configure(image=img_tk, text="")
                self.video_label.image = img_tk

            self.after(10, self.update_frame)

if __name__ == "__main__":
    app = RehbarProApp()
    app.mainloop()