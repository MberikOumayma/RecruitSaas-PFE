using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Recrutement_api.Migrations
{
    /// <inheritdoc />
    public partial class AddTelephoneToUtilisateur : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Colonne incluse dans InitialCreate (ordre des migrations corrigé pour Docker)
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
        }
    }
}
