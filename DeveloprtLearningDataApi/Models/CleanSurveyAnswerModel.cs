using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace DeveloprtLearningDataApi.Models;

[BsonIgnoreExtraElements]
public class CleanSurveyAnswer
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; } = null!;

    [BsonElement("responseId")]
    public long ResponseId { get; set; }

    [BsonElement("age")]
    public string Age { get; set; } = string.Empty;

    [BsonElement("yearsCode")]
    public long? YearsCode { get; set; }

    [BsonElement("devType")]
    public string? DevType { get; set; }

    [BsonElement("learnCodeChoose")]
    public string? LearnCodeChoose { get; set; }

    [BsonElement("learningMethods")]
    public List<string>? LearningMethods { get; set; }

    [BsonElement("learnCodeAI")]
    public string? LearnCodeAI { get; set; }

    [BsonElement("aiLearningMethods")]
    public List<string>? AiLearningMethods { get; set; }

    [BsonElement("aiUsage")]
    public string? AiUsage { get; set; }

    [BsonElement("aiTrust")]
    public string? AiTrust { get; set; }

    [BsonElement("aiSentiment")]
    public string? AiSentiment { get; set; }

    [BsonElement("experienceLevel")]
    public string ExperienceLevel { get; set; } = string.Empty;

    [BsonElement("usesDocumentation")]
    public bool UsesDocumentation { get; set; }

    [BsonElement("usesAIForLearning")]
    public bool UsesAIForLearning { get; set; }

    [BsonElement("usesStackOverflow")]
    public bool UsesStackOverflow { get; set; }
}