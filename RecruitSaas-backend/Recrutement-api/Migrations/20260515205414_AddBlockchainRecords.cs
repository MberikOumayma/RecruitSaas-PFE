using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Recrutement_api.Migrations
{
    /// <inheritdoc />
    public partial class AddBlockchainRecords : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "BlockchainRecords",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    CandidatureId = table.Column<Guid>(type: "uuid", nullable: false),
                    TxHash = table.Column<string>(type: "text", nullable: false),
                    BlockNumber = table.Column<long>(type: "bigint", nullable: false),
                    CvHash = table.Column<string>(type: "text", nullable: false),
                    CreeLe = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_BlockchainRecords", x => x.Id);
                    table.ForeignKey(
                        name: "FK_BlockchainRecords_Candidatures_CandidatureId",
                        column: x => x.CandidatureId,
                        principalTable: "Candidatures",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_BlockchainRecords_CandidatureId",
                table: "BlockchainRecords",
                column: "CandidatureId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "BlockchainRecords");
        }
    }
}
