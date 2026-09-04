using DeveloprtLearningDataApi.Models;
using DeveloprtLearningDataApi.Repository;
using MongoDB.Bson;
using MongoDB.Driver;
var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var mongoSettings = builder.Configuration.GetSection("MongoSettings");
var connectionString = mongoSettings["ConnectionString"];
var databaseName = mongoSettings["DatabaseName"];
var collectionName = mongoSettings["CollectionName"];

builder.Services.AddSingleton<IMongoClient>(sp => new MongoClient(connectionString));

builder.Services.AddScoped<IMongoCollection<CleanSurveyAnswer>>(sp =>
{
    var client = sp.GetRequiredService<IMongoClient>();
    var database = client.GetDatabase(databaseName);
    return database.GetCollection<CleanSurveyAnswer>(collectionName);
});
builder.Services.AddScoped<ISurvyRepository, SurvyRepository>();

var app = builder.Build();
// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
