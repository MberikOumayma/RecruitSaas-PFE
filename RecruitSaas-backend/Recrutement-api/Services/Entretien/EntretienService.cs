using Microsoft.EntityFrameworkCore;
using Recrutement_api.DTOs.Entretien;
using Recrutement_api.Data;
using Recrutement_api.Models;
using System.Text.Json;

namespace Recrutement_api.Services.Entretien
{
    public class EntretienService : IEntretienService
    {
        private readonly ApplicationDbContext _db;
        private readonly ILogger<EntretienService> _logger;
        private readonly IConfiguration _config;
        private readonly Recrutement_api.Services.Shared.EmailService _emailService;

        public EntretienService(
            ApplicationDbContext db,
            ILogger<EntretienService> logger,
            IConfiguration config,
            Recrutement_api.Services.Shared.EmailService emailService)
        {
            _db           = db;
            _logger       = logger;
            _config       = config;
            _emailService = emailService;
        }

        // ── Planifier ─────────────────────────────────────────────────────────
        public async Task<object> PlanifierAsync(Guid candidatureId, PlanifierDto dto)
        {
            var candidature = await _db.Candidatures
                .Include(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Include(c => c.Offre).ThenInclude(o => o.Entreprise)
                .FirstOrDefaultAsync(c => c.Id == candidatureId)
                ?? throw new Exception("Candidature introuvable");

            var entretien = await _db.EntretiensIA
                .FirstOrDefaultAsync(e => e.CandidatureId == candidatureId);

            if (entretien == null)
            {
                entretien = new EntretienIA
                {
                    Id            = Guid.NewGuid(),
                    CandidatureId = candidatureId,
                    Statut        = "LienEnvoye",
                    CreeLe        = DateTime.UtcNow
                };
                _db.EntretiensIA.Add(entretien);
            }

            entretien.LienToken           = Convert.ToBase64String(Guid.NewGuid().ToByteArray())
                                              .Replace("+", "-").Replace("/", "_").Replace("=", "");
            entretien.CreneauxDisponibles = JsonSerializer.Serialize(
                dto.Creneaux.Select(d => d.ToUniversalTime()).ToList());
            entretien.Statut              = "LienEnvoye";
            entretien.MisAJourLe          = DateTime.UtcNow;

            await _db.SaveChangesAsync();

            var frontendUrl   = _config["Frontend:Url"] ?? "http://localhost:5173";
            var schedulingUrl = $"{frontendUrl}/schedule-interview/{entretien.LienToken}";

            try
            {
                var nomComplet = $"{candidature.Candidat.Utilisateur.Prenom} {candidature.Candidat.Utilisateur.Nom}".Trim();
                await _emailService.SendInterviewInviteAsync(
                    candidature.Candidat.Utilisateur.Email,
                    nomComplet,
                    candidature.Offre.Titre,
                    candidature.Offre.Entreprise?.Nom ?? "RecruitSaaS",
                    schedulingUrl,
                    dto.Message);
            }
            catch (Exception ex)
            {
                _logger.LogWarning("[Entretien] Email non envoyé : {Err}", ex.Message);
            }

            return new
            {
                entretien.Id, entretien.Statut, entretien.LienToken,
                SchedulingUrl = schedulingUrl,
                Creneaux      = dto.Creneaux,
                NomCandidat   = candidature.Candidat.Utilisateur.Nom,
                EmailCandidat = candidature.Candidat.Utilisateur.Email,
                TitreOffre    = candidature.Offre.Titre
            };
        }

        // ── GetAll ────────────────────────────────────────────────────────────
        public async Task<List<object>> GetAllAsync(Guid? offreId, string? statut)
        {
            var query = _db.EntretiensIA
                .Include(e => e.Candidature).ThenInclude(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Include(e => e.Candidature).ThenInclude(c => c.Offre).ThenInclude(o => o.Entreprise)
                .AsQueryable();

            if (offreId.HasValue)
                query = query.Where(e => e.Candidature.OffreId == offreId.Value);
            if (!string.IsNullOrWhiteSpace(statut))
                query = query.Where(e => e.Statut == statut);

            var list = await query.OrderByDescending(e => e.DateScheduled ?? e.CreeLe).ToListAsync();

            return list.Select(e => (object)new
            {
                e.Id, e.Statut, e.DateScheduled, e.Score, e.LienToken, e.CreeLe,
                e.RapportIA, e.QuestionsIA, e.DureeMinutes, e.VerificationFacialeOk, e.NbChangementsOnglet,
                NomCandidat   = $"{e.Candidature.Candidat.Utilisateur.Prenom} {e.Candidature.Candidat.Utilisateur.Nom}".Trim(),
                TitreOffre    = e.Candidature.Offre.Titre,
                NomEntreprise = e.Candidature.Offre.Entreprise?.Nom,
                CandidatureId = e.CandidatureId
            }).ToList();
        }

        // ── GetById ───────────────────────────────────────────────────────────
        public async Task<object?> GetByIdAsync(Guid id)
        {
            var e = await _db.EntretiensIA
                .Include(x => x.Candidature).ThenInclude(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Include(x => x.Candidature).ThenInclude(c => c.Offre)
                .FirstOrDefaultAsync(x => x.Id == id);
            if (e == null) return null;

            List<DateTime> creneaux = new();
            if (!string.IsNullOrEmpty(e.CreneauxDisponibles))
                try { creneaux = JsonSerializer.Deserialize<List<DateTime>>(e.CreneauxDisponibles) ?? new(); } catch { }

            return new
            {
                e.Id, e.Statut, e.DateScheduled, e.Score, e.Transcript, e.CreeLe,
                e.QuestionsIA, e.RapportIA, e.AlertesSecurite,
                e.DureeMinutes, e.VerificationFacialeOk, e.NbChangementsOnglet,
                CreneauxDisponibles = creneaux,
                NomCandidat   = $"{e.Candidature.Candidat.Utilisateur.Prenom} {e.Candidature.Candidat.Utilisateur.Nom}".Trim(),
                TitreOffre    = e.Candidature.Offre.Titre,
                CandidatureId = e.CandidatureId
            };
        }

        // ── Annuler ───────────────────────────────────────────────────────────
        public async Task AnnulerAsync(Guid id)
        {
            var e = await _db.EntretiensIA.FindAsync(id)
                ?? throw new Exception("Entretien introuvable");
            e.Statut = "Annule"; e.MisAJourLe = DateTime.UtcNow;
            await _db.SaveChangesAsync();
        }

        // ── GetCreneauxByTokenAsync ───────────────────────────────────────────
        public async Task<object?> GetCreneauxByTokenAsync(string token)
        {
            var e = await _db.EntretiensIA
                .Include(x => x.Candidature).ThenInclude(c => c.Offre).ThenInclude(o => o.Entreprise)
                .FirstOrDefaultAsync(x => x.LienToken == token);
            if (e == null || e.Statut == "Annule") return null;

            List<DateTime> creneaux = new();
            if (!string.IsNullOrEmpty(e.CreneauxDisponibles))
                try { creneaux = JsonSerializer.Deserialize<List<DateTime>>(e.CreneauxDisponibles) ?? new(); } catch { }

            return new
            {
                e.Id, e.Statut, e.DateScheduled,
                CreneauxDisponibles = creneaux,
                TitreOffre    = e.Candidature.Offre.Titre,
                NomEntreprise = e.Candidature.Offre.Entreprise?.Nom
            };
        }

        // ── ConfirmerCreneauAsync ─────────────────────────────────────────────
        public async Task<object?> ConfirmerCreneauAsync(string token, DateTime dateChoisie)
        {
            var e = await _db.EntretiensIA
                .Include(x => x.Candidature).ThenInclude(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Include(x => x.Candidature).ThenInclude(c => c.Offre)
                .FirstOrDefaultAsync(x => x.LienToken == token);
            if (e == null || e.Statut == "Annule") return null;

            List<DateTime> creneaux = new();
            if (!string.IsNullOrEmpty(e.CreneauxDisponibles))
                try { creneaux = JsonSerializer.Deserialize<List<DateTime>>(e.CreneauxDisponibles) ?? new(); } catch { }

            var dateUTC = dateChoisie.ToUniversalTime();
            if (!creneaux.Any(c => Math.Abs((c - dateUTC).TotalMinutes) < 1)) return null;

            e.DateScheduled = dateUTC;
            e.Statut        = "Planifie";
            e.MisAJourLe    = DateTime.UtcNow;
            await _db.SaveChangesAsync();

            var frontendUrl = _config["Frontend:Url"] ?? "http://localhost:5173";
            return new
            {
                e.Id, e.Statut, DateScheduled = dateUTC,
                EntretienUrl = $"{frontendUrl}/interview/{e.LienToken}/rejoindre",
                TitreOffre   = e.Candidature.Offre.Titre,
                NomCandidat  = e.Candidature.Candidat.Utilisateur.Nom,
                message      = $"Entretien confirmé le {dateUTC:dd/MM/yyyy à HH:mm} UTC"
            };
        }

        // ── GetEntretiensByCandidatAsync ──────────────────────────────────────
        public async Task<List<object>> GetEntretiensByCandidatAsync(Guid userId)
        {
            var list = await _db.EntretiensIA
                .Include(e => e.Candidature).ThenInclude(c => c.Offre).ThenInclude(o => o.Entreprise)
                .Include(e => e.Candidature).ThenInclude(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Where(e =>
                    e.Candidature.Candidat.Id == userId ||
                    e.Candidature.Candidat.Utilisateur.Id == userId)
                .OrderByDescending(e => e.DateScheduled ?? e.CreeLe)
                .ToListAsync();

            return list.Select(e => (object)new
            {
                e.Id, e.Statut, e.DateScheduled, e.LienToken, e.Score, e.Transcript, e.CreeLe,
                e.RapportIA,
                TitreOffre    = e.Candidature.Offre.Titre,
                NomEntreprise = e.Candidature.Offre.Entreprise?.Nom ?? "RecruitSaaS",
                CandidatureId = e.CandidatureId
            }).ToList();
        }

        // ── RejoindreAsync ────────────────────────────────────────────────────
        public async Task<EntretienRejoindreResult?> RejoindreAsync(string token)
        {
            var e = await _db.EntretiensIA
                .Include(x => x.Candidature).ThenInclude(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Include(x => x.Candidature).ThenInclude(c => c.Offre)
                .FirstOrDefaultAsync(x => x.LienToken == token);
            if (e == null || e.Statut == "Annule") return null;

            var now      = DateTime.UtcNow;
            bool estActif = e.DateScheduled.HasValue
                && now >= e.DateScheduled.Value.AddMinutes(-5)
                && now <= e.DateScheduled.Value.AddMinutes(35);

            if (estActif && e.Statut == "Planifie")
            {
                e.Statut = "EnCours"; e.LienActif = true; e.MisAJourLe = DateTime.UtcNow;
                await _db.SaveChangesAsync();
            }

            // Compétences depuis analyse CV
            var competences = new List<string>();
            try
            {
                // Cherche le DbSet AnalyseCV (nom exact selon ton ApplicationDbContext)
                var analyse = await _db.AnalysesCV
                    .AsNoTracking()
                    .FirstOrDefaultAsync(a => a.CandidatureId == e.CandidatureId);
                if (analyse != null && !string.IsNullOrEmpty(analyse.Competences))
                    competences = JsonSerializer.Deserialize<List<string>>(analyse.Competences) ?? new();
            }
            catch { /* AnalyseCV non disponible */ }

            var rawAvatar = await _db.CandidateProfiles.AsNoTracking()
                .Where(p => p.CandidatId == e.Candidature.CandidatId)
                .Select(p => p.AvatarUrl).FirstOrDefaultAsync();

            var frontendUrl = _config["Frontend:Url"] ?? "http://localhost:5173";

            return new EntretienRejoindreResult
            {
                EstActif         = estActif,
                DateScheduled    = e.DateScheduled,
                LienEntretien    = estActif ? $"{frontendUrl}/interview/{token}/rejoindre" : null,
                NomCandidat      = $"{e.Candidature.Candidat.Utilisateur.Prenom} {e.Candidature.Candidat.Utilisateur.Nom}".Trim(),
                TitreOffre       = e.Candidature.Offre.Titre,
                DescriptionOffre = e.Candidature.Offre.Description,
                PhotoProfilUrl   = ResolvePublicAssetUrl(rawAvatar),
                QuestionsIA      = e.QuestionsIA,
                Competences      = competences
            };
        }

        // ── StartEntretienAsync ───────────────────────────────────────────────
        public async Task<bool> StartEntretienAsync(string token, List<object> questions)
        {
            var e = await _db.EntretiensIA.FirstOrDefaultAsync(x => x.LienToken == token);
            if (e == null) return false;
            e.QuestionsIA = JsonSerializer.Serialize(questions);
            e.Statut      = "EnCours";
            e.MisAJourLe  = DateTime.UtcNow;
            await _db.SaveChangesAsync();
            return true;
        }

        // ── SaveAnswerAsync ───────────────────────────────────────────────────
        public async Task<bool> SaveAnswerAsync(
            string token, int questionId, string reponse, float score, string feedback)
        {
            var e = await _db.EntretiensIA.FirstOrDefaultAsync(x => x.LienToken == token);
            if (e == null) return false;

            if (!string.IsNullOrEmpty(e.QuestionsIA))
            {
                try
                {
                    var questions = JsonSerializer.Deserialize<List<JsonElement>>(e.QuestionsIA) ?? new();
                    var updated = questions.Select(q =>
                    {
                        if (q.TryGetProperty("id", out var idProp) && idProp.GetInt32() == questionId)
                        {
                            var dict = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(q.GetRawText())
                                       ?? new Dictionary<string, JsonElement>();
                            dict["reponse"]  = JsonSerializer.SerializeToElement(reponse);
                            dict["score"]    = JsonSerializer.SerializeToElement(score);
                            dict["feedback"] = JsonSerializer.SerializeToElement(feedback);
                            return dict;
                        }
                        return (object)q;
                    }).ToList();
                    e.QuestionsIA = JsonSerializer.Serialize(updated);
                }
                catch { }
            }

            e.MisAJourLe = DateTime.UtcNow;
            await _db.SaveChangesAsync();
            return true;
        }

        // ── CompleteEntretienAsync ────────────────────────────────────────────
        public async Task<object?> CompleteEntretienAsync(string token, CompleteEntretienDto dto)
        {
            var e = await _db.EntretiensIA
                .Include(x => x.Candidature).ThenInclude(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Include(x => x.Candidature).ThenInclude(c => c.Offre)
                .FirstOrDefaultAsync(x => x.LienToken == token);
            if (e == null) return null;

            var transcript = string.Join("\n\n", dto.Questions
                .Select(q => JsonSerializer.Deserialize<JsonElement>(JsonSerializer.Serialize(q)))
                .Where(q => q.TryGetProperty("reponse", out var r) && r.GetString() != null)
                .Select(q =>
                    $"Q: {(q.TryGetProperty("texte", out var t) ? t.GetString() : "")}\n" +
                    $"R: {(q.TryGetProperty("reponse", out var r) ? r.GetString() : "")}"));

            e.QuestionsIA             = JsonSerializer.Serialize(dto.Questions);
            e.RapportIA               = dto.RapportIA;
            e.Score                   = dto.ScoreGlobal;
            e.Transcript              = transcript;
            e.Statut                  = "Termine";
            e.DureeMinutes            = dto.DureeMinutes;
            e.NbChangementsOnglet     = dto.NbChangementsOnglet;
            e.VerificationFacialeOk   = dto.VerificationFacialeOk;
            e.AlertesSecurite         = dto.AlertesSecurite.HasValue
                ? dto.AlertesSecurite.Value.GetRawText()
                : "[]";
            e.MisAJourLe              = DateTime.UtcNow;

            await _db.SaveChangesAsync();

            return new
            {
                e.Id, e.Statut, e.Score,
                e.DureeMinutes, e.VerificationFacialeOk, e.NbChangementsOnglet,
                NomCandidat = $"{e.Candidature.Candidat.Utilisateur.Prenom} {e.Candidature.Candidat.Utilisateur.Nom}".Trim(),
                TitreOffre  = e.Candidature.Offre.Titre,
                message     = "Entretien terminé et rapport sauvegardé"
            };
        }

        // ── Helper ────────────────────────────────────────────────────────────
        private string? ResolvePublicAssetUrl(string? raw)
        {
            if (string.IsNullOrWhiteSpace(raw)) return null;
            raw = raw.Trim();
            if (raw.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                raw.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
                return raw;
            var origin = _config["AppSettings:PublicOrigin"]?.TrimEnd('/') ?? "http://localhost:5202";
            return raw.StartsWith('/') ? $"{origin}{raw}" : $"{origin}/{raw}";
        }
    }
}