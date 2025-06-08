package main

import (
	"log"
	"time"
	"yourproject/whistle"
	"yourproject/yolo"
	"gocv.io/x/gocv"
)

type State int

const (
	StateIdle State = iota
	StateActive
	StateCooldown
)

func main() {
	// Init YOLO
	detector := yolo.New("best.onnx", "data.yaml")
	defer detector.Close()

	// Init Whistle
	whistle := whistle.New()
	defer whistle.Stop()
	defer rpio.Close()

	// State machine
	var (
		state       = StateIdle
		lastDogTime time.Time
		cooldown    = 10 * time.Second
		activeTime  = 10 * time.Second
	)

	// Camera
	webcam, _ := gocv.VideoCaptureDevice(0)
	defer webcam.Close()

	// Main loop
	for {
		frame := gocv.NewMat()
		if ok := webcam.Read(&frame); !ok {
			log.Println("Camera error")
			continue
		}

		// Run detection in goroutine (concurrent)
		dogDetected := make(chan bool)
		go func() {
			dogDetected <- detector.Detect(frame)
		}()

		// State machine logic
		select {
		case isDog := <-dogDetected:
			now := time.Now()
			switch state {
			case StateIdle:
				if isDog {
					whistle.Start()
					lastDogTime = now
					state = StateActive
				}

			case StateActive:
				if !isDog {
					whistle.Stop()
					state = StateIdle
				} else if now.Sub(lastDogTime) >= activeTime {
					whistle.Stop()
					state = StateCooldown
					lastDogTime = now
				}

			case StateCooldown:
				if !isDog {
					state = StateIdle
				} else if now.Sub(lastDogTime) >= cooldown {
					whistle.Start()
					state = StateActive
					lastDogTime = now
				}
			}
		}

		frame.Close()
	}
}
