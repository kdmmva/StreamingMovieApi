import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const MovieSearch = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [movies, setMovies] = useState([]);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const navigate = useNavigate();

    const handleSearch = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.get(`http://localhost:7210/search?query=${searchTerm}`);
            console.log('Server response:', response);
            setMovies(response.data);
            setIsModalOpen(true);
        } catch (err) {
            setError(err);
            console.error('Error fetching movies:', err);
        }
    };

    const handleMovieClick = async (movie) => {
        try {
            const response = await axios.post('http://localhost:5000/generate-movie-url', {
                title: movie.title,
            });
    
            if (response.data && response.data.streams) {
                const streams = response.data.streams; 
                console.log("Stream URLs for movie:", movie.title, streams);
    
                navigate(`/movies/${movie.id}`, {
                    state: {
                        movie: {
                            ...movie,
                            streams, 
                        },
                    },
                });
            } else {
                console.error('Stream data missing in response:', response.data);
                setError(new Error('No stream data received from server.'));
            }
        } catch (err) {
            console.error('Error fetching movie stream data:', err);
            setError(err);
        }
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-bl from-indigo-700 via-purple-800 to-gray-900 text-white">
            <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-8 rounded-xl shadow-2xl w-full max-w-md transform transition-all hover:scale-105">
                <h1 className="text-4xl font-extrabold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                    Movie Search
                </h1>
                <form onSubmit={handleSearch} className="flex flex-col items-center">
                    <input
                        type="text"
                        placeholder="Enter movie title"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-300 bg-gray-800 shadow-md mb-4 placeholder-gray-500"
                    />
                    <button
                        type="submit"
                        className="w-full bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-4 py-2 rounded-lg hover:opacity-90 transition-all duration-300 shadow-lg transform hover:scale-105"
                    >
                        Search
                    </button>
                </form>

                {error && (
                    <div className="mt-4 text-red-400 text-center">
                        Error: {error.response?.data || error.message}
                    </div>
                )}
            </div>

            {isModalOpen && (
                <>
                    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
                        <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-black p-6 rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto relative">
                            <h2 className="text-2xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">
                                Search Results
                            </h2>
                            <div>
                                {movies && movies.length > 0 ? (
                                    <ul className="space-y-4">
                                        {movies.map((movie, index) => (
                                            <li
                                                key={index}
                                                className="border-b border-gray-600 pb-2 cursor-pointer hover:bg-gray-700 p-2 rounded-lg"
                                                onClick={() => handleMovieClick(movie)}
                                            >
                                                <h3 className="text-lg font-semibold text-purple-400">
                                                    {movie.title}
                                                </h3>
                                                <p className="text-sm text-gray-500">
                                                    Release Date: {movie.release_Date}
                                                </p>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="text-gray-400">
                                        No movies found.
                                    </p>
                                )}
                            </div>
                            <button
                                onClick={closeModal}
                                className="absolute top-4 right-4 text-2xl text-gray-300 bg-gray-700 rounded-full p-2 hover:bg-red-600 transition-colors"
                            >
                                &times;
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default MovieSearch;
