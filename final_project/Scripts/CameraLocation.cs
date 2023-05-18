using NRKernal;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraLocation : MonoBehaviour
{
    private GameObject holder;
    // Start is called before the first frame update

    void Update()
    {
        holder = GameObject.Find("PlaneDetector");
        if (holder != null)
            holder.GetComponent<PlacementController>().CameraRig = this.gameObject;
    }
}
