import os
import sys
import time
import requests
import json
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip, concatenate_videoclips, vfx, afx, ColorClip

# Force immediate log flushing
sys.stdout.reconfigure(line_buffering=True)

# ==========================================
# 1. SETTINGS & PRO DESIGN (Earn Smart Hindi)
# ==========================================
HINDI_FONT_FILE = "Hindi.ttf" 
TARGET_W, TARGET_H = 1080, 1920 

chat_id = os.environ.get('CHAT_ID')
pexels_key = os.environ.get('PEXELS_API_KEY')
scenes_data = json.loads(os.environ.get('SCENES_DATA', '[]'))
resume_url = os.environ.get('RESUME_URL')

print("\n--- 🚀 EARN SMART HINDI: GENERATING VIRAL CONTENT ---")
print(f"Total Scenes to process: {len(scenes_data)}\n")

video_clips = []
master_audio_clips = []
current_time = 0.0
headers = {"Authorization": pexels_key}

try:
    whoosh_sfx = AudioFileClip("whoosh.mp3").volumex(0.35)
except:
    whoosh_sfx = None

viral_colors = ['#39FF14', '#FFD400', '#00FFFF', '#FFFFFF'] 

# ==========================================
# 3. SCENE RENDERING
# ==========================================
for i, scene in enumerate(scenes_data):
    print(f"\n--- [SCENE {i+1}/{len(scenes_data)}] ---")
    keyword = scene.get('keyword', 'finance')
    text_line = scene.get('text', '').strip()
    
    if not text_line:
        print(f"Skipping empty text.")
        continue

    audio_path = f"voice_scene_{i}.mp3"
    temp_txt_path = f"temp_{i}.txt"
    
    try:
        print(f"Step A: Saving text to temp file...")
        with open(temp_txt_path, "w", encoding="utf-8") as f:
            f.write(text_line)
            
        print(f"Step B: Generating Voiceover with edge-tts...")
        # 100% Hang-proof command execution (using file input -f)
        cmd = ["edge-tts", "--voice", "hi-IN-SwaraNeural", "-f", temp_txt_path, "--write-media", audio_path]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Cleanup temp text file immediately
        if os.path.exists(temp_txt_path): os.remove(temp_txt_path)
        
        print(f"Step C: Processing Audio speed...")
        scene_audio = AudioFileClip(audio_path).fx(vfx.speedx, 1.1)
        scene_duration = scene_audio.duration
        master_audio_clips.append(scene_audio.set_start(current_time))
        if whoosh_sfx: master_audio_clips.append(whoosh_sfx.set_start(current_time))
        
    except Exception as e:
        print(f"❌ Audio Error on scene {i+1}: {e}")
        continue
    
    try:
        print(f"Step D: Fetching Pexels API (keyword: {keyword})...")
        search_query = f"{keyword} finance technology"
        try:
            res = requests.get(f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=portrait", headers=headers, timeout=10).json()
        except requests.exceptions.Timeout:
            print("Pexels API Timeout! Using fallback URL.")
            res = {'videos': []}

        if 'videos' in res and len(res['videos']) > 0:
            video_url = res['videos'][0]['video_files'][0]['link']
        else:
            print("Using abstract fallback video...")
            res = requests.get("https://api.pexels.com/videos/search?query=abstract technology&per_page=1&orientation=portrait", headers=headers, timeout=10).json()
            video_url = res['videos'][0]['video_files'][0]['link']
            
        vid_path = f"vid_{i}.mp4"
        print(f"Step E: Downloading Pexels MP4...")
        with open(vid_path, "wb") as f:
            f.write(requests.get(video_url, timeout=15).content)
            
        print(f"Step F: Creating Video Composition...")
        clip = VideoFileClip(vid_path).subclip(0, scene_duration)
        clip = clip.resize(height=TARGET_H)
        if clip.w < TARGET_W:
            clip = clip.resize(width=TARGET_W)
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=TARGET_W, height=TARGET_H)
        
        zoomed_clip = clip.resize(lambda t: 1.0 + 0.05 * (t / scene_duration)).set_position(('center', 'center'))
        dark_overlay = ColorClip(size=(TARGET_W, TARGET_H), color=(0,0,0)).set_opacity(0.4).set_duration(scene_duration)
        
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
        
        final_scene = CompositeVideoClip([zoomed_clip, dark_overlay] + word_clips, size=(TARGET_W, TARGET_H)).set_duration(scene_duration)
        video_clips.append(final_scene)
        
        current_time += scene_duration
        print(f"✅ Scene {i+1} Done. (Length: {scene_duration:.2f}s)")
        
    except Exception as e:
        print(f"❌ Video Error on scene {i+1}: {e}")

# Cleanup all audio MP3s
for i in range(len(scenes_data)):
    if os.path.exists(f"voice_scene_{i}.mp3"): os.remove(f"voice_scene_{i}.mp3")

# ==========================================
# 4. FINAL STITCHING & EXPORT
# ==========================================
print("\n🔄 [STAGE 2] Stitching scenes together...")
final_video = concatenate_videoclips(video_clips, method="compose")

progress_bar = ColorClip(size=(TARGET_W, 15), color=(255, 0, 0))
progress_bar = progress_bar.set_position(lambda t: (-TARGET_W + int(TARGET_W * (t / final_video.duration)), 'bottom'))
progress_bar = progress_bar.set_duration(final_video.duration)

final_video = CompositeVideoClip([final_video, progress_bar])

try:
    bgm = AudioFileClip("bgm.mp3").volumex(0.12)
    if bgm.duration < final_video.duration:
        bgm = afx.audio_loop(bgm, duration=final_video.duration)
    else:
        bgm = bgm.subclip(0, final_video.duration)
    master_audio_clips.append(bgm)
except: pass

final_video = final_video.set_audio(CompositeAudioClip(master_audio_clips))

print("\n🎬 [STAGE 3] Rendering Final MP4...")
output_name = "final_video.mp4"
final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac", threads=2, bitrate="1500k", preset="ultrafast")

print("\n🚀 [STAGE 4] Starting Upload Process...")
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
        print(f"📤 Uploading to {name}...")
        files = {field: open(output_name, 'rb')}
        data = {'reqtype': 'fileupload'} if "catbox" in url else {}
        res = requests.post(url, files=files, data=data, timeout=300) 
        
        if res.status_code == 200:
            link = get_link(res)
            if "http" in link: 
                video_link = link
                print(f"✅ Link Success: {video_link}")
    except Exception as e: 
        print(f"❌ {name} failed: {e}")

# ==========================================
# 6. CALLBACK TO N8N
# ==========================================
print(f"\n🔥 FULL PIPELINE COMPLETE! Link: {video_link} 🔥")

if resume_url:
    payload = {"chat_id": chat_id, "message": "✅ Bhai! Video Ready!", "youtube_url": video_link}
    try:
        requests.post(resume_url, json={"body": payload}, timeout=15)
        print("✅ Resume ping sent to n8n.")
    except Exception as e:
        print(f"❌ Failed to resume n8n: {e}")
