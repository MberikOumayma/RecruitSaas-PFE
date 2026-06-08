using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Recrutement_api.Migrations
{
    public partial class AddExternalAuthToUtilisateur : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterColumn<string>(
                name: "MotDePasseHash",
                table: "Utilisateurs",
                type: "text",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "text");

            migrationBuilder.AddColumn<string>(
                name: "AuthProvider",
                table: "Utilisateurs",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ExternalId",
                table: "Utilisateurs",
                type: "text",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Utilisateurs_AuthProvider_ExternalId",
                table: "Utilisateurs",
                columns: new[] { "AuthProvider", "ExternalId" },
                unique: true,
                filter: "\"AuthProvider\" IS NOT NULL AND \"ExternalId\" IS NOT NULL");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Utilisateurs_AuthProvider_ExternalId",
                table: "Utilisateurs");

            migrationBuilder.DropColumn(
                name: "AuthProvider",
                table: "Utilisateurs");

            migrationBuilder.DropColumn(
                name: "ExternalId",
                table: "Utilisateurs");

            migrationBuilder.AlterColumn<string>(
                name: "MotDePasseHash",
                table: "Utilisateurs",
                type: "text",
                nullable: false,
                defaultValue: "",
                oldClrType: typeof(string),
                oldType: "text",
                oldNullable: true);
        }
    }
}
