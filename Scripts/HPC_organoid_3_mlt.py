import os
import cv2
import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from skimage import measure, morphology
from skimage.morphology import binary_dilation, binary_closing, disk


def process_pair(brightfield_path, gfp_path, output_subdir, input_root):
    try:
        rel_input_path = brightfield_path.relative_to(input_root)
    except ValueError:
        rel_input_path = brightfield_path.name
    print(f"Processing: {rel_input_path}")

    img_bf = cv2.imread(str(brightfield_path), cv2.IMREAD_UNCHANGED)
    if img_bf is None:
        print(f"[ERROR] Cannot read: {brightfield_path}")
        return None

    img_bf = cv2.normalize(img_bf, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    blurred = cv2.GaussianBlur(img_bf, (11, 11), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    clean = morphology.remove_small_objects(thresh.astype(bool), min_size=2000)
    clean = binary_dilation(clean, disk(20))
    clean = binary_closing(clean, disk(20))
    organoid_mask = measure.label(clean) > 0

    props = measure.regionprops(organoid_mask.astype(int))
    if not props:
        print(f"[WARNING] No organoid in: {brightfield_path.name}")
        return None

    org = props[0]
    y0, x0 = org.centroid
    area = org.area
    perimeter = org.perimeter
    circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter else 0
    diameter = 2 * np.sqrt(area / np.pi)
    solidity = org.solidity
    eccentricity = org.eccentricity
    extent = org.extent
    minr, minc, maxr, maxc = org.bbox
    aspect_ratio = (maxc - minc) / (maxr - minr + 1e-5)

    gfp_area = gfp_mean_intensity = gfp_std_dev = gfp_total_intensity = gfp_percent_area = 0
    gfp_num_clusters = gfp_mean_distance_to_centroid = 0
    gfp_positive_mask = np.zeros_like(organoid_mask, dtype=np.uint8)

    if gfp_path and gfp_path.exists():
        img_gfp = cv2.imread(str(gfp_path), cv2.IMREAD_UNCHANGED).astype(np.float32)
        gfp_values = img_gfp[organoid_mask == 1]
        gfp_min, gfp_max = np.percentile(gfp_values, [1, 99])
        gfp_norm = np.clip((img_gfp - gfp_min) / (gfp_max - gfp_min), 0, 1) * organoid_mask

        gfp_thresh_val = 0.85
        gfp_positive_mask = (gfp_norm > gfp_thresh_val).astype(np.uint8)
        gfp_area = np.sum(gfp_positive_mask)
        if gfp_area > 0:
            gfp_vals = gfp_norm[gfp_positive_mask == 1]
            gfp_mean_intensity = np.mean(gfp_vals)
            gfp_std_dev = np.std(gfp_vals)
            gfp_total_intensity = np.sum(gfp_vals)
            gfp_percent_area = gfp_area / area

            labeled = measure.label(gfp_positive_mask)
            gfp_num_clusters = np.max(labeled)
            gfp_props = measure.regionprops(labeled)
            distances = [np.linalg.norm([x0, y0] - np.array(p.centroid[::-1])) for p in gfp_props]
            gfp_mean_distance_to_centroid = np.mean(distances) if distances else 0

    overlay = cv2.cvtColor(img_bf, cv2.COLOR_GRAY2BGR)
    if gfp_path and gfp_path.exists():
        overlay[gfp_positive_mask.astype(bool)] = [0, 0, 255]  # Red

    contours, _ = cv2.findContours(organoid_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (0, 255, 255), 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(overlay, brightfield_path.name, (10, 40), font, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

    mask_path = output_subdir / "masks" / f"mask_{brightfield_path.stem}.png"
    overlay_path = output_subdir / "overlays" / f"overlay_{brightfield_path.stem}.png"
    mask_path.parent.mkdir(parents=True, exist_ok=True)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)

    cv2.imwrite(str(mask_path), (organoid_mask.astype(np.uint8)) * 255)
    cv2.imwrite(str(overlay_path), overlay)

    return {
        "filename": str(rel_input_path),
        "centroid_x": round(x0, 2),
        "centroid_y": round(y0, 2),
        "area": round(area, 2),
        "diameter": round(diameter, 2),
        "perimeter": round(perimeter, 2),
        "circularity": round(circularity, 4),
        "solidity": round(solidity, 4),
        "eccentricity": round(eccentricity, 4),
        "extent": round(extent, 4),
        "aspect_ratio": round(aspect_ratio, 4),
        "gfp_positive_area": int(gfp_area),
        "gfp_mean_intensity": round(gfp_mean_intensity, 4),
        "gfp_std_dev": round(gfp_std_dev, 4),
        "gfp_total_intensity": round(gfp_total_intensity, 4),
        "gfp_percent_area": round(gfp_percent_area, 4),
        "gfp_num_clusters": int(gfp_num_clusters),
        "gfp_mean_distance_to_centroid": round(gfp_mean_distance_to_centroid, 2)
    }


def collect_image_pairs(input_root, use_gfp=True):
    input_root = Path(input_root)
    image_pairs = []
    for bf_path in input_root.rglob("*"):
        if bf_path.suffix.lower() not in (".jpg", ".png", ".tif", ".tiff"):
            continue
        if "BRIGHTFIELD" not in bf_path.name:
            continue
        if "GFP" in bf_path.name:
            continue
        gfp_path = bf_path.with_name(bf_path.name.replace("BRIGHTFIELD", "GFP")) if use_gfp else None
        image_pairs.append((bf_path, gfp_path))
    return image_pairs


def main():
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)

    input_root = Path(config["input_root"])
    output_root = Path(config["output_root"])
    threads = os.cpu_count() if config.get("threads", "auto") == "auto" else int(config["threads"])
    use_gfp = config.get("use_gfp", True)

    image_pairs = collect_image_pairs(input_root, use_gfp)
    results = []

    def task(bf_path, gfp_path):
        relative_folder = bf_path.parent.relative_to(input_root)
        out_subdir = output_root / relative_folder
        return process_pair(bf_path, gfp_path, out_subdir, input_root)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(task, bf, gfp) for bf, gfp in image_pairs]
        for future in tqdm(futures, desc="Processing Images"):
            result = future.result()
            if result:
                results.append(result)

    df = pd.DataFrame(results)
    df.to_csv(output_root / "organoid_gfp_analysis.csv", index=False)
    print(f"[DONE] Results saved to {output_root / 'organoid_gfp_analysis.csv'}")


if __name__ == "__main__":
    main()