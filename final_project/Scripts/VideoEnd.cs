using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Video;


namespace NRKernal
{
    public class VideoEnd : MonoBehaviour
    {
        public GameObject videoPlayerHolder;
        private VideoPlayer videoPlayer;
        private long totalFrames = 0;
        private long currentFrame = 0;

        // Start is called before the first frame update
        void Start()
        {
            videoPlayer = videoPlayerHolder.GetComponent<VideoPlayer>();
            totalFrames = Convert.ToInt64(videoPlayer.frameCount);
        }

        // Update is called once per frame
        void Update()
        {
            currentFrame = videoPlayer.frame;
            if (currentFrame + 5 >= totalFrames || NRInput.GetButtonDown(ControllerButton.APP))
            {
                SceneManager.LoadScene("MainMenu");
            }
        }
        
    }

}

