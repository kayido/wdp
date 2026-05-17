import cv2
import numpy as np
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List
from .models import ClassificationDefine

def convert_numpy_types(obj):
    if isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


def load_image(image_path: str) -> np.ndarray:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"L'image {image_path} n'existe pas.")
    img_data = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Impossible de charger l'image {image_path}. Vérifiez le format ou l'intégrité du fichier.")
    if img.shape[0] < 10 or img.shape[1] < 10:
        raise ValueError(f"L'image {image_path} est trop petite (hauteur: {img.shape[0]}, largeur: {img.shape[1]}).")
    return img



def get_basic_features(img: np.ndarray, image_path: str) -> Dict:
    height, width = img.shape[:2]
    file_size = os.path.getsize(image_path) / 1024
    aspect_ratio = height / width if width > 0 else 0
    return {
        "height": height,
        "width": width,
        "aspect_ratio": aspect_ratio,
        "file_size_kb": file_size
    }


def get_color_features(img: np.ndarray) -> Dict:
    b, g, r = cv2.split(img)
    rgb_features = {
        "mean_r": np.mean(r) if r.size > 0 else 0,
        "std_r": np.std(r) if r.size > 0 else 0,
        "mean_g": np.mean(g) if g.size > 0 else 0,
        "std_g": np.std(g) if g.size > 0 else 0,
        "mean_b": np.mean(b) if b.size > 0 else 0,
        "std_b": np.std(b) if b.size > 0 else 0
    }
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    
    gray_features = {
        "mean_gray": np.mean(gray) if gray.size > 0 else 0,
        "std_gray": np.std(gray) if gray.size > 0 else 0,
        "histogram_gray": gray_hist.tolist(),
        "histogram_gray_mean": np.mean(gray_hist) if gray_hist.size > 0 else 0,
        "histogram_gray_max": np.max(gray_hist) if gray_hist.size > 0 else 0,
        "percent_dark_pixels": np.sum(gray < 50) / gray.size * 100 if gray.size > 0 else 0,
        "percent_bright_pixels": np.sum(gray > 200) / gray.size * 100 if gray.size > 0 else 0
    }
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    hue_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180]).flatten()

    
    dominant_hue = np.argmax(hue_hist) if hue_hist.size > 0 else 0
    hsv_features = {
        "mean_saturation": np.mean(s) if s.size > 0 else 0,
        "mean_value": np.mean(v) if v.size > 0 else 0,
        "dominant_hue": float(dominant_hue),
        "histogram_hue": hue_hist.tolist(),
        "histogram_hue_mean": np.mean(hue_hist) if hue_hist.size > 0 else 0,
        "histogram_hue_max": np.max(hue_hist) if hue_hist.size > 0 else 0
    }
    return {**rgb_features, **gray_features, **hsv_features}


def get_texture_features(img: np.ndarray) -> Dict:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    contrast = np.std(gray) if gray.size > 0 else 0
    energy = np.sum(gray.astype(float) ** 2) if gray.size > 0 else 0
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist = hist / hist.sum() if hist.sum() > 0 else hist
    entropy = -np.sum(hist * np.log2(hist + 1e-10)) if hist.sum() > 0 else 0
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
    mean_gradient = np.mean(gradient_magnitude) if gradient_magnitude.size > 0 else 0
    edges = cv2.Canny(gray, 100, 250)
    edge_density = np.sum(edges > 0) / edges.size if edges.size > 0 else 0
    return {
        "contrast": contrast,
        "energy": energy,
        "entropy": entropy,
        "mean_gradient": mean_gradient,
        "edge_density": edge_density
    }


