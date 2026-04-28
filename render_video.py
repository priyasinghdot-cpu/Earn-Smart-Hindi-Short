import os
import sys
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
chat_id = os.environ.get('CHAT_ID')
webhook_url = os.environ.get('WEBHOOK_URL')
pexels_key = os.environ.get('PEXELS_API_KEY')
scenes_data = json.loads(os.environ.get('SCENES_DATA', '[]'))
resume_url = os.environ.get('RESUME_URL')

print(f"--- 🚀 EARN SMART HINDI: GENERATING VIRAL CONTENT ---")
print(f"Total Scenes to render: {len(scenes_data)}")

video_clips = []
master_audio_clips = []
current_time = 0.0
headers = {"Authorization": pexels_key}

# Sound Effects
try:
    whoosh_sfx = AudioFileClip("whoosh.mp3").volumex(0.35)
    pop_sfx = AudioFileClip("pop.mp3").volumex(0.25)
except:
    whoosh_sfx = pop_sfx = None

viral_colors = ['#39FF14', '#FFD400', '#00FFFF', '#FFFFFF'] 

# ==========================================
# 3. SCENE RENDERING (100% PERFECT SYNC & NO HANGS)
# ==========================================
for i, scene in enumerate(scenes_data):
    print(f"\n---> Starting Scene {i+1}...")
    keyword = scene.get('keyword', 'finance')
    text_line = scene.get('text', '').strip()
    
    if not text_line:
        continue

    audio_path = f"voice_scene_{i}.mp3"
    temp_txt_path = "temp_text.txt"
    
    try:
        # ✅ ANTI-HANG FIX 1: Text ko file mein save karo taaki terminal quotes se confuse na ho
        with open(temp_txt_path, "w", encoding="utf-8") as f:
            f.write(text_line)
            
        print(f"[{i+1}] Generating audio via edge-tts...")
        # Direct file passing (-f) avoids all command line injection hangs
        subprocess.run([sys.executable, "-m", "edge_tts", "--voice", "hi-IN-SwaraNeural", "-f", temp_txt_path, "--write-media", audio_path], check=True)
        
        # Load audio and speed it up
        scene_audio = AudioFileClip(audio_path).fx(vfx.speedx, 1.1)
        scene_duration = scene_audio.duration
        
        # Add voiceover and sfx to the master audio timeline
        master_audio_clips.append(scene_audio.set_start(current_time))
        if whoosh_sfx: master_audio_clips.append(whoosh_sfx.set_start(current_time))
        
    except Exception as e:
        print(f"❌ Audio generation failed on scene {i+1}: {e}")
        continue
    
    try:
        print(f"[{i+1}] Fetching video from Pexels for keyword: '{keyword}'...")
        # ✅ ANTI-HANG FIX 2: Strict timeouts added (15 seconds)
        search_query = f"{keyword} finance technology"
        res = requests.get(f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=portrait", headers=headers, timeout=15).json()
        
        if 'videos' in res and len(res['videos']) > 0:
            video_url = res['videos'][0]['video_files'][0]['link']
        else:
            print(f"[{i+1}] No video found, fetching fallback...")
            res = requests.get(f"https://api.pexels.com/videos/search?query=abstract technology&per_page=1&orientation=portrait", headers=headers, timeout=15).json()
            video_url = res['videos'][0]['video_files'][0]['link']
            
        print(f"[{i+1}] Downloading video file...")
        vid_path = f"vid_{i}.mp4"
        with open(vid_path, "wb") as f:
            # ✅ Added timeout to video download as well
            f.write(requests.get(video_url, timeout=30).content)
            
        print(f"[{i+1}] Processing Video and Text formatting...")
        clip = VideoFileClip(vid_path).subclip(0, scene_duration)
        
        # Resize and Crop
        clip = clip.resize(height=TARGET_H)
        if clip.w < TARGET_W:
            clip = clip.resize(width=TARGET_W)
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=TARGET_W, height=TARGET_H)
        
        # Zoom & Dark Overlay
        zoomed_clip = clip.resize(lambda t: 1.0 + 0.05 * (t / scene_duration)).set_position(('center', 'center'))
        dark_overlay = ColorClip(size=(TARGET_W, TARGET_H), color=(0,0,0)).set_opacity(0.4).set_duration(scene_duration)
        
        # 2-Word Fast Captions exactly synced to the scene_duration
        words = text_line.split(' ')
        chunk_size = 2 
        chunks = [' '.join(words[j:j + chunk_size]) for j in range(0, len(words), chunk_size)]
        
        word_clips = []
        duration_per_chunk = scene_duration / max(len(chunks), 1)
        
        for w_i, chunk in enumerate(chunks):
            current_color = viral_colors[w_i % len(viral_colors)]
            txt_pos = ('center', 450)
            
            bg_txt = TextClip(chunk, fontsize=130, color='black', font=HINDI_FONT_FILE, stroke_color='black', stroke_width=20, method='caption', size=(950, None))
            bg_txt = bg_txt.set_position(txt_pos).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            main_txt = TextClip(chunk, fontsize=130, color=current_color, font=HINDI_FONT_FILE, stroke_color='black', stroke_width=4, method='caption', size=(950, None))
            main_txt = main_txt.set_position(txt_pos).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            word_clips.extend([bg_txt, main_txt])
        
        # Combine video and text for this exact duration
        final_scene = CompositeVideoClip([zoomed_clip, dark_overlay] + word_clips, size=(TARGET_W, TARGET_H)).set_duration(scene_duration)
        video_clips.append(final_scene)
        
        # Move timeline forward by exact audio length
        current_time += scene_duration
        print(f"✅ Scene {i+1} Successfully Completed! ({scene_duration:.2f}s)")
        
    except Exception as e:
        print(f"❌ Error rendering scene {i+1}: {e}")

