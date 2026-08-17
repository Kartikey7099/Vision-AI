# 👁️ Vision AI Studio

### Multimodal Computer Vision powered by Florence-2

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Streamlit-red?style=for-the-badge)](https://vision-ai-02.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-ee4c2c?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Transformers-yellow?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

> 🧠 An interactive multimodal Computer Vision workspace that uses **Florence-2** to understand, analyze and extract information from images through multiple vision-language tasks.

---

## 🚀 Live Demo

🌐 **Try Vision AI Studio:**  
https://vision-ai-02.streamlit.app/

---

## 📌 Overview

**Vision AI Studio** is a multimodal Computer Vision application built around Microsoft's **Florence-2 Vision-Language Model**.

The application provides a unified interface for performing multiple image-understanding tasks without requiring users to interact directly with model APIs or notebooks.

Users can provide images through:

- 📤 Image Upload
- 📷 Camera Capture
- 🔗 Image URL

and run different Florence-2 vision tasks from a single interactive workspace.

The application combines **Computer Vision, Vision-Language Models, PyTorch inference and Streamlit** into a practical AI application.

---

## ✨ Key Features

### 👁️ Multimodal Vision Tasks

Vision AI Studio currently supports **7 major Florence-2 capabilities**:

| Capability | Description |
|---|---|
| 🎯 Object Detection | Detect objects and identify their regions in an image |
| 📝 Image Captioning | Generate a concise description of an image |
| 📖 Detailed Caption | Generate a more descriptive image explanation |
| 📜 More Detailed Caption | Generate paragraph-level visual descriptions |
| 🧩 Dense Region Caption | Describe multiple regions of an image |
| 🔤 OCR | Extract text directly from images |
| ⌗ Region Proposal | Generate relevant regions within an image |

---

## 🖼️ Image Input

Multiple image sources are supported:

- 📤 **Upload** PNG, JPG, JPEG and WebP images
- 📷 **Camera** capture directly from the browser
- 🔗 **URL** based image loading

The selected image is then passed through the vision pipeline for analysis.

---

## ⚙️ Image Preprocessing

Before inference, images can be enhanced using configurable preprocessing controls:

- ☀️ Brightness adjustment
- 🎚️ Contrast adjustment
- ✨ Sharpness enhancement
- 🌈 RGB image conversion

This allows experimentation with image quality and its effect on model inference.

---

## 🧠 Florence-2 Vision Pipeline

The application uses Florence-2 as the core Vision-Language Model.

### Processing Flow

```text
             ┌──────────────────┐
             │   Image Input    │
             └────────┬─────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Upload       Camera       URL
          └───────────┼───────────┘
                      ▼
             ┌──────────────────┐
             │ Image Processing │
             │ Brightness       │
             │ Contrast         │
             │ Sharpness        │
             └────────┬─────────┘
                      ▼
             ┌──────────────────┐
             │ Florence-2       │
             │ Processor        │
             └────────┬─────────┘
                      ▼
             ┌──────────────────┐
             │ Florence-2 VLM   │
             │ PyTorch Inference│
             └────────┬─────────┘
                      ▼
             ┌──────────────────┐
             │ Generated Tokens │
             └────────┬─────────┘
                      ▼
             ┌──────────────────┐
             │ Post Processing  │
             └────────┬─────────┘
                      ▼
             ┌──────────────────┐
             │ Vision Result    │
             └──────────────────┘
