using MongoDB.Driver;
using DeveloprtLearningDataApi.Models;
using MongoDB.Driver.Linq;
namespace DeveloprtLearningDataApi.Repository;

public class SurvyRepository: ISurvyRepository
{
    private readonly IMongoCollection<CleanSurveyAnswer> _collection;
    public SurvyRepository(IMongoCollection<CleanSurveyAnswer> collection)
    {
        _collection = collection;        
    }
    public async Task<IEnumerable<CleanSurveyAnswer>> GetRespondsByExpirienceLevelAsync(string experienceLevel)
    {
        return await _collection.AsQueryable()
            .Where(e => e.ExperienceLevel == experienceLevel)
            .Take(10)
            .ToListAsync();
    }
    public async Task<IEnumerable<CleanSurveyAnswer>> GetRespondsByAITrustAsync(string AITrust)
    {
        return await _collection.AsQueryable()
            .Where(a => a.AiTrust == AITrust)
            .Take(10)
            .ToListAsync();
    }
    public async Task<IEnumerable<CleanSurveyAnswer>> GetUseDocsAsync()
    {
        return await _collection.AsQueryable()
            .Where(d => d.UsesDocumentation == true)
            .Take(10)
            .ToListAsync();
    }
    public async Task<IEnumerable<CleanSurveyAnswer>> GetUseDocsAndAIAsync()
    {
        return await _collection.AsQueryable()
            .Where(d => d.UsesDocumentation == true && d.UsesAIForLearning==true)
            .Take(10)
            .ToListAsync();
    }
}
