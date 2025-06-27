import React, { useState } from 'react';

const MusicSequencer = () => {
  const [isGridViewOpen, setIsGridViewOpen] = useState(false);

  const handleOpenGridView = () => {
    setIsGridViewOpen(true);
  };

  const handleCloseGridView = () => {
    setIsGridViewOpen(false);
  };

  return (
    <div>
      <button onClick={handleOpenGridView}>Open Grid View</button>
      {isGridViewOpen && (
        <div className="grid-view">
          {/* Grid view code goes here */}
          <div className="bg-gray-800 rounded-lg p-4 h-full overflow-auto">
            {/* Step Numbers */}
            <div className="flex mb-2">
              <div className="w-16 flex-shrink-0"></div>
              <div className="flex gap-1 flex-1">
                {Array.from({ length: 16 }, (_, i) => (
                  <div key={i} className="flex-1 text-center text-xs py-1 rounded">
                    {i + 1}
                  </div>
                ))}
              </div>
            </div>

            {/* Track Rows */}
            {tracks.map((track, trackIndex) => (
              <div key={trackIndex} className="flex items-center gap-1 mb-2">
                {/* Track Label */}
                <div
                  className={`w-16 flex-shrink-0 text-xs font-medium px-2 py-2 rounded border ${
                    track.name.includes('#')
                      ? 'bg-gray-800 text-white border-gray-600'
                      : 'bg-white text-black border-gray-300'
                  }`}
                >
                  {track.name}
                </div>

                {/* Step Buttons */}
                <div className="flex gap-1 flex-1">
                  {pattern[trackIndex].map((isActive, stepIndex) => (
                    <button
                      key={stepIndex}
                      onClick={() => toggleStep(trackIndex, stepIndex)}
                      className={`flex-1 h-8 rounded transition-all duration-100 ${
                        detectedNotes[trackIndex] && detectedNotes[trackIndex][stepIndex]
                          ? `bg-green-500`
                          : isActive
                            ? `shadow-lg ${track.name.includes('#') ? 'bg-red-500' : 'bg-blue-500'}`
                            : 'bg-gray-700 hover:bg-gray-600 bg-opacity-50'
                      } ${
                        currentStep === stepIndex && isPlaying
                          ? 'ring-2 ring-yellow-400'
                          : ''
                      }`}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MusicSequencer;