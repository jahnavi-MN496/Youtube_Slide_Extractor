import yt_dlp
import cv2
import numpy as np
import os
from fpdf import FPDF
from PIL import Image

def download_video(url, save_path="video.mp4"):
    try:
        print(f"Downloading video from: {url}")
        if os.path.exists(save_path):
            os.remove(save_path)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  
            'outtmpl': save_path,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Video title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 'Unknown')} seconds")
            ydl.download([url])
        
        if not os.path.exists(save_path):
            raise Exception("Video file was not created after download")
            
        print(f"Video downloaded: {save_path}")
        return save_path
        
    except Exception as e:
        raise Exception(f"Failed to download video: {str(e)}")

def is_similar(img1, img2, threshold=0.9):
    try:
        if len(img1.shape) == 3:
            img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        if len(img2.shape) == 3:
            img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        img1 = cv2.resize(img1, (320, 240))
        img2 = cv2.resize(img2, (320, 240))

        diff = cv2.absdiff(img1, img2)
        non_zero_count = np.count_nonzero(diff)
        total_pixels = diff.size
        similarity = 1 - (non_zero_count / total_pixels)
        return similarity >= threshold
        
    except Exception as e:
        print(f"Error comparing images: {e}")
        return False

def extract_slides(video_path, interval=30, threshold=0.9, output_folder="slides"):
    print(f"Extracting slides from: {video_path}")
    
    if not os.path.exists(video_path):
        raise Exception(f"Video file not found: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30 
        
    frame_interval = int(fps * interval)
    print(f"Video FPS: {fps}, Frame interval: {frame_interval}")
    
    count = 0
    slide_num = 0
    last_frame = None
    
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if count % frame_interval == 0:
                if last_frame is None or not is_similar(frame, last_frame, threshold):
                    slide_path = os.path.join(output_folder, f"slide_{slide_num:03d}.jpg")
                    success = cv2.imwrite(slide_path, frame)
                    if success:
                        slide_num += 1
                        last_frame = frame.copy()
                        print(f"Extracted slide {slide_num}")
                    else:
                        print(f"Failed to save slide {slide_num}")
            count += 1
            
    finally:
        cap.release()
    
    print(f"Total slides extracted: {slide_num}")
    return slide_num

def generate_pdf(output_folder="slides", output_pdf="slides.pdf"):
    print(f"Generating PDF from folder: {output_folder}")
    
    if not os.path.exists(output_folder):
        raise Exception(f"Slides folder not found: {output_folder}")
    
    images = [f for f in os.listdir(output_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    images.sort()
    
    if not images:
        raise Exception("No slide images found to create PDF")
    
    pdf = FPDF()
    
    for img_name in images:
        img_path = os.path.join(output_folder, img_name)
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                page_width = 210
                page_height = 297

                img_ratio = width / height
                page_ratio = page_width / page_height
                
                if img_ratio > page_ratio:
                    new_width = page_width
                    new_height = page_width / img_ratio
                else:
                    new_height = page_height
                    new_width = page_height * img_ratio

                x = (page_width - new_width) / 2
                y = (page_height - new_height) / 2
                
                pdf.add_page()
                pdf.image(img_path, x, y, new_width, new_height)
                
        except Exception as e:
            print(f"Error processing image {img_name}: {e}")
            continue
    
    pdf.output(output_pdf)
    print(f"PDF generated: {output_pdf}")

def process_video(url, interval=30, threshold=0.85):
    try:
        video_path = download_video(url)
        slide_count = extract_slides(video_path, interval, threshold)
        
        if slide_count == 0:
            raise Exception("No slides were extracted. Try adjusting the similarity threshold.")

        generate_pdf()
        
        return slide_count
        
    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")

if __name__ == "__main__":
    print("YouTube Slide Extractor - Core Module")
    print("This module contains the core logic for video processing.")
    print("Use gui.py to run the graphical interface.")