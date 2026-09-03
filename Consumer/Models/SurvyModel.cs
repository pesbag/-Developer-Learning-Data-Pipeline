namespace Consumer.Models;

using MongoDB.Bson.Serialization.Attributes;
using System.Text.Json.Serialization;

public class DeveloperSurveyResponse
{
    [BsonId]
    [BsonElement("responseId")]
    [JsonPropertyName("responseId")]
    public int ResponseId { get; set; }

    [BsonElement("age")]
    [JsonPropertyName("age")]
    public string? Age { get; set; }

    [BsonElement("aiLearningMethods")]
    [JsonPropertyName("aiLearningMethods")]
    public List<string>? AiLearningMethods { get; set; }

    [BsonElement("aiSentiment")]
    [JsonPropertyName("aiSentiment")]
    public string? AiSentiment { get; set; }

    [BsonElement("aiTrust")]
    [JsonPropertyName("aiTrust")]
    public string? AiTrust { get; set; }

    [BsonElement("aiUsage")]
    [JsonPropertyName("aiUsage")]
    public string? AiUsage { get; set; }

    [BsonElement("devType")]
    [JsonPropertyName("devType")]
    public string? DevType { get; set; }

    [BsonElement("experienceLevel")]
    [JsonPropertyName("experienceLevel")]
    public string? ExperienceLevel { get; set; }

    [BsonElement("learnCodeAI")]
    [JsonPropertyName("learnCodeAI")]
    public string? LearnCodeAI { get; set; }

    [BsonElement("learnCodeChoose")]
    [JsonPropertyName("learnCodeChoose")]
    public string? LearnCodeChoose { get; set; }

    [BsonElement("learningMethods")]
    [JsonPropertyName("learningMethods")]
    public List<string>? LearningMethods { get; set; }

    [BsonElement("usesAIForLearning")]
    [JsonPropertyName("usesAIForLearning")]
    public bool UsesAIForLearning { get; set; }

    [BsonElement("usesDocumentation")]
    [JsonPropertyName("usesDocumentation")]
    public bool UsesDocumentation { get; set; }

    [BsonElement("usesStackOverflow")]
    [JsonPropertyName("usesStackOverflow")]
    public bool UsesStackOverflow { get; set; }

    [BsonElement("yearsCode")]
    [JsonPropertyName("yearsCode")]
    public int YearsCode { get; set; }
}