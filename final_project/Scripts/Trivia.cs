using NRKernal;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using TMPro;
using Unity.VisualScripting.Antlr3.Runtime.Tree;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class Trivia : MonoBehaviour
{
    
    [Header("Input text file")]
    public TextAsset rawQuestionsAnswers;
    public List<Sprite> images = new List<Sprite>();
    public GameObject questionImage;
    public GameObject questionImageVertical;
    public GameObject questionText;
    public GameObject questionTextVertical;
    public GameObject scoreText;
    public List<GameObject> answerButtons = new List<GameObject>();
    public GameObject correctText;
    public GameObject wrongText;
    public GameObject correctImage;
    public GameObject wrongImage;
    public GameObject nextQuestionButton;
    public GameObject endButton;
    public GameObject endScoreText;

    public AudioSource correctSound;
    public AudioSource wrongSound;
    
    struct Entry
    {
        public int number;
        public string question;
        public string[] answers;
        public string correct;
    }
    private List<Entry> entries = new List<Entry>();

    private int score = 0;
    private int currentQuestion = 0;
    private string correctOption = "";
    private void parseEntries()
    {
        //string lines = System.IO.File.ReadAllText("A:\\Unity\\Projects\\ZavrsniRad\\Assets\\Scripts\\entries.txt");
        string lines = rawQuestionsAnswers.text;
        foreach (string line in lines.Split(";"))
        {
            if(entries.Count == 14)
            {
                string[] split = line.Split("/");
                for(int i = 0; i < split.Length; ++i)
                {
                    Entry str = entries[i];
                    str.correct = split[i];
                    entries[i] = str;
                }
            }
            else
            {
                string[] split = line.Split("%");
                Entry entry = new Entry();
                if (entries.Count <= 8)
                {
                    entry.number = int.Parse(split[0].Substring(0, 1));
                    entry.question = split[0].Substring(2);
                }
                else
                {
                    entry.number = int.Parse(split[0].Substring(0, 2));
                    entry.question = split[0].Substring(3);
                }
                

                entry.answers = new string[3];
                int i = 0;
                foreach (string ans in split[1].Split("/"))
                {
                    entry.answers[i] = ans;
                    i++;
                }
                entries.Add(entry);
                
            }
            
        }
        //Debug.Log(entries);

    }

    void Answer(string answer)
    {
        if (answer.Equals(correctOption))
        {
            score++;
            scoreText.GetComponent<TextMeshProUGUI>().text = score.ToString() + "/14";
            CorrectAnswer();
        } else
        {
            WrongAnswer();
        }
       

    }
    // Start is called before the first frame update
    void Start()
    {
        parseEntries();
        nextQuestionButton.GetComponent<Button>().onClick.AddListener(() => NextQuestion());
        for (int i = 0;i < answerButtons.Count; ++i) {
            Button btn = answerButtons[i].GetComponent<Button>();
            btn.onClick.AddListener(() => Answer(btn.GetComponentInChildren<TextMeshProUGUI>().text));
        }
        StartTrivia();
    }

    // Update is called once per frame
    void Update()
    {
        
        if (NRInput.GetButtonDown(ControllerButton.APP))
        {
            SceneManager.LoadScene("MainMenu");
        }
    }

    void StartTrivia()
    {
        Entry question = entries[currentQuestion];
        questionImage.GetComponent<Image>().sprite = images[currentQuestion];
        questionText.GetComponent<TextMeshProUGUI>().text = question.question;
        correctOption = question.correct;
        scoreText.GetComponent<TextMeshProUGUI>().text = score.ToString() + "/14";

        for (int i = 0; i < question.answers.Length; i++)
        {
            if(question.answers[i] != null)
            {
                answerButtons[i].transform.GetChild(0).GetComponent<TextMeshProUGUI>().text = question.answers[i];
                answerButtons[i].SetActive(true);
            }
            
        }

    }
    
    void CorrectAnswer()
    {
        questionImageVertical.SetActive(false);
        questionImage.SetActive(false);
        questionText.SetActive(false);
        questionTextVertical.SetActive(false);
        scoreText.GetComponent<TextMeshProUGUI>().text = score.ToString() + "/14";
        correctSound.Play();

        foreach (var answerBtn in answerButtons)
        {
            answerBtn.SetActive(false);
        }
        correctImage.SetActive(true);
        correctText.SetActive(true);
        if (currentQuestion >= 13)
        {
            Invoke("EndScreen", 3f);
        }
        else
        {
            nextQuestionButton.SetActive(true);
        }

    }
    void WrongAnswer()
    {
        questionImageVertical.SetActive(false);
        questionImage.SetActive(false);
        questionText.SetActive(false);
        questionTextVertical.SetActive(false);
        scoreText.GetComponent<TextMeshProUGUI>().text = score.ToString() + "/14";
        wrongSound.Play();

        foreach (var answerBtn in answerButtons)
        {
            answerBtn.SetActive(false);
        }
        wrongImage.SetActive(true);
        wrongText.SetActive(true);
        if (currentQuestion >= 13)
        {
            Invoke("EndScreen", 3f);
        } else
        {
            nextQuestionButton.SetActive(true);
        }
        
    }
    void NextQuestion() {
        correctImage.SetActive(false);
        correctText.SetActive(false);
        wrongText.SetActive(false);
        wrongImage.SetActive(false);
        nextQuestionButton.SetActive(false);
        scoreText.GetComponent<TextMeshProUGUI>().text = score.ToString() + "/14";
        currentQuestion++;

        Entry question = entries[currentQuestion];

        if(currentQuestion + 1 is 5 or 6 or 9 or 13)
        {
            questionImageVertical.GetComponent<Image>().sprite = images[currentQuestion];
            questionImageVertical.SetActive(true);
            questionTextVertical.GetComponent<TextMeshProUGUI>().text = question.question;
            questionTextVertical.SetActive(true);
        } else
        {
            questionImage.GetComponent<Image>().sprite = images[currentQuestion];
            questionImage.SetActive(true);
            questionText.GetComponent<TextMeshProUGUI>().text = question.question;
            questionText.SetActive(true);
        }
        
        correctOption = question.correct;

        for (int i = 0; i < question.answers.Length; i++)
        {
            if (question.answers[i] != null)
            {
                answerButtons[i].transform.GetChild(0).GetComponent<TextMeshProUGUI>().text = question.answers[i];
                answerButtons[i].SetActive(true);
            }

        }

    }

    void EndScreen()
    {
        correctImage.SetActive(false);
        correctText.SetActive(false);
        wrongText.SetActive(false);
        wrongImage.SetActive(false);
        nextQuestionButton.SetActive(false);
        scoreText.SetActive(false);

        endButton.SetActive(true);
        endScoreText.SetActive(true);
        endScoreText.GetComponent<TextMeshProUGUI>().text = score.ToString() + "/14";

    }

   
}
