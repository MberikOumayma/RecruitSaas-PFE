using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Recrutement_api.Data;
using Recrutement_api.Models;
using Recrutement_api.DTOs.Candidature;
using Recrutement_api.Services.CvExtraction;
using Recrutement_api.Services.Interfaces;
using Recrutement_api.Services.TenantServices;

namespace Recrutement_api.Services.AI
{
    public class AiOrchestratorService : IAiOrchestratorService
    {
        // Verrou par candidature pour éviter les race conditions lors de l'extraction
        private static readonly System.Collections.Concurrent.ConcurrentDictionary<Guid, SemaphoreSlim>
            _extractionLocks = new();

        private readonly ApplicationDbContext _dbContext;
        private readonly ICvExtractionService _cvExtractionService;
        private readonly CandidatureService _candidatureService;
        private readonly ICurrentUserService _currentUser;
        private readonly HttpClient _httpClient;
        private readonly ILogger<AiOrchestratorService> _logger;

        private readonly string _aiBaseUrl = "http://127.0.0.1:8000/ai";

        private static readonly JsonSerializerOptions _jsonOptions = new()
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        };

        public AiOrchestratorService(
            ApplicationDbContext dbContext,
            ICvExtractionService cvExtractionService,
            CandidatureService candidatureService,
            ICurrentUserService currentUser,
            HttpClient httpClient,
            ILogger<AiOrchestratorService> logger)
        {
            _dbContext            = dbContext;
            _cvExtractionService  = cvExtractionService;
            _candidatureService   = candidatureService;
            _currentUser          = currentUser;
            _httpClient           = httpClient;
            _logger               = logger;
        }

        private async Task<AnalyseCV> EnsureTextExtractedAsync(Guid candidatureId)
        {
            var candidature = await _dbContext.Candidatures
                .Include(c => c.Offre)
                .Include(c => c.AnalyseCV)
                .FirstOrDefaultAsync(c => c.Id == candidatureId);

            if (candidature == null)
                throw new Exception("Candidature introuvable");

            // Texte déjà extrait et utilisable → retourne directement
            if (candidature.AnalyseCV != null && HasUsableText(candidature.AnalyseCV))
                return candidature.AnalyseCV;

            var semaphore = _extractionLocks.GetOrAdd(candidatureId, _ => new SemaphoreSlim(1, 1));
            await semaphore.WaitAsync();
            try
            {
                // Re-vérifie après acquisition du verrou (double-check)
                _dbContext.ChangeTracker.Clear();
                var fresh = await _dbContext.Candidatures
                    .Include(c => c.AnalyseCV)
                    .FirstOrDefaultAsync(c => c.Id == candidatureId);

                if (fresh?.AnalyseCV != null && HasUsableText(fresh.AnalyseCV))
                    return fresh.AnalyseCV;

                _logger.LogInformation($"Texte absent pour {candidatureId}. Extraction en cours...");
                return await _cvExtractionService.ProcessCvAsync(candidatureId);
            }
            finally
            {
                semaphore.Release();
                _extractionLocks.TryRemove(candidatureId, out _);
            }
        }

        /// <summary>
        /// Retourne true si le texte est utilisable par l'IA (longueur suffisante).
        /// </summary>
        private static bool HasUsableText(AnalyseCV analyse)
            => !string.IsNullOrWhiteSpace(analyse.TexteExtrait)
               && analyse.TexteExtrait.Trim().Length >= 20;

        /// <summary>
        /// Same candidate + same CV file → keep skills/experiences identical across applications.
        /// </summary>
        private async Task SyncExtractedFieldsToSameCvAsync(
            Guid candidatureId,
            string? competencesJson,
            string? experienceJson = null)
        {
            if (string.IsNullOrEmpty(competencesJson) && string.IsNullOrEmpty(experienceJson))
                return;

            var current = await _dbContext.Candidatures
                .AsNoTracking()
                .FirstOrDefaultAsync(c => c.Id == candidatureId);
            if (current == null || string.IsNullOrWhiteSpace(current.CvUrl))
                return;

            var siblings = await _dbContext.Candidatures
                .Include(c => c.AnalyseCV)
                .Where(c =>
                    c.CandidatId == current.CandidatId
                    && c.CvUrl == current.CvUrl
                    && c.Id != candidatureId
                    && c.AnalyseCV != null)
                .ToListAsync();

            if (siblings.Count == 0)
                return;

            foreach (var sibling in siblings)
            {
                if (!string.IsNullOrEmpty(competencesJson))
                    sibling.AnalyseCV!.Competences = competencesJson;
                if (!string.IsNullOrEmpty(experienceJson))
                    sibling.AnalyseCV!.Experience = experienceJson;
            }

            await _dbContext.SaveChangesAsync();
            _logger.LogInformation(
                "[AI] Synced extracted fields to {Count} sibling candidature(s) for CV {CvUrl}",
                siblings.Count, current.CvUrl);
        }

