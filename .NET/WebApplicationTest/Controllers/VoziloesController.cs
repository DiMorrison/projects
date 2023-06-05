using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using WebApplicationTest.Data;
using WebApplicationTest.Models;

namespace WebApplicationTest.Controllers
{
    public class VoziloesController : Controller
    {
        private readonly ApplicationDbContext _context;

        public VoziloesController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: Voziloes
        public async Task<IActionResult> Index()
        {
            var applicationDbContext = _context.Vozila.Include(v => v.Tip);
            return View(await applicationDbContext.ToListAsync());
        }

        //GET /Voziloes/Expired
        public async Task<IActionResult> Expired()
        {
            if (_context.Vozila != null)
            {
                var vozilo = _context.Vozila
                .Include(v => v.Tip);
                return View(await vozilo.ToListAsync());

            } else {
                return View(); 
            }
        }

        //GET /Voziloes/Expired
        public async Task<IActionResult> Search(string searchString)
        {
            if (_context.Vozila != null)
            {
                if (!String.IsNullOrEmpty(searchString))
                {
                    var vozilo = _context.Vozila.Where(s => s.Naziv!.Contains(searchString)).Include(v => v.Tip);
                    return View(await vozilo.ToListAsync());
                } else
                { 
                    return View(); 
                }         

            }
            else
            {
                return View();
            }
        }

        //GET /Voziloes/SearchDate
        public async Task<IActionResult> SearchDate(DateTime startDate, DateTime endDate)
        {
            if (_context.Vozila != null)
            {
                if (startDate != DateTime.MinValue && endDate != DateTime.MinValue)
                {
                    var vozilo = _context.Vozila.Where(s => (startDate <= s.DatumIsteka.Date && s.DatumIsteka.Date <= endDate)).Include(v => v.Tip);
                    return View(await vozilo.ToListAsync());

                } else if(endDate != DateTime.MinValue && startDate == DateTime.MinValue)
                {
                    var vozilo = _context.Vozila.Where(s => s.DatumIsteka.Date <= endDate).Include(v => v.Tip);
                    return View(await vozilo.ToListAsync());
                }
          
                else if (startDate != DateTime.MinValue && endDate == DateTime.MinValue)
                {
                    var vozilo = _context.Vozila.Where(s => startDate <= s.DatumIsteka.Date).Include(v => v.Tip);
                    return View(await vozilo.ToListAsync());
                }
                else
                {
                    return View();
                }

            }
            else
            {
                return View();
            }
        }


        // GET: Voziloes/Details/5
        public async Task<IActionResult> Details(int? id)
        {
            if (id == null || _context.Vozila == null)
            {
                return NotFound();
            }

            var vozilo = await _context.Vozila
                .Include(v => v.Tip)
                .FirstOrDefaultAsync(m => m.idVozila == id);
            if (vozilo == null)
            {
                return NotFound();
            }

            return View(vozilo);
        }

        // GET: Voziloes/Create
        public IActionResult Create()
        {
            ViewData["TipID"] = new SelectList(_context.TipoviVozila, "IdTip", "Naziv");
            return View();
        }

        // POST: Voziloes/Create
        // To protect from overposting attacks, enable the specific properties you want to bind to.
        // For more details, see http://go.microsoft.com/fwlink/?LinkId=317598.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create([Bind("idVozila,Naziv,TipID,RegOznaka,DatumIsteka")] Vozilo vozilo)
        {
            //if (ModelState.IsValid)
            //{
                _context.Add(vozilo);
                await _context.SaveChangesAsync();
                return RedirectToAction(nameof(Index));
            //}
            ViewData["TipID"] = new SelectList(_context.TipoviVozila, "IdTip", "Naziv", vozilo.TipID);
            return View(vozilo);
        }

        // GET: Voziloes/Edit/5
        public async Task<IActionResult> Edit(int? id)
        {
            if (id == null || _context.Vozila == null)
            {
                return NotFound();
            }

            var vozilo = await _context.Vozila.FindAsync(id);
            if (vozilo == null)
            {
                return NotFound();
            }
            ViewData["TipID"] = new SelectList(_context.TipoviVozila, "IdTip", "Naziv", vozilo.TipID);
            return View(vozilo);
        }

        // POST: Voziloes/Edit/5
        // To protect from overposting attacks, enable the specific properties you want to bind to.
        // For more details, see http://go.microsoft.com/fwlink/?LinkId=317598.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, [Bind("idVozila,Naziv,TipID,RegOznaka,DatumIsteka")] Vozilo vozilo)
        {
            if (id != vozilo.idVozila)
            {
                return NotFound();
            }

            //if (ModelState.IsValid)
            {
                try
                {
                    _context.Update(vozilo);
                    await _context.SaveChangesAsync();
                }
                catch (DbUpdateConcurrencyException)
                {
                    if (!VoziloExists(vozilo.idVozila))
                    {
                        return NotFound();
                    }
                    else
                    {
                        throw;
                    }
                }
                return RedirectToAction(nameof(Index));
            }
            ViewData["TipID"] = new SelectList(_context.TipoviVozila, "IdTip", "Naziv", vozilo.TipID);
            return View(vozilo);
        }

        // GET: Voziloes/Delete/5
        public async Task<IActionResult> Delete(int? id)
        {
            if (id == null || _context.Vozila == null)
            {
                return NotFound();
            }

            var vozilo = await _context.Vozila
                .Include(v => v.Tip)
                .FirstOrDefaultAsync(m => m.idVozila == id);
            if (vozilo == null)
            {
                return NotFound();
            }

            return View(vozilo);
        }

        // POST: Voziloes/Delete/5
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteConfirmed(int id)
        {
            if (_context.Vozila == null)
            {
                return Problem("Entity set 'ApplicationDbContext.Vozila'  is null.");
            }
            var vozilo = await _context.Vozila.FindAsync(id);
            if (vozilo != null)
            {
                _context.Vozila.Remove(vozilo);
            }

            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Index));
        }

        private bool VoziloExists(int id)
        {
            return (_context.Vozila?.Any(e => e.idVozila == id)).GetValueOrDefault();
        }

        
    }
}
