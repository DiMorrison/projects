using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Provjera : MonoBehaviour
{
    public Text pitanjeTxt;
    public Button[] buttons;
    public Pitanja[] pitanja;
    private Pitanja pitan;
    public Image Ima;
    public Image Ima2;
    public Image Ima3;
    public Text pitanjeTxt2;
    public Text numeracija;
    public Button[] buttons2;
    public Button provjera;
    public Button dalje;
    public Text TNTxt;
    public Image KvacicaX;
    public Text RezTxt;
    private TextAsset ucitaj;
    private int br;
    private int rez=0;
    private string c="";
    private bool flag;
    public Button Povratak;
    public AudioSource izvor;
    public AudioClip tocno;
    public AudioClip krivo;

    public struct Pitanja
    {
        public string txtpitanje;
        public string[] odgovori;
        public string tocno;
    }

    public void Start()
    {
        PlayerPrefs.SetInt("tr", 0);
        //provjera.onClick.AddListener(() => Pocetak(PlayerPrefs.GetInt("tr")));
        Pocetak(PlayerPrefs.GetInt("tr"));
        dalje.onClick.AddListener(() => Pocetak(PlayerPrefs.GetInt("tr")));
        Povratak.onClick.AddListener(() => Pocetak(-1));
    }

    public void Pocetak(int tren)
    {
        if (PlayerPrefs.GetInt("tr") == 14 || tren==-1)
        {
            RezTxt.text = "Rezultat\n" + rez.ToString() + "/14";
            RezTxt.gameObject.SetActive(true);
            numeracija.gameObject.SetActive(false);
            TNTxt.gameObject.SetActive(false);
            KvacicaX.gameObject.SetActive(false);
            dalje.gameObject.SetActive(false);
            PlayerPrefs.SetInt("tr", 0);
            c = "";
            br = 0;
            rez = 0;
        }
        else
        {
            RezTxt.gameObject.SetActive(false);
            dalje.gameObject.SetActive(false);
            ucitaj = (TextAsset)Resources.Load("pitanjaOdgovori", typeof(TextAsset));
            pitan = DohvatiSve(ucitaj, tren);
            pitanjeTxt2.text = pitan.txtpitanje;
            pitanjeTxt.text = pitan.txtpitanje;
            TNTxt.gameObject.SetActive(false);
            KvacicaX.gameObject.SetActive(false);
            int help = PlayerPrefs.GetInt("tr") + 1;
            Ima.sprite = Resources.Load<Sprite>("Slike/" + help.ToString());
            Ima2.sprite = Resources.Load<Sprite>("Slike/" + help.ToString());
            Ima3.sprite = Resources.Load<Sprite>("Slike/" + help.ToString());

            if (br == 5 || br == 6 || br == 9 || br == 13)
            {
                pitanjeTxt2.gameObject.SetActive(true);
                pitanjeTxt.gameObject.SetActive(false);
                Ima.gameObject.SetActive(false);
                if (br == 6)
                {
                    Ima3.SetNativeSize();
                    Ima3.gameObject.SetActive(true);
                    Ima2.gameObject.SetActive(false);
                }
                else
                {
                    Ima2.gameObject.SetActive(true);
                    Ima3.gameObject.SetActive(false);
                }
            }
            else
            {
                pitanjeTxt2.gameObject.SetActive(false);
                pitanjeTxt.gameObject.SetActive(true);
                Ima.gameObject.SetActive(true);
                Ima2.gameObject.SetActive(false);
                Ima3.gameObject.SetActive(false);
            }

            numeracija.text = help.ToString() + "/14";

            for (int i = 0; i < buttons.Length; i++)
            {
                if (i >= pitan.odgovori.Length)
                {
                    buttons2[i].gameObject.SetActive(false);
                    buttons[i].gameObject.SetActive(false);
                    continue;
                }

                string odg = pitan.odgovori[i];
                if (br == 5 || br == 6 || br == 9 || br == 13)
                {
                    buttons[i].gameObject.SetActive(false);
                    buttons2[i].gameObject.SetActive(true);
                }
                else
                {
                    buttons[i].gameObject.SetActive(true);
                    buttons2[i].gameObject.SetActive(false);
                }
                buttons[i].GetComponentInChildren<Text>().text = odg;
                buttons2[i].GetComponentInChildren<Text>().text = odg;
            }
            InitializeButtons(tren);
        }
    }

    public void InitializeButtons(int tren)
    {
        for (int i=0; i<pitan.odgovori.Length; i++)
        {
            Button button = buttons[i];
            Button button2 = buttons2[i];
            int btnind = i;
            button.onClick.AddListener(() => ProvjeriOdg(button.GetComponentInChildren<Text>().text, br));
            button2.onClick.AddListener(() => ProvjeriOdg(button2.GetComponentInChildren<Text>().text, br));
        }
    }
    public void ProvjeriOdg(string txt, int id)
    {
        if (txt.Equals(pitan.tocno))
        {
            TNTxt.text = "Točan odgovor!";
            TNTxt.gameObject.SetActive(true);
            pitanjeTxt.gameObject.SetActive(false);
            pitanjeTxt2.gameObject.SetActive(false);
            Ima.gameObject.SetActive(false);
            Ima2.gameObject.SetActive(false);
            Ima3.gameObject.SetActive(false);
            KvacicaX.sprite = Resources.Load<Sprite>("GreenCheckmark4");
            KvacicaX.gameObject.SetActive(true);
            izvor.clip = tocno;
            izvor.Play();
            flag = true;
        }
        else
        {
            TNTxt.text = "Netočan odgovor!";
            TNTxt.gameObject.SetActive(true);
            pitanjeTxt.gameObject.SetActive(false);
            pitanjeTxt2.gameObject.SetActive(false);
            Ima.gameObject.SetActive(false);
            Ima2.gameObject.SetActive(false);
            Ima3.gameObject.SetActive(false);
            KvacicaX.sprite = Resources.Load<Sprite>("RedXMark");
            KvacicaX.gameObject.SetActive(true);
            izvor.clip = krivo;
            izvor.Play();
            flag = false;
        }
        for (int i = 0; i < buttons.Length; i++)
        {
            buttons[i].gameObject.SetActive(false);
            buttons2[i].gameObject.SetActive(false);
        }

        dalje.gameObject.SetActive(true);
        PlayerPrefs.SetInt("tr", id);
    }

    public string[] Pretvori(TextAsset ucitano)
    {
        string[] poljeP;
        string output = ucitano.ToString();
        poljeP = output.Split(';');
        return poljeP;
    }
  
    public string DohvatiTrenutnoPitanje(TextAsset ucitano, int tren)
    {
        string pit = null;
        string[] poljeP;
        poljeP = Pretvori(ucitano);
        string[] poljePitanja = null;
        if (tren < poljeP.Length - 1)
        {
            poljePitanja = poljeP[tren].Split('%');
        }
        pit = poljePitanja[0];
        return pit;
    }

    public string[] DohvatiOdgovore(string[] poljeP, string pitanje)
    {
        string[] polje = null;
        string pomoc;
        string[] poljePitanjeodgovor;

        for (int i = 0; i < poljeP.Length-1; i++)
        {
            poljePitanjeodgovor = poljeP[i].Split('%');
            if (poljePitanjeodgovor[0].Equals(pitanje))
            {
                pomoc = poljePitanjeodgovor[1];
                polje = pomoc.Split('/');
                break;
            }
        }
        return polje;
    }

    public string DohvatiTocno(string[] poljeP, string pitanje)
    {
        string[] polje;
        string pomoc;
        string[] poljePitanjeodgovor;
        int duljina = poljeP.Length;
        string odgovor=null;

        for (int i = 0; i < poljeP.Length - 1; i++)
        {
            poljePitanjeodgovor = poljeP[i].Split('%');
            if (poljePitanjeodgovor[0].Equals(pitanje))
            {
                pomoc = poljeP[duljina-1];
                polje = pomoc.Split('/');
                odgovor = polje[i];
                break;
            }
        }
        return odgovor;
    }

    public Pitanja DohvatiSve(TextAsset ucitano, int tren)
    {
        int t = 1;
        if (flag)
        {
            rez = rez + 1;
        }
        c = c + t.ToString();
        br = c.Length;
        Pitanja p;
        p.txtpitanje = DohvatiTrenutnoPitanje(ucitano, tren);
        p.odgovori = DohvatiOdgovore(Pretvori(ucitano), p.txtpitanje);
        p.tocno = DohvatiTocno(Pretvori(ucitano), p.txtpitanje);
        return p;
    } 
}
