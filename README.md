
# 👁️ REHBAR (رہبر) - AI Assistive Vision System

> **"Digital Vision for the Visually Impaired"**

Rehbar is a real-time, AI-powered computer vision application designed specifically to assist blind and visually impaired individuals in navigating their environments. Acting as a digital guide, the system uses a camera to detect objects in the user's path and provides instant auditory feedback, significantly enhancing independence and spatial awareness.

## ✨ Key Features

* **Real-Time Object Detection:** Powered by the lightweight and highly efficient **YOLO** (You Only Look Once) architecture, capable of identifying 80+ everyday objects with high accuracy.
* **Intelligent Audio Feedback:** Converts visual data into spoken alerts using offline Text-to-Speech (TTS). 
* **Smart Repetition Cooldown:** Implements a 5-second "smart delay" to prevent audio spam when the user is standing in front of a stationary object.
* **Database Logging:** Automatically records every detection event (Object ID, Name, Accuracy Score, and Timestamp) into a secure local SQLite database for safety auditing and history tracking.
* **Evidence Snapshot:** A one-click tool to capture and save high-resolution images of the current camera feed.
* **Accessible Dashboard:** Features a high-contrast, modern dark-themed GUI built with CustomTkinter, allowing guardians or supervisors to easily monitor and configure the system.
* **Custom Object Mapping:** Includes built-in logic to translate or rename default AI object classes into custom vocabulary for better user context.

---

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **Computer Vision:** OpenCV (`cv2`), Ultralytics YOLO
* **Graphical Interface:** CustomTkinter (`ctk`), Pillow (`PIL`)
* **Database:** SQLite3
* **Audio Engine:** Pyttsx3 (Offline TTS)

---

## 🚀 Getting Started

### Prerequisites
* A laptop or desktop running Windows, macOS, or Linux.
* Python 3.10 or higher installed (Ensure "Add Python to PATH" is checked during installation).
* A built-in webcam or an external USB camera.

### Installation

1. **Clone or Download the Repository:**
   ```bash
   git clone [https://github.com/your-username/Rehbar-AI.git](https://github.com/your-username/Rehbar-AI.git)
   cd Rehbar-AI
   ```

2. **Install Required Dependencies:**
   Run the following command in your terminal to install all necessary libraries:
   ```bash
   pip install ultralytics opencv-python customtkinter pillow pyttsx3
   ```

3. **Run the Application:**
   ```bash
   python main_rehbar.py
   ```
   *(Note: On the first run, the system will automatically download the lightweight YOLO weights file to your directory).*

---

## 💻 Usage Guide

Once the Rehbar dashboard is open, sighted users or guardians can configure the system using the right-hand control panel:

1. **Start System:** Clicks initialize the camera and AI engine. The system will announce its startup audibly.
2. **Stop System:** Safely releases the camera hardware and pauses the AI.
3. **Voice Feedback Toggle:** Enables or disables the spoken alerts.
4. **Snapshot:** Saves the current frame to the `/captures` directory.
5. **View Logs:** Opens a separate window displaying the localized detection database.

---

## 🔮 Future Enhancements

* **Distance Estimation:** Integration of depth-sensing logic to announce how far an object is (e.g., "Chair, 2 meters ahead").
* **Facial Recognition:** Adding the ability to register and recognize specific family members or friends.
* **Mobile Portability:** Migrating the core logic to Android/iOS for use on smartphones.

---

## 👨‍💻 Developer Information

**Developed by:** Mohammad Umair  
**Institution:** National University of Technology (NUTECH), Islamabad  
**Project Type:** Academic / Assistive Technology  

---
*Disclaimer: This software is a functional prototype designed for educational and assistive purposes. Users should not rely solely on this application for navigation in highly dangerous or traffic-heavy environments.*
```