        /// <summary>
        /// Appelle le microservice Python.
        /// Gère 400 (texte vide) et autres erreurs sans crasher.
        /// </summary>
        private async Task<T?> PostToAiAsync<T>(string endpoint, object payload)
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload, _jsonOptions),
                Encoding.UTF8,
                "application/json");

            HttpResponseMessage response;
            try
            {
                response = await _httpClient.PostAsync($"{_aiBaseUrl}/{endpoint}", content);
            }
            catch (Exception ex)
            {
                _logger.LogError($"[AI] Impossible de joindre {endpoint} : {ex.Message}");
                return default;
            }

            if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
            {
                var detail = await response.Content.ReadAsStringAsync();
                _logger.LogWarning($"[AI] {endpoint} → 400 (PDF vide/scanné) : {detail}");
                return default;
            }

            if (!response.IsSuccessStatusCode)
            {
                var detail = await response.Content.ReadAsStringAsync();
                _logger.LogError($"[AI] {endpoint} → {(int)response.StatusCode} : {detail}");
                return default;
            }

            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<T>(json, _jsonOptions);
        }

        // ── Score ──────────────────────────────────────────────────────────────
        public async Task<object> CalculateScoreAsync(Guid candidatureId)
        {
            var analyse = await EnsureTextExtractedAsync(candidatureId);
            var jsonOpts = _jsonOptions;

            var skills = ParseSkills(analyse.Competences, jsonOpts);
            var experiences = ParseExperiences(analyse.Experience, jsonOpts);

            var offre = (await _dbContext.Candidatures
                .Include(c => c.Offre)
                .FirstOrDefaultAsync(c => c.Id == candidatureId))?.Offre;

            var payload = new
            {
                texteExtrait = analyse.TexteExtrait,
                titreOffre = offre?.Titre,
                description = offre?.Description,
                typeContrat = offre?.TypeContrat.ToString(),
                skills,
                experiences,
                candidatureId = candidatureId.ToString(),
                offreId = offre?.Id.ToString(),
            };
            var aiResult = await PostToAiAsync<AiScoreResponse>("score", payload);

            analyse.Score = (float)Math.Round(aiResult?.Score ?? 0);
            _dbContext.AnalysesCV.Update(analyse);
            await _dbContext.SaveChangesAsync();

            var (statut, autoDeclined) = await _candidatureService.ApplyAutoDeclineIfNeededAsync(
                candidatureId, analyse.Score ?? 0f);

            return new
            {
                score      = analyse.Score,
                domainFit  = aiResult?.DomainFit,
                technical  = aiResult?.Technical,
                experience = aiResult?.Experience,
                statut,
                autoDeclined,
            };
        }

        // ── Classement FAISS (toutes les candidatures d'une offre) ───────────────
        public async Task<object> RankCandidaturesForOffreAsync(Guid offreId)
        {
            var tenantId = _currentUser.TenantId;
            if (!tenantId.HasValue)
                throw new UnauthorizedAccessException("Tenant requis pour le classement.");

            var offre = await _dbContext.OffresEmploi
                .Include(o => o.Entreprise)
                .FirstOrDefaultAsync(o => o.Id == offreId);

            if (offre == null || offre.Entreprise.TenantId != tenantId)
                throw new KeyNotFoundException("Offre introuvable.");

            var candidatures = await _dbContext.Candidatures
                .Include(c => c.AnalyseCV)
                .Include(c => c.Candidat).ThenInclude(ca => ca.Utilisateur)
                .Include(c => c.Offre).ThenInclude(o => o.Entreprise)
                .Where(c => c.OffreId == offreId && c.Offre.Entreprise.TenantId == tenantId)
                .ToListAsync();

            if (candidatures.Count == 0)
                return new { offreId, ranked = Array.Empty<RankedCandidatureResponseDto>() };

            var candidatIds = candidatures.Select(c => c.CandidatId).Distinct().ToList();
            var avatarByCandidat = await _dbContext.CandidateProfiles.AsNoTracking()
                .Where(p => candidatIds.Contains(p.CandidatId))
                .ToDictionaryAsync(p => p.CandidatId, p => p.AvatarUrl);

            var candidatesPayload = candidatures.Select(c =>
            {
                var analyse = c.AnalyseCV;
                return new
                {
                    id = c.Id.ToString(),
                    skills = ParseSkills(analyse?.Competences, _jsonOptions),
                    experiences = ParseExperiences(analyse?.Experience, _jsonOptions),
                    texteExtrait = analyse?.TexteExtrait ?? "",
                };
            }).ToList();

            var payload = new
            {
                titreOffre = offre.Titre,
                description = offre.Description,
                typeContrat = offre.TypeContrat.ToString(),
                offreId = offreId.ToString(),
                candidates = candidatesPayload,
            };

            var aiResult = await PostToAiAsync<AiRankResponse>("rank-candidates", payload);
            if (aiResult?.Ranked == null || aiResult.Ranked.Count == 0)
                throw new Exception("Le service IA n'a pas pu classer les candidatures.");

            var byId = candidatures.ToDictionary(c => c.Id.ToString());

            var ranked = new List<RankedCandidatureResponseDto>();
            foreach (var item in aiResult.Ranked.OrderBy(r => r.Rank))
            {
                if (!byId.TryGetValue(item.Id, out var c))
                    continue;

                var u = c.Candidat?.Utilisateur;
                var nom = u == null
                    ? "Candidat"
                    : $"{u.Prenom} {u.Nom}".Trim();
                avatarByCandidat.TryGetValue(c.CandidatId, out var avatarUrl);

                ranked.Add(new RankedCandidatureResponseDto
                {
                    Id = c.Id,
                    NomCandidat = string.IsNullOrWhiteSpace(nom) ? u?.Email ?? "Candidat" : nom,
                    EmailCandidat = u?.Email ?? "",
                    AvatarUrl = avatarUrl,
                    OffreId = c.OffreId,
                    TitreOffre = c.Offre?.Titre ?? offre.Titre,
                    EntrepriseId = c.Offre?.EntrepriseId ?? offre.EntrepriseId,
                    NomEntreprise = c.Offre?.Entreprise?.Nom ?? offre.Entreprise?.Nom ?? "",
                    Statut = c.Statut,
                    CreeLe = c.CreeLe,
                    CvUrl = c.CvUrl,
                    ScoreIA = c.AnalyseCV?.Score ?? item.Score,
                    Rank = item.Rank,
                    FaissScore = item.Score,
                    VectorSimilarity = item.VectorSimilarity,
                    DomainFit = item.DomainFit,
                    Technical = item.Technical,
                    Experience = item.Experience,
                });
            }

            var rankedIds = new HashSet<string>(aiResult.Ranked.Select(r => r.Id));
            foreach (var c in candidatures)
            {
                var id = c.Id.ToString();
                if (rankedIds.Contains(id))
                    continue;

                var u = c.Candidat?.Utilisateur;
                var nom = u == null ? "Candidat" : $"{u.Prenom} {u.Nom}".Trim();
                avatarByCandidat.TryGetValue(c.CandidatId, out var avatarUrl);
                ranked.Add(new RankedCandidatureResponseDto
                {
                    Id = c.Id,
                    NomCandidat = string.IsNullOrWhiteSpace(nom) ? u?.Email ?? "Candidat" : nom,
                    EmailCandidat = u?.Email ?? "",
                    AvatarUrl = avatarUrl,
                    OffreId = c.OffreId,
                    TitreOffre = c.Offre?.Titre ?? offre.Titre,
                    EntrepriseId = c.Offre?.EntrepriseId ?? offre.EntrepriseId,
                    NomEntreprise = c.Offre?.Entreprise?.Nom ?? offre.Entreprise?.Nom ?? "",
                    Statut = c.Statut,
                    CreeLe = c.CreeLe,
                    CvUrl = c.CvUrl,
                    ScoreIA = c.AnalyseCV?.Score,
                    Rank = ranked.Count + 1,
                    FaissScore = c.AnalyseCV?.Score ?? 0,
                });
            }

            return new { offreId, ranked };
        }

        // ── Score en lecture seule ─────────────────────────────────────────────
        public async Task<object> GetScoreAsync(Guid candidatureId)
        {
            var analyse = await _dbContext.AnalysesCV
                .FirstOrDefaultAsync(a => a.CandidatureId == candidatureId);

            if (analyse?.Score != null)
                return new { score = analyse.Score };

            return await CalculateScoreAsync(candidatureId);
        }

        // ── Classification ─────────────────────────────────────────────────────
        public async Task<object> ClassifyCandidateAsync(Guid candidatureId)
        {
            var analyse = await EnsureTextExtractedAsync(candidatureId);

            if (!HasUsableText(analyse))
            {
                _logger.LogWarning($"[AI] Classify : texte vide pour {candidatureId}");
                return new { classification = "Not Qualified", warning = "CV illisible — texte non extrait (image/PDF ou OCR)" };
            }

            var offre = (await _dbContext.Candidatures
                .Include(c => c.Offre)
                .FirstOrDefaultAsync(c => c.Id == candidatureId))?.Offre;

            var payload  = new { texteExtrait = analyse.TexteExtrait, titreOffre = offre?.Titre, description = offre?.Description, typeContrat = offre?.TypeContrat.ToString() };
            var aiResult = await PostToAiAsync<AiClassifyResponse>("classify", payload);

            analyse.Classification = aiResult?.Classification ?? "Not Qualified";
            _dbContext.AnalysesCV.Update(analyse);
            await _dbContext.SaveChangesAsync();

            return new { classification = analyse.Classification };
        }

        // ── Résumé ─────────────────────────────────────────────────────────────
        public async Task<object> SummarizeCvAsync(Guid candidatureId)
        {
            var analyse = await EnsureTextExtractedAsync(candidatureId);

            if (!HasUsableText(analyse))
                return new { summary = "", warning = "CV illisible — texte non extrait (image/PDF ou OCR)" };

            var jsonOpts = _jsonOptions;

            // Utiliser skills/experiences extraites ; les générer si absentes
            var skills = ParseSkills(analyse.Competences, jsonOpts);
            if (skills.Count == 0)
            {
                var aiSkills = await PostToAiAsync<AiSkillsResponse>(
                    "extract-skills", new { texteExtrait = analyse.TexteExtrait });
                skills = aiSkills?.Skills?.ToList() ?? new List<string>();
                analyse.Competences = JsonSerializer.Serialize(skills, jsonOpts);
            }

            var experiences = ParseExperiences(analyse.Experience, jsonOpts);
            if (experiences.Count == 0)
            {
                var aiExp = await PostToAiAsync<AiExperienceResponse>(
                    "extract-experience", new { texteExtrait = analyse.TexteExtrait });
                experiences = aiExp?.Experiences?.ToList() ?? new List<ExperienceItem>();
                analyse.Experience = JsonSerializer.Serialize(experiences, jsonOpts);
            }

            var competencesJson = JsonSerializer.Serialize(skills, jsonOpts);
            await SyncExtractedFieldsToSameCvAsync(
                candidatureId,
                competencesJson,
                analyse.Experience);

            var offre = (await _dbContext.Candidatures
                .Include(c => c.Offre)
                .FirstOrDefaultAsync(c => c.Id == candidatureId))?.Offre;

            var payload = new SummarizePayload
            {
                TexteExtrait = analyse.TexteExtrait,
                TitreOffre   = offre?.Titre,
                Description  = offre?.Description,
                TypeContrat  = offre?.TypeContrat.ToString(),
                Skills       = skills,
                Experiences  = experiences,
            };

            if (skills.Count == 0 && experiences.Count == 0)
                return new { summary = "", warning = "Aucune compétence ni expérience extraite du CV.", skills, experiences };

            var aiResult = await PostToAiAsync<AiSummaryResponse>("summarize", payload);

            analyse.Resume = aiResult?.Summary ?? "";
            _dbContext.AnalysesCV.Update(analyse);
            await _dbContext.SaveChangesAsync();

            return new { summary = analyse.Resume, skills, experiences };
        }

        private static List<string> ParseSkills(string? json, JsonSerializerOptions opts)
        {
            if (string.IsNullOrWhiteSpace(json)) return new List<string>();
            try
            {
                return JsonSerializer.Deserialize<List<string>>(json, opts) ?? new List<string>();
            }
            catch { return new List<string>(); }
        }

        private static List<ExperienceItem> ParseExperiences(string? json, JsonSerializerOptions opts)
        {
            if (string.IsNullOrWhiteSpace(json)) return new List<ExperienceItem>();
            try
            {
                return JsonSerializer.Deserialize<List<ExperienceItem>>(json, opts) ?? new List<ExperienceItem>();
            }
            catch { return new List<ExperienceItem>(); }
        }

        // ── Compétences ────────────────────────────────────────────────────────
        public async Task<object> ExtractCompetencesAsync(Guid candidatureId)
        {
            var analyse = await EnsureTextExtractedAsync(candidatureId);

            var offre = (await _dbContext.Candidatures
                .Include(c => c.Offre)
                .FirstOrDefaultAsync(c => c.Id == candidatureId))?.Offre;

            var payload = new
            {
                texteExtrait = analyse.TexteExtrait,
                titreOffre   = offre?.Titre,
                description  = offre?.Description
            };

            if (!HasUsableText(analyse))
                return new { skills = Array.Empty<string>(), warning = "CV illisible — texte non extrait. Réessayez après redémarrage du backend ; pour une image, vérifiez Tesseract (TESSERACT_CMD)." };

            var aiResult = await PostToAiAsync<AiSkillsResponse>("extract-skills", new { texteExtrait = analyse.TexteExtrait });

            if (aiResult == null)
                return new { skills = Array.Empty<string>(), warning = "Service IA indisponible ou erreur d'extraction (vérifiez recruit-ai-service sur le port 8000)." };

            var skills = aiResult.Skills ?? Array.Empty<string>();
            var competencesJson = JsonSerializer.Serialize(skills, _jsonOptions);
            analyse.Competences = competencesJson;
            _dbContext.AnalysesCV.Update(analyse);
            await _dbContext.SaveChangesAsync();
            await SyncExtractedFieldsToSameCvAsync(candidatureId, competencesJson);

            if (skills.Length == 0)
                return new { skills, warning = "Aucune compétence détectée dans le CV." };

            return new { skills };
        }

        // ── Expérience ─────────────────────────────────────────────────────────
        public async Task<object> ExtractExperienceAsync(Guid candidatureId)
        {
            var analyse = await EnsureTextExtractedAsync(candidatureId);

            if (!HasUsableText(analyse))
                return new { experiences = Array.Empty<object>(), warning = "CV illisible — texte non extrait. Réessayez après redémarrage du backend ; pour une image, vérifiez Tesseract (TESSERACT_CMD)." };

            var aiResult = await PostToAiAsync<AiExperienceResponse>("extract-experience", new { texteExtrait = analyse.TexteExtrait });

            if (aiResult == null)
                return new { experiences = Array.Empty<object>(), warning = "Service IA indisponible ou erreur d'extraction (vérifiez recruit-ai-service sur le port 8000)." };

            var experiences = aiResult.Experiences ?? Array.Empty<ExperienceItem>();
            var experienceJson = JsonSerializer.Serialize(experiences, _jsonOptions);
            analyse.Experience = experienceJson;
            _dbContext.AnalysesCV.Update(analyse);
            await _dbContext.SaveChangesAsync();
            await SyncExtractedFieldsToSameCvAsync(candidatureId, null, experienceJson);

            if (!experiences.Any())
                return new { experiences, warning = "Aucune expérience détectée dans le CV." };

            return new { experiences };
        }

        // ── Entreprises ────────────────────────────────────────────────────────
        public async Task<object> ExtractCompaniesAsync(Guid candidatureId)
        {
            var analyse = await EnsureTextExtractedAsync(candidatureId);

            if (!HasUsableText(analyse))
                return new { companies = Array.Empty<object>(), warning = "PDF illisible ou scanné" };

            var aiResult = await PostToAiAsync<AiCompaniesResponse>("extract-companies", new { texteExtrait = analyse.TexteExtrait });

            return new { companies = aiResult?.Companies ?? Array.Empty<object>() };
        }

        // ── Certifications ─────────────────────────────────────────────────────
        public async Task<object> ExtractCertificationsAsync(Guid candidatureId)
        {
            var analyse = await EnsureTextExtractedAsync(candidatureId);

            if (!HasUsableText(analyse))
                return new { certifications = Array.Empty<object>(), warning = "PDF illisible ou scanné" };

            var aiResult = await PostToAiAsync<AiCertificationsResponse>("extract-certifications", new { texteExtrait = analyse.TexteExtrait });

            var certifications = aiResult?.Certifications ?? Array.Empty<object>();
            analyse.Certifications = JsonSerializer.Serialize(certifications, _jsonOptions);
            _dbContext.AnalysesCV.Update(analyse);
            await _dbContext.SaveChangesAsync();

            return new { certifications };
        }

        // ── Génération de Quiz ─────────────────────────────────────────────────
        public async Task<object> GenerateQuizAsync(Guid offreId, int numQuestions = 10, int timePerQuestion = 60)
        {
            var offre = await _dbContext.OffresEmploi.FindAsync(offreId);
            if (offre == null)
                throw new Exception("Offre introuvable");

            var payload = new
            {
                titreOffre        = offre.Titre,
                description       = offre.Description,
                num_questions     = Math.Max(3, Math.Min(numQuestions, 20)),
                time_per_question = Math.Max(15, Math.Min(timePerQuestion, 300))
            };

            var aiResult = await PostToAiAsync<AiQuizResponse>("generate-quiz", payload);
            return aiResult ?? new AiQuizResponse();
        }

        // ── DTOs ───────────────────────────────────────────────────────────────
        private class AiQuizQuestion
        {
            [JsonPropertyName("id")]
            public int Id { get; set; }

            [JsonPropertyName("question")]
            public string Question { get; set; } = "";

            [JsonPropertyName("choices")]
            public string[] Choices { get; set; } = Array.Empty<string>();

            [JsonPropertyName("correct_index")]
            public int CorrectIndex { get; set; }
        }

        private class AiQuizResponse
        {
            [JsonPropertyName("questions")]
            public AiQuizQuestion[] Questions { get; set; } = Array.Empty<AiQuizQuestion>();
        }

        private class AiScoreResponse
        {
            public float Score { get; set; }

            [JsonPropertyName("domain_fit")]
            public float? DomainFit { get; set; }

            [JsonPropertyName("technical")]
            public float? Technical { get; set; }

            [JsonPropertyName("experience")]
            public float? Experience { get; set; }
        }

        private class AiRankResponse
        {
            public List<AiRankItem> Ranked { get; set; } = new();
        }

        private class AiRankItem
        {
            public string Id { get; set; } = "";

            public int Rank { get; set; }

            public float Score { get; set; }

            [JsonPropertyName("vector_similarity")]
            public float? VectorSimilarity { get; set; }

            [JsonPropertyName("domain_fit")]
            public float? DomainFit { get; set; }

            [JsonPropertyName("technical")]
            public float? Technical { get; set; }

            [JsonPropertyName("experience")]
            public float? Experience { get; set; }
        }

        private class AiClassifyResponse      { public string Classification { get; set; } = ""; }
        private class AiSummaryResponse        { public string Summary        { get; set; } = ""; }
        private class AiSkillsResponse         { public string[] Skills       { get; set; } = Array.Empty<string>(); }
        private class AiExperienceResponse     { public ExperienceItem[] Experiences  { get; set; } = Array.Empty<ExperienceItem>(); }
        private class AiCompaniesResponse      { public object[] Companies    { get; set; } = Array.Empty<object>(); }
        private class AiCertificationsResponse { public object[] Certifications { get; set; } = Array.Empty<object>(); }

        private class SummarizePayload
        {
            public string TexteExtrait { get; set; } = "";
            public string? TitreOffre { get; set; }
            public string? Description { get; set; }
            public string? TypeContrat { get; set; }
            public List<string> Skills { get; set; } = new();
            public List<ExperienceItem> Experiences { get; set; } = new();
        }

        private class ExperienceItem
        {
            public string Role { get; set; } = "";
            public string Entreprise { get; set; } = "";
            public string Years { get; set; } = "";
            public string Summary { get; set; } = "";
        }
    }
}