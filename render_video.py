import os
import requests
import json
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip, concatenate_videoclips, vfx, afx, ColorClip

# ==========================================
# 1. SETTINGS & PRO DESIGN (Earn Smart Hindi)
# ==========================================
HINDI_FONT_FILE = "Hindi.ttf" 
TARGET_W, TARGET_H = 1080, 1920 

# GitHub Actions / n8n Data Fetching
full_text = os.environ.get('FULL_TEXT', 'Paise kamane ka naya tarika.')
chat_id = os.environ.get('CHAT_ID')
webhook_url = os.environ.get('WEBHOOK_URL')
pexels_key = os.environ.get('PEXELS_API_KEY')
scenes_data = json.loads(os.environ.get('SCENES_DATA', '[]'))
resume_url = os.environ.get('RESUME_URL')

print(f"--- 🚀 EARN SMART HINDI: GENERATING VIRAL CONTENT ---")
print(f"Total Scenes: {len(scenes_data)}")

# ==========================================
# 2. PRO VOICE & SOUNDS
# ==========================================
# Voice: Swara (Professional & Authoritative)
print("Generating AI Voiceover...")
subprocess.run(['edge-tts', '--voice', 'hi-IN-SwaraNeural', '--text', full_text, '--write-media', 'voiceover.mp3'])

voiceover = AudioFileClip("voiceover.mp3")
# VIRAL HACK: 1.1x Speed boost for fast-paced retention
voiceover = voiceover.fx(vfx.speedx, 1.1)

total_chars = sum(len(s['text']) for s in scenes_data)
video_clips = []
audio_clips = [voiceover]
headers = {"Authorization": pexels_key}
current_time = 0.0

# Sound Effects
try:
    whoosh_sfx = AudioFileClip("whoosh.mp3").volumex(0.35)
    pop_sfx = AudioFileClip("pop.mp3").volumex(0.25)
except:
    whoosh_sfx = pop_sfx = None

# Wealth Colors: Green (Money), Yellow (Caution/Alert), Cyan (Tech), White
viral_colors = ['#39FF14', '#FFD400', '#00FFFF', '#FFFFFF'] 

# ==========================================
# 3. SCENE RENDERING (The Retention Machine)
# ==========================================
for i, scene in enumerate(scenes_data):
    keyword = scene.get('keyword', 'finance')
    text_line = scene.get('text', '')
    
    # Precise timing calculation based on sped-up voiceover
    scene_duration = voiceover.duration * (len(text_line) / max(total_chars, 1))
    if scene_duration < 1.2: scene_duration = 1.2
    
    try:
        # Pexels API - Adding 'finance' to keyword for earning niche visuals
        search_query = f"{keyword} finance technology"
        res = requests.get(f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=portrait", headers=headers).json()
        
        # Fallback if no video found
        if 'videos' in res and len(res['videos']) > 0:
            video_url = res['videos'][0]['video_files'][0]['link']
        else:
            print(f"No video found for {keyword}, using default abstract.")
            res = requests.get(f"https://api.pexels.com/videos/search?query=abstract technology&per_page=1&orientation=portrait", headers=headers).json()
            video_url = res['videos'][0]['video_files'][0]['link']
            
        vid_path = f"vid_{i}.mp4"
        with open(vid_path, "wb") as f:
            f.write(requests.get(video_url).content)
            
        clip = VideoFileClip(vid_path).subclip(0, scene_duration)
        
        # Resize and Crop for Vertical Shorts
        clip = clip.resize(height=TARGET_H)
        if clip.w < TARGET_W:
            clip = clip.resize(width=TARGET_W)
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=TARGET_W, height=TARGET_H)
        
        # Subtle Zoom & Dark Overlay
        zoomed_clip = clip.resize(lambda t: 1.0 + 0.05 * (t / scene_duration)).set_position(('center', 'center'))
        dark_overlay = ColorClip(size=(TARGET_W, TARGET_H), color=(0,0,0)).set_opacity(0.4).set_duration(scene_duration)
        
        # Fast Captions (2 words per screen)
        words = text_line.split(' ')
        chunk_size = 2 
        chunks = [' '.join(words[j:j + chunk_size]) for j in range(0, len(words), chunk_size)]
        
        word_clips = []
        duration_per_chunk = scene_duration / len(chunks)
        
        for w_i, chunk in enumerate(chunks):
            current_color = viral_colors[w_i % len(viral_colors)]
            
            # Positioned at Top-Center (500px) to avoid YouTube UI overlap
            txt_pos = ('center', 450)
            
            bg_txt = TextClip(chunk, fontsize=130, color='black', font=HINDI_FONT_FILE, stroke_color='black', stroke_width=20, method='caption', size=(950, None))
            bg_txt = bg_txt.set_position(txt_pos).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            main_txt = TextClip(chunk, fontsize=130, color=current_color, font=HINDI_FONT_FILE, stroke_color='black', stroke_width=4, method='caption', size=(950, None))
            main_txt = main_txt.set_position(txt_pos).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            word_clips.extend([bg_txt, main_txt])
        
        # Composite the scene
        final_scene = CompositeVideoClip([zoomed_clip, dark_overlay] + word_clips, size=(TARGET_W, TARGET_H)).set_duration(scene_duration)
        video_clips.append(final_scene)
        
        # Add SFX Timing
        if whoosh_sfx: audio_clips.append(whoosh_sfx.set_start(current_time))
        current_time += scene_duration
        print(f"✅ Scene {i+1} Ready: {keyword}")
        
    except Exception as e:
        print(f"❌ Error on scene {i}: {e}")

