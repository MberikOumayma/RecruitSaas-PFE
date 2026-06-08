using System;
using System.ComponentModel.DataAnnotations;

namespace Recrutement_api.Models
{
    public enum RoleUtilisateur
    {
        Admin,
        Tenant,
        Expert,
        Candidat
    }

    public class Utilisateur
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();

        [Required]
        [EmailAddress]
        public string Email { get; set; }

        
        public string? MotDePasseHash { get; set; }

        /// <summary>google | facebook | linkedin — null for email/password accounts.</summary>
        public string? AuthProvider { get; set; }

        public string? ExternalId { get; set; }

        public string? Prenom { get; set; }
        [Required]
        public string Nom { get; set; }
        
        public string? Telephone { get; set; }
        public RoleUtilisateur Role { get; set; }

        public bool EstActif { get; set; } = true;

        public DateTime CreeLe { get; set; } = DateTime.UtcNow;
       
    }
}
