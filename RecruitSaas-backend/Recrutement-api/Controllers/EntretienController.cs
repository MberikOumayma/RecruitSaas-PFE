using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using Recrutement_api.DTOs.Entretien;
using Recrutement_api.Services.Entretien;

namespace Recrutement_api.Controllers
{
    [ApiController]
    [Route("api/entretiens")]
    public class EntretienController : ControllerBase
    {
        private readonly IEntretienService _service;
        public EntretienController(IEntretienService service) => _service = service;

        // ── TENANT/EXPERT : planifier ─────────────────────────────────────────
        [HttpPost("{candidatureId}/planifier")]
        [Authorize]
        public async Task<IActionResult> Planifier(Guid candidatureId, [FromBody] PlanifierDto dto)
        {
            var result = await _service.PlanifierAsync(candidatureId, dto);
            return Ok(result);
        }

        // ── TENANT/EXPERT : liste ─────────────────────────────────────────────
        [HttpGet]
        [Authorize]
        public async Task<IActionResult> GetAll(
            [FromQuery] Guid? offreId, [FromQuery] string? statut)
        {
            var result = await _service.GetAllAsync(offreId, statut);
            return Ok(result);
        }

        // ── TENANT/EXPERT : détail ────────────────────────────────────────────
        [HttpGet("{id}")]
        [Authorize]
        public async Task<IActionResult> GetById(Guid id)
        {
            var result = await _service.GetByIdAsync(id);
            if (result == null) return NotFound();
            return Ok(result);
        }

        // ── TENANT/EXPERT : annuler ───────────────────────────────────────────
        [HttpPost("{id}/annuler")]
        [Authorize]
        public async Task<IActionResult> Annuler(Guid id)
        {
            await _service.AnnulerAsync(id);
            return Ok(new { message = "Entretien annulé" });
        }

        // ── CANDIDAT : ses entretiens ─────────────────────────────────────────
        [HttpGet("mes-entretiens")]
        [Authorize]
        public async Task<IActionResult> GetMesEntretiens()
        {
            var idStr = User.FindFirstValue("candidatId")
                     ?? User.FindFirstValue("userId")
                     ?? User.FindFirstValue(ClaimTypes.NameIdentifier);

            if (string.IsNullOrEmpty(idStr) || !Guid.TryParse(idStr, out var id))
                return Unauthorized(new { message = "Token invalide" });

            var result = await _service.GetEntretiensByCandidatAsync(id);
            return Ok(result);
        }

        // ── PUBLIC : créneaux disponibles ─────────────────────────────────────
        [HttpGet("public/{token}/creneaux")]
        [AllowAnonymous]
        public async Task<IActionResult> GetCreneaux(string token)
        {
            var result = await _service.GetCreneauxByTokenAsync(token);
            if (result == null) return NotFound(new { message = "Lien invalide ou expiré" });
            return Ok(result);
        }

        // ── PUBLIC : confirmer créneau ────────────────────────────────────────
        [HttpPost("public/{token}/confirmer")]
        [AllowAnonymous]
        public async Task<IActionResult> ConfirmerCreneau(
            string token, [FromBody] ConfirmerCreneauDto dto)
        {
            var result = await _service.ConfirmerCreneauAsync(token, dto.DateChoisie);
            if (result == null) return BadRequest(new { message = "Créneau invalide ou lien expiré" });
            return Ok(result);
        }

        // ── PUBLIC : rejoindre ────────────────────────────────────────────────
        [HttpGet("public/{token}/rejoindre")]
        [AllowAnonymous]
        public async Task<IActionResult> Rejoindre(string token)
        {
            var result = await _service.RejoindreAsync(token);
            if (result == null) return NotFound(new { message = "Lien invalide ou expiré" });
            return Ok(result);
        }

        // ── PUBLIC : démarrer l'entretien IA ─────────────────────────────────
        [HttpPost("public/{token}/start")]
        [AllowAnonymous]
        public async Task<IActionResult> Start(string token, [FromBody] StartDto dto)
        {
            var ok = await _service.StartEntretienAsync(token, dto.Questions);
            if (!ok) return BadRequest(new { message = "Impossible de démarrer" });
            return Ok(new { message = "Entretien démarré" });
        }

        // ── PUBLIC : sauvegarder une réponse ─────────────────────────────────
        [HttpPost("public/{token}/save-answer")]
        [AllowAnonymous]
        public async Task<IActionResult> SaveAnswer(string token, [FromBody] SaveAnswerDto dto)
        {
            var ok = await _service.SaveAnswerAsync(
                token, dto.QuestionId, dto.Reponse, dto.Score, dto.Feedback);
            if (!ok) return BadRequest(new { message = "Impossible de sauvegarder" });
            return Ok(new { message = "Réponse sauvegardée" });
        }

        // ── PUBLIC : terminer + rapport ───────────────────────────────────────
        [HttpPost("public/{token}/complete")]
        [AllowAnonymous]
        public async Task<IActionResult> Complete(string token, [FromBody] CompleteEntretienDto dto)
        {
            var result = await _service.CompleteEntretienAsync(token, dto);
            if (result == null) return BadRequest(new { message = "Impossible de terminer" });
            return Ok(result);
        }
    }
}