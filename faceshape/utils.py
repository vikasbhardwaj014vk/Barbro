"""
Core face-shape detection logic for Barbro
Compatible with modern MediaPipe (Tasks API)
"""

import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Optional, Dict, List, Tuple, Any


def analyze_face(
    image_path: str,
    gender: str = "unisex",
    use_llm: bool = True,
    extra: dict = None
) -> dict:
    """
    Main function – detects face shape and optionally gets LLM recommendations.
    """
    result = get_landmarks(image_path)

    # ---------- No face detected ----------
    if result is None:
        return {
            "shape": None,
            "ratios": {},
            "recommendations": [],
            "tip": "",
            "gender": gender,
            "error": "No face detected. Please upload a clear, front-facing photo with good lighting.",
            "llm": None,
        }

    # ---------- Face detected ----------
    points, _ = result
    ratios = calculate_ratios(points)         
    shape = classify_face_shape(ratios)

    response = {
        "shape": shape,
        "ratios": {k: round(v, 3) for k, v in ratios.items() if isinstance(v, (int, float))},
        "gender": gender,
        "error": None,
        "llm": None,
    }

    # ---------- LLM recommendations ----------
    if use_llm:
        try:
            from .llm_recommender import get_llm_recommendations
            llm_data = get_llm_recommendations(
                face_shape=shape,
                gender=gender,
                extra=extra or {}
            )
            response["llm"] = llm_data
            response["recommendations"] = [item["name"] for item in llm_data.get("best_haircuts", [])]
            response["tip"] = llm_data.get("pro_tip", "")
        except Exception as e:
            # Fallback to static recommendations if LLM fails
            recs = RECOMMENDATIONS.get(shape, {})
            response["recommendations"] = recs.get(gender, recs.get("men", []))
            response["tip"] = recs.get("tip", "")
            response["llm_error"] = str(e)
    else:
        # Static recommendations (no LLM)
        # recs = RECOMMENDATIONS.get(shape, {})
        # if gender == "men":
        #     response["recommendations"] = recs.get("men", [])
        # elif gender == "women":
        #     response["recommendations"] = recs.get("women", [])
        # else:
        #     response["recommendations"] = list(dict.fromkeys(
        #         recs.get("men", []) + recs.get("women", [])
        #     ))
        # response["tip"] = recs.get("tip", "")
        print("LLM recommendations are not working")
    return response


# ────────────────────────────────────────────────
# Model path (download once)
# ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "face_landmarker.task")


def download_model_if_needed():
    """Download the Face Landmarker model if it doesn't exist."""
    if os.path.exists(MODEL_PATH):
        return

    print("Downloading MediaPipe Face Landmarker model...")
    import urllib.request
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Model downloaded successfully!")


# Download model on first import
download_model_if_needed()


# ────────────────────────────────────────────────
# Landmark indices (same as before)
# ────────────────────────────────────────────────
LANDMARKS = {
    "forehead_top": 10,
    "chin": 152,
    "left_cheek": 234,
    "right_cheek": 454,
    "left_jaw": 172,
    "right_jaw": 397,
    "left_forehead": 103,
    "right_forehead": 332,
}


def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return float(np.linalg.norm(np.array(p1) - np.array(p2)))


def get_landmarks(image_path: str) -> Optional[Tuple[List[Tuple[float, float]], Tuple[int, int]]]:
    """
    Detect face using MediaPipe Face Landmarker (Tasks API)
    Returns list of (x, y) pixel coordinates + image size
    """
    image = cv2.imread(image_path)
    if image is None:
        return None

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]

    # Create FaceLandmarker
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    detector = vision.FaceLandmarker.create_from_options(options)

    # Convert to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    # Detect
    detection_result = detector.detect(mp_image)

    if not detection_result.face_landmarks:
        return None

    # Get first face landmarks
    face_landmarks = detection_result.face_landmarks[0]
    points = [(lm.x * w, lm.y * h) for lm in face_landmarks]

    return points, (w, h)


