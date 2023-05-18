using System.Collections;
using System.Collections.Generic;
using System.Runtime.Remoting.Messaging;
using UnityEngine;
using UnityEngine.SceneManagement;

public class ChangeScene : MonoBehaviour
{
    [Header ("Next Scene Name")]
    public string SceneName;

    public void Change()
    {
        SceneManager.LoadScene(SceneName);
    }
}