# ==========================================
# 4. FINAL STITCHING & BGM
# ==========================================
print("Stitching scenes together...")
final_video = concatenate_videoclips(video_clips, method="compose")

# Red Progress Bar (Engagement Hack)
progress_bar = ColorClip(size=(TARGET_W, 15), color=(255, 0, 0))
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
except: 
    print("Warning: bgm.mp3 not found. Skipping background music.")

final_video = final_video.set_audio(CompositeAudioClip(audio_clips))

# ==========================================
# 5. EXPORT & BULLETPROOF UPLOAD
# ==========================================
print("Rendering Final Video (Ultrafast Mode)...")
output_name = "final_video.mp4"
final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac", threads=4, bitrate="2000k", preset="ultrafast")

print("\n🚀 Starting Bulletproof Upload System...")
video_link = "Upload Failed"

# 4-Layer robust upload to prevent 'No Binary Data' errors
endpoints = [
    ("File.io", "https://file.io", "file", lambda r: r.json()['link']),
    ("Bashupload", "https://bashupload.com/", "file", lambda r: r.text.strip().split('\n')[0]),
    ("Uguu.se", "https://uguu.se/upload.php", "files[]", lambda r: r.json()['files'][0]['url']),
    ("Catbox.moe", "https://catbox.moe/user/api.php", "fileToUpload", lambda r: r.text.strip())
]

for name, url, field, get_link in endpoints:
    if video_link != "Upload Failed": break
    try:
        print(f"Trying upload to {name}...")
        files = {field: open(output_name, 'rb')}
        data = {'reqtype': 'fileupload'} if "catbox" in url else {}
        res = requests.post(url, files=files, data=data, timeout=300)
        
        if res.status_code == 200:
            link = get_link(res)
            if "http" in link: 
                video_link = link
                print(f"✅ Upload Success: {video_link}")
    except Exception as e: 
        print(f"❌ {name} failed: {e}")

# ==========================================
# 6. CALLBACK TO N8N WEBHOOK
# ==========================================
print(f"\n🔥 FINAL LINK: {video_link} 🔥")

payload = {
    "chat_id": chat_id, 
    "message": "✅ Bhai! Earn Smart Hindi Video Ready!", 
    "youtube_url": video_link
}

if resume_url:
    print(f"Resuming n8n workflow at: {resume_url}")
    try:
        requests.post(resume_url, json={"body": payload}, timeout=15)
        print("✅ Workflow Resumed Successfully.")
    except Exception as e:
        print(f"❌ Warning: Failed to resume n8n. Error: {e}")
