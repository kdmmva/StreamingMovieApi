import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ReactPlayer from 'react-player';
import { FaForward, FaBackward, FaSpinner } from 'react-icons/fa';

const VideoPlayer = () => {
    const location = useLocation();
    const playerRef = useRef(null);

    const movieTitle = location.state?.movie?.title || 'Unknown Movie';
    const movieStreamUrls = location.state?.movie?.stream_urls || {}; // Ссылаемся на объект с качествами и URL

    const [videoSource, setVideoSource] = useState('');
    const [selectedQuality, setSelectedQuality] = useState('');
    const [loading, setLoading] = useState(true);
    const [playing, setPlaying] = useState(true);
    const [volume, setVolume] = useState(0.8);
    const [muted, setMuted] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [progress, setProgress] = useState(0);

    // Устанавливаем URL по умолчанию
    useEffect(() => {
        if (movieStreamUrls && Object.keys(movieStreamUrls).length > 0) {
            const lastSelectedQuality = localStorage.getItem('selectedQuality');
            const defaultQuality =
                lastSelectedQuality && movieStreamUrls[lastSelectedQuality]
                    ? lastSelectedQuality
                    : Object.keys(movieStreamUrls)[0];

            setSelectedQuality(defaultQuality);
            setVideoSource(movieStreamUrls[defaultQuality]);
            console.log(`Default video source set to: ${movieStreamUrls[defaultQuality]}`);
        }
    }, [movieStreamUrls]);

    // Обработка смены качества
    const handleQualityChange = (quality) => {
        console.log('Selected quality:', quality);
    
        const storedUrls = JSON.parse(localStorage.getItem('movieStreamUrls'));
        console.log('Stored URLs:', storedUrls);
    
        if (storedUrls && storedUrls[quality]) {
            const videoUrl = Array.isArray(storedUrls[quality]) ? storedUrls[quality][0] : storedUrls[quality];
    
            // Проверяем как URL, так и качество
            if (videoSource !== videoUrl || selectedQuality !== quality) {
                setVideoSource(videoUrl);
                setSelectedQuality(quality);
                localStorage.setItem('selectedQuality', quality); // Сохраняем выбранное качество
                console.log(`Video source set to: ${videoUrl}`);
            } else {
                console.warn('Selected quality and URL are the same as current.');
            }
        } else {
            console.error(`URL not found for quality: ${quality}`);
        }
    };
    
    // Обработка загрузки видео
    const handleReady = () => {
        setLoading(false); // Скрыть индикатор загрузки
    };

    // Перемотка видео
    const handleForward = () => {
        const currentTime = playerRef.current.getCurrentTime();
        playerRef.current.seekTo(currentTime + 10);
    };

    const handleBackward = () => {
        const currentTime = playerRef.current.getCurrentTime();
        playerRef.current.seekTo(currentTime - 10);
    };

    // Обработка полного экрана
    const handleFullscreen = () => {
        const player = playerRef.current.wrapper;

        if (player.requestFullscreen) {
            player.requestFullscreen();
        } else if (player.webkitRequestFullscreen) {
            player.webkitRequestFullscreen();
        } else if (player.mozRequestFullScreen) {
            player.mozRequestFullScreen();
        } else if (player.msRequestFullscreen) {
            player.msRequestFullscreen();
        }
    };

    return (
        <div
            className="relative bg-black rounded-md overflow-hidden max-w-4xl mx-auto shadow-lg"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div className="absolute top-0 left-0 right-0 bg-black bg-opacity-80 text-white p-4 text-lg flex justify-between items-center">
                <span className="truncate">{movieTitle}</span>
                <button
                    onClick={handleFullscreen}
                    className="text-white text-lg"
                >
                    ⤢
                </button>
            </div>

            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                    <FaSpinner className="animate-spin text-white text-4xl" />
                </div>
            )}

            <ReactPlayer
                key={selectedQuality}
                ref={playerRef}
                url={videoSource}
                playing={playing}
                volume={volume}
                muted={muted}
                width="100%"
                height="100%"
                className="rounded-lg"
                onReady={handleReady}
                onProgress={({ played }) => setProgress(played * 100)}
                controls={true}
            />

            <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white p-2 rounded-md">
                <select
                    value={selectedQuality}
                    onChange={(e) => handleQualityChange(e.target.value)}
                    className="bg-transparent text-white"
                >
                    {Object.keys(movieStreamUrls).map((quality) => (
                        <option key={quality} value={quality}>
                            {quality}
                        </option>
                    ))}
                </select>
            </div>

            {isHovered && (
                <div className="absolute top-1/2 transform -translate-y-1/2 w-full flex justify-between">
                    <button
                        onClick={handleBackward}
                        className="text-white text-3xl ml-4"
                    >
                        <FaBackward />
                    </button>
                    <button
                        onClick={handleForward}
                        className="text-white text-3xl mr-4"
                    >
                        <FaForward />
                    </button>
                </div>
            )}
        </div>
    );
};

export default VideoPlayer;
