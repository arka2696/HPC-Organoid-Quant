# HPC-Organoid-Quant


# Organoid Detection and GFP Quantification

This project provides a complete and modular pipeline to detect organoids from **brightfield microscopy images**, with optional quantification of **GFP-positive regions** from corresponding fluorescence images.

### Features

- Works with **brightfield-only** images or **brightfield + GFP**
- Detects **irregular and fragmented organoids** as a **single object**
- Computes key morphological features:
  - Area
  - Centroid
  - Perimeter
  - Circularity
- If GFP is provided:
  - Quantifies GFP+ area
  - Calculates mean and total GFP intensity
- Generates annotated overlay images for visualization



## Project Structure

```

Organoid\_GFP\_Analysis/
│
├── notebooks/
│   └── organoid\_analysis.ipynb      # Main Colab notebook
│
├── example\_data/
│   └── BRIGHTFIELD\_*.TIF            # Brightfield image(s)
│   └── GFP\_*.TIF                     # GFP fluorescence (optional)
│
├── outputs/
│   ├── organoid\_gfp\_analysis.csv    # Measurement results
│   └── overlay\_output.png           # Visual overlay (organoid + GFP)
│
├── README.md
└── requirements.txt (optional)

````

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Organoid_GFP_Analysis.git
cd Organoid_GFP_Analysis
````

### 2. Launch in Google Colab

> Best used with Google Drive integration.

* Open `notebooks/organoid_analysis.ipynb`
* Update paths to your own brightfield and GFP images
* Run all cells

---

## 📊 Output Example

* `.csv` file with organoid measurements
* Overlay image:

  * 🔵 Organoid outline
  * 🔴 GFP+ region (if applicable)

<p align="center">
  <img src="https://your-link-to-overlay-image-if-public.png" alt="Overlay Example" width="500"/>
</p>

---

## Dependencies

All dependencies are standard and available in Google Colab:

* `OpenCV`
* `NumPy`
* `Matplotlib`
* `scikit-image`
* `Pandas`

If you want to run locally, create a `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Notes

* The script assumes images are **grayscale TIFFs**
* If your organoids are fragmented, the pipeline includes morphological merging to treat them as one object
* GFP quantification thresholds can be adjusted in the notebook

---

## Contact

For questions or suggestions, feel free to open an issue or reach out via GitHub.

---

## License

MIT License. See `LICENSE` file for details.

```

