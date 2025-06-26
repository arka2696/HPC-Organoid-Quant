## **Organoid Morphological Features**

| Parameter                   | Description                                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `filename`                  | Name of the brightfield image being analyzed.                                                                                                    |
| `centroid_x` / `centroid_y` | X and Y coordinates of the center (centroid) of the detected organoid.                                                                           |
| `area`                      | Total number of pixels within the organoid mask. If pixel size is known, this can be converted to μm².                                           |
| `diameter`                  | Diameter of a circle with the same area as the organoid: useful for estimating size.                                                             |
| `perimeter`                 | Length of the outer boundary of the organoid (in pixels).                                                                                        |
| `circularity`               | Defined as $4\pi \times \text{Area} / \text{Perimeter}^2$. Values near 1 indicate a perfect circle; lower values indicate more irregular shapes. |
| `solidity`                  | Ratio of organoid area to its convex hull area. Measures how concave or filled in the shape is.                                                  |
| `eccentricity`              | Ratio of the distance between foci of the ellipse and its major axis. 0 = circle, close to 1 = elongated.                                        |
| `extent`                    | Ratio of organoid area to bounding box area. Indicates how much of the surrounding box is filled.                                                |
| `aspect_ratio`              | Ratio of bounding box width to height. Useful for assessing elongation or asymmetry.                                                             |

---

## **GFP (Green Fluorescent Protein) Quantification**

These metrics are only calculated if a corresponding GFP image is provided:

| Parameter                       | Description                                                                                                                                                     |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gfp_positive_area`             | Total number of pixels in the GFP channel that exceed a normalized intensity threshold (default: 0.85). Represents GFP+ regions.                                |
| `gfp_mean_intensity`            | Mean intensity of GFP signal within the GFP+ regions. Indicates average expression.                                                                             |
| `gfp_std_dev`                   | Standard deviation of intensity within GFP+ areas. Shows variability across the organoid.                                                                       |
| `gfp_total_intensity`           | Sum of all pixel intensities in the GFP+ mask. Reflects total GFP expression load.                                                                              |
| `gfp_percent_area`              | Ratio of GFP+ area to total organoid area. Measures how much of the organoid is GFP+.                                                                           |
| `gfp_num_clusters`              | Number of disconnected GFP+ clusters (e.g., patches of high expression). Could relate to spatial patterning or heterogeneity.                                   |
| `gfp_mean_distance_to_centroid` | Mean Euclidean distance between each GFP+ cluster's centroid and the organoid centroid. Reflects spatial distribution of GFP+ regions—closer to center or edge. |

---

## **Interpretation and Use Cases**

* **Size-related** (`area`, `diameter`) metrics help estimate growth or compaction of organoids.
* **Shape-related** (`circularity`, `solidity`, `eccentricity`) metrics capture morphological changes under different treatments.
* **GFP metrics** quantify not just **how much** GFP is expressed but also **how localized**, **clustered**, or **dispersed** the expression is within the organoid. This can be vital when:

  * Tracking differentiation markers.
  * Assessing drug response.
  * Monitoring reporter gene activity.

---

### Solidity is a shape descriptor that quantifies **how convex (compact) a shape is**, defined as:

$$
\textbf{Solidity} = \frac{\text{Area}}{\text{Convex Hull Area}}
$$

---

### 🔹 **Range of Solidity Values:**

* **Range:** $0 < \text{Solidity} \leq 1$
* **Interpretation:**

| Solidity Value | Morphology                                         | Biological Interpretation                      |
| -------------- | -------------------------------------------------- | ---------------------------------------------- |
| \~**1.00**     | Perfectly convex (e.g., smooth circle or ellipse)  | Healthy, compact organoid or spheroid          |
| **0.85–0.99**  | Slightly irregular but still fairly compact        | Minor disaggregation or blebbing               |
| **0.6–0.85**   | Moderate irregularities, lobed or protruding shape | Potential cell migration, budding, or stress   |
| **< 0.6**      | Highly concave or fragmented                       | Disorganized, apoptotic, or broken-up organoid |

---

### 🔸 **Visual Examples (if plotted):**

You can visualize solidity values using overlays or color-coded metrics:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Example
sns.histplot(df['solidity'], bins=20, kde=True)
plt.xlabel('Solidity')
plt.title('Distribution of Organoid Solidity')
plt.axvline(0.85, color='orange', linestyle='--', label='Moderate Irregularity')
plt.axvline(0.6, color='red', linestyle='--', label='High Irregularity')
plt.legend()
plt.show()
```

---

### 🔸 **When is Solidity Useful?**

* **Quality control**: Detecting damaged or overly fragmented organoids.
* **Phenotyping**: Identifying spreading vs. non-spreading morphologies.
* **Drug response**: Cytotoxic agents often reduce solidity due to fragmentation.