# Cleanup temp file
if os.path.exists("temp_text.txt"):
    os.remove("temp_text.txt")

# ==========================================
# 4. FINAL STITCHING & AUDIO MIXING
# ==========================================
print("\n🔄 Stitching all scenes together (This may take a few minutes)...")
final_video = concatenate_videoclips(video_clips, method="compose")

# Red Progress Bar
progress_bar = ColorClip(size=(TARGET_W, 15), color=(255, 0, 0))
progress_bar = progress_bar.set_position(lambda t: (-TARGET_W + int(TARGET_W * (t / final_video.duration)), 'bottom'))
progress_bar = progress_bar.set_duration(final_video.duration)

final_video = CompositeVideoClip([final_video, progress_bar])

# Background Music
try:
    print("🎵 Adding Background Music...")
    bgm = AudioFileClip("bgm.mp3").volumex(0.12)
    if bgm.duration < final_video.duration:
        bgm = afx.audio_loop(bgm, duration=final_video.duration)
    else:
        bgm = bgm.subclip(0, final_video.duration)
    master_audio_clips.append(bgm)
except: 
    print("Warning: bgm.mp3 not found. Skipping BGM.")

# Apply perfectly synced master audio timeline to video
final_video = final_video.set_audio(CompositeAudioClip(master_audio_clips))

# ==========================================
# 5. EXPORT & BULLETPROOF UPLOAD
# ==========================================
print("\n🎬 Rendering Final Video...")
output_name = "final_video.mp4"
# ✅ ANTI-HANG FIX 3: Threads changed from 4 to 2 to prevent GitHub Runner freezing
final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac", threads=2, bitrate="2000k", preset="ultrafast")

print("\n🚀 Starting Bulletproof Upload System...")
video_link = "Upload Failed"

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
        # Keep upload timeout generous since video files are large
        res = requests.post(url, files=files, data=data, timeout=300) 
        
        if res.status_code == 200:
            link = get_link(res)
            if "http" in link: 
                video_link = link
                print(f"✅ Upload Success: {video_link}")
    except Exception as e: 
        print(f"❌ {name} failed: {e}")

# ==========================================
# 6. CALLBACK TO N8N
# ==========================================
print(f"\n🔥 FINAL LINK: {video_link} 🔥")

payload = {
    "chat_id": chat_id, 
    "message": "✅ Bhai! Earn Smart Hindi Video Ready (Perfect Sync)! 🔥", 
    "youtube_url": video_link
}

if resume_url:
    try:
        requests.post(resume_url, json={"body": payload}, timeout=15)
        print("✅ Workflow Resumed Successfully.")
    except Exception as e:
        print(f"❌ Warning: Failed to resume n8n. Error: {e}")
