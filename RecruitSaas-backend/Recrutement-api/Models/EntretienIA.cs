using System.ComponentModel.DataAnnotations;
namespace Recrutement_api.Models
{
    public class EntretienIA
    {
        [Key]
        public Guid Id { get; set; }
        public Guid CandidatureId { get; set; }
        public Candidature Candidature { get; set; }

        // Créneaux proposés par le tenant/expert (JSON array de DateTime)
        public string? CreneauxDisponibles { get; set; }

        // Créneau choisi par le candidat
        public DateTime? DateScheduled { get; set; }

        // Lien unique envoyé au candidat (token sécurisé)
        public string? LienToken { get; set; }

        // Lien devient actif uniquement à DateScheduled
        public bool LienActif { get; set; } = false;

        // Qui a planifié (tenant ou expert)
        public Guid? PlanifiePar { get; set; }

        // Transcript de la conversation (texte brut)
        public string Transcript { get; set; } = string.Empty;

        // Score global IA (0-100)
        public float? Score { get; set; }

        // Statuts : EnAttente | LienEnvoye | Planifie | EnCours | Termine | Annule
        public string Statut { get; set; } = "EnAttente";

        // ── Nouveaux champs entretien IA ──────────────────────────────────────

        // Questions générées par l'IA (JSON array)
        public string? QuestionsIA { get; set; }

        // Rapport final généré par l'IA (JSON object)
        public string? RapportIA { get; set; }

        // Durée réelle de l'entretien en minutes
        public int? DureeMinutes { get; set; }

        // Alertes sécurité détectées (JSON array : tab_change, face_absent, multiple_faces)
        public string? AlertesSecurite { get; set; }

        // Nombre de fois que le candidat a quitté l'onglet
        public int NbChangementsOnglet { get; set; } = 0;

        // Vérification faciale OK
        public bool VerificationFacialeOk { get; set; } = false;

        public DateTime CreeLe { get; set; } = DateTime.UtcNow;
        public DateTime? MisAJourLe { get; set; }
    }
}