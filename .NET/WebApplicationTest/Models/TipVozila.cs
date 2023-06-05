using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WebApplicationTest.Models
{
    public class TipVozila
    {
        public TipVozila()
        {

        }
        public TipVozila(int idTip, string naziv)
        {
            IdTip = idTip;
            Naziv = naziv;
        }

        [Key]
        public int IdTip { get; set; }

        [DataType(DataType.Text)]
        [Required(ErrorMessage = "Please enter the vehicle type name")]
        public string Naziv { get; set; }


    }
}
