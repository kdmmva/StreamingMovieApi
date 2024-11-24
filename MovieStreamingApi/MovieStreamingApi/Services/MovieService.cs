using System.Net.Http.Json;
using MovieStreamingApi.Data.Models;
using MovieStreamingApi.Data.Responces;

namespace MovieStreamingApi.Services
{
    public class MovieService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private const string BaseImageUrl = "https://image.tmdb.org/t/p/w780"; 

        public MovieService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _configuration = configuration;
        }

        public async Task<IEnumerable<Movie>> GetPopularMoviesAsync()
        {
            var apiKey = _configuration["ApiKey:Key"];
            var response = await _httpClient.GetAsync($"http://api.themoviedb.org/3/movie/popular?api_key={apiKey}");
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<MoviesResponse>();
            if (result?.Results == null)
                return Enumerable.Empty<Movie>();

            foreach (var movie in result.Results)
            {
                movie.PosterUrl = GetPosterUrl(movie.Poster_Path);
            }

            return result.Results;
        }

        public async Task<IEnumerable<Movie>> SearchMoviesAsync(string query)
        {
            var apiKey = _configuration["ApiKey:Key"];
            var response = await _httpClient.GetAsync($"http://api.themoviedb.org/3/search/movie?api_key={apiKey}&query={query}");
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<MoviesResponse>();
            if (result?.Results == null)
                return Enumerable.Empty<Movie>();

            foreach (var movie in result.Results)
            {
                movie.PosterUrl = GetPosterUrl(movie.Poster_Path); 
            }

            return result.Results;
        }

        private string GetPosterUrl(string posterPath)
        {
            if (string.IsNullOrEmpty(posterPath))
                return "https://via.placeholder.com/500x750?text=No+Poster"; 

            return $"{BaseImageUrl}{posterPath}";
        }
    }
}
