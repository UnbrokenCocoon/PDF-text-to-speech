# 📚 PDF-to-Speech Reader

A Python script to convert PDF documents into audio files using text-to-speech. It automatically scans a folder for new PDFs, cleans and chunks the text, generates `.wav` audio files, and tracks how many times each file has been listened to.

## ✅ Features

- 🔍 Scans a folder for new `.pdf` files
- 🧼 Cleans text (removes URLs, punctuation, numbers, etc.)
- 🧩 Splits content into 500-word chunks
- 🔊 Converts full text to `.wav` audio using `pyttsx3`
- 📁 Stores audio in a structured folder
- 🧠 Tracks listen count per file
- 🖥️ CLI menu for playing files (Windows only)

---

## 🗂 Folder Structure

```
PDF Store/
├── your_files.pdf
├── audio_outputs/
│   └── generated_audio.wav
├── saved_data.pkl       # Tracks processed PDFs and listen counts
```

Ensure your `.pdf` files are stored in the `PDF Store` folder.

---

## 🛠 Requirements

Install required Python libraries:

```bash
pip install -r requirements.txt
```

> Make sure you are using Python 3.7 or newer.

---

## 📦 requirements.txt

```
pandas>=1.0.0
pyttsx3>=2.90
PyPDF2>=3.0.0
```

### Optional for MP3 conversion:
```
pydub>=0.25.1
```

> Note: `pydub` requires FFmpeg to be installed and added to your system PATH.

---

## 🚀 Usage

1. Place PDFs in the folder specified by `pdf_folder` in the script.
2. Run the script:

```bash
python your_script_name.py
```

3. Use the CLI to choose and play audio files:

```
====== MAIN MENU ======
1. Read (play) a saved PDF
2. Exit
```

---

## 🎛 How It Works

- `extract_pdf_to_df`: Reads and chunks each page of a PDF
- `clean_text`: Removes unnecessary characters and formatting
- `generate_audio_for_pdf`: Converts text to `.wav` using `pyttsx3`
- `play_audio_file`: Opens the audio file with your default media player
- `saved_data.pkl`: Stores all metadata between sessions

---

## ⚠️ Limitations

- Playback is Windows-only (uses `start` command)
- Only `.wav` files are created by default
- Doesn't support selecting individual pages or sections

---

## 🔄 Future Enhancements

- Cross-platform audio playback
- Per-page or per-chunk audio generation
- Voice and language selection
- GUI version using PyQt or Tkinter

---

## 👨‍💻 Author

Built for personal use — ideal for listening to academic papers or long-form content while multitasking.
