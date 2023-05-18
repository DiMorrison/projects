using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LightLookAtScript : MonoBehaviour
{
    [Header("Light movement and rotation settings")]   
    public GameObject model;
 
    void Update()
    {
        model = GameObject.Find("Howitzer6");

        if (model != null)
        {
            transform.LookAt(model.transform);
        }
        
    }
}
