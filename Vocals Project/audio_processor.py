import librosa
import numpy as np
from typing import Tuple, Dict, List

class AudioProcessor:
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3']
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.note_range = {
            'Piano': ('A0', 'C8'),
            'Guitar': ('E2', 'E6'),
            'Violin': ('G3', 'A7'),
            'Bass': ('E1', 'G4')
        }

    def process_audio(self, audio_data: bytes) -> Tuple[np.ndarray, float]:
        """Process audio data and return signal and sample rate"""
        try:
            y, sr = librosa.load(audio_data)
            return y, sr
        except Exception as e:
            raise Exception(f"Error processing audio: {str(e)}")

    def detect_pitch(self, y: np.ndarray, sr: float) -> np.ndarray:
        """Detect pitch using librosa with improved accuracy"""
        pitches, magnitudes = librosa.piptrack(
            y=y, 
            sr=sr,
            fmin=librosa.note_to_hz('C1'),
            fmax=librosa.note_to_hz('C8')
        )
        return pitches

    def detect_notes(self, y: np.ndarray, sr: float) -> Dict:
        """Detect musical notes with improved accuracy and timing"""
        notes = []
        confidences = []
        onset_frames = librosa.onset.onset_detect(
            y=y, 
            sr=sr,
            units='frames',
            hop_length=512,
            backtrack=True,
            pre_max=20,
            post_max=20,
            pre_avg=50,
            post_avg=50,
            delta=0.2
        )

        # Get pitch track
        pitches, magnitudes = librosa.piptrack(
            y=y, 
            sr=sr,
            fmin=librosa.note_to_hz('C1'),
            fmax=librosa.note_to_hz('C8')
        )

        for frame in onset_frames:
            if frame < pitches.shape[1]:
                # Get the highest magnitude pitch at this frame
                pitch_index = magnitudes[:, frame].argmax()
                pitch_hz = pitches[pitch_index, frame]

                if pitch_hz > 0:
                    note = librosa.hz_to_note(pitch_hz)
                    confidence = magnitudes[pitch_index, frame]

                    if confidence > 0.1:  # Filter out low confidence detections
                        notes.append(note)
                        confidences.append(float(confidence))

        return {
            'onset_frames': onset_frames,
            'notes': notes,
            'confidences': confidences
        }

    def classify_instrument(self, y: np.ndarray, sr: float) -> Dict[str, float]:
        """Enhanced instrument classification using multiple features"""
        # Extract features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)

        # Calculate feature statistics
        avg_centroid = float(np.mean(spectral_centroid))
        avg_rolloff = float(np.mean(spectral_rolloff))
        avg_bandwidth = float(np.mean(spectral_bandwidth))
        avg_zcr = float(np.mean(zero_crossing_rate))

        # Normalized confidence scores for each instrument
        confidence_scores = {}

        # Piano detection (wide frequency range, moderate brightness)
        piano_score = (
            0.8 if 500 < avg_centroid < 4000 else 0.3
        ) * (
            0.7 if 2000 < avg_rolloff < 8000 else 0.4
        )

        # Guitar detection (mid-range frequencies, moderate brightness)
        guitar_score = (
            0.8 if 300 < avg_centroid < 3000 else 0.3
        ) * (
            0.7 if 1500 < avg_rolloff < 6000 else 0.4
        )

        # Violin detection (higher frequencies, brighter sound)
        violin_score = (
            0.8 if 800 < avg_centroid < 5000 else 0.3
        ) * (
            0.7 if 3000 < avg_rolloff < 10000 else 0.4
        )

        # Bass detection (low frequencies, darker sound)
        bass_score = (
            0.8 if avg_centroid < 1000 else 0.3
        ) * (
            0.7 if avg_rolloff < 2000 else 0.4
        )

        # Normalize scores
        total = piano_score + guitar_score + violin_score + bass_score
        confidence_scores = {
            'Piano': round(piano_score / total, 2),
            'Guitar': round(guitar_score / total, 2),
            'Violin': round(violin_score / total, 2),
            'Bass': round(bass_score / total, 2)
        }

        return confidence_scores