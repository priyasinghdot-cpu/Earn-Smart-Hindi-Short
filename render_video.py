import os
import requests
import json
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip, concatenate_videoclips, vfx, afx, ImageClip, ColorClip

# 1. Configuration & Constants
HINDI_FONT_FILE = "Hindi.ttf" 
TARGET_W, TARGET_H = 1080, 1920 # Vertical Shorts Format

# Environment Variables (Passed from GitHub Actions)
full_text = os.environ.get('FULL_TEXT', 'Ek naya earning idea.')
chat_id = os.environ.get('CHAT_ID')
webhook_url = os.environ.get('WEBHOOK_URL')
pexels_key = os.environ.get('PEXELS_API_KEY')
scenes_data = json.loads(os.environ.get('SCENES_DATA', '[]'))
resume_url = os.environ.get('RESUME_URL')

print(f"Starting Render for Earn Smart Hindi. Scenes: {len(scenes_data)}")

# 2. GENERATE AI VOICEOVER 
# Professional & Energetic voice for Earning Tips
subprocess.run(['edge-tts', '--voice', 'hi-IN-SwaraNeural', '--text', full_text, '--write-media', 'voiceover.mp3'])

voiceover = AudioFileClip("voiceover.mp3")
total_chars = sum(len(s['text']) for s in scenes_data)
video_clips = []
audio_clips = [voiceover]
headers = {"Authorization": pexels_key}
current_time = 0.0

# Wealth & Attention Colors (Green & Yellow)
viral_colors = ['#39FF14', '#FFD400', '#FFFFFF', '#00FFFF'] 

# Sound Effects for Fast-Paced Edits
try:
    whoosh_sfx = AudioFileClip("whoosh.mp3").volumex(0.3)
    pop_sfx = AudioFileClip("pop.mp3").volumex(0.2)
except:
    whoosh_sfx = pop_sfx = None

# 3. PROCESS EACH SCENE
for i, scene in enumerate(scenes_data):
    keyword = scene.get('keyword', 'money')
    text_line = scene.get('text', '')
    
    # Timing sync based on character length
    scene_duration = voiceover.duration * (len(text_line) / max(total_chars, 1))
    if scene_duration < 1.2: scene_duration = 1.2
    
    try:
        # Pexels API - Optimized search for Earning Visuals
        search_query = f"{keyword} technology" 
        res = requests.get(f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=portrait", headers=headers).json()
        video_url = res['videos'][0]['video_files'][0]['link']
        
        vid_path = f"vid_{i}.mp4"
        with open(vid_path, "wb") as f:
            f.write(requests.get(video_url).content)
            
        clip = VideoFileClip(vid_path).subclip(0, scene_duration)
        clip = clip.resize(height=TARGET_H)
        if clip.w < TARGET_W:
            clip = clip.resize(width=TARGET_W)
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=TARGET_W, height=TARGET_H)
        
        # Subtle Zoom & Dark Overlay
        zoomed_clip = clip.resize(lambda t: 1.0 + 0.05 * (t / scene_duration))
        dark_overlay = ColorClip(size=(TARGET_W, TARGET_H), color=(0,0,0)).set_opacity(0.4).set_duration(scene_duration)
        
        # Fast Captions (2 words per screen)
        words = text_line.split(' ')
        chunk_size = 2 
        chunks = [' '.join(words[j:j + chunk_size]) for j in range(0, len(words), chunk_size)]
        
        word_clips = []
        duration_per_chunk = scene_duration / len(chunks)
        
        for w_i, chunk in enumerate(chunks):
            current_color = viral_colors[w_i % len(viral_colors)]
            
            # Positioned at 500 (Top-Center) to avoid YouTube UI overlap
            txt_pos = ('center', 500)
            
            bg_txt = TextClip(chunk, fontsize=130, color='black', font=HINDI_FONT_FILE, stroke_color='black', stroke_width=20, method='caption', size=(950, None))
            bg_txt = bg_txt.set_position(txt_pos).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            main_txt = TextClip(chunk, fontsize=130, color=current_color, font=HINDI_FONT_FILE, stroke_color='black', stroke_width=4, method='caption', size=(950, None))
            main_txt = main_txt.set_position(txt_pos).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            word_clips.extend([bg_txt, main_txt])
        
        final_scene = CompositeVideoClip([zoomed_clip, dark_overlay] + word_clips, size=(TARGET_W, TARGET_H)).set_duration(scene_duration)
        video_clips.append(final_scene)
        
        if whoosh_sfx: audio_clips.append(whoosh_sfx.set_start(current_time))
        current_time += scene_duration
        print(f"Scene {i+1} Ready: {keyword}")
        
    except Exception as e:
        print(f"Error on scene {i}: {e}")

# 4. FINAL STITCHING
final_video = concatenate_videoclips(video_clips, method="compose")

# Red Progress Bar (Engagement Hack)
progress_bar = ColorClip(size=(TARGET_W, 20), color=(255, 0, 0))
progress_bar = progress_bar.set_position(lambda t: (-TARGET_W + int(TARGET_W * (t / final_video.duration)), 'bottom'))
progress_bar = progress_bar.set_duration(final_video.duration)

final_video = CompositeVideoClip([final_video, progress_bar])

# Background Music (Upbeat/Lo-fi for Finance)
try:
    bgm = AudioFileClip("bgm.mp3").volumex(0.12)
    if bgm.duration < final_video.duration:
        bgm = afx.audio_loop(bgm, duration=final_video.duration)
    else:
        bgm = bgm.subclip(0, final_video.duration)
    audio_clips.append(bgm)
except: pass

final_video = final_video.set_audio(CompositeAudioClip(audio_clips))

# 5. EXPORT & UPLOAD
print("Rendering Final Video...")
output_name = "final_video.mp4"
final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac", threads=4, bitrate="2000k", preset="ultrafast")

# Multi-Layer Upload System
video_link = "Upload Failed"
endpoints = [
    ("0x0.st", "https://0x0.st", "file"),
    ("Uguu.se", "https://uguu.se/upload.php", "files[]"),
    ("Catbox.moe", "https://catbox.moe/user/api.php", "fileToUpload")
]

for name, url, field in endpoints:
    try:
        files = {field: open(output_name, 'rb')}
        data = {'reqtype': 'fileupload'} if "catbox" in url else {}
        res = requests.post(url, files=files, data=data, timeout=300)
        if res.status_code == 200:
            link = res.text.strip()
            if "http" in link:
                video_link = link if "catbox" in url else (res.json()['files'][0]['url'] if "uguu" in url else link)
                break
    except: continue

# 6. NOTIFY TELEGRAM / N8N
payload = {"chat_id": chat_id, "message": "✅ Bhai! Earn Smart Hindi Video Ready!", "youtube_url": video_link}
if resume_url:
    requests.post(resume_url, json={"body": payload})
    print(f"Workflow Resumed. Video: {video_link}")
