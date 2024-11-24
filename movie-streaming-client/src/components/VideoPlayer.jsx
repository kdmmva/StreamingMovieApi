import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ReactPlayer from 'react-player';
import {
    FaPlay,
    FaPause,
    FaForward,
    FaBackward,
    FaVolumeUp,
    FaVolumeMute,
    FaSpinner,
    FaExpand
} from 'react-icons/fa';

const VideoPlayer = () => {
    const location = useLocation();
    const playerRef = useRef(null);

    const movieTitle = location.state?.movie?.title || 'Unknown Movie';
    const movieStreamUrls = location.state?.movie?.stream_urls || {};

    const [videoSource, setVideoSource] = useState('');
    const [selectedQuality, setSelectedQuality] = useState('');
    const [loading, setLoading] = useState(true);
    const [playing, setPlaying] = useState(true);
    const [volume, setVolume] = useState(0.8);
    const [muted, setMuted] = useState(false);
    const [progress, setProgress] = useState(0);
    const [playbackRate, setPlaybackRate] = useState(1);

    const [isDragging, setIsDragging] = useState(false);

    useEffect(() => {
        if (movieStreamUrls && Object.keys(movieStreamUrls).length > 0) {
            const lastSelectedQuality = localStorage.getItem('selectedQuality');
            const defaultQuality =
                lastSelectedQuality && movieStreamUrls[lastSelectedQuality]
                    ? lastSelectedQuality
                    : Object.keys(movieStreamUrls)[0];

            setSelectedQuality(defaultQuality);
            setVideoSource(movieStreamUrls[defaultQuality]);
        }
    }, [movieStreamUrls]);

    useEffect(() => {
        const handleKeyDown = (event) => {
            if (!playerRef.current) return;

            if (event.key === ' ') {
                event.preventDefault();
                togglePlay();
            } else if (event.key === 'ArrowRight') {
                handleFastForward();
            } else if (event.key === 'ArrowLeft') {
                handleRewind();
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, []);

    const handleQualityChange = (quality) => {
        if (movieStreamUrls[quality]) {
            setVideoSource(movieStreamUrls[quality]);
            setSelectedQuality(quality);
            localStorage.setItem('selectedQuality', quality);
        }
    };

    const togglePlay = () => setPlaying((prev) => !prev);
    const toggleMute = () => setMuted((prev) => !prev);

    const handleVolumeChange = (e) => {
        const newVolume = parseFloat(e.target.value);
        setVolume(newVolume);
        setMuted(newVolume === 0);
    };

    const handleProgressClick = (e) => {
        const rect = e.target.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        const newTime = percent * playerRef.current.getDuration();
        playerRef.current.seekTo(newTime);
        setProgress(percent * 100);
    };

    const handleReady = () => setLoading(false);

    const handleRewind = () => {
        const currentTime = playerRef.current.getCurrentTime();
        playerRef.current.seekTo(currentTime - 10);
    };

    const handleFastForward = () => {
        const currentTime = playerRef.current.getCurrentTime();
        playerRef.current.seekTo(currentTime + 10);
    };

    const handlePlaybackRateChange = (rate) => {
        setPlaybackRate(rate);
    };

    const handleDragStart = (e) => {
        setIsDragging(true);
        handleProgressClick(e);
    };

    const handleDragEnd = () => {
        setIsDragging(false);
    };

    const handleDrag = (e) => {
        if (!isDragging) return;
        handleProgressClick(e);
    };

    return (
        <div className="relative bg-black rounded-lg overflow-hidden max-w-4xl mx-auto shadow-lg">
            <div className="absolute top-0 left-0 right-0 bg-black bg-opacity-80 text-white p-3 text-lg flex justify-between items-center">
                <span className="truncate">{movieTitle}</span>
            </div>

            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                    <FaSpinner className="animate-spin text-white text-4xl" />
                </div>
            )}

            <ReactPlayer
                ref={playerRef}
                url={videoSource}
                playing={playing}
                volume={volume}
                muted={muted}
                playbackRate={playbackRate}
                width="100%"
                height="100%"
                className="rounded-lg"
                onReady={handleReady}
                onProgress={({ played }) => !isDragging && setProgress(played * 100)}
                controls={false}
            />

            <div
                className="absolute bottom-14 left-0 right-0 h-3 bg-gray-800 rounded-full cursor-pointer transition-all duration-300 hover:h-5"
                onMouseDown={handleDragStart}
                onMouseUp={handleDragEnd}
                onMouseMove={handleDrag}
            >
                <div
                    className="h-full bg-gradient-to-r from-red-500 to-yellow-500 rounded-full"
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-90 text-white p-4 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleRewind}
                        className="text-2xl hover:text-red-500 transition"
                    >
                        <FaBackward />
                    </button>

                    <button onClick={togglePlay} className="text-2xl hover:text-red-500 transition">
                        {playing ? <FaPause /> : <FaPlay />}
                    </button>

                    <button
                        onClick={handleFastForward}
                        className="text-2xl hover:text-red-500 transition"
                    >
                        <FaForward />
                    </button>

                    <button onClick={toggleMute} className="text-2xl hover:text-red-500 transition">
                        {muted ? <FaVolumeMute /> : <FaVolumeUp />}
                    </button>

                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={volume}
                        onChange={handleVolumeChange}
                        className="w-24"
                    />
                </div>

                <select
                    value={playbackRate}
                    onChange={(e) => handlePlaybackRateChange(Number(e.target.value))}
                    className="bg-gray-800 text-white rounded-md px-2 py-1"
                >
                    {[0.5, 1, 1.5, 2].map((rate) => (
                        <option key={rate} value={rate}>
                            {rate}x
                        </option>
                    ))}
                </select>

                <select
                    value={selectedQuality}
                    onChange={(e) => handleQualityChange(e.target.value)}
                    className="bg-gray-800 text-white rounded-md px-2 py-1"
                >
                    {Object.keys(movieStreamUrls).map((quality) => (
                        <option key={quality} value={quality}>
                            {quality}
                        </option>
                    ))}
                </select>

                <button
                    onClick={() => playerRef.current.wrapper.requestFullscreen()}
                    className="text-2xl hover:text-red-500 transition"
                >
                    <FaExpand />
                </button>
            </div>
        </div>
    );
};

export default VideoPlayer;
