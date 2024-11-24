using MovieStreamingApi.Services;
using MovieStreamingApi.Endpoints;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpClient<MovieService>();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp",
        builder =>
        {
            builder.WithOrigins("http://localhost:3000")
                   .AllowAnyHeader()
                   .AllowAnyMethod();
        });
});

var app = builder.Build();

app.UseCors("AllowReactApp");
app.UseRouting();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

MovieEndpoints.MapMovieEndpoints(app);

app.Run();
