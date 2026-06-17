🎯 Real-Time Sudoku Solver

A Computer Vision and Deep Learning project that detects a Sudoku puzzle from a live webcam feed, recognizes digits using a CNN, solves the puzzle using backtracking, and overlays the solution back onto the physical board in real time.

✨ Features
Real-time Sudoku board detection
Perspective correction using homography
Grid line removal and digit extraction
CNN-based digit recognition
Custom fine-tuning for challenging Sudoku fonts
Temporal voting across multiple frames to reduce OCR noise
Sudoku validity checks before solving
Backtracking-based Sudoku solver
Augmented Reality overlay of solved digits

🛠️ Tech Stack
Python
OpenCV
TensorFlow / Keras
NumPy
Imutils

🔍 Pipeline
Webcam Feed
    ↓
Board Detection
    ↓
Perspective Transform
    ↓
Digit Segmentation
    ↓
CNN Recognition
    ↓
Temporal Voting
    ↓
Sudoku Validation
    ↓
Backtracking Solver
    ↓
AR Overlay

🚀 Highlights
Uses multiple geometric checks to ensure correct Sudoku detection.
Aggregates predictions from 15 consecutive frames using majority voting for robust digit recognition.
Fine-tuned the CNN with custom-generated Sudoku-style digits to improve accuracy on real-world puzzles.
Projects the solved puzzle back onto the original board using homography.

📸 Example

![alt text](image.png)

🚧 Challenges Solved
Noisy Digit Recognition

Real-world camera feeds often produce inconsistent digit predictions due to lighting changes, blur, shadows, and slight camera movement.

Solution: Implemented temporal voting across 15 consecutive frames, using majority voting to obtain stable digit predictions.

Sudoku Font Variations

A model trained only on MNIST struggled with certain Sudoku-style digits, especially 1, 4, and 5.

Solution: Fine-tuned the CNN using custom-generated digit samples and targeted augmentation for commonly misclassified digits.

False Sudoku Detections

Many rectangular objects and contours can resemble Sudoku boards.

Solution: Added multiple validation stages including:

Quadrilateral contour detection
Aspect ratio checks
Minimum area constraints
Minimum digit count requirements
Sudoku rule validation before solving
Perspective Distortion

Sudoku boards are rarely perfectly aligned with the camera.

Solution: Applied perspective transformation and homography to obtain a top-down board view and accurately project the solution back onto the original frame.

Real-Time Performance

Running detection, OCR, solving, and rendering every frame can introduce instability.

Solution: Designed a lightweight pipeline combining OpenCV preprocessing, CNN inference, temporal aggregation, and efficient backtracking for smooth real-time operation.