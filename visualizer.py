import plotly.graph_objects as go
import numpy as np
from typing import List, Dict
import streamlit as st
import base64

class AudioVisualizer:
    def __init__(self):
        self.note_freqs = {
            'A0': 27.50, 'A#0/Bb0': 29.14, 'B0': 30.87,
            'C1': 32.70, 'C#1/Db1': 34.65, 'D1': 36.71,
            'D#1/Eb1': 38.89, 'E1': 41.20, 'F1': 43.65,
            'F#1/Gb1': 46.25, 'G1': 49.00, 'G#1/Ab1': 51.91,
            'A1': 55.00, 'A#1/Bb1': 58.27, 'B1': 61.74,
            'C2': 65.41, 'C#2/Db2': 69.30, 'D2': 73.42,
            'D#2/Eb2': 77.78, 'E2': 82.41, 'F2': 87.31,
            'F#2/Gb2': 92.50, 'G2': 98.00, 'G#2/Ab2': 103.83,
            'A2': 110.00, 'A#2/Bb2': 116.54, 'B2': 123.47,
            'C3': 130.81, 'C#3/Db3': 138.59, 'D3': 146.83,
            'D#3/Eb3': 155.56, 'E3': 164.81, 'F3': 174.61,
            'F#3/Gb3': 185.00, 'G3': 196.00, 'G#3/Ab3': 207.65,
            'A3': 220.00, 'A#3/Bb3': 233.08, 'B3': 246.94,
            'C4': 261.63, 'C#4/Db4': 277.18, 'D4': 293.66,
            'D#4/Eb4': 311.13, 'E4': 329.63, 'F4': 349.23,
            'F#4/Gb4': 369.99, 'G4': 392.00, 'G#4/Ab4': 415.30,
            'A4': 440.00, 'A#4/Bb4': 466.16, 'B4': 493.88,
            'C5': 523.25, 'C#5/Db5': 554.37, 'D5': 587.33,
            'D#5/Eb5': 622.25, 'E5': 659.25, 'F5': 698.46,
            'F#5/Gb5': 739.99, 'G5': 783.99, 'G#5/Ab5': 830.61,
            'A5': 880.00, 'A#5/Bb5': 932.33, 'B5': 987.77,
            'C6': 1046.50, 'C#6/Db6': 1108.73, 'D6': 1174.66,
            'D#6/Eb6': 1244.51, 'E6': 1318.51, 'F6': 1396.91,
            'F#6/Gb6': 1479.98, 'G6': 1567.98, 'G#6/Ab6': 1661.22,
            'A6': 1760.00, 'A#6/Bb6': 1864.66, 'B6': 1975.53,
            'C7': 2093.00, 'C#7/Db7': 2217.46, 'D7': 2349.32,
            'D#7/Eb7': 2489.02, 'E7': 2637.02, 'F7': 2793.83,
            'F#7/Gb7': 2959.96, 'G7': 3135.96, 'G#7/Ab7': 3322.44,
            'A7': 3520.00, 'A#7/Bb7': 3729.31, 'B7': 3951.07,
            'C8': 4186.01
        }

    def create_pitch_map(self, pitches: np.ndarray, sr: float) -> go.Figure:
        fig = go.Figure()
        times = np.arange(pitches.shape[1]) * 512 / sr
        fig.add_trace(go.Heatmap(
            x=times,
            y=np.arange(pitches.shape[0]),
            z=pitches,
            colorscale=[
                [0, 'rgb(255,255,255)'],
                [0.2, 'rgb(240,240,255)'],
                [0.4, 'rgb(200,200,255)'],
                [0.6, 'rgb(150,150,255)'],
                [0.8, 'rgb(100,100,255)'],
                [1, 'rgb(50,50,255)']
            ],
            showscale=True,
            colorbar=dict(
                title=dict(
                    text='Pitch Intensity',
                    side='right'
                )
            )
        ))
        fig.update_layout(
            title='Pitch Map',
            xaxis_title='Time (s)',
            yaxis_title='Frequency (Hz)',
            template='plotly_white',
            height=400
        )
        return fig

    def create_virtual_keyboard(self, active_notes: List[str] = None) -> str:
        if active_notes is None:
            active_notes = []
        active_notes = [note.split('/')[0] for note in active_notes]
        keyboard_css = """
        <style>
        .piano-container {
            margin: 20px auto;
            text-align: center;
        }
        .piano {
            display: inline-flex;
            justify-content: center;
            padding: 20px;
            background: #363636;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .key {
            position: relative;
            width: 40px;
            height: 150px;
            border: 1px solid #000;
            background-color: white;
            margin: 0 1px;
            border-radius: 0 0 4px 4px;
            transition: background-color 0.1s;
        }
        .black-key {
            position: absolute;
            width: 24px;
            height: 90px;
            background-color: black;
            margin-left: -12px;
            z-index: 1;
            border-radius: 0 0 3px 3px;
            transition: background-color 0.1s;
        }
        .key.active {
            background-color: #98FB98;
            box-shadow: 0 0 8px #98FB98;
        }
        .black-key.active {
            background-color: #3CB371;
            box-shadow: 0 0 8px #3CB371;
        }
        .key:hover {
            background-color: #f0f0f0;
        }
        .black-key:hover {
            background-color: #333;
        }
        </style>
        """
        keys_html = '<div class="piano-container"><div class="piano">'
        octaves = ['4', '5']
        for octave in octaves:
            for note in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
                active_class = 'active' if f'{note}{octave}' in active_notes else ''
                keys_html += f'<div class="key {active_class}" data-note="{note}{octave}">'
                if note not in ['E', 'B']:
                    sharp_note = f'{note}#{octave}'
                    active_class = 'active' if sharp_note in active_notes else ''
                    keys_html += f'<div class="black-key {active_class}" data-note="{sharp_note}"></div>'
                keys_html += '</div>'
        keys_html += '</div></div>'
        return keyboard_css + keys_html

    def create_note_visualization(self, notes: List[str], onset_frames: List[int], sr: float, confidences: List[float] = None) -> go.Figure:
        fig = go.Figure()
        times = [frame * 512 / sr for frame in onset_frames]
        if not confidences:
            confidences = [1.0] * len(notes)
        note_positions = {note: idx for idx, note in enumerate(sorted(set(notes)))}
        y_positions = [note_positions[note] for note in notes]
        for note in sorted(set(notes)):
            is_black = '#' in note or 'b' in note
            color = 'rgba(50, 50, 50, 0.1)' if is_black else 'rgba(200, 200, 200, 0.1)'
            fig.add_shape(
                type="rect",
                x0=min(times) if times else 0,
                x1=max(times) if times else 1,
                y0=note_positions[note] - 0.4,
                y1=note_positions[note] + 0.4,
                fillcolor=color,
                line=dict(color="rgba(0,0,0,0.2)"),
                layer="below"
            )
        colors = ['rgba(31, 119, 180, {})'.format(conf) for conf in confidences]
        fig.add_trace(go.Scatter(
            x=times,
            y=y_positions,
            mode='markers',
            marker=dict(
                size=12,
                color=colors,
                symbol='square',
                line=dict(
                    color='rgba(0,0,0,0.5)',
                    width=1
                )
            ),
            text=[f"{note}<br>Confidence: {conf:.2f}" for note, conf in zip(notes, confidences)],
            hoverinfo='text',
            name='Notes'
        ))
        fig.update_layout(
            title='Piano Roll View',
            xaxis_title='Time (s)',
            yaxis=dict(
                title='Notes',
                ticktext=sorted(set(notes)),
                tickvals=list(range(len(set(notes)))),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            showlegend=False,
            height=max(400, len(set(notes)) * 25),
            template='plotly_white',
            plot_bgcolor='rgba(255,255,255,0.95)'
        )
        return fig

    def create_audio_player_with_keyboard(self, audio_data: bytes, notes_data: Dict) -> str:
        audio_b64 = base64.b64encode(audio_data).decode()

        # Complete piano frequency mapping from C0 to B7 (96 keys)
        note_frequencies = {
            'C0': 16.35, 'C#0': 17.32, 'D0': 18.35, 'D#0': 19.45, 'E0': 20.60, 'F0': 21.83,
            'F#0': 23.12, 'G0': 24.50, 'G#0': 25.96, 'A0': 27.50, 'A#0': 29.14, 'B0': 30.87,
            'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'D#1': 38.89, 'E1': 41.20, 'F1': 43.65,
            'F#1': 46.25, 'G1': 49.00, 'G#1': 51.91, 'A1': 55.00, 'A#1': 58.27, 'B1': 61.74,
            'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41, 'F2': 87.31,
            'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47,
            'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61,
            'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23,
            'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
            'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46,
            'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
            'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51, 'E6': 1318.51, 'F6': 1396.91,
            'F#6': 1479.98, 'G6': 1567.98, 'G#6': 1661.22, 'A6': 1760.00, 'A#6': 1864.66, 'B6': 1975.53,
            'C7': 2093.00, 'C#7': 2217.46, 'D7': 2349.32, 'D#7': 2489.02, 'E7': 2637.02, 'F7': 2793.83,
            'F#7': 2959.96, 'G7': 3135.96, 'G#7': 3322.44, 'A7': 3520.00, 'A#7': 3729.31, 'B7': 3951.07
        }

        # Prepare note timing data for JS animation
        note_timings = []
        for i, frame in enumerate(notes_data['onset_frames']):
            if i < len(notes_data['notes']):
                timing_ms = frame * 512 / notes_data['sr'] * 1000
                note_name = notes_data['notes'][i]
                note_name = note_name.replace('♯', '#').replace('b', '')  # normalize
                note_timings.append({
                    'note': note_name,
                    'time': timing_ms,
                    'duration': 400  # ms key highlight
                })
        
        import json
        note_timings_json = json.dumps(note_timings)
        note_frequencies_json = json.dumps(note_frequencies)

        html = f"""
        <html>
        <head>
        <style>
            .container {{
                background: #191b22;
                padding: 18px;
                border-radius: 10px;
                font-family: Arial, sans-serif;
            }}
            .audio-player {{
                width: 100%;
                margin-bottom: 14px;
            }}
            .audio-section {{
                margin-bottom: 20px;
            }}
            .audio-label {{
                color: #fff;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 8px;
                display: block;
            }}
            .converted-audio-controls {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 14px;
            }}
            .play-button {{
                background: #3a7cff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.2s;
            }}
            .play-button:hover {{
                background: #2a6ce8;
            }}
            .play-button:disabled {{
                background: #555;
                cursor: not-allowed;
            }}
            .progress-bar {{
                flex: 1;
                height: 6px;
                background: #333;
                border-radius: 3px;
                overflow: hidden;
                cursor: pointer;
            }}
            .progress-fill {{
                height: 100%;
                background: #3a7cff;
                width: 0%;
                transition: width 0.1s;
            }}
            .time-display {{
                color: #ccc;
                font-size: 12px;
                min-width: 80px;
            }}
            .piano-wrapper {{
                overflow-x: auto;
                overflow-y: hidden;
                padding: 10px 0;
                border-radius: 9px;
                background: #242835;
                max-width: 100%;
            }}
            .piano {{
                display: flex;
                position: relative;
                justify-content: flex-start;
                background: #242835;
                padding: 12px 3px 30px 3px;
                border-radius: 9px;
                min-height: 185px;
                user-select: none;
                width: max-content;
            }}
            .key {{
                width: 41px;
                height: 152px;
                background: #fff;
                border: 1.2px solid #222;
                position: relative;
                margin: 0 2px;
                border-radius: 0 0 6px 6px;
                box-sizing: border-box;
                z-index: 1;
                cursor: pointer;
                transition: background 0.18s, box-shadow 0.22s, border-color 0.19s;
            }}
            .key.detected {{
                background: #ffe95e !important;
                box-shadow: 0 0 20px #ffe95ecc, 0 0 2px #c5a200;
                border-color: #c5a200;
                z-index: 2;
            }}
            .key.hover {{
                background: #89f3ec !important;
                box-shadow: 0 0 10px #3df7e3a0;
                border-color: #105a52;
                z-index: 3;
            }}
            .black-key {{
                width: 25px;
                height: 93px;
                background: #222;
                position: absolute;
                top: 0;
                left: 29px;
                margin-left: -13px;
                z-index: 10;
                border-radius: 0 0 3px 3px;
                box-shadow: 1px 2px 10px #111b;
                transition: background 0.18s, box-shadow 0.22s;
                cursor: pointer;
            }}
            .black-key.detected {{
                background: #ffc641 !important;
                box-shadow: 0 0 16px #ffc979;
            }}
            .black-key.hover {{
                background: #56cc9d !important;
                box-shadow: 0 0 10px #41ffc2b0;
            }}
            .note-label {{
                position: absolute;
                bottom: 5px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 11px;
                color: #2b4025;
                z-index: 30;
                pointer-events: none;
            }}
            .black-key .note-label {{
                color: #f3ffe0;
                bottom: 4px;
            }}
            /* Custom scrollbar styling */
            .piano-wrapper::-webkit-scrollbar {{
                height: 8px;
            }}
            .piano-wrapper::-webkit-scrollbar-track {{
                background: #1a1a1a;
                border-radius: 4px;
            }}
            .piano-wrapper::-webkit-scrollbar-thumb {{
                background: #555;
                border-radius: 4px;
            }}
            .piano-wrapper::-webkit-scrollbar-thumb:hover {{
                background: #777;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="audio-section">
                    <label class="audio-label">Original Audio File</label>
                    <audio id="audio-player" class="audio-player" controls>
                        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                
                <div class="audio-section">
                    <label class="audio-label">Converted Piano Audio</label>
                    <div class="converted-audio-controls">
                        <button id="play-converted-btn" class="play-button">Play</button>
                        <div class="progress-bar" id="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        <span class="time-display" id="time-display">0:00 / 0:00</span>
                    </div>
                </div>
                
                <div class="piano-wrapper">
                    <div class="piano" id="piano">
        """

        # Generate complete piano keyboard from C0 to B7 (8 octaves, 96 keys total)
        white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        black_key_positions = {
            'C': 'C#', 'D': 'D#', 'F': 'F#', 'G': 'G#', 'A': 'A#'
        }
        
        for octave in range(0, 8):  # C0 to B7
            for white_key in white_keys:
                note_name = f"{white_key}{octave}"
                html += f'<div class="key" data-note="{note_name}"><span class="note-label">{note_name}</span>'
                
                # Add black key if it exists for this white key
                if white_key in black_key_positions:
                    black_note = f"{black_key_positions[white_key]}{octave}"
                    html += f'<div class="black-key" data-note="{black_note}"><span class="note-label">{black_note}</span></div>'
                
                html += '</div>'

        html += """
                    </div>
                </div>
            </div>
        <script>
        const piano = document.getElementById('piano');
        const audio = document.getElementById('audio-player');
        const playConvertedBtn = document.getElementById('play-converted-btn');
        const progressBar = document.getElementById('progress-bar');
        const progressFill = document.getElementById('progress-fill');
        const timeDisplay = document.getElementById('time-display');
        const noteData = """ + note_timings_json + """;
        const noteFrequencies = """ + note_frequencies_json + """;
        
        // Audio context for sound generation
        let audioContext = null;
        let isPlayingConverted = false;
        let convertedAudioStartTime = 0;
        let convertedAudioDuration = 0;
        let animationId = null;
        
        // Calculate total duration from note data
        if (noteData.length > 0) {
            convertedAudioDuration = Math.max(...noteData.map(n => n.time)) / 1000 + 2; // Add 2 seconds buffer
        }
        
        // Initialize audio context
        function initAudioContext() {
            if (audioContext) return;
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                console.error("Web Audio API not supported:", e);
            }
        }

        function normalize(note) {
            return note.replace("♯", "#").replace("b", "");
        }

        // Enhanced grand piano sound synthesis with authentic low-end timbre
        function playRealisticPianoSound(noteName, startTime = null) {
            initAudioContext();
            
            if (!audioContext) {
                console.error("Audio context not available");
                return;
            }

            try {
                const frequency = noteFrequencies[noteName];
                if (!frequency) {
                    console.warn("Frequency not found for note:", noteName);
                    return;
                }

                const now = startTime || audioContext.currentTime;
                
                // Enhanced duration and characteristics for different frequency ranges
                let duration, baseAmplitude, waveType, harmonicCount;
                
                if (frequency <= 196) { // C0 to G3 - Enhanced bass characteristics
                    duration = 1.5; // Shorter for converted audio
                    baseAmplitude = 0.4; // Reduced amplitude for mixing
                    waveType = 'sawtooth';
                    harmonicCount = 6;
                } else if (frequency <= 523) { // A3 to C5 - Mid range
                    duration = 1.2;
                    baseAmplitude = 0.3;
                    waveType = 'triangle';
                    harmonicCount = 4;
                } else if (frequency <= 1500) { // Mid-high range
                    duration = 1.0;
                    baseAmplitude = 0.25;
                    waveType = 'triangle';
                    harmonicCount = 3;
                } else { // High treble
                    duration = 0.8;
                    baseAmplitude = 0.2;
                    waveType = 'sine';
                    harmonicCount = 2;
                }

                const oscillators = [];
                const gainNodes = [];

                // Fundamental frequency
                const osc1 = audioContext.createOscillator();
                const gain1 = audioContext.createGain();
                osc1.connect(gain1);
                gain1.connect(audioContext.destination);
                osc1.frequency.setValueAtTime(frequency, now);
                osc1.type = waveType;
                oscillators.push(osc1);
                gainNodes.push(gain1);

                // Enhanced harmonic series
                const harmonicRatios = [2, 3, 4, 5, 6, 7];
                const harmonicAmplitudes = frequency <= 196 ? 
                    [0.25, 0.15, 0.1, 0.06, 0.04, 0.03] : 
                    frequency <= 523 ? 
                    [0.2, 0.12, 0.08, 0.05] : 
                    frequency <= 1500 ? 
                    [0.15, 0.1, 0.05] : 
                    [0.12, 0.06];

                for (let i = 0; i < Math.min(harmonicCount - 1, harmonicRatios.length); i++) {
                    const harmonic = audioContext.createOscillator();
                    const harmonicGain = audioContext.createGain();
                    harmonic.connect(harmonicGain);
                    harmonicGain.connect(audioContext.destination);
                    
                    harmonic.frequency.setValueAtTime(frequency * harmonicRatios[i], now);
                    harmonic.type = i < 2 ? 'sine' : 'triangle';
                    
                    oscillators.push(harmonic);
                    gainNodes.push(harmonicGain);
                }

                // ADSR envelope
                const amplitudes = [baseAmplitude, ...harmonicAmplitudes.slice(0, harmonicCount - 1)];
                
                gainNodes.forEach((gain, index) => {
                    if (index < amplitudes.length) {
                        const amp = amplitudes[index];
                        
                        let attackTime, decayTime, sustainLevel;
                        
                        if (frequency <= 196) {
                            attackTime = 0.05;
                            decayTime = 0.2;
                            sustainLevel = 0.7;
                        } else if (frequency <= 523) {
                            attackTime = 0.03;
                            decayTime = 0.15;
                            sustainLevel = 0.6;
                        } else {
                            attackTime = 0.02;
                            decayTime = 0.1;
                            sustainLevel = 0.5;
                        }
                        
                        gain.gain.setValueAtTime(0, now);
                        gain.gain.linearRampToValueAtTime(amp, now + attackTime);
                        gain.gain.exponentialRampToValueAtTime(amp * sustainLevel, now + attackTime + decayTime);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + duration);
                    }
                });

                // Start all oscillators
                oscillators.forEach(osc => {
                    osc.start(now);
                    osc.stop(now + duration);
                });

            } catch (e) {
                console.error("Error playing piano sound:", e);
            }
        }

        // Play converted audio sequence
        function playConvertedAudio() {
            if (isPlayingConverted) {
                stopConvertedAudio();
                return;
            }
            
            initAudioContext();
            if (!audioContext) return;
            
            isPlayingConverted = true;
            convertedAudioStartTime = audioContext.currentTime;
            playConvertedBtn.textContent = 'Stop';
            
            // Schedule all notes
            noteData.forEach(noteInfo => {
                const noteTime = convertedAudioStartTime + (noteInfo.time / 1000);
                playRealisticPianoSound(normalize(noteInfo.note), noteTime);
            });
            
            // Start progress animation
            updateConvertedProgress();
        }
        
        function stopConvertedAudio() {
            isPlayingConverted = false;
            playConvertedBtn.textContent = 'Play';
            if (animationId) {
                cancelAnimationFrame(animationId);
                animationId = null;
            }
            progressFill.style.width = '0%';
            updateTimeDisplay(0);
        }
        
        function updateConvertedProgress() {
            if (!isPlayingConverted) return;
            
            const currentTime = audioContext.currentTime - convertedAudioStartTime;
            const progress = Math.min(currentTime / convertedAudioDuration, 1);
            
            progressFill.style.width = (progress * 100) + '%';
            updateTimeDisplay(currentTime);
            
            // Highlight keys during playback
            noteData.forEach(noteInfo => {
                const noteTime = noteInfo.time / 1000;
                if (Math.abs(currentTime - noteTime) < 0.1) {
                    highlightDetectedKey(normalize(noteInfo.note), 200);
                }
            });
            
            if (progress >= 1) {
                stopConvertedAudio();
            } else {
                animationId = requestAnimationFrame(updateConvertedProgress);
            }
        }
        
        function updateTimeDisplay(currentTime) {
            const current = Math.max(0, currentTime);
            const total = convertedAudioDuration;
            
            const formatTime = (time) => {
                const minutes = Math.floor(time / 60);
                const seconds = Math.floor(time % 60);
                return minutes + ':' + seconds.toString().padStart(2, '0');
            };
            
            timeDisplay.textContent = formatTime(current) + ' / ' + formatTime(total);
        }
        
        // Progress bar click handler
        progressBar.addEventListener('click', (e) => {
            if (!isPlayingConverted) return;
            
            const rect = progressBar.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const progress = clickX / rect.width;
            const newTime = progress * convertedAudioDuration;
            
            // Restart from new position
            stopConvertedAudio();
            setTimeout(() => {
                convertedAudioStartTime = audioContext.currentTime - newTime;
                isPlayingConverted = true;
                playConvertedBtn.textContent = 'Stop';
                
                // Schedule remaining notes
                noteData.forEach(noteInfo => {
                    const noteTime = noteInfo.time / 1000;
                    if (noteTime >= newTime) {
                        const scheduleTime = convertedAudioStartTime + noteTime;
                        playRealisticPianoSound(normalize(noteInfo.note), scheduleTime);
                    }
                });
                
                updateConvertedProgress();
            }, 100);
        });

        // Highlight for detected notes
        function highlightDetectedKey(noteName, duration = 400) {
            const el = piano.querySelector('[data-note="' + noteName + '"]');
            if (!el) return;
            if (!el.classList.contains('detected')) {
                el.classList.add("detected");
                setTimeout(() => el.classList.remove("detected"), duration);
            }
        }

        // Original audio animation
        let raf = null;
        function animateKeys() {
            const tNow = audio.currentTime * 1000;
            for (let nd of noteData) {
                if (Math.abs(tNow - nd.time) < 80) {
                    highlightDetectedKey(normalize(nd.note), nd.duration || 400);
                }
            }
            if (!audio.paused && !audio.ended) {
                raf = requestAnimationFrame(animateKeys);
            }
        }
        
        // Event listeners
        playConvertedBtn.addEventListener('click', playConvertedAudio);
        
        audio.addEventListener('play', () => {
            if (raf) cancelAnimationFrame(raf);
            animateKeys();
        });
        audio.addEventListener('pause', () => { 
            if (raf) cancelAnimationFrame(raf); 
        });
        audio.addEventListener('ended', () => { 
            if (raf) cancelAnimationFrame(raf); 
        });

        // Attach event listeners to all keys
        function attachKeyEvents() {
            const allKeys = piano.querySelectorAll('.key, .black-key');
            
            allKeys.forEach(function(key) {
                // Hover effects
                key.addEventListener('mouseenter', function() {
                    this.classList.add('hover');
                });
                key.addEventListener('mouseleave', function() {
                    this.classList.remove('hover');
                });
                
                // Click events
                key.addEventListener('mousedown', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const noteName = this.getAttribute('data-note');
                    playRealisticPianoSound(noteName);
                    this.classList.add('hover');
                    setTimeout(() => this.classList.remove('hover'), 200);
                });
                
                // Touch events for mobile
                key.addEventListener('touchstart', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const noteName = this.getAttribute('data-note');
                    playRealisticPianoSound(noteName);
                    this.classList.add('hover');
                    setTimeout(() => this.classList.remove('hover'), 200);
                });
            });
        }
        
        // Initialize audio context on first user interaction
        document.addEventListener('click', initAudioContext, {once: true});
        document.addEventListener('touchstart', initAudioContext, {once: true});
        
        // Attach events when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', attachKeyEvents);
        } else {
            attachKeyEvents();
        }
        
        // Initialize time display
        updateTimeDisplay(0);
        
        // Fallback to ensure events are attached
        setTimeout(attachKeyEvents, 100);
        </script>
        </body>
        </html>
        """
        return html

    def create_instrument_confidence_chart(self, confidence_scores: Dict[str, float]) -> go.Figure:
        fig = go.Figure()
        instruments = list(confidence_scores.keys())
        scores = list(confidence_scores.values())
        colors = ['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 
                 'rgba(44, 160, 44, 0.8)', 'rgba(214, 39, 40, 0.8)']
        fig.add_trace(go.Bar(
            x=instruments,
            y=scores,
            marker_color=colors,
            text=[f'{score:.0%}' for score in scores],
            textposition='auto',
        ))
        fig.update_layout(
            title='Instrument Detection Confidence',
            yaxis=dict(
                title='Confidence Score',
                range=[0, 1],
                tickformat='%'
            ),
            template='plotly_white',
            height=300
        )
        return fig