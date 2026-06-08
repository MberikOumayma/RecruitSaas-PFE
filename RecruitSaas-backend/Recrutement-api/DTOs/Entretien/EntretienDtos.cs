namespace Recrutement_api.DTOs.Entretien
{
    // ── Existants ─────────────────────────────────────────────────────────────
    public class PlanifierDto
    {
        public List<DateTime> Creneaux { get; set; } = new();
        public string?        Message  { get; set; }
    }

    public class ConfirmerCreneauDto
    {
        public DateTime DateChoisie { get; set; }
    }

    // ── Nouveaux ──────────────────────────────────────────────────────────────
    public class StartDto
    {
        public List<object> Questions { get; set; } = new();
    }

    public class SaveAnswerDto
    {
        public int    QuestionId { get; set; }
        public string Reponse    { get; set; } = "";
        public float  Score      { get; set; }
        public string Feedback   { get; set; } = "";
    }
}