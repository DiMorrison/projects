using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace WebApplicationTest.Data.Migrations
{
    public partial class second : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateIndex(
                name: "IX_Vozila_TipID",
                table: "Vozila",
                column: "TipID");

            migrationBuilder.AddForeignKey(
                name: "FK_Vozila_TipoviVozila_TipID",
                table: "Vozila",
                column: "TipID",
                principalTable: "TipoviVozila",
                principalColumn: "IdTip",
                onDelete: ReferentialAction.Cascade);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Vozila_TipoviVozila_TipID",
                table: "Vozila");

            migrationBuilder.DropIndex(
                name: "IX_Vozila_TipID",
                table: "Vozila");
        }
    }
}
