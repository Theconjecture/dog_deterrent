package whistle

import (
	"log"
	"time"
	"github.com/stianeikeland/go-rpio/v4"
)

const (
	BuzzerPin = 14 // GPIO14 (Pin 8)
)

type WhistleController struct {
	active bool
}

func New() *WhistleController {
	if err := rpio.Open(); err != nil {
		log.Fatalf("Failed to init GPIO: %v", err)
	}
	return &WhistleController{}
}

func (w *WhistleController) Start() {
	if w.active {
		return
	}
	pin := rpio.Pin(BuzzerPin)
	pin.Output()
	pin.High() // Activate whistle
	w.active = true
}

func (w *WhistleController) Stop() {
	if !w.active {
		return
	}
	rpio.Pin(BuzzerPin).Low()
	w.active = false
}

func (w *WhistleController) Pulse(duration time.Duration) {
	w.Start()
	time.Sleep(duration)
	w.Stop()
}
