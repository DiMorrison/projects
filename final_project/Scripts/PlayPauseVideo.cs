using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;

public class PlayPauseVideo : MonoBehaviour
{
    public GameObject videoPlayerHolder;
    private VideoPlayer videoPlayer;

    void Start()
    {
        videoPlayer = videoPlayerHolder.GetComponent<VideoPlayer>();
    }
    public void Pause()
    {
        if (videoPlayer != null)
        {
            videoPlayer.Pause();
        }
    }
    public void Play()
    {
        if (videoPlayer != null)
        {
            videoPlayer.Play();
        }
    }
}
