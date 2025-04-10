import os
import edge_tts
import asyncio
import textwrap
import time
import datetime
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from threading import Lock, Thread

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/videos'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Progress tracking
progress_data = {}
progress_lock = Lock()
FONT_PATH = "arial.ttf"  # Make sure this font exists or provide full path

def update_progress(task_id, progress, status):
    with progress_lock:
        progress_data[task_id] = {'progress': progress, 'status': status, 'filename': None}

def create_slide_image(text, index):
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(FONT_PATH, 40)
    except:
        font = ImageFont.load_default()

    wrapper = textwrap.TextWrapper(width=40)
    wrapped_text = wrapper.fill(text=text)

    text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    x = (width - (text_bbox[2] - text_bbox[0])) // 2
    y = (height - (text_bbox[3] - text_bbox[1])) // 2

    draw.text((x, y), wrapped_text, fill=(0, 0, 0), font=font)
    slide_path = f"slide_{index}.png"
    image.save(slide_path)
    return slide_path

async def generate_voice(text, audio_path):
    communicate = edge_tts.Communicate(text, voice="hi-IN-SwaraNeural")
    await communicate.save(audio_path)

def generate_video_task(text, task_id):
    try:
        update_progress(task_id, 0, "Initializing...")
        
        # Create output filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        out_file = f"video_{timestamp}.mp4"
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_file)

        # Proper paragraph splitting
        paragraphs = []
        current_paragraph = []
        for line in text.split('\n'):
            stripped = line.strip()
            if stripped:  # If line has content
                current_paragraph.append(stripped)
            else:  # Empty line indicates paragraph break
                if current_paragraph:  # Only add if we have content
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
        # Add the last paragraph if exists
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))

        if not paragraphs:
            update_progress(task_id, 100, "Error: No content")
            return

        total_steps = len(paragraphs) + 4  # intro + slides + outro + render
        current_step = 0

        clips = []
        temp_files = []

        # Create intro
        update_progress(task_id, 5, "Creating intro...")
        intro_img = create_slide_image("Educational Video", "intro")
        temp_files.append(intro_img)
        intro_clip = ImageClip(intro_img).set_duration(3)
        clips.append(intro_clip)
        current_step += 1

        # Process each paragraph as a separate slide
        for idx, para in enumerate(paragraphs):
            progress = int((current_step / total_steps) * 90)
            update_progress(task_id, progress, f"Creating slide {idx+1}/{len(paragraphs)}")
            
            # Create slide
            slide_img = create_slide_image(para, idx)
            temp_files.append(slide_img)
            
            # Generate audio
            audio_path = f"audio_{idx}.mp3"
            try:
                asyncio.run(generate_voice(para, audio_path))
            except Exception as e:
                update_progress(task_id, 100, f"Error generating audio: {str(e)}")
                return
            
            temp_files.append(audio_path)
            
            # Create clip
            try:
                audio_clip = AudioFileClip(audio_path)
                slide_clip = ImageClip(slide_img).set_duration(audio_clip.duration)
                slide_clip = slide_clip.set_audio(audio_clip)
                clips.append(slide_clip)
                current_step += 1
            except Exception as e:
                update_progress(task_id, 100, f"Error creating clip: {str(e)}")
                return

        # Create outro
        update_progress(task_id, 92, "Creating outro...")
        outro_img = create_slide_image("Thanks for watching!", "outro")
        temp_files.append(outro_img)
        outro_clip = ImageClip(outro_img).set_duration(3)
        clips.append(outro_clip)
        current_step += 1

        # Render final video
        update_progress(task_id, 95, "Rendering video...")
        try:
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(
                out_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="ultrafast",
                logger=None
            )
            
            # Update with filename when complete
            with progress_lock:
                progress_data[task_id]['filename'] = out_file
                progress_data[task_id]['progress'] = 100
                progress_data[task_id]['status'] = "Complete!"
                
        except Exception as e:
            update_progress(task_id, 100, f"Error rendering video: {str(e)}")
            return

    except Exception as e:
        update_progress(task_id, 100, f"Unexpected error: {str(e)}")
    finally:
        # Cleanup temporary files
        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Could not delete {file_path}: {str(e)}")
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if text := request.form.get('content', '').strip():
            task_id = str(time.time())
            Thread(target=generate_video_task, args=(text, task_id)).start()
            return redirect(url_for('show_progress', task_id=task_id))
        return render_template('index.html', error="Please enter some content")
    return render_template('index.html')

@app.route('/progress/<task_id>')
def show_progress(task_id):
    return render_template('progress.html', task_id=task_id)

@app.route('/get_progress/<task_id>')
def get_progress(task_id):
    with progress_lock:
        return jsonify(progress_data.get(task_id, {
            'progress': 0, 
            'status': 'Starting...',
            'filename': None
        }))

@app.route('/video/<filename>')
def show_video(filename):
    return render_template('video.html', video_file=filename)

@app.route('/static/videos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
