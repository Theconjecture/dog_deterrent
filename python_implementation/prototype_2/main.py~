import time
from datetime import datetime as dt
from yolo_predictor import YOLODetector
#from whistle import start_whistle, stop_whistle
import cv2

STATE_IDLE = "IDLE"
STATE_ACTIVE = "WHISTLE_ON"
STATE_COOLDOWN = "COOLDOWN"

state = STATE_IDLE
timer = dt
timer_start: float = 0.0 
now = dt
camera = cv2.VideoCapture('../media/dog.mp4')

# Get video properties for the output file
frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(camera.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID' for AVI
out = cv2.VideoWriter('output_with_boxes.mp4', fourcc, fps, (frame_width, frame_height))

detector = YOLODetector("best.onnx", "data.yaml")


try:
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Camera error!")
            break
        
        # Get detections and draw boxes
        boxes, indices = detector.detect(frame)
        dog_detected = len(indices) > 0
        
        # Draw bounding boxes
        for i in indices:
            x1, y1, x2, y2 = boxes[i]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Dog", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
        
        # Display state info
        state_text = f"State: {state}"
        cv2.putText(frame, state_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
        # Show timer if active
        if state in [STATE_ACTIVE, STATE_COOLDOWN]:
            elapsed = now.now().timestamp() - timer_start
            timer_text = f"Timer: {elapsed}s"
            cv2.putText(frame, timer_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
        # Write the frame with boxes to output video
        out.write(frame)

        # Display frame
        #cv2.imshow("Dog Detector", frame) 

        if state == STATE_IDLE:
            if dog_detected:
                print("Dog detected - starting whistle")
                #start_whistle()
                timer_start = now.now().timestamp()
                state = STATE_ACTIVE

        elif state == STATE_ACTIVE:
            if not dog_detected:
                print("Dog lost - stopping whistle")
                #stop_whistle()
                state = STATE_IDLE
                timer_start = 0.0
            elif now.now().timestamp() - timer_start >= 10:
                print("10s passed - entering cooldown")
                #stop_whistle()
                timer_start = now.now().timestamp()
                state = STATE_COOLDOWN

        elif state == STATE_COOLDOWN:
            if not dog_detected:
                print("Cooldown done, no dog - back to IDLE")
                state = STATE_IDLE
                timer_start = 0.0
            elif now.now().timestamp() - timer_start >= 10:
                print("Cooldown done, dog still here - reactivating whistle")
                #start_whistle()
                timer_start = now.now().timestamp()
                state = STATE_ACTIVE


except KeyboardInterrupt:
    print("Exiting...")
    out.release()
    camera.release()
    #stop_whistle()
