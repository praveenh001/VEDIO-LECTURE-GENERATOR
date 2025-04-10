# VEDIO-LECTURE-GENERATOR

This is an AI-based web project that will convert the content provided by the user into a video with voiceover on slides. The system generates dynamic educational videos from user-provided content.

### **Overview**

The **Video-Lecture-Generator** is an educational video generation system that transforms user-provided content into a video with slides and clear audio narration. The project is designed to provide an easy-to-use platform for creating educational videos that can be used for online learning, presentations, and other educational purposes.

## Features

- **Text to Video Conversion**: Converts the user's provided text content into a video with slides, each slide containing a portion of the content. The video includes voiceover based on the text-to-speech synthesis of the provided content.
- **Voiceover on Slides**: Adds clear, intelligible voiceover to each slide of the video using Edge TTS or other text-to-speech engines.
- **Temporary File Handling**: Automatically deletes temporary files after the video is generated, keeping only the final video to optimize storage.
- **Dynamic Content Rendering**: Supports dynamic content changes, so users can see live previews and adjust content before final rendering.

## Requirements

To run this project, you need to have the following installed:

- **Python 3.8+**: Required for running the project.
- **FFmpeg**: Used for video processing (e.g., combining video and audio).
- **Edge TTS**: For converting text into speech (voiceover).
- **MoviePy**: A Python library for video editing.
- **Pillow**: A Python Imaging Library used for creating and processing images for the video slides.
- **Flask**: A lightweight Python web framework to handle the web interface and user interactions.

## Installation

Follow these steps to set up the **Video-Lecture-Generator** on your local machine:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/praveenh001/VEDIO-LECTURE-GENERATOR.git

2. **Create a Virtual Environment(optional)**:
   ```bash
   python -m venv venv
   venv\Scripts\activate

3. **nstall Dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Ensure Node.js is Installed**:
   ```bash
   node -v

5. **Running the Application**:
   ```bash
   python app.py
