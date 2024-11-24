using Microsoft.AspNetCore.Mvc;
using MovieStreamingApi.Data.Models;
using MovieStreamingApi.Services;

namespace MovieStreamingApi.Endpoints
{
    public static class MovieEndpoints
    {
        public static IEndpointRouteBuilder MapMovieEndpoints(this IEndpointRouteBuilder app)
        {
            app.MapGet("/movies", GetAllMovies);
            app.MapGet("/search", SearchMovies);

            return app;
        }

        private static async Task<IResult> GetAllMovies(MovieService tmdbService)
        {
            var movies = await tmdbService.GetPopularMoviesAsync();
            return movies.Any()
                ? Results.Ok(movies)
                : Results.NotFound("No movies found.");
        }

        private static async Task<IResult> SearchMovies(string query, MovieService tmdbService)
        {
            var movies = await tmdbService.SearchMoviesAsync(query);
            return movies.Any()
                ? Results.Ok(movies)
                : Results.NotFound("No movies found.");
        }
    }


}
