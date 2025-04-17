# 🕊️ Sandhill Crane Detection Using AI

This project leverages deep learning and image slicing techniques to detect and count **Sandhill Cranes** in aerial thermal imagery. It combines object detection models (YOLOv5) with efficient inference strategies (SAHI) and is being extended into a fully deployable app with MLOps best practices.

> 📌 Ongoing collaboration with wildlife conservation efforts to monitor crane populations in protected habitats.

---

## 🌱 Project Goals

- Detect Sandhill Cranes in aerial thermal images using deep learning
- Improve inference accuracy using Sliced Aided Hyper Inference (SAHI)
- Build a user-facing web app where users can upload images and receive bird counts with bounding boxes
- Refactor training/inference pipelines for reproducibility and deployment
- Deploy the app using **AWS + Docker + Streamlit**

---

## 🛠️ Tools & Technologies

- **YOLOv5**: Object detection architecture (via Ultralytics)
- **SAHI**: Efficient inference on large images through slicing
- **PyTorch**: Model training & experimentation
- **OpenCV**: Image preprocessing
- **Streamlit**: UI for uploading and visualizing results
- **AWS S3 + Lambda** (planned): Hosting and model serving
- **Docker**: Containerized deployment
- **GitHub Actions + DVC** (in progress): CI/CD and data/model versioning

---

## 📈 Key Features

- 🖼️ Handles large aerial images with small, sparse bird targets
- 📦 Modular pipeline for training, evaluation, and inference
- 📸 Returns output image with bounding boxes and crane count
- 🌐 Web app in development to allow non-technical users to interact with the model
