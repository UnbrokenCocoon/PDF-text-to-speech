import os
import pandas as pd
import re
import time
import pyttsx3
import subprocess
from PyPDF2 import PdfReader

# ========== CONFIG ==========

pdf_folder = r'path/to/your/dir' #insert your dir
audio_folder = os.path.join(pdf_folder, "audio_outputs")
saved_data = os.path.join(pdf_folder, "saved_data.pkl")
chunk_size = 500
default_wpm = 300


# ========== TEXT CLEANING ==========

def clean_text(text):
    if not text:
        return ""

    # Replace newlines with space
    text = text.replace('\n', ' ')

    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # Remove unwanted punctuation (keep apostrophes)
    text = re.sub(r"[^\w\s']", '', text)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ========== MAIN FUNCTIONS ==========

def split_text_into_chunks(text, max_length=chunk_size):
    words = text.split()
    chunks = []
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += (" " if current_chunk else "") + word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def extract_pdf_to_df(pdf_path):
    reader = PdfReader(pdf_path)
    all_chunks = []
    for page_idx, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if not page_text:
            continue
        chunks = split_text_into_chunks(page_text)
        for chunk_idx, chunk in enumerate(chunks):
            cleaned_chunk = clean_text(chunk)
            all_chunks.append({
                'chunk_text': cleaned_chunk,
                'chunk_number': chunk_idx,
                'source_file': os.path.basename(pdf_path),
                'listened_count': 0  # Default 0 listens
            })
    return pd.DataFrame(all_chunks)


def load_master_df():
    if os.path.exists(saved_data):
        return pd.read_pickle(saved_data)
    else:
        return pd.DataFrame(columns=['chunk_text', 'chunk_number', 'source_file', 'listened_count'])


def save_master_df(df):
    df.to_pickle(saved_data)


def ensure_audio_folder():
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)


def generate_audio_for_pdf(filename, engine):
    filepath = os.path.join(pdf_folder, filename)
    output_mp3 = os.path.join(audio_folder, f"{os.path.splitext(filename)[0]}.mp3")

    if os.path.exists(output_mp3):
        print(f"Audio already exists for {filename}. Skipping regeneration.")
        return output_mp3

    print(f"Generating audio for {filename}...")

    reader = PdfReader(filepath)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += " " + page_text

    full_text = clean_text(full_text)

    # Save to a temporary WAV first because pyttsx3 saves WAVs easily
    temp_wav = os.path.join(audio_folder, f"{os.path.splitext(filename)[0]}.wav")
    engine.save_to_file(full_text, temp_wav)
    engine.runAndWait()

    # Convert WAV to MP3 if you want (optional). For now, use WAV directly.

    return temp_wav  # Return the WAV path


def setup_engine():
    engine = pyttsx3.init()

    # Set Hazel voice automatically
    voices = engine.getProperty('voices')
    hazel_voice = next((v for v in voices if "Hazel" in v.name), None)
    if hazel_voice:
        engine.setProperty('voice', hazel_voice.id)
        print(f"Using voice: {hazel_voice.name}")
    else:
        print("Hazel voice not found, using default system voice.")

    # Set default WPM speed
    engine.setProperty('rate', default_wpm)
    print(f"Speaking speed set to {default_wpm} words per minute.")

    return engine


def list_saved_pdfs(master_df):
    return sorted(master_df['source_file'].unique())


def play_audio_file(audio_path):
    try:
        subprocess.Popen(['start', '', audio_path], shell=True)  # Windows only
        print(f"Now playing {os.path.basename(audio_path)}...")
    except Exception as e:
        print(f"Error playing audio: {e}")


def update_listen_count(master_df, filename):
    mask = master_df['source_file'] == filename
    if mask.any():
        master_df.loc[mask, 'listened_count'] += 1
        save_master_df(master_df)
        print(f"Updated listen count for {filename}.")
    else:
        print(f"No entry found for {filename} to update listen count.")


def update_with_new_pdfs(master_df):
    processed_files = set(master_df['source_file'].unique())
    all_pdfs = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    new_pdfs = [f for f in all_pdfs if f not in processed_files]

    if not new_pdfs:
        print("\nNo new PDFs found.")
        return master_df

    print(f"\n{len(new_pdfs)} new PDFs found.")
    updated_dfs = []

    for idx, filename in enumerate(new_pdfs, 1):
        print(f"Processing {idx} of {len(new_pdfs)}: {filename}")
        pdf_path = os.path.join(pdf_folder, filename)
        try:
            new_df = extract_pdf_to_df(pdf_path)
            updated_dfs.append(new_df)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if updated_dfs:
        combined_df = pd.concat([master_df] + updated_dfs, ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset='chunk_text').reset_index(drop=True)
        save_master_df(combined_df)
        print(f"\nFinished processing {len(new_pdfs)} new PDFs.\n")
        return combined_df
    else:
        return master_df


# ========== MAIN PROGRAM ==========

def main():
    print("\n====== Initialising Text-to-Speech Reader ======")
    ensure_audio_folder()
    master_df = load_master_df()
    master_df = update_with_new_pdfs(master_df)

    engine = setup_engine()

    try:
        while True:
            print("\n====== MAIN MENU ======")
            print("1. Read (play) a saved PDF")
            print("2. Exit")

            choice = input("Enter your choice (1/2): ").strip()

            if choice == "1":
                saved_pdfs = list_saved_pdfs(master_df)
                if not saved_pdfs:
                    print("No saved PDFs found.")
                    continue

                print("\nSaved PDFs available:")
                for idx, file in enumerate(saved_pdfs):
                    listens = master_df[master_df['source_file'] == file]['listened_count'].max()
                    print(f"{idx}: {file} (listened {listens} times)")

                try:
                    idx = int(input("Enter the number of the PDF you want to read: "))
                    selected_file = saved_pdfs[idx]
                    print(f"\nNow preparing audio for '{selected_file}'...")

                    audio_path = generate_audio_for_pdf(selected_file, engine)
                    play_audio_file(audio_path)

                    # Wait briefly to make sure player launches
                    time.sleep(2)

                    # Immediately update listen count
                    update_listen_count(master_df, selected_file)

                except (IndexError, ValueError):
                    print("Invalid choice. Please try again.")

            elif choice == "2":
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid input. Please enter 1 or 2.")
    except KeyboardInterrupt:
        print("\nUser stopped the program. Exiting safely.")


# ========== RUN ==========
if __name__ == "__main__":
    main()
