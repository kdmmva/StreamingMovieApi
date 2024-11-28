using MovieStreamingApi.Data.Models;
using System.Text.Json.Serialization;

namespace MovieStreamingApi.Data.Responses
{
    public class MoviesResponse
    {
        [JsonPropertyName("results")]
        public List<Movie>? Results { get; set; }
    }
}
