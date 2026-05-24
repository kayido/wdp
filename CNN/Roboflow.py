API_KEY = "kjYCVDfZoAW9R5uV54Qj"
MODEL_1 = "garbage_detection-wvzwv/9"       # déchets au sol
MODEL_2 = "garbage-can-overflow/1"          # état poubelle


DIRTY_CLASSES  = {"close_full", "open_full", "trash flow", "overflowing", "broken"}

CLEAN_CLASSES  = {"empty", "healthy"}

import sys, json, base64, requests

def call_api(image_b64: str, model_id: str) -> list:
    url = (
        f"https://serverless.roboflow.com/{model_id}"
        f"?api_key={API_KEY}&confidence=20&overlap=30"
    )
    r = requests.post(url, data=image_b64,
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
    return r.json().get("predictions", []) if r.ok else []


def predict(image_path: str) -> dict:
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    preds_m1 = call_api(img_b64, MODEL_1)
    preds_m2 = call_api(img_b64, MODEL_2)

    # Score modèle 1 (déchets au sol) 
    score_m1 = max((p["confidence"] for p in preds_m1), default=0.0)

    # Score modele 2 (état poubelle) 
    score_m2 = 0.0
    for p in preds_m2:
        cls  = p["class"].lower()
        conf = p["confidence"]
        if any(d in cls for d in DIRTY_CLASSES):
            score_m2 = max(score_m2, conf)          # dirty → score plein
        elif any(c in cls for c in CLEAN_CLASSES):
            score_m2 = max(score_m2, conf * 0.05)   # clean → quasi 0

    # Score final 
    score = round(max(score_m1, score_m2), 3)
    label = "dirty" if score >= 0.5 else "clean"

    return {
        "label"          : label,
        "score"          : score,
        "alert"          : score >= 0.7,
        "n_detections"   : len(preds_m1) + len(preds_m2),
        "score_sol"      : round(score_m1, 3),
        "score_poubelle" : round(score_m2, 3),
        "details"        : (
            [{"model": "sol",      "class": p["class"], "confidence": round(p["confidence"], 2)} for p in preds_m1] +
            [{"model": "poubelle", "class": p["class"], "confidence": round(p["confidence"], 2)} for p in preds_m2]
        ),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage : python Roboflow.py "chemin/image.jpg"')
        sys.exit(1)
    result = predict(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))