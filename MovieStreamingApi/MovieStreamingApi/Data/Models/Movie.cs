namespace MovieStreamingApi.Data.Models
{
    public class Movie
    {
        public int Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public string Overview { get; set; } = string.Empty;
        public string Release_Date { get; set; } = string.Empty;
        public string Poster_Path { get; set; } = string.Empty;

        public string PosterUrl { get; set; } = string.Empty;
    }
}
