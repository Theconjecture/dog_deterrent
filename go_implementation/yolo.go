package yolo

import (
	"gocv.io/x/gocv"
)

type Detector struct {
	net    gocv.Net
	labels []string
}

func New(modelPath, yamlPath string) *Detector {
	net := gocv.ReadNetFromONNX(modelPath)
	if net.Empty() {
		panic("Failed to load YOLO model")
	}
	labels := loadLabels(yamlPath)
	return &Detector{net: net, labels: labels}
}

func (d *Detector) Detect(frame gocv.Mat) bool {
	blob := gocv.BlobFromImage(frame, 1.0/255.0, imageSize, gocv.NewScalar(0, 0, 0, 0), true, false)
	defer blob.Close()
	d.net.SetInput(blob, "")
	prob := d.net.Forward("")
	defer prob.Close()

	// Detection logic here (simplified)
	return hasDog(prob)
}
