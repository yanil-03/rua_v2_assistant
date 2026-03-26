import os
import urllib.request
import zipfile
import shutil
import sys

# The URL for the Massive 1.8GB English Model
# (If you find you need the Indian-English specific one later, you can swap this URL to:
#  https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip )
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
MODEL_NAME = MODEL_URL.split("/")[-1]
EXTRACTED_FOLDER_NAME = MODEL_NAME.replace(".zip", "")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
ZIP_PATH = os.path.join(MODELS_DIR, MODEL_NAME)
TARGET_FOLDER = os.path.join(MODELS_DIR, "vosk-large")

def report_progress(block_num, block_size, total_size):
    """Prints a dynamic progress bar to the terminal."""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = downloaded * 100 / total_size
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        # Overwrite the same line in the console
        sys.stdout.write(f"\r📥 Downloading... {percent:.1f}%  ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)")
        sys.stdout.flush()

def download_and_setup_model():
    print(f"🚀 Preparing to download the Large Vosk Model...")
    
    # 1. Create the models directory if it doesn't exist
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        print(f"📁 Created directory: {MODELS_DIR}")

    # 2. Check if the target folder already exists
    if os.path.exists(TARGET_FOLDER):
        print(f"✅ The model is already installed at {TARGET_FOLDER}. Exiting.")
        return

    # 3. Download the .zip file
    print(f"🔗 Fetching from: {MODEL_URL}")
    try:
        urllib.request.urlretrieve(MODEL_URL, ZIP_PATH, reporthook=report_progress)
        print("\n✅ Download complete!")
    except Exception as e:
        print(f"\n❌ Error downloading file: {e}")
        return

    # 4. Extract the .zip file
    print(f"📦 Extracting the massive model (this might take a minute)...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(MODELS_DIR)
        print("✅ Extraction complete!")
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return

    # 5. Rename the extracted folder to 'vosk-large'
    extracted_path = os.path.join(MODELS_DIR, EXTRACTED_FOLDER_NAME)
    if os.path.exists(extracted_path):
        os.rename(extracted_path, TARGET_FOLDER)
        print(f"🔄 Renamed folder to: {TARGET_FOLDER}")
    else:
        print(f"⚠️ Could not find the extracted folder to rename: {extracted_path}")

    # 6. Clean up the zip file to save space
    print(f"🧹 Cleaning up the leftover .zip file...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
        print("✅ Cleanup complete!")

    print(f"\n🎉 Success! RUA's high-accuracy STT brain is installed at: {TARGET_FOLDER}")

if __name__ == "__main__":
    download_and_setup_model()