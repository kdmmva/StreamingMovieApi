using MovieStreamingApi.Data.Models;
using Newtonsoft.Json;

namespace MovieStreamingApi.Data.Responces
{
    public class MoviesResponse
    {
        [JsonProperty("results")]
        public List<Movie>? Results { get; set; }
    }
}