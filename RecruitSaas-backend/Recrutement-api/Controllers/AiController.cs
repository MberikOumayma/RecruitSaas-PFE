using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Recrutement_api.Services.AI;

namespace Recrutement_api.Controllers
{
    [ApiController]
    [Route("api/ai")]
    [Authorize]
    public class AiController : ControllerBase
    {
        private readonly IAiOrchestratorService _ai;

        public AiController(IAiOrchestratorService ai)
        {
            _ai = ai;
        }

        // ── Score ──────────────────────────────────────────────────────────────
        [HttpGet("{candidatureId}/score")]
        [HttpPost("{candidatureId}/score/recalculate")]
        public async Task<IActionResult> GetScore(Guid candidatureId)
        {
            var result = await _ai.CalculateScoreAsync(candidatureId);
            return Ok(result);
        }

        // ── Classification ─────────────────────────────────────────────────────
        [HttpPost("{candidatureId}/classify")]
        public async Task<IActionResult> Classify(Guid candidatureId)
        {
            var result = await _ai.ClassifyCandidateAsync(candidatureId);
            return Ok(result);
        }

        // ── Résumé ─────────────────────────────────────────────────────────────
        [HttpGet("{candidatureId}/summary")]
        public async Task<IActionResult> GetSummary(Guid candidatureId)
        {
            var result = await _ai.SummarizeCvAsync(candidatureId);
            return Ok(result);
        }

        // ── Compétences ────────────────────────────────────────────────────────
        [HttpGet("{candidatureId}/skills")]
        public async Task<IActionResult> GetSkills(Guid candidatureId)
        {
            var result = await _ai.ExtractCompetencesAsync(candidatureId);
            return Ok(result);
        }

        // ── Expérience ─────────────────────────────────────────────────────────
        [HttpGet("{candidatureId}/experience")]
        public async Task<IActionResult> GetExperience(Guid candidatureId)
        {
            var result = await _ai.ExtractExperienceAsync(candidatureId);
            return Ok(result);
        }

        // ── Certifications ─────────────────────────────────────────────────────
        [HttpGet("{candidatureId}/certifications")]
        public async Task<IActionResult> GetCertifications(Guid candidatureId)
        {
            var result = await _ai.ExtractCertificationsAsync(candidatureId);
            return Ok(result);
        }

        // ── Entreprises citées dans le CV ──────────────────────────────────────
        [HttpGet("{candidatureId}/companies")]
        public async Task<IActionResult> GetCompanies(Guid candidatureId)
        {
            var result = await _ai.ExtractCompaniesAsync(candidatureId);
            return Ok(result);
        }
    }
}