import os
from typing import Tuple

def validate_audio_file(file) -> Tuple[bool, str]:
    """Validate uploaded audio file"""
    if file is None:
        return False, "No file uploaded"
    
    # Check file size (10MB limit)
    if file.size > 10 * 1024 * 1024:
        return False, "File size too large (max 10MB)"
    
    # Check file extension
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in ['.wav', '.mp3']:
        return False, "Unsupported file format. Please upload WAV or MP3"
    
    return True, "File is valid"
