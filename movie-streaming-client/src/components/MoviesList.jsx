import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const MoviesList = () => {
    const [movies, setMovies] = useState([]);
    const [error, setError] = useState(null);
    const [selectedMovie, setSelectedMovie] = useState(null);
    const navigate = useNavigate();

    const fetchMovies = async () => {
        try {
            const response = await axios.get('http://localhost:7210/movies');
            setMovies(response.data);
            setError(null);
        } catch (err) {
            setError(err);
            console.error('Error fetching movies:', err);
        }
    };

    useEffect(() => {
        fetchMovies();
    }, []);

    const handleMovieClick = async (movie) => {
        try {
            const response = await axios.post('http://localhost:5000/generate-movie-url', {
                title: movie.title,
            });
    
            if (response.data && response.data.stream_urls) {
                const streamUrls = response.data.stream_urls;
    
                console.log("Stream URLs for movie:", movie.title);
                Object.entries(streamUrls).forEach(([quality, url]) => {
                    console.log(`${quality}: ${url}`);
                });
    
                navigate(`/movies/${movie.id}`, {
                    state: {
                        movie: {
                            ...movie,
                            stream_urls: streamUrls,  
                        },
                    },
                });
    
            } else {
                console.error('Stream URLs missing in response:', response.data);
                setError(new Error('No stream URLs received from server.'));
            }
        } catch (err) {
            console.error('Error fetching movie stream URLs:', err);
            setError(err);
        }
    };

    const handleModalClose = () => {
        setSelectedMovie(null); 
    };

    return (
        <div className="max-w-4xl mx-auto bg-gray-50 p-6 my-8 rounded-lg shadow-lg">
            <h2 className="text-3xl font-semibold mb-6">Movies List</h2>
            {error && <div className="text-red-500 mb-4">Error: {error.message}</div>}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {Array.isArray(movies) && movies.length > 0 ? (
                    movies.map(movie => (
                        <div
                            key={movie.id}
                            className="bg-white shadow-md rounded-lg overflow-hidden cursor-pointer"
                            onClick={() => setSelectedMovie(movie)} 
                        >
                            <img
                                src={movie.posterUrl || '/placeholder.jpg'}
                                alt={movie.title}
                                className="w-full h-64 object-cover"
                            />
                            <div className="p-4">
                                <h3 className="text-xl font-bold mb-2">{movie.title}</h3>
                                <div className="mt-4">
                                    <span className="text-indigo-500 font-semibold">Release Date:</span> {movie.release_Date}
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="col-span-3 text-center text-gray-500">No movies found.</div>
                )}
            </div>

            {selectedMovie && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
                        <h3 className="text-2xl font-bold mb-4">{selectedMovie.title}</h3>
                        <p className="text-gray-700 mb-4">{selectedMovie.overview}</p>
                        <div className="text-right">
                            <button
                                className="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600 mr-2"
                                onClick={() => handleMovieClick(selectedMovie)}
                            >
                                Watch Now
                            </button>
                            <button
                                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                                onClick={handleModalClose}
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MoviesList;
