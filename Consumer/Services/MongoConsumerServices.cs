using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using MongoDB.Bson;
using MongoDB.Driver;
using Confluent.Kafka;

namespace Consumer.Services;

public class MongoConsumerServices: BackgroundService
{
    private readonly ConsumerConfig _consumerConfig;
    private readonly IMongoCollection<BsonDocument> _collection;
    private readonly string _topic;

    public MongoConsumerServices(
        ConsumerConfig consumerConfig,
        IMongoDatabase database,
        IConfiguration configuration)
    {
        _consumerConfig = consumerConfig;
        _collection = database.GetCollection<BsonDocument>("CleanAnswers");
        _topic = configuration["Kafka:Topic"]!;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await Task.Run(async () =>
        {
            using var consumer = new ConsumerBuilder<Ignore, string>(_consumerConfig).Build();
            consumer.Subscribe(_topic);

            try
            {
                while (!stoppingToken.IsCancellationRequested)
                {
                    ConsumeResult<Ignore, string>? consumeResult = null;

                    try
                    {
                        consumeResult = consumer.Consume(stoppingToken);
                    }
                    catch (OperationCanceledException) { break; }
                    catch (ConsumeException ex)
                    {
                        Console.WriteLine($"Error: {ex.Error.Reason}");
                        continue;
                    }

                    if (consumeResult?.Message?.Value == null || string.IsNullOrWhiteSpace(consumeResult.Message.Value)){  continue; }

                    try
                    {
                        var document = BsonDocument.Parse(consumeResult.Message.Value);

                        await _collection.InsertOneAsync(document, cancellationToken: stoppingToken);

                        consumer.Commit(consumeResult);
                    }
                    catch (FormatException jsonEx)
                    {
                        Console.WriteLine($"Error in JSON: {jsonEx.Message}");
                        consumer.Commit(consumeResult);
                    }
                    catch (MongoException mongoEx)
                    {
                        Console.WriteLine($"Error in saving to MongoDB: {mongoEx.Message}");
                    }
                }
            }
            finally
            {
                consumer.Close();
            }
        }, stoppingToken);
    }
}


