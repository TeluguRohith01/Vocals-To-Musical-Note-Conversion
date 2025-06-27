import React, { useState, useEffect } from 'react';

const PianoRollGrid = () => {
  const [grid, setGrid] = useState(Array(16).fill(Array(12).fill(false))); // 16 time steps, 12 notes
  const [isPlaying, setIsPlaying] = useState(false);
  const [bpm, setBpm] = useState(120);
  const [audioContext, setAudioContext] = useState(null);
  const [audioBuffer, setAudioBuffer] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const notes = ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4'];

  useEffect(() => {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    setAudioContext(context);
  }, []);

  const toggleNote = (step, noteIndex) => {
    const newGrid = grid.map((row, rIndex) => {
      if (rIndex === noteIndex) {
        const newRow = [...row];
        newRow[step] = !newRow[step];
        return newRow;
      }
      return row;
    });
    setGrid(newGrid);
  };

  const playNotes = () => {
    setIsPlaying(true);
    let step = 0;
    const interval = (60 / bpm) * 1000; // Calculate interval based on BPM

    const playStep = () => {
      if (step >= grid[0].length) {
        step = 0; // Reset to the first step
      }
      grid.forEach((row, noteIndex) => {
        if (row[step]) {
          playSound(noteIndex);
        }
      });
      step++;
    };

    const intervalId = setInterval(playStep, interval);
    return () => clearInterval(intervalId);
  };

  const playSound = (noteIndex) => {
    const frequencies = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88];
    const oscillator = audioContext.createOscillator();
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(frequencies[noteIndex], audioContext.currentTime);
    oscillator.connect(audioContext.destination);
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.1); // Play for 100ms
  };

  const handlePlay = () => {
    playNotes();
  };

  const handleStop = () => {
    setIsPlaying(false);
  };

  const handleClear = () => {
    setGrid(Array(16).fill(Array(12).fill(false)));
  };

  const handleBPMChange = (e) => {
    setBpm(e.target.value);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = async (e) => {
      const arrayBuffer = e.target.result;
      const audioData = await audioContext.decodeAudioData(arrayBuffer);
      setAudioBuffer(audioData);
      // Here you would implement note detection logic
      // For simplicity, we will simulate detected notes
      simulateNoteDetection();
    };
    reader.readAsArrayBuffer(file);
  };

  const simulateNoteDetection = () => {
    // Simulate detected notes for demonstration
    const simulatedNotes = [
      { note: 0, time: 0 }, // C4 at time step 0
      { note: 2, time: 4 }, // D4 at time step 4
      { note: 4, time: 8 }, // E4 at time step 8
    ];
    const newGrid = Array(16).fill(Array(12).fill(false));
    simulatedNotes.forEach(({ note, time }) => {
      newGrid[time][note] = true;
    });
    setGrid(newGrid);
  };

  return (
    <div className="piano-roll-grid">
      <div className="controls">
        <input type="file" accept="audio/*" onChange={handleFileUpload} />
        <button onClick={handlePlay}>Play</button>
        <button onClick={handleStop}>Stop</button>
        <button onClick={handleClear}>Clear</button>
        <input
          type="number"
          value={bpm}
          onChange={handleBPMChange}
          min="60"
          max="240"
        />
        <span>BPM: {bpm}</span>
      </div>
      <div className="grid">
        {notes.map((note, noteIndex) => (
          <div key={note} className="note-row">
            <div className="note-label">{note}</div>
            {grid[noteIndex].map((isActive, stepIndex) => (
              <div
                key={stepIndex}
                className={`grid-cell ${isActive ? 'active' : ''}`}
                onClick={() => toggleNote(stepIndex, noteIndex)}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PianoRollGrid;