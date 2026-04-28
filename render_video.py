import os
import sys
import requests
import json
import subprocess
# ✅ Use Native Async Edge-TTS
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip, concatenate_videoclips, vfx, afx, ColorClip

# Force standard output to be unbuffered (immediate logs in GitHub Actions)
sys.stdout.reconfigure(line_buffering=True)

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

print(f"\n--- 🚀 EARN SMART HINDI: GENERATING VIRAL CONTENT ---")
print(f"Total Scenes to render: {len(scenes_data)}\n")

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
# 3. SCENE RENDERING (Perfect Sync & Anti-Hang)
# ==========================================
for i, scene in enumerate(scenes_data):
    print(f"▶️ [START] Scene {i+1}...")
    keyword = scene.get('keyword', 'finance')
    text_line = scene.get('text', '').strip()
    
    if not text_line:
        print(f"⏭️ Skipping empty scene {i+1}")
        continue

    audio_path = f"voice_scene_{i}.mp3"
    
    try:
        print(f"   🎙️ Generating AI Voiceover...")
        
        # ✅ ANTI-HANG FIX 1: Native Python Async Call (No Subprocess/Terminal commands)
        async def generate_voice():
            communicate = edge_tts.Communicate(text_line, "hi-IN-SwaraNeural")
            await communicate.save(audio_path)
            
        asyncio.run(generate_voice())
        
        print(f"   ✅ Audio generated.")
        
        # Load audio and speed it up
        scene_audio = AudioFileClip(audio_path).fx(vfx.speedx, 1.1)
        scene_duration = scene_audio.duration
        
        master_audio_clips.append(scene_audio.set_start(current_time))
        if whoosh_sfx: master_audio_clips.append(whoosh_sfx.set_start(current_time))
        
    except Exception as e:
        print(f"❌ Error generating audio for scene {i+1}: {e}")
        continue
    
    try:
        print(f"   🎥 Fetching video for keyword: '{keyword}'...")
        # ✅ ANTI-HANG FIX 2: Strict Network Timeouts
        search_query = f"{keyword} finance technology"
        res = requests.get(f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=portrait", headers=headers, timeout=10).json()
        
        if 'videos' in res and len(res['videos']) > 0:
            video_url = res['videos'][0]['video_files'][0]['link']
        else:
            print(f"   ⚠️ No video found, using fallback...")
            res = requests.get(f"https://api.pexels.com/videos/search?query=abstract technology&per_page=1&orientation=portrait", headers=headers, timeout=10).json()
            video_url = res['videos'][0]['video_files'][0]['link']
            
        print(f"   ⬇️ Downloading video...")
        vid_path = f"vid_{i}.mp4"
        with open(vid_path, "wb") as f:
            f.write(requests.get(video_url, timeout=20).content)
            
        print(f"   ✂️ Processing Text & Zoom FX...")
        clip = VideoFileClip(vid_path).subclip(0, scene_duration)
        
        # Resize and Crop
        clip = clip.resize(height=TARGET_H)
        if clip.w < TARGET_W:
            clip = clip.resize(width=TARGET_W)
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=TARGET_W, height=TARGET_H)
        
        # Zoom & Dark Overlay
        zoomed_clip = clip.resize(lambda t: 1.0 + 0.05 * (t / scene_duration)).set_position(('center', 'center'))
        dark_overlay = ColorClip(size=(TARGET_W, TARGET_H), color=(0,0,0)).set_opacity(0.4).set_duration(scene_duration)
        
        # 2-Word Fast Captions exactly synced
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
        print(f"✅ [DONE] Scene {i+1} Ready! ({scene_duration:.2f}s)\n")
        
    except Exception as e:
        print(f"❌ Error rendering scene {i+1}: {e}\n")

# Cleanup audio files
for i in range(len(scenes_data)):
    if os.path.exists(f"voice_scene_{i}.mp3"): os.remove(f"voice_scene_{i}.mp3")

# ==========================================
# 4. FINAL STITCHING & AUDIO MIXING
# ==========================================
print("🔄 Stitching all scenes together...")
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
    print("⚠️ Warning: bgm.mp3 not found. Skipping BGM.")

# Apply master audio timeline
final_video = final_video.set_audio(CompositeAudioClip(master_audio_clips))

# ==========================================
# 5. EXPORT & UPLOAD
# ==========================================
print("\n🎬 Rendering Final Video...")
output_name = "final_video.mp4"

# ✅ ANTI-HANG FIX 3: Threads changed from 4 to 2, preset to ultrafast (Less CPU load)
final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac", threads=2, bitrate="1500k", preset="ultrafast")

print("\n🚀 Starting Upload System...")
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
        print(f"📤 Trying upload to {name}...")
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
