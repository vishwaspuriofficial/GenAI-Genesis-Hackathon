import requests
import os
import json
import time
import zipfile
import shutil
from typing import List

# Configuration
API_URL = "http://localhost:8000/api/files/download"
TEMP_DIR = "temp_downloads"  # Temporary download directory that will be deleted
FINAL_DIR = "./raw_files"  # Current directory where files will be placed


file_urls = [
    "https://storage.googleapis.com/genai-genesis-2025-64499.firebasestorage.app/Backend/tesing_20250322151532.pdf",
    "https://storage.googleapis.com/genai-genesis-2025-64499.firebasestorage.app/Backend/tesing_copy_4_20250322150457.pdf",
]

def download_to_current_directory(file_urls: List[str]):
    """
    Download multiple files, extract them directly to the current directory,
    and delete all temporary files and folders
    """
    print("\n" + "="*70)
    print("DOWNLOADING FILES TO CURRENT DIRECTORY".center(70))
    print("="*70)
    
    # Create temporary directory for downloads
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Clean any previous files in temporary directory
    for item in os.listdir(TEMP_DIR):
        item_path = os.path.join(TEMP_DIR, item)
        try:
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Error cleaning temporary directory {item_path}: {e}")
    
    print(f"API URL: {API_URL}")
    print(f"Files to download: {len(file_urls)}")
    for i, url in enumerate(file_urls):
        print(f"  {i+1}. {os.path.basename(url)}")
    
    try:
        # Make the API request
        print("\nSending request to download files...")
        start_time = time.time()
        response = requests.post(
            API_URL,
            json={"file_urls": file_urls},
            stream=True
        )
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"❌ API request failed with status code {response.status_code}")
            print(f"Error message: {response.text}")
            return False
        
        print("✅ API responded successfully!")
        
        # Get the filename from the Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition')
        zip_filename = None
        if content_disposition and "filename=" in content_disposition:
            zip_filename = content_disposition.split('filename=')[1].strip('"')
        else:
            # Generate a filename if none provided
            zip_filename = f"downloaded_files_{int(time.time())}.zip"
        
        # Save the ZIP file to temporary directory
        zip_path = os.path.join(TEMP_DIR, zip_filename)
        print(f"Downloading ZIP to temporary location: {zip_path}")
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        download_time = time.time() - start_time
        print(f"✅ Download completed in {download_time:.2f} seconds")
        
        # Extract the ZIP file
        print(f"\nExtracting files directly to {os.path.abspath(FINAL_DIR)}...")
        extract_start_time = time.time()
        
        # Get list of files before extraction to identify new files
        existing_files = set(os.listdir(FINAL_DIR))
        
        # Extract all files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of all files in the ZIP
            zip_files = zip_ref.namelist()
            
            for file_name in zip_files:
                # Extract to temporary location first
                zip_ref.extract(file_name, TEMP_DIR)
                
                # Prepare source and destination paths
                source_path = os.path.join(TEMP_DIR, file_name)
                target_path = os.path.join(FINAL_DIR, file_name)
                
                # Handle file collisions
                if os.path.exists(target_path):
                    print(f"  ⚠️ File already exists, adding timestamp: {file_name}")
                    name, ext = os.path.splitext(file_name)
                    new_name = f"{name}_{int(time.time())}{ext}"
                    target_path = os.path.join(FINAL_DIR, new_name)
                
                # Move the file to the final destination
                shutil.move(source_path, target_path)
                print(f"  ✓ Extracted: {os.path.basename(target_path)}")
        
        # Identify new files by comparing with the list before extraction
        new_files = []
        for file_name in os.listdir(FINAL_DIR):
            file_path = os.path.join(FINAL_DIR, file_name)
            if os.path.isfile(file_path) and file_name not in existing_files:
                new_files.append((file_name, os.path.getsize(file_path)))
        
        # Display list of extracted files
        print("\nFiles extracted to current directory:")
        print("-" * 70)
        
        # Sort files by name for a cleaner output
        new_files.sort()
        
        for i, (file_name, file_size) in enumerate(new_files):
            print(f"  {i+1}. {file_name} ({file_size / 1024:.1f} KB)")
        
        # Clean up - remove temporary directory
        print(f"\nCleaning up - removing temporary directory: {TEMP_DIR}")
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"✅ Temporary directory deleted successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not delete temporary directory: {str(e)}")
        
        extract_time = time.time() - extract_start_time
        total_time = time.time() - start_time
        print(f"\n✅ Extraction and cleanup completed in {extract_time:.2f} seconds")
        print(f"✅ Total process time: {total_time:.2f} seconds")
        print(f"✅ {len(new_files)} files are now available in your current directory")
        print(f"📂 Directory: {os.path.abspath(FINAL_DIR)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during download and extract: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to clean up temporary directory even if error occurred
        try:
            if os.path.exists(TEMP_DIR):
                shutil.rmtree(TEMP_DIR)
                print(f"✅ Cleaned up temporary directory after error")
        except:
            pass
            
        return False

if __name__ == "__main__":
    success = download_to_current_directory()
    
    if success:
        print("\n🎉 DONE! All files are now available in your current directory.")
    else:
        print("\n❌ Failed to download and extract files. Please check the errors above.") 