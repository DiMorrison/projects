using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class HighlightModule : MonoBehaviour
{
    public TextAsset rawTooltips;
    List<string> tooltips = new List<string>();
    public GameObject tooltipPanel;
    public GameObject[] moduleButtons;
    private string activeModule = "";

    public Material defaultMaterial;
    public Material highlightMaterial;
    private GameObject lastHighlighted = null;
    void ParseTooltips()
    {
        string lines = rawTooltips.text;
        foreach (string line in lines.Split(";"))
        {
            tooltips.Add(line.Trim());
        }
    }

    void HandleModuleButton(GameObject button)
    {
        if (button.name.Equals(activeModule))
        {
            if (lastHighlighted != null)
            {
                lastHighlighted.GetComponent<MeshRenderer>().material = defaultMaterial;
            }
            tooltipPanel.SetActive(false);
            activeModule = "";
            return;
        }
        
        string tooltip = "";
        string text = button.transform.GetChild(0).GetComponent<TextMeshProUGUI>().text;
        foreach (string line in tooltips)
        {
            if (line.Contains(text))
            {
                tooltip = line.Split(":")[1];
                break;
            }
        }

        if (lastHighlighted != null)
        {
            lastHighlighted.GetComponent<MeshRenderer>().material = defaultMaterial;
        }

        lastHighlighted = GameObject.Find(text);
        lastHighlighted.GetComponent<MeshRenderer>().material = highlightMaterial;
        
        tooltipPanel.GetComponentInChildren<TextMeshProUGUI>().text = tooltip;
        tooltipPanel.SetActive(true);
        activeModule= button.name;
    }
    // Start is called before the first frame update
    void Start()
    {
        ParseTooltips();
        tooltipPanel.SetActive(false);
        foreach (var button in moduleButtons)
        {
            button.GetComponent<Button>().onClick.AddListener(() => HandleModuleButton(button));
        }
    }

}
