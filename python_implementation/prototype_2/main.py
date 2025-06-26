import threading
import time
from datetime import datetime as dt
import cv2
from yolo_predictor import YOLODetector
import numpy as np
from typing import Optional

# States
STATE_IDLE = "IDLE"
STATE_ACTIVE = "WHISTLE_ON"
STATE_COOLDOWN = "COOLDOWN"
frate = 30 

detector = YOLODetector("best.onnx", "data.yaml")
class SharedData:
    def __init__(self):
        self.frame: Optional[np.ndarray] = None
        self.processed_frame: Optional[np.ndarray] = None
        self.dog_detected = False
        self.lock = threading.Lock()
        self.running = True
        self.new_frame_event = threading.Event()  # Signals when new frame is available
        self.frame_processed = threading.Event()  # Signals when frame processing is done

def capture_and_detect(data: SharedData, detector: YOLODetector, video_source: int = 0):
    camera = cv2.VideoCapture(video_source)
    
    # Get video properties for the output file
    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(camera.get(cv2.CAP_PROP_FPS))
    frate = fps
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('../media/output_with_boxes.mp4', fourcc, fps, (frame_width, frame_height))
    
    try:
        while data.running:
            ret, frame = camera.read()
            if not ret:
                print("Camera error or end of video!")
                data.running = False
                break

            # Signal that we have a new frame to process
            with data.lock:
                data.frame = frame
                data.new_frame_event.set()

            # Wait for state machine to process the frame
            if data.frame_processed.wait(timeout=1/fps):
                data.frame_processed.clear()
                
                # Write the processed frame to output video
                with data.lock:
                    if data.processed_frame is not None:
                        out.write(data.processed_frame)
    finally:
        camera.release()
        out.release()
        data.new_frame_event.set()  # Ensure state machine can exit

def state_machine(data: SharedData):
    state = STATE_IDLE
    timer_start = 0.0
    frame_counter = 0

    while data.running:
        # Wait for a new frame to be available
        if not data.new_frame_event.wait(timeout=1.0):
            continue  # Timeout, check if we should still run
        
        data.new_frame_event.clear()
        frame_counter += 1
        print(f"Processing frame {frame_counter}")

        with data.lock:
            frame = data.frame
            if frame is None:
                continue

        # Detect dogs
        boxes, indices = detector.detect(frame)
        detected = len(indices) > 0

        # Annotate frame
        annotated_frame = frame.copy()
        for i in indices:
            x1, y1, x2, y2 = boxes[i]
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, "Dog", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

        # State machine logic
        now_ts = dt.now().timestamp()

        if state == STATE_IDLE:
            if detected:
                print(f"Frame {frame_counter}: Dog detected - starting whistle")
                #start_whistle()
                timer_start = now_ts
                state = STATE_ACTIVE

        elif state == STATE_ACTIVE:
            if not detected:
                print(f"Frame {frame_counter}: Dog lost - stopping whistle")
                #stop_whistle()
                state = STATE_IDLE
                timer_start = 0.0
            elif now_ts - timer_start >= 10:
                print(f"Frame {frame_counter}: 10s passed - entering cooldown")
                #stop_whistle()
                timer_start = now_ts
                state = STATE_COOLDOWN

        elif state == STATE_COOLDOWN:
            if not detected:
                print(f"Frame {frame_counter}: Cooldown done, no dog - back to IDLE")
                state = STATE_IDLE
                timer_start = 0.0
            elif now_ts - timer_start >= 10:
                print(f"Frame {frame_counter}: Cooldown done, dog still here - reactivating whistle")
                #start_whistle()
                timer_start = now_ts
                state = STATE_ACTIVE

        # Store the processed frame and detection result
        with data.lock:
            data.processed_frame = annotated_frame
            data.dog_detected = detected
            data.frame_processed.set()  # Signal that processing is complete

    # Clean up
    #stop_whistle()

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
            time.sleep(1/frate)
    except KeyboardInterrupt:
        print("Stopping...")
        data.running = False

    t1.join()
    t2.join()

if __name__ == '__main__':
    main()
