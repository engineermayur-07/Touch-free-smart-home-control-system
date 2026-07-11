import cv2
import mediapipe as mp
import serial
import time

# Bluetooth setup
bluetooth = serial.Serial('COM6', 9600)
time.sleep(2)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

last_command = None
last_sent_time = time.time()

def count_fingers(hand_landmarks):
    fingers = []
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[2].x:
        fingers.append(1)
    else:
        fingers.append(0)
    for tip in [8, 12, 16, 20]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return sum(fingers)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    current_command = None

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            fingers_up = count_fingers(hand)

            if fingers_up == 1: current_command = b'1'
            elif fingers_up == 2: current_command = b'3'
            elif fingers_up == 3: current_command = b'5'
            elif fingers_up == 4: current_command = b'6'
            elif fingers_up == 0: current_command = b'2'
            elif fingers_up == 5: current_command = b'4'

    current_time = time.time()
    if current_command == last_command:
        if current_time - last_sent_time > 3 and current_command is not None:
            bluetooth.write(current_command)
            bluetooth.write(b'7')
            time.sleep(1)
            bluetooth.write(b'8')
            last_sent_time = current_time
    else:
        last_command = current_command
        last_sent_time = current_time

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
bluetooth.close()
cv2.destroyAllWindows()
