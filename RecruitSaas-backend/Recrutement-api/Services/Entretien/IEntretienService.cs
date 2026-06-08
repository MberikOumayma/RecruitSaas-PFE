using System.Text.Json;
using Recrutement_api.DTOs.Entretien;
namespace Recrutement_api.Services.Entretien
{
    public interface IEntretienService
    {
        // ── Existants ─────────────────────────────────────────────────────────
        Task<object>              PlanifierAsync(Guid candidatureId, PlanifierDto dto);
        Task<List<object>>        GetAllAsync(Guid? offreId, string? statut);
        Task<object?>             GetByIdAsync(Guid id);
        Task                      AnnulerAsync(Guid id);
        Task<object?>             GetCreneauxByTokenAsync(string token);
        Task<object?>             ConfirmerCreneauAsync(string token, DateTime dateChoisie);
        Task<EntretienRejoindreResult?> RejoindreAsync(string token);
        Task<List<object>>        GetEntretiensByCandidatAsync(Guid candidatId);

        // ── Nouveaux : cycle entretien IA ─────────────────────────────────────
        Task<bool>   StartEntretienAsync(string token, List<object> questions);
        Task<bool>   SaveAnswerAsync(string token, int questionId, string reponse, float score, string feedback);
        Task<object?> CompleteEntretienAsync(string token, CompleteEntretienDto dto);
    }

    public class EntretienRejoindreResult
    {
        public bool      EstActif       { get; set; }
        public DateTime? DateScheduled  { get; set; }
        public string?   LienEntretien  { get; set; }
        public string?   NomCandidat    { get; set; }
        public string?   TitreOffre     { get; set; }
        public string?   DescriptionOffre { get; set; }
        public string?   PhotoProfilUrl { get; set; }
        public string?   QuestionsIA    { get; set; }
        public List<string> Competences { get; set; } = new();
    }

    public class CompleteEntretienDto
    {
        public List<object> Questions           { get; set; } = new();
        public string       RapportIA           { get; set; } = "";
        public float        ScoreGlobal         { get; set; }
        public int          DureeMinutes        { get; set; }
        public int          NbChangementsOnglet { get; set; }
        public bool         VerificationFacialeOk { get; set; }
        public JsonElement? AlertesSecurite     { get; set; }
    }
}