def calculate_ratios(points: List[Tuple[float, float]]) -> Dict[str, float]:
    forehead_top = points[LANDMARKS["forehead_top"]]
    chin = points[LANDMARKS["chin"]]
    left_cheek = points[LANDMARKS["left_cheek"]]
    right_cheek = points[LANDMARKS["right_cheek"]]
    left_jaw = points[LANDMARKS["left_jaw"]]
    right_jaw = points[LANDMARKS["right_jaw"]]
    left_forehead = points[LANDMARKS["left_forehead"]]
    right_forehead = points[LANDMARKS["right_forehead"]]

    face_length = _distance(forehead_top, chin)
    face_width = _distance(left_cheek, right_cheek)
    jaw_width = _distance(left_jaw, right_jaw)
    forehead_width = _distance(left_forehead, right_forehead)

    if face_width < 1e-5:
        face_width = 1.0

    return {
        "face_length": face_length,
        "face_width": face_width,
        "jaw_width": jaw_width,
        "forehead_width": forehead_width,
        "length_width_ratio": face_length / face_width,
        "jaw_cheek_ratio": jaw_width / face_width,
        "forehead_cheek_ratio": forehead_width / face_width,
    }


def classify_face_shape(ratios: Dict[str, float]) -> str:
    lw = ratios["length_width_ratio"]
    jc = ratios["jaw_cheek_ratio"]
    fc = ratios["forehead_cheek_ratio"]

    if lw > 1.55:
        return "Oblong"
    if lw < 1.28 and jc > 0.90:
        return "Square"
    if lw < 1.28:
        return "Round"
    if fc > jc + 0.07:
        return "Heart"
    if jc < 0.80 and fc < 0.85:
        return "Diamond"
    return "Oval"


RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {"Oval": {
        "men": ["llm not working", "llm not working", "llm not working", "llm not working", "llm not working"],
        "women": ["llm not working", "llm not working", "llm not working", "llm not working", "llm not working"],
        "tip": "llm not working",
    }},
    

# {
#     "Oval": {
#         "men": ["Classic side part", "Textured crop", "Pompadour", "Quiff", "Medium length with soft layers"],
#         "women": ["Long layers", "Blunt bob", "Curtain bangs", "Soft waves", "Pixie cut"],
#         "tip": "Most versatile shape — almost any style works. Focus on balance.",
#     },
#     "Round": {
#         "men": ["High fade with volume on top", "Angular fringe / textured quiff", "Side-swept undercut", "Short sides + height on top"],
#         "women": ["Long layers past the chin", "Side part", "High ponytail / volume at crown", "Angular or asymmetric bob"],
#         "tip": "Add vertical length and angles. Avoid chin-length blunt cuts that widen the face.",
#     },
#     "Square": {
#         "men": ["Soft textured top", "Side part with movement", "Medium length with texture", "Beard styling to soften the jaw"],
#         "women": ["Soft layers around the jaw", "Side-swept bangs", "Waves / curls at jaw level", "Lob with texture"],
#         "tip": "Soften the strong angular jaw with curves and movement.",
#     },
#     "Heart": {
#         "men": ["Side part", "Textured fringe", "Medium length", "Avoid extreme height on top"],
#         "women": ["Chin-length bob", "Side-swept bangs", "Soft waves at the jaw", "Layered lob"],
#         "tip": "Add visual weight at the jaw/chin area and soften the forehead.",
#     },
#     "Diamond": {
#         "men": ["Side part", "Textured crop with soft fringe", "Avoid extreme height", "Medium length with width at sides"],
#         "women": ["Side-swept bangs", "Chin-length styles", "Soft layers at cheekbones", "Waves for width at jaw"],
#         "tip": "Balance the wide cheekbones — volume at the jaw and a soft fringe help.",
#     },
#     "Oblong": {
#         "men": ["Side part with horizontal width", "Textured sides / French crop", "Avoid tall volume on top", "Medium length with side volume"],
#         "women": ["Chin-length bob or lob", "Side-swept bangs", "Soft waves for width", "Layers that add horizontal volume"],
#         "tip": "Add horizontal width and break the long vertical line. Avoid extra height.",
#     },
# }




