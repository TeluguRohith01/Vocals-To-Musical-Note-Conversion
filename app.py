import streamlit as st
import io
from audio_processor import AudioProcessor
from visualizer import AudioVisualizer
from utils import validate_audio_file
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from auth import auth_bp, db
from config import Config


def main():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from Config class

    # Initialize the SQLAlchemy database instance
    db.init_app(app)

    # Setup Flask-Login's LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated

    # Register the authentication blueprint with URL prefix '/auth'
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Protected route that requires login
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')  # Render the dashboard template

    # Create database tables within the app context before running the app
    with app.app_context():
        db.create_all()  # Create all database tables

    st.set_page_config(
        page_title="Audio Analysis Tool",
        page_icon="🎵",
        layout="wide"
    )
    
    # Enhanced dark theme with white subject styling
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #181818 !important;
            background-image: none !important;
        }
        .block-container, .st-cg, .st-cg > div, .st-cj, .st-ce {
            background-color: #222222 !important;
        }
        header, .st-af, .st-b7, .st-eb, .st-em {
            background: #212121 !important;
        }
        /* Text and subject color adjustments */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown, .stText, .stSubheader, .st-b3, .st-ag, .st-ah, .st-ax, label,
        .css-10trblm, .css-1cpxqw2, .stExpander, .st-bb, .st-ax {
            color: #fff !important;
        }
        p, span, .stMarkdown p, .markdown-text-container {
            color: #e0e0e0 !important;
        }
        /* Cards and widgets backgrounds */
        .stTextInput, .stSlider, .stSelectbox, .stButton, .stFileUploader, .stDataFrame, .stPlotlyChart, .st-cy {
            background-color: #252525 !important;
            color: #fafafa !important;
            border-radius: 6px;
        }
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #181818 !important;
        }
        /* File uploader SVG (icon) styles - modern, accent, flat */
        [data-testid="stFileUploader"] svg {
            fill: #3a7cff !important;      /* Accent blue for high contrast */
            stroke: none !important;       /* Remove border */
            width: 32px !important;
            height: 32px !important;
            display: block;
            margin: 0 auto 12px auto;
            filter: drop-shadow(0 2px 6px rgba(58,124,255,0.2)); /* Subtle glow, no boldness */
            box-shadow: none !important;
        }

        /* File uploader helper text styles - all text visible and bold */
        [data-testid="stFileUploader"] span {
            color: #fff !important;      /* White text for better contrast */
            font-size: 1.08rem;
            font-weight: 700;            /* Bold weight for better visibility */
            letter-spacing: 0.2px;
        }
        
        [data-testid="stFileUploader"] label {
            color: #e0e0e0 !important;   /* Light gray for better visibility */
            font-weight: 500;
        }

        /* File uploader drag and drop area styling - clean flat look no border */
        [data-testid="stFileUploader"] > div {
            background-color: #212226 !important;
            border: none !important;
            color: #fff !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08); /* Slight depth only */
            border-radius: 10px !important;
        }
        
        /* Focus and drag hover effect */
        [data-testid="stFileUploader"] > div:focus,
        [data-testid="stFileUploader"] > div:hover {
            background-color: #252942 !important;
            box-shadow: 0 0 16px rgba(58,124,255,0.15); /* Subtle glow on hover */
        }
        
        /* Piano visualization: animated hover/active style */
        .piano .key,
        .piano-container .key {
            transition: background 0.15s, box-shadow 0.15s;
        }
        
        .piano .key.active, 
        .piano-container .key.active {
            background: #3a7cff !important;
            box-shadow: 0 0 8px #3a7cff99;
            color: #fff;
            border: none;
        }
        
        .piano .black-key.active, 
        .piano-container .black-key.active {
            background: #1e6be8 !important;
            box-shadow: 0 0 14px #3a7cff99;
            color: #fff;
            border: none;
        }
        
        .piano .key:hover, 
        .piano-container .key:hover {
            background: #285adf !important;
            box-shadow: 0 0 8px #285adf99;
            color: #fff;
            cursor: pointer;
        }
        
        .piano .black-key:hover, 
        .piano-container .black-key:hover {
            background: #174092 !important;
            box-shadow: 0 0 14px #174092bb;
            color: #fff;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Set only the uploader helper text ("Drag and drop file here") to black
    st.markdown(
        """
        <style>
        [data-testid="stFileUploader"] span {
            color: inherit !important; /* Reset in case set elsewhere */
        }
        [data-testid="stFileUploader"] span:has-text('Drag and drop file') {
            color: #000 !important; font-weight: 700 !important;
        }
        /* For extra compatibility if :has-text isn't supported (some older browsers/Streamlit versions): */
        [data-testid="stFileUploader"] span[style*="Drag and drop file"], 
        [data-testid="stFileUploader"] span:contains("Drag and drop file"), 
        [data-testid="stFileUploader"] span {
            /* fallback via JS beneath */
        }
        </style>
        <script>
        // Fallback for browsers/Streamlit that don't support :has-text
        setTimeout(function() {
          document.querySelectorAll('[data-testid="stFileUploader"] span').forEach(function(span) {
            if (span.textContent.includes('Drag and drop file')) {
              span.style.color = '#000';
              span.style.fontWeight = '700';
            }
          });
        }, 300);
        </script>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<h1 style='color: white;'>🎵 Audio Analysis Tool</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color: white;'>Upload an audio file to analyze pitch and detect musical notes</p>",
        unsafe_allow_html=True
    )

    # Initialize processors
    audio_processor = AudioProcessor()
    visualizer = AudioVisualizer()

    # File upload
    uploaded_file = st.file_uploader(
        "Choose an audio file (WAV or MP3)", 
        type=['wav', 'mp3']
    )

    if uploaded_file is not None:
        # Validate file
        is_valid, message = validate_audio_file(uploaded_file)

        if not is_valid:
            st.error(message)
            return

        try:
            # Process audio
            with st.spinner('Processing audio file...'):
                audio_bytes = uploaded_file.read()
                y, sr = audio_processor.process_audio(io.BytesIO(audio_bytes))

                # Detect notes and create visualizations
                notes_data = audio_processor.detect_notes(y, sr)
                notes_data['sr'] = sr  # Add sample rate to notes data

                # Display audio player with synchronized keyboard
                st.subheader("Audio Player with Virtual Piano")
                audio_player_html = visualizer.create_audio_player_with_keyboard(
                    audio_bytes,
                    notes_data
                )
                # Ensure HTML is rendered properly with components.html
                import streamlit.components.v1 as components
                components.html(audio_player_html, height=350)

                # Create columns for visualizations
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Pitch Analysis")
                    pitches = audio_processor.detect_pitch(y, sr)
                    pitch_fig = visualizer.create_pitch_map(pitches, sr)
                    st.plotly_chart(pitch_fig, use_container_width=True)

                with col2:
                    st.subheader("Note Detection")
                    notes_fig = visualizer.create_note_visualization(
                        notes_data['notes'],
                        notes_data['onset_frames'],
                        sr,
                        notes_data['confidences']
                    )
                    st.plotly_chart(notes_fig, use_container_width=True)

                # Instrument classification
                st.subheader("Instrument Classification")
                confidence_scores = audio_processor.classify_instrument(y, sr)
                instrument_fig = visualizer.create_instrument_confidence_chart(confidence_scores)
                st.plotly_chart(instrument_fig, use_container_width=True)

                # Display detected notes
                st.subheader("Detected Musical Notes")
                if notes_data['notes']:
                    note_counts = {}
                    for note in notes_data['notes']:
                        note_counts[note] = note_counts.get(note, 0) + 1

                    st.write("Most common notes detected:")
                    for note, count in sorted(note_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                        st.write(f"- {note}: {count} times")
                else:
                    st.write("No musical notes detected in the audio")

        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")

    # Add information section
    with st.expander("ℹ️ About this tool"):
        st.write("""
        This enhanced audio analysis tool provides:
        - Interactive virtual piano keyboard synchronized with audio playback
        - Detailed pitch visualization with frequency mapping
        - Piano roll view of detected musical notes
        - Instrument classification with confidence scores
        - Note occurrence statistics

        Supported file formats: WAV, MP3
        Maximum file size: 10MB

        The tool analyzes the audio using advanced signal processing techniques to:
        1. Generate a frequency-based pitch map
        2. Detect and display musical notes on a piano roll
        3. Identify the most likely musical instrument
        4. Show note statistics and patterns
        """)

if __name__ == "__main__":
    main()