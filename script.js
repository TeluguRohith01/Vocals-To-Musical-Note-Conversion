// script.js
const pianoGrid = document.querySelector('.piano-grid');
const gridContainer = document.querySelector('.grid-container');
const rows = document.querySelectorAll('.row');
const cols = document.querySelectorAll('.col');

// add event listeners to columns
cols.forEach((col) => {
  col.addEventListener('click', () => {
    // toggle active class
    col.classList.toggle('active');
    // play note
    playNote(col.getAttribute('data-note'));
  });
});

// function to play note
function playNote(note) {
  // use Web Audio API to play note
  const audioContext = new AudioContext();
  const oscillator = audioContext.createOscillator();
  oscillator.type = 'sine';
  oscillator.frequency.value = getFrequency(note);
  oscillator.connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + 1);
}

// function to get frequency of note
function getFrequency(note) {
  const noteFrequencies = {
    'C3': 261.63,
    'C#3/Db3': 277.18,
    'D3': 293.66,
    // ... add more notes
  };
  return noteFrequencies[note];
}