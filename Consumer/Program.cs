//using System.IO;
//using Confluent.Kafka;
//using Consumer.Services;
//using Microsoft.Extensions.Configuration;
//using Microsoft.Extensions.DependencyInjection;
//using Microsoft.Extensions.Hosting;
//using MongoDB.Driver;

//var configuration = new ConfigurationBuilder()
//    .SetBasePath(Directory.GetCurrentDirectory())
//    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
//    .Build();

//var builder = Host.CreateDefaultBuilder(args);

//builder.ConfigureServices((hostContext, services) =>
//{
//    var consumerConfig = new ConsumerConfig();
//    configuration.GetSection("Kafka:Consumer").Bind(consumerConfig);
//    services.AddSingleton(consumerConfig);

//    services.AddSingleton<IMongoClient>(sp =>
//        new MongoClient(configuration["MongoDb:ConnectionString"]));

//    services.AddSingleton<IMongoDatabase>(sp =>
//    {
//        var client = sp.GetRequiredService<IMongoClient>();
//        return client.GetDatabase(configuration["MongoDb:DatabaseName"]);
//    });

//    services.AddHostedService<MongoConsumerServices>();
//});

//await builder.Build().RunAsync();



using System.IO;
using Confluent.Kafka;
using Consumer.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MongoDB.Driver;

var builder = Host.CreateDefaultBuilder(args);

builder.ConfigureServices((hostContext, services) =>
{
    var configuration = hostContext.Configuration;

    var consumerConfig = new ConsumerConfig();
    configuration.GetSection("Kafka:Consumer").Bind(consumerConfig);
    services.AddSingleton(consumerConfig);

    services.AddSingleton<IMongoClient>(sp =>
        new MongoClient(configuration["MongoDb:ConnectionString"]));

    services.AddSingleton<IMongoDatabase>(sp =>
    {
        var client = sp.GetRequiredService<IMongoClient>();
        return client.GetDatabase(configuration["MongoDb:DatabaseName"]);
    });

    services.AddHostedService<MongoConsumerServices>();
});

await builder.Build().RunAsync();



