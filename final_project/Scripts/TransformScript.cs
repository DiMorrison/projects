using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using NRKernal;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using Unity.VisualScripting;

public class TransformScript : MonoBehaviour
{
    public GameObject CameraRig = null;
    public GameObject howitzer;

    private bool rotate = true;

    public GameObject rotateButton;
    public GameObject scaleButton;

    public GameObject buttonHolder;
    public GameObject moduleHolder;


    void HandleButtonHolder()
    {
        Vector3 userPosition = CameraRig.transform.position;
        Vector3 userOrientation = CameraRig.transform.forward;

        buttonHolder.transform.LookAt(CameraRig.transform.position);
        
        buttonHolder.transform.position = userPosition + userOrientation * 1.75f;
        buttonHolder.transform.position = new Vector3(buttonHolder.transform.position.x, -2.5f, buttonHolder.transform.position.z);
    }

    void HandleModuleHolder()
    {
        Vector3 userPosition = CameraRig.transform.position;
        Vector3 userOrientation = CameraRig.transform.forward;

        moduleHolder.transform.LookAt(CameraRig.transform.position);

        moduleHolder.transform.position = userPosition + userOrientation;
        moduleHolder.transform.position = new Vector3(moduleHolder.transform.position.x - 0.4f, 0f, moduleHolder.transform.position.z -0.5f);
    }
    // Start is called before the first frame update
    void Start()
    {
        
        rotate = true;
        rotateButton.GetComponent<Button>().interactable = false;
        scaleButton.GetComponent<Button>().interactable = true;
        rotateButton.GetComponent<Button>().onClick.AddListener(() => { 
            this.rotate = true;
            rotateButton.GetComponent<Button>().interactable = false;
            scaleButton.GetComponent<Button>().interactable = true;
        });
        scaleButton.GetComponent<Button>().onClick.AddListener(() => {
            this.rotate = false;
            rotateButton.GetComponent<Button>().interactable = true;
            scaleButton.GetComponent<Button>().interactable = false;
        });
        HandleButtonHolder();
        HandleModuleHolder();
    }

    // Update is called once per frame
    void Update()
    {
        HandleButtonHolder();
        HandleModuleHolder();
        if (NRInput.GetButtonDown(ControllerButton.APP))
        {
            SceneManager.LoadScene("MainMenu");
        }

        
        var touch_delta = NRInput.GetDeltaTouch();
        //this.transform.LookAt(cameraRig.transform.position);

        if (rotate)
        {
            if (touch_delta.x > 0.005)
            {
                float angle = (howitzer.transform.rotation.eulerAngles.y + 80f * Time.deltaTime) % 360f;
                howitzer.transform.rotation = Quaternion.Euler(0, angle, 0);
            }
            else if (touch_delta.x < -0.005)
            {
                float angle = (howitzer.transform.rotation.eulerAngles.y - 80f * Time.deltaTime) % 360f;
                howitzer.transform.rotation = Quaternion.Euler(0, angle, 0);
            }
        }
        else
        {
            if (touch_delta.y > 0.008)
            {
                Vector3 scaleChange = new Vector3(0.0005f, 0.0005f, 0.0005f);
                howitzer.transform.localScale += scaleChange;
            }
            else if (touch_delta.y < -0.008)
            {
                Vector3 scaleChange = new Vector3(-0.0005f, -0.0005f, -0.0005f);
                if (howitzer.transform.localScale.x > 0.01 && howitzer.transform.localScale.y > 0.01 && howitzer.transform.localScale.z > 0.01)
                    howitzer.transform.localScale += scaleChange;
            }
        }
        
        
        

    }
}
