import tkinter as tk
from tkinter import messagebox, ttk
from threading import Thread
from slide_extractor import download_video, extract_slides, generate_pdf

def run_extraction(url, interval, threshold, progress_var, status_label):
    try:
        status_label.config(text="Downloading video...")
        progress_var.set(25)
        video_path = download_video(url)

        status_label.config(text="Extracting slides...")
        progress_var.set(50)
        slide_count = extract_slides(video_path, int(interval), float(threshold))
        
        if slide_count == 0:
            messagebox.showwarning("Warning", "No slides were extracted. Try adjusting the similarity threshold.")
            return

        status_label.config(text="Generating PDF...")
        progress_var.set(75)

        generate_pdf()

        progress_var.set(100)
        status_label.config(text="Complete!")
        messagebox.showinfo("Success", f"Extraction complete!\n{slide_count} slides extracted and PDF generated!")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        print(f"Detailed error: {e}")
    finally:
        progress_var.set(0)
        status_label.config(text="Ready")

def validate_inputs(url, interval, threshold):
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return False
    
    if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
        messagebox.showerror("Error", "Please enter a valid YouTube URL")
        return False
    
    try:
        interval_val = int(interval)
        if interval_val <= 0:
            raise ValueError()
    except ValueError:
        messagebox.showerror("Error", "Interval must be a positive integer")
        return False
    
    try:
        threshold_val = float(threshold)
        if not (0 <= threshold_val <= 1):
            raise ValueError()
    except ValueError:
        messagebox.showerror("Error", "Threshold must be a number between 0 and 1")
        return False
    
    return True

def create_main_window():
    root = tk.Tk()
    root.title("YouTube Slide Extractor")
    root.geometry("500x350")
    
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    
    return root, main_frame

def create_input_fields(main_frame):
    ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
    url_entry = ttk.Entry(main_frame, width=60)
    url_entry.grid(row=0, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
    
    ttk.Label(main_frame, text="Interval (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
    interval_entry = ttk.Entry(main_frame, width=20)
    interval_entry.insert(0, "30")  
    interval_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
    
    ttk.Label(main_frame, text="Similarity Threshold (0-1):").grid(row=2, column=0, sticky=tk.W, pady=5)
    threshold_entry = ttk.Entry(main_frame, width=20)
    threshold_entry.insert(0, "0.85")  
    threshold_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
    
    return url_entry, interval_entry, threshold_entry

def create_progress_elements(main_frame):
    """Create progress bar and status label"""
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100)
    progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
    
    status_label = ttk.Label(main_frame, text="Ready")
    status_label.grid(row=4, column=0, columnspan=2, pady=5)
    
    return progress_var, status_label

def create_extract_button(main_frame, url_entry, interval_entry, threshold_entry, progress_var, status_label):
    def on_extract():
        url = url_entry.get().strip()
        interval = interval_entry.get().strip()
        threshold = threshold_entry.get().strip()
        
        if not validate_inputs(url, interval, threshold):
            return
        
        extract_button.config(state='disabled')
        
        def extraction_wrapper():
            try:
                run_extraction(url, interval, threshold, progress_var, status_label)
            finally:
                extract_button.config(state='normal')
        
        Thread(target=extraction_wrapper, daemon=True).start()
    
    extract_button = ttk.Button(main_frame, text='Extract Slides', command=on_extract)
    extract_button.grid(row=5, column=0, columnspan=2, pady=20)
    
    return extract_button

def start_gui():
    root, main_frame = create_main_window()
    url_entry, interval_entry, threshold_entry = create_input_fields(main_frame)
    progress_var, status_label = create_progress_elements(main_frame)
    extract_button = create_extract_button(
        main_frame, url_entry, interval_entry, threshold_entry, 
        progress_var, status_label
    )
    root.mainloop()

if __name__ == "__main__":
    print("Starting YouTube Slide Extractor GUI...")
    print("Make sure you have installed: pip install yt-dlp opencv-python fpdf2 pillow")
    start_gui()