def get_shape_features(img: np.ndarray) -> Dict:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    gray = cv2.equalizeHist(gray)
    thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh2 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.bitwise_and(thresh1, thresh2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("Aucun contour détecté dans l'image.")
        return {
            "num_contours": 0,
            "total_area_objects": 0.0,
            "area_ratio": 0.0,
            "mean_compactness": 0.0,
            "mean_eccentricity": 0.0,
            "center_contour_density": 0.0
        }
    total_area = 0
    total_perimeter = 0
    compactness_list = []
    eccentricity_list = []
    center_contours = 0
    height, width = gray.shape
    total_pixels = height * width
    x_min = width // 4
    x_max = 3 * width // 4
    y_min = height // 4
    y_max = 3 * height // 4
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

    # Ignorer les contours dans la zone haute (par exemple, au-dessus de 1/3 de l'image)
        if y + h < height // 3:
            continue

        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        total_area += area
        total_perimeter += perimeter

        if area > 0:
            compactness = (perimeter ** 2) / (4 * np.pi * area)
            compactness_list.append(compactness)

        eccentricity = w / h if h > 0 else 0
        eccentricity_list.append(eccentricity)

        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            if x_min <= cx <= x_max and y_min <= cy <= y_max:
                center_contours += 1

    return {
        "num_contours": len(contours),
        "total_area_objects": total_area,
        "area_ratio": total_area / total_pixels if total_pixels > 0 else 0,
        "mean_compactness": np.mean(compactness_list) if compactness_list else 0,
        "mean_eccentricity": np.mean(eccentricity_list) if eccentricity_list else 0,
        "center_contour_density": center_contours / len(contours) if contours else 0
    }


def get_zone_features(img: np.ndarray) -> Dict:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    height, width = gray.shape
    zone_height = height // 3
    if zone_height < 1:
        print("L'image est trop petite pour être divisée en zones.")
        return {
            "top": {"histogram_mean": 0.0, "mean_brightness": 0.0, "edge_density": 0.0, "histogram": [0.0] * 256},
            "middle": {"histogram_mean": 0.0, "mean_brightness": 0.0, "edge_density": 0.0, "histogram": [0.0] * 256},
            "bottom": {"histogram_mean": 0.0, "mean_brightness": 0.0, "edge_density": 0.0, "histogram": [0.0] * 256}
        }
    zones = {
        "top": gray[:zone_height, :],
        "middle": gray[zone_height:2 * zone_height, :],
        "bottom": gray[2 * zone_height:, :]
    }
    zone_features = {}
    for zone_name, zone_img in zones.items():
        if zone_img.size == 0:
            print(f"Zone {zone_name} vide ou trop petite.")
            zone_features[zone_name] = {
                "histogram_mean": 0.0,
                "mean_brightness": 0.0,
                "edge_density": 0.0,
                "histogram": [0.0] * 256
            }
            continue
        hist = cv2.calcHist([zone_img], [0], None, [256], [0, 256]).flatten()
        mean_brightness = np.mean(zone_img) if zone_img.size > 0 else 0
        edges = cv2.Canny(zone_img, 100, 250)
        edge_density = np.sum(edges > 0) / edges.size if edges.size > 0 else 0
        zone_features[zone_name] = {
            "histogram_mean": np.mean(hist) if hist.size > 0 else 0,
            "mean_brightness": mean_brightness,
            "edge_density": edge_density,
            "histogram": hist.tolist()
        }
    return zone_features

def get_contours_from_image(image_path: str) -> Tuple[np.ndarray, List[np.ndarray]]:
    img = load_image(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    gray = cv2.equalizeHist(gray)

    thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
    thresh2 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)[1]

    # Aligner forme et type
    if thresh1.shape != thresh2.shape:
        thresh2 = cv2.resize(thresh2, (thresh1.shape[1], thresh1.shape[0]))
    if thresh1.dtype != thresh2.dtype:
        thresh2 = thresh2.astype(thresh1.dtype)

    thresh = cv2.bitwise_and(thresh1, thresh2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return img, contours



def classify_trash_can(features: Dict) -> str:
    rules = list(ClassificationDefine.objects.filter(active=True))

    if not rules:
        rule = ClassificationDefine.objects.create()
        rule.active = True
        rule.save()
    else :
        rule = rules[0]
        print(rule)
        
    required_keys = ["basic", "color", "texture", "shape", "zones"]
    for key in required_keys:
        if key not in features or features[key] is None:
            print(f"Caractéristique '{key}' manquante ou None. Classification par défaut : Vide.")
            return "Vide"

    mean_saturation = features["color"].get("mean_saturation", 0.0)
    area_ratio = features["shape"].get("area_ratio", 0.0)
    num_contours = features["shape"].get("num_contours", 0)
    edge_density = features["texture"].get("edge_density", 0.0)
    center_contour_density = features["shape"].get("center_contour_density", 0.0)
    zone_middle_mean_brightness = features["zones"]["middle"].get("mean_brightness", 0.0)
    contrast = features["texture"].get("contrast", 0.0)
    entropy = features["texture"].get("entropy", 0.0)
    mean_gray = features["color"].get("mean_gray", 0.0)

    # Règles fortes pour vide
    if num_contours < rule.num_contours_rule_1_vide and area_ratio < rule.area_ratio_rule_1_vide:
        print("Règle 0 satisfaite : num_contours < 35 ET area_ratio < 0.25")
        return "vide"
    if mean_gray > rule.mean_gray_rule_2_vide and edge_density < rule.edge_density_rule_2_vide:
        print("Règle 7 satisfaite : mean_gray > 140 ET edge_density < 0.05")
        return "vide"
    if area_ratio < rule.area_ratio_rule_3_vide and edge_density < rule.edge_density_rule_3_vide:
        print("Règle 8 satisfaite : area_ratio < 0.1 ET edge_density < 0.02")
        return "vide"
    if center_contour_density < rule.center_contour_density_rule_4_vide and zone_middle_mean_brightness < rule.zone_middle_mean_brightness_rule_4_vide:
        print("Règle 9 satisfaite : center_contour_density < 0.2 ET zone_middle_mean_brightness < 70")
        return "vide"

    # Règle forte pour pleine
    if mean_saturation > rule.mean_saturation_rule_1_pleine and area_ratio > rule.area_ratio_rule_1_pleine:
        print("Règle 1 satisfaite : mean_saturation > 75 ET area_ratio > 0.2")
        return "pleine"

    is_full_score = 0
    if area_ratio > rule.area_ratio_rule_2_pleine or num_contours > rule.num_contours_rule_2_pleine:
        is_full_score += 1
        print("Règle 2 satisfaite : area_ratio > 0.3 OU num_contours > 60")
    if edge_density > rule.edge_density_rule_3_pleine and mean_saturation > rule.mean_saturation_rule_3_pleine:
        is_full_score += 1
        print("Règle 3 satisfaite : edge_density > 0.05 ET mean_saturation > 75")
    if center_contour_density > rule.center_contour_density_rule_4_pleine and zone_middle_mean_brightness > rule.zone_middle_mean_brightness_rule_4_pleine:
        is_full_score += 1
        print("Règle 4 satisfaite : center_contour_density > 0.35 ET zone_middle_mean_brightness > 80")
    if contrast > rule.contrast_rule_5_pleine and entropy > rule.entropy_rule_5_pleine:
        is_full_score += 1
        print("Règle 5 satisfaite : contrast > 50 ET entropy > 7.0")

    print(f"Score final : {is_full_score}")
    return "pleine" if is_full_score >= rule.is_full_score else "vide"

def save_to_excel(results: List[Dict], output_path: str) -> None:
    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False, sheet_name="Classification")
    print(f"Résultats sauvegardés dans '{output_path}'")


def save_features_json(features: Dict, output_path: str) -> None:
    with open(output_path, 'w') as f:
        json.dump(features, f, indent=4)


def visualize_debug(img: np.ndarray, features: Dict, contours: List, filename: str) -> None:
    img_contours = img.copy()
    cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 2)
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title(f"Image avec contours: {filename}")
    plt.imshow(cv2.cvtColor(img_contours, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.title("Histogrammes")
    plt.plot(features["color"]["histogram_gray"], label="Niveaux de gris", color='gray')
    plt.plot(features["color"]["histogram_hue"], label="Teinte (HSV)", color='blue')
    plt.xlabel("Valeur")
    plt.ylabel("Nombre de pixels")
    plt.legend()
    plt.show()
    plt.figure(figsize=(15, 5))
    for i, (zone_name, zone_data) in enumerate(features["zones"].items(), 1):
        plt.subplot(1, 3, i)
        plt.title(f"Histogramme zone {zone_name}")
        plt.plot(zone_data["histogram"], color='gray')
        plt.xlabel("Valeur")
        plt.ylabel("Nombre de pixels")
    plt.tight_layout()
    plt.show()


def process_folder(folder_path: str, true_label: str, debug: bool = False) -> Tuple[List[Dict], int]:
    results = []
    correct_predictions = 0
    total_images = 0

    if not os.path.exists(folder_path):
        print(f"Le dossier {folder_path} n'existe pas.")
        return results, correct_predictions, total_images


    current_directory = os.getcwd()
    features_json_dir = f"{current_directory}/media/features"
    os.makedirs(features_json_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
            if filename == true_label : 
                image_path = os.path.join(folder_path, filename)
                print(f"\nTraitement de l'image : {filename} ({true_label})")
                try:
                    features = extract_features(image_path, debug=debug, filename=filename)
                    classification = classify_trash_can(features)
                    print(f"Classification de {filename} : {classification}")

                    results.append({
                        "Image": filename,
                        "Classification": classification,
                        "area_ratio": features["shape"]["area_ratio"],
                        "num_contours": features["shape"]["num_contours"],
                        "edge_density": features["texture"]["edge_density"],
                        "mean_saturation": features["color"]["mean_saturation"],
                        "center_contour_density": features["shape"]["center_contour_density"],
                        "zone_middle_mean_brightness": features["zones"]["middle"]["mean_brightness"],
                        "zone_bottom_mean_brightness": features["zones"]["bottom"]["mean_brightness"],
                        "contrast": features["texture"]["contrast"],
                        "entropy": features["texture"]["entropy"],
                        "percent_dark_pixels": features["color"]["percent_dark_pixels"],
                        "percent_bright_pixels": features["color"]["percent_bright_pixels"],
                        "mean_gray": features["color"]["mean_gray"]
                    })

                    features_json_path = os.path.join(features_json_dir, f"{filename}_features.json")
                    save_features_json(features, features_json_path)
                
                    if not debug:
                        try:
                            pass
                            # img, contours = get_contours_from_image(image_path)
                            # visualize_debug(img, features, contours, filename)
                        except Exception as inner_e:
                            print(f"Erreur de visualisation debug : {str(inner_e)}")

                except Exception as e:
                    print(f"Erreur lors du traitement de {filename} : {str(e)}")

    return results, total_images



def extract_features(image_path: str, debug: bool = False, filename: str = "") -> Dict:
    img = load_image(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    gray = cv2.equalizeHist(gray)

    thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh2 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)[1]

# 🔧 Correction : alignement des tailles et types
    if thresh1.shape != thresh2.shape:
        thresh2 = cv2.resize(thresh2, (thresh1.shape[1], thresh1.shape[0]))
    if thresh1.dtype != thresh2.dtype:
        thresh2 = thresh2.astype(thresh1.dtype)

    thresh = cv2.bitwise_and(thresh1, thresh2)


    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    features = {
        "basic": get_basic_features(img, image_path),
        "color": get_color_features(img),
        "texture": get_texture_features(img),
        "shape": get_shape_features(img),
        "zones": get_zone_features(img)
    }

    features = convert_numpy_types(features)
    if debug:
        visualize_debug(img, features, contours, filename)
    return features


def traitement(name):
    clean_folder ="media\\uploads"
    debug = False
    # Traitement des poubelles vides

    print("\n=== Traitement de la poubelle ===")
    print(f"{name}")
    clean_results,  clean_total = process_folder(clean_folder, name, debug)
    if clean_total > 0:
        print(f"\nRésumé pour les poubelles vides :")
        print(f"Nombre total d'images : {clean_total}")
        print(f"Results : {clean_results}")
    else:
        print("Aucune image vide trouvée.")


if __name__ == "__main__":
    traitement()
