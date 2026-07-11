<div align="center">

![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=28&pause=1000&color=00C9A7&center=true&vCenter=true&width=750&lines=%F0%9F%8F%A0+Touch-Free+Smart+Home+Control;Hand+Gesture+%2B+Arduino+%2B+Bluetooth;Computer+Vision+meets+Embedded+Systems)

<br/>

**Control home appliances using hand gestures — no touch, no remote, no voice.**
**Real-time hand tracking via MediaPipe → Bluetooth → Arduino → physical devices**

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-0097A7?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev)
[![Arduino](https://img.shields.io/badge/Arduino-C%2B%2B-00979D?style=for-the-badge&logo=arduino&logoColor=white)](https://arduino.cc)
[![Bluetooth](https://img.shields.io/badge/Bluetooth-Serial%20HC--05-0082FC?style=for-the-badge&logo=bluetooth&logoColor=white)](https://en.wikipedia.org/wiki/HC-05)
[![License](https://img.shields.io/badge/License-MIT-F4A261?style=for-the-badge)](LICENSE)

</div>

---

## <img src="https://img.shields.io/badge/-💡 Project Overview-0D1117?style=for-the-badge&labelColor=C0392B&color=E74C3C" />

**Touch-Free Smart Home Control System** is an IoT project that bridges **computer vision** and **embedded systems** to create a completely touchless home automation experience. A standard webcam captures the user's hand in real time, **Google MediaPipe** detects and tracks 21 hand landmarks, a custom finger-counting algorithm maps the gesture to a command, and that command is transmitted over **Bluetooth serial** to an **Arduino Uno** which switches real physical appliances ON or OFF — all in under a second.

This project was built and documented as a **group academic mini-project** with a full technical report (`PG05_REPORT.pdf`).

---

## <img src="https://img.shields.io/badge/-🔁 System Architecture-0D1117?style=for-the-badge&labelColor=117A65&color=1ABC9C" />

```
┌─────────────────────────────────────────────────────────┐
│                   PC / Laptop (Python)                   │
│                                                         │
│  Webcam  ──►  OpenCV  ──►  MediaPipe  ──►  Finger      │
│  (live feed)  (capture)   (21 landmarks) Count Logic   │
│                                              │           │
│                              Gesture → Command byte     │
│                                              │           │
│                         PySerial (Bluetooth COM6)       │
└──────────────────────────────────────────────┼──────────┘
                                               │ Bluetooth (HC-05)
                                               ▼
┌──────────────────────────────────────────────────────────┐
│                    Arduino Uno                           │
│                                                         │
│  Serial.read(command)                                   │
│       │                                                 │
│       ├── '1' → Fan ON      (Pin 2)                    │
│       ├── '2' → Fan OFF     (Pin 2)                    │
│       ├── '3' → Light ON    (Pin 3)                    │
│       ├── '4' → Light OFF   (Pin 3)                    │
│       ├── '5' → Pump ON     (Pin 5)                    │
│       ├── '6' → Pump OFF    (Pin 5)                    │
│       ├── '7' → Buzzer ON   (Pin 4)                    │
│       └── '8' → Buzzer OFF  (Pin 4)                    │
│                                                         │
│  Gas Sensor (A0) → auto Buzzer if gas > 400            │
│  16×2 LCD Display → shows real-time status             │
└──────────────────────────────────────────────────────────┘
```

---

## <img src="https://img.shields.io/badge/-🤚 Gesture Command Mapping-0D1117?style=for-the-badge&labelColor=6E2FBF&color=8E44AD" />

The Python script counts the number of raised fingers using **MediaPipe hand landmark positions** and maps each count to an appliance command sent over Bluetooth:

| Fingers Up | Gesture | Command Sent | Appliance Action |
|:---:|---|:---:|---|
| ✊ 0 fingers | Fist | `'2'` | **Fan → OFF** |
| ☝️ 1 finger | Index up | `'1'` | **Fan → ON** |
| ✌️ 2 fingers | Peace sign | `'3'` | **Light → ON** |
| 🤟 3 fingers | Three up | `'5'` | **Pump → ON** |
| 🖖 4 fingers | Four up | `'6'` | **Pump → OFF** |
| 🖐️ 5 fingers | Open palm | `'4'` | **Light → OFF** |

> **Debounce logic:** The same gesture must be held for **3 seconds** before a command is re-transmitted, preventing accidental rapid switching. On command send, the **Buzzer fires briefly** (`'7'` then `'8'`) as an audible confirmation beep.

---

## <img src="https://img.shields.io/badge/-🧠 How the Finger Counter Works-0D1117?style=for-the-badge&labelColor=1A5276&color=2980B9" />

MediaPipe returns 21 landmark points for a detected hand. The `count_fingers()` function uses landmark **y-coordinates** (and x-coordinate for the thumb) to determine which fingers are extended:

```python
def count_fingers(hand_landmarks):
    fingers = []

    # Thumb — compare x position of tip (4) vs knuckle (2)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[2].x:
        fingers.append(1)   # Thumb extended
    else:
        fingers.append(0)

    # Index, Middle, Ring, Pinky — compare tip y vs PIP joint y
    # A finger is "up" when its tip is above its second knuckle
    for tip in [8, 12, 16, 20]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)   # Total raised fingers: 0–5
```

> The frame is **mirrored** (`cv2.flip(frame, 1)`) before processing so that the on-screen hand matches the user's natural left/right orientation.

---

## <img src="https://img.shields.io/badge/-⚡ Arduino Hardware Layer-0D1117?style=for-the-badge&labelColor=0B5345&color=148F77" />

### Connected Components

| Component | Arduino Pin | Role |
|---|:---:|---|
| Fan (relay module) | `D2` | Controlled ON/OFF via commands `'1'` / `'2'` |
| LED / Light (relay) | `D3` | Controlled via commands `'3'` / `'4'` |
| Buzzer | `D4` | Audible confirmation beep + gas alarm |
| Water Pump (relay) | `D5` | Controlled via commands `'5'` / `'6'` |
| Gas Sensor (MQ-2) | `A0` | Analog read — auto-triggers buzzer if value > 400 |
| 16×2 LCD Display | `D6–D11` | Shows live appliance status |
| HC-05 Bluetooth | `TX/RX` | Receives serial commands from Python at 9600 baud |

### Gas Safety Feature

The Arduino independently monitors the gas sensor on every loop cycle. If the analog reading exceeds **400** (indicating dangerous gas concentration), the buzzer fires automatically for 5 seconds — completely independent of any gesture input. This runs **even if the Python script is disconnected**.

```cpp
int gasValue = analogRead(gasSensorPin);
if (gasValue > 400) {
    digitalWrite(buzzerPin, HIGH);
    lcd.clear();
    lcd.print("Gas Detected!");
    delay(5000);
    digitalWrite(buzzerPin, LOW);
}
```

---

## <img src="https://img.shields.io/badge/-🛠️ Tech Stack-0D1117?style=for-the-badge&labelColor=784212&color=A04000" />

| Layer | Technology | Purpose |
|---|---|---|
| Computer Vision | OpenCV (`cv2`) | Webcam capture, frame flipping, display window |
| Hand Tracking | MediaPipe (`mediapipe`) | Real-time 21-point hand landmark detection |
| Serial Communication | PySerial (`serial`) | Bluetooth serial communication to Arduino via HC-05 |
| Microcontroller | Arduino Uno (C++) | Hardware switching — relay control, LCD, gas sensing |
| Display | 16×2 LCD (`LiquidCrystal.h`) | Real-time appliance status on hardware display |
| Wireless Protocol | Bluetooth (HC-05, 9600 baud) | Wireless bridge between PC and Arduino |

---

## <img src="https://img.shields.io/badge/-📁 Project Structure-0D1117?style=for-the-badge&labelColor=1C2833&color=2C3E50" />

```
Touch-free-smart-home-control-system/
│
├── python.py           # PC-side — MediaPipe hand tracking + Bluetooth serial TX
├── Arduino.cpp         # Arduino-side — serial RX + relay switching + gas detection
└── PG05_REPORT.pdf     # Full technical project report
```

---

## <img src="https://img.shields.io/badge/-🚀 Getting Started-0D1117?style=for-the-badge&labelColor=4A235A&color=7D3C98" />

### Prerequisites

**Hardware required:**
- Arduino Uno
- HC-05 Bluetooth module
- MQ-2 Gas sensor
- 16×2 LCD display
- Relay modules (3×) for Fan, Light, Pump
- Buzzer
- A webcam (built-in or USB)

**Software required:**
- Python 3.10+
- Arduino IDE

### Step 1 — Flash the Arduino

Open `Arduino.cpp` in the Arduino IDE and upload it to your Arduino Uno. Ensure the HC-05 Bluetooth module is connected to the TX/RX pins.

### Step 2 — Python Setup

```bash
# Clone the repository
git clone https://github.com/engineermayur-07/Touch-free-smart-home-control-system.git
cd Touch-free-smart-home-control-system

# Install Python dependencies
pip install opencv-python mediapipe pyserial
```

### Step 3 — Configure Bluetooth Port

In `python.py`, update the COM port to match your system's Bluetooth serial port:

```python
# Windows
bluetooth = serial.Serial('COM6', 9600)

# Linux / macOS
bluetooth = serial.Serial('/dev/rfcomm0', 9600)
```

Pair the HC-05 module with your PC via Bluetooth settings first. Default pairing PIN: `1234` or `0000`.

### Step 4 — Run

```bash
python python.py
```

A window titled **"Gesture Control"** will open showing the live webcam feed with hand landmarks overlaid. Raise fingers to control appliances. Press `Q` to quit.

---

## <img src="https://img.shields.io/badge/-⚠️ Known Limitations-0D1117?style=for-the-badge&labelColor=7D6608&color=B7950B" />

- Finger counting is based on landmark positions, so **poor lighting** or **fast hand movement** can reduce accuracy
- The thumb detection uses x-axis comparison, which works for the **right hand**; left-hand gestures may behave differently
- Bluetooth range is limited to approximately **10 metres** (HC-05 Class 2)
- COM port is **hardcoded** — must be changed manually per system
- The 3-second debounce means rapid switching requires deliberate gesture holds

---

## <img src="https://img.shields.io/badge/-🔮 Future Improvements-0D1117?style=for-the-badge&labelColor=1C5985&color=2471A3" />

- [ ] Dynamic COM port detection — auto-scan for connected Bluetooth devices
- [ ] Two-hand gesture support for more commands
- [ ] Left/right hand detection for separate appliance zones
- [ ] GUI dashboard showing live appliance states
- [ ] Wi-Fi upgrade (ESP8266/ESP32) to remove Bluetooth range limitation
- [ ] Voice command fallback for accessibility

---

## <img src="https://img.shields.io/badge/-📄 Project Report-0D1117?style=for-the-badge&labelColor=0B3D2E&color=148F77" />

A complete technical report (`PG05_REPORT.pdf`) is included in the repository, covering:
- Problem statement and motivation
- System design and block diagram
- Component specifications
- Circuit schematic
- Results and observations
- Future scope

---

 

---

<div align="center">

<img src="https://img.shields.io/badge/Computer%20Vision-MediaPipe-0097A7?style=for-the-badge&logo=google&logoColor=white" />
&nbsp;
<img src="https://img.shields.io/badge/Embedded%20Systems-Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white" />
&nbsp;
<img src="https://img.shields.io/badge/Wireless-Bluetooth%20HC--05-0082FC?style=for-the-badge&logo=bluetooth&logoColor=white" />

<br/><br/>

*⭐ If this project impressed you, a star goes a long way!*

</div>
