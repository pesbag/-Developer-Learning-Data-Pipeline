using DeveloprtLearningDataApi.Models;

namespace DeveloprtLearningDataApi.Repository;

public interface ISurvyRepository
{
    Task<IEnumerable<CleanSurveyAnswer>> GetRespondsByExpirienceLevelAsync(string experienceLevel);
    Task<IEnumerable<CleanSurveyAnswer>> GetRespondsByAITrustAsync(string AITrust);
}
