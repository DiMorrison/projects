using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WebApplicationTest.Models
{
    public class Vozilo
    {
        [Key]
        public int idVozila { get; set; }

        [DataType(DataType.Text)]
        [Required(ErrorMessage = "Please enter the vehicle name")]
        public string Naziv { get; set; }

        [Required]
        [ForeignKey("TipVozila")]
        public int TipID { get; set; }
        public TipVozila Tip { get; set; }

        [DataType(DataType.Text)]
        [Required(ErrorMessage = "Please enter the vehicle registration number")]
   
        public string RegOznaka { get; set; }

        [DataType(DataType.Date)]
        [Required(ErrorMessage = "Please enter the vehicle registration expire date")]
        public DateTime DatumIsteka { get; set; }

        public Vozilo()
        {

        }

        public Vozilo(int idVozila, string naziv, int tipID, string regOznaka, DateTime datumIsteka)
        {
            this.idVozila = idVozila;
            Naziv = naziv;
            TipID = tipID;
            RegOznaka = regOznaka;
            DatumIsteka = datumIsteka;
        }
    }
}
