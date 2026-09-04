using DeveloprtLearningDataApi.Repository;
using Microsoft.AspNetCore.Mvc;
using DeveloprtLearningDataApi.Models;

namespace DeveloprtLearningDataApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SurveyAnswersController : ControllerBase
{
    private readonly ISurvyRepository _repo;
    public SurveyAnswersController(ISurvyRepository repo)
    {
        _repo = repo;
    }

    [HttpGet("ExperienceLevel/{experienceLevel}")]
    public async Task<ActionResult<IEnumerable<CleanSurveyAnswer>>> GetByExperienceLevel(string experienceLevel)
    {
        var answers = await _repo.GetRespondsByExpirienceLevelAsync(experienceLevel);
        if (!answers.Any())
        {
            return NotFound();
        }
        return Ok(answers);
    }
    [HttpGet("AITrust/{AITrust}")]
    public async Task<ActionResult<IEnumerable<CleanSurveyAnswer>>> GetByAITrustAsync(string AITrust)
    {
        var answers = await _repo.GetRespondsByAITrustAsync(AITrust);
        if (!answers.Any())
        {
            return NotFound();
        }
        return Ok(answers);
    }
    [HttpGet("UseDocumentation")]
    public async Task<ActionResult<IEnumerable<CleanSurveyAnswer>>> GetUseDocumentationAsync()
    {
        var answers = await _repo.GetUseDocsAsync();
        if (!answers.Any())
        {
            return NotFound();
        }
        return Ok(answers);
    }
    [HttpGet("Use-Documentation-Ai")]
    public async Task<ActionResult<IEnumerable<CleanSurveyAnswer>>> GetUseDocumentationAndAIAsync()
    {
        var answers = await _repo.GetUseDocsAndAIAsync();
        if (!answers.Any())
        {
            return NotFound();
        }
        return Ok(answers);
    }
    [HttpGet("Top-backend-ai-learners")]
    public async Task<ActionResult<IEnumerable<CleanSurveyAnswer>>> GetTopBackEndAILearners()
    {
        var respondents = await _repo.GetTop20BackEndAILearnersAsync();

        if (!respondents.Any())
        {
            return NotFound();
        }

        return Ok(respondents);
    }
}