import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MovieSearch from './components/MovieSearch';
import MoviesList from './components/MoviesList';
import VideoPlayer from './components/VideoPlayer';

const App = () => {
    const [movies, setMovies] = useState([]);

    return (
        <Router>
            <div className="app-container min-h-screen flex flex-col">
            <header className="bg-gradient-to-r from-gray-700 via-gray-800 to-black text-white p-6 text-center shadow-lg border-b border-gray-600">
    <h1 className="text-4xl font-bold tracking-tight font-[Poppins]">
        Movie Streaming Service
    </h1>
</header>

                <main className="p-4 flex-grow">
                    <Routes>
                        <Route
                            path="/"
                            element={
                                <>
                                    <MovieSearch setMovies={setMovies} />
                                    <MoviesList movies={movies} />
                                </>
                            }
                        />
                        <Route path="/movies/:id" element={<VideoPlayer />} />
                    </Routes>
                </main>
                <footer className="text-center py-4 bg-gray-900 text-white">
                    <p>&copy; 2024 Movie Streaming Service</p>
                </footer>
            </div>
        </Router>
    );
};

export default App;

