/****************************************************************************
* This is modified HelloMRController code. It is used for educational purposes.
* All rights go to Nreal Technology Limited.
* 
* 
* Copyright 2019 Nreal Techonology Limited. All rights reserved.
*                                                                                                                                                          
* This file is part of NRSDK.                                                                                                          
*                                                                                                                                                           
* https://www.nreal.ai/        
* 
*****************************************************************************/

using NRKernal.NRExamples;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace NRKernal
{
    public class PlacementController : MonoBehaviour
    {
        /// <summary> A model to place when a raycast from a user touch hits a plane. </summary>
        public GameObject HowitzerPrefab;
        public GameObject HowitzerGhostPrefab;
        public GameObject CameraRig;
        private bool ghostInit = false;
        /// <summary> Updates this object. </summary>
        [System.Obsolete]

        void Start()
        {
            HowitzerGhostPrefab.SetActive(false);
        }
        void Update() {            
            // Get controller laser origin.
            var handControllerAnchor = NRInput.DomainHand == ControllerHandEnum.Left ? ControllerAnchorEnum.LeftLaserAnchor : ControllerAnchorEnum.RightLaserAnchor;
            Transform laserAnchor = NRInput.AnchorsHelper.GetAnchor(NRInput.RaycastMode == RaycastModeEnum.Gaze ? ControllerAnchorEnum.GazePoseTrackerAnchor : handControllerAnchor);

            RaycastHit hitResult;
            if (Physics.Raycast(new Ray(laserAnchor.transform.position, laserAnchor.transform.forward), out hitResult, 10))
            {
                if (hitResult.collider.gameObject != null && hitResult.collider.gameObject.GetComponent<NRTrackableBehaviour>() != null)
                {
                    var behaviour = hitResult.collider.gameObject.GetComponent<NRTrackableBehaviour>();
                    if (behaviour.Trackable.GetTrackableType() != TrackableType.TRACKABLE_PLANE)
                    {
                        return;
                    }

                    if(!ghostInit)
                    {
                        HowitzerGhostPrefab.SetActive(true);
                        ghostInit= true;
                    }
                    
                    HowitzerGhostPrefab.transform.position = hitResult.point;
                    // If the player doesn't click the trigger button, we are done with this update.
                    if (!NRInput.GetButtonDown(ControllerButton.TRIGGER))
                    {
                        return;
                    }

                    if (GameObject.Find("HowitzerGroup") == null && GameObject.Find("HowitzerGroup(Clone)") == null)
                    {
                        HowitzerGhostPrefab.SetActive(false);
                        // Instantiate Howitzer model at the hit point / compensate for the hit point rotation.
                        Instantiate(HowitzerPrefab, hitResult.point, Quaternion.identity, behaviour.transform);
                        GameObject.Find("HowitzerGroup(Clone)").GetComponent<TransformScript>().CameraRig = this.CameraRig;
                        gameObject.GetComponent<NRExamples.PlaneDetector>().enabled = false;
                        GameObject howitzer = GameObject.Find("Howitzer6");
                        for (int i = 0; i < howitzer.transform.childCount; i++)
                        {
                            var child = howitzer.transform.GetChild(i);
                            Renderer component = child.GetComponent <Renderer>();
                            if (component != null)
                                component.enabled = true;
                            Collider collider = child.GetComponent<Collider>();
                            if (collider != null)
                                collider.enabled = false;
                        }

                        PolygonPlaneVisualizer[] foundPlanes = GameObject.FindObjectsOfType<PolygonPlaneVisualizer>();
                        foreach (var foundPlane in foundPlanes)
                        {
                            GameObject plane = foundPlane.gameObject;
                            plane.GetComponent<MeshRenderer>().enabled = false;
                            plane.GetComponent<MeshCollider>().enabled = false;

                        }
                        
                        
                    }
                    
                    
                }
            }
            else
            {
                HowitzerGhostPrefab.SetActive(false);
                ghostInit = false;
            }
        }
    }
}
