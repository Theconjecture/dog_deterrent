import threading
import time
from datetime import datetime as dt
import cv2
from yolo_predictor import YOLODetector
from whistle import start_whistle, stop_whistle
import numpy as np

# States
STATE_IDLE = "IDLE"
STATE_ACTIVE = "WHISTLE_ON"
STATE_COOLDOWN = "COOLDOWN"

class SharedData:
    def __init__(self):
        self.frame: Optional[np.ndarray] = None
        self.dog_detected = False
        self.lock = threading.Lock()
        self.running = True


def capture_and_detect(data: SharedData, detector: YOLODetector, video_source: str = 'dog.mp4'):
    camera = cv2.VideoCapture(video_source)
    while data.running:
        ret, frame = camera.read()
        if not ret:
            print("Camera error or end of video!")
            data.running = False
            break

        # Detect dogs
        boxes, indices = detector.detect(frame)
        detected = len(indices) > 0
        print(f"[DETECTION] Boxes: {len(indices)}")


        # Annotate frame
        for i in indices:
            print(boxes[i])
            x1, y1, x2, y2 = boxes[i]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Dog", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

        # Update shared data
        with data.lock:
            data.frame = frame
            data.dog_detected = detected

        time.sleep(0.03)  # throttle ~30 FPS
    camera.release()


def state_machine(data: SharedData):
    state = STATE_IDLE
    timer_start = 0.0

    while data.running:
        with data.lock:
            detected = data.dog_detected

        now_ts = dt.now().timestamp()

        if state == STATE_IDLE:
            if detected:
                print("Dog detected - starting whistle")
                start_whistle()
                timer_start = now_ts
                state = STATE_ACTIVE

        elif state == STATE_ACTIVE:
            if not detected:
                print("Dog lost - stopping whistle")
                stop_whistle()
                state = STATE_IDLE
                timer_start = 0.0
            elif now_ts - timer_start >= 10:
                print("10s passed - entering cooldown")
                stop_whistle()
                timer_start = now_ts
                state = STATE_COOLDOWN

        elif state == STATE_COOLDOWN:
            if not detected:
                print("Cooldown done, no dog - back to IDLE")
                state = STATE_IDLE
                timer_start = 0.0
            elif now_ts - timer_start >= 10:
                print("Cooldown done, dog still here - reactivating whistle")
                start_whistle()
                timer_start = now_ts
                state = STATE_ACTIVE

        # Optionally display frame with state overlay
        with data.lock:
            frame = data.frame.copy() if data.frame is not None else None
        if frame is not None:
            cv2.putText(frame, f"State: {state}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            cv2.putText(frame, f"Timer: {int(now_ts - timer_start)}s", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            cv2.imshow("Dog Detector", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                 data.running = False

        time.sleep(0.1)  # state checks every 100ms

    # Clean up
    stop_whistle()
    cv2.destroyAllWindows()


def main():
    detector = YOLODetector("best.onnx", "data.yaml")
    data = SharedData()

    # Threads
    t1 = threading.Thread(target=capture_and_detect, args=(data, detector), daemon=True)
    t2 = threading.Thread(target=state_machine, args=(data,), daemon=True)

    t1.start()
    t2.start()

    try:
        while data.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        data.running = False

    t1.join()
    t2.join()

if __name__ == '__main__':
    main()

