[System.Serializable]
public class TriviaEntry 
{
    public string question;
    public string[] answers;
    public int correctAnswer;

    public TriviaEntry(string question, string[] answers, int correctAnswer)
    {
        this.question = question;
        this.answers = answers;
        this.correctAnswer = correctAnswer;
    }

}
