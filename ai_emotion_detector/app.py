import cv2
import time
import random
import mediapipe as mp
from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

camera = cv2.VideoCapture(0)
base_options = python.BaseOptions(model_asset_path="face_landmarker.task")

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1,
    output_face_blendshapes=True
)

landmarker = vision.FaceLandmarker.create_from_options(options)

score_history = deque(maxlen = 10)

countdown = 3
countdown_start = time.time()

game_state = "menu"
go_start = None
play_duration = 7

final_score = 0
current_score = 0

target_emotion = random.choice(["HAPPY", "SAD", "DISGUSTED", "ANGRY", "SURPRISED"])

high_scores = {
    "HAPPY": 0,
    "SAD": 0,
    "DISGUSTED": 0,
    "ANGRY": 0,
    "SURPRISED": 0
}

disregard_round = False


def get_features(blendshapes):
    features = {}

    for category in blendshapes:
        features[category.category_name] = category.score

    return features


def happy(features):
    raw = (features["mouthSmileRight"] + features["mouthSmileLeft"]) / 2

    if raw <= 0.01:
        score = raw / 0.01 * 10

    elif raw <= 0.10:
        score = (10 + (raw - 0.01) / (0.10 - 0.01) * 15)

    elif raw <= 0.70:
        score = (25 + (raw - 0.10) / (0.70 - 0.10) * 40)

    elif raw <= 0.80:
        score = (65 + (raw - 0.70) / (0.80 - 0.70) * 15)

    elif raw <= 0.85:
        score = (80 + (raw - 0.80) / (0.85 - 0.80) * 12)

    elif raw <= 1.00:
        score = (90 + (raw - 0.85) / (1.00 - 0.85) * 8)
    
    else:
        score = 100

    return min(score, 100) / 100


def sad(features):
    eye_squint = (features["eyeSquintLeft"] + features["eyeSquintRight"]) / 2

    mouth_stretch = (features["mouthStretchLeft"] + features["mouthStretchRight"]) / 2

    brow_down = (features["browDownLeft"] + features["browDownRight"]) / 2

    if eye_squint <= 0.30:
        eye_score = 0

    elif eye_squint <= 0.60:
        eye_score = ((eye_squint - 0.30) / (0.60 - 0.30)) * 70

    elif eye_squint <= 0.75:
        eye_score = (70 + (eye_squint - 0.60) / (0.75 - 0.60) * 30)

    else:
        eye_score = 100


    if mouth_stretch <= 0.005:
        mouth_score = 0

    elif mouth_stretch <= 0.15:
        mouth_score = ((mouth_stretch - 0.005) / (0.15 - 0.005)) * 80

    elif mouth_stretch <= 0.30:
        mouth_score = (80 + (mouth_stretch - 0.15) / (0.30 - 0.15) * 20)

    else:
        mouth_score = 100


    if brow_down <= 0.02:
        brow_score = 0

    elif brow_down <= 0.15:
        brow_score = ((brow_down - 0.02) / (0.15 - 0.02)) * 70

    elif brow_down <= 0.30:
        brow_score = (70 + (brow_down - 0.15) / (0.30 - 0.15) * 30)

    else:
        brow_score = 100


    score = (eye_score * 0.50 + mouth_score * 0.30 + brow_score * 0.20)

    return min(score, 100) / 100


def disgusted(features):
    upper_lip = (features["mouthUpperUpLeft"] + features["mouthUpperUpRight"]) / 2

    brow_down = (features["browDownLeft"] + features["browDownRight"]) / 2

    if upper_lip <= 0.05:
        upper_score = 0

    elif upper_lip <= 0.33:
        upper_score = ((upper_lip - 0.05) / (0.33 - 0.05) * 60)

    elif upper_lip <= 0.36:
        upper_score = (60 + (upper_lip - 0.33) / (0.36 - 0.33) * 10)

    elif upper_lip <= 0.55:
        upper_score = (70 + (upper_lip - 0.36) / (0.55 - 0.36) * 30)

    else:
        upper_score = 100


    if brow_down <= 0.15:
        brow_score = 0

    elif brow_down <= 0.33:
        brow_score = ((brow_down - 0.15) / (0.33 - 0.15) * 60)

    elif brow_down <= 0.38:
        brow_score = (60 + (brow_down - 0.33) / (0.38 - 0.33) * 10)

    elif brow_down <= 0.55:
        brow_score = (70 + (brow_down - 0.38) / (0.55 - 0.38) * 30)

    else:
        brow_score = 100


    score = ((upper_score * 0.50) + (brow_score * 0.50))

    return min(score, 100) / 100


def angry(features):
    brow_down = (features["browDownLeft"] + features["browDownRight"]) / 2

    mouth_stretch = (features["mouthStretchLeft"] + features["mouthStretchRight"]) / 2

    if brow_down <= 0.12:
        brow_score = 0

    elif brow_down <= 0.18:
        brow_score = ((brow_down - 0.12) / (0.18 - 0.12)) * 50

    elif brow_down <= 0.25:
        brow_score = (50 + (brow_down - 0.18) / (0.25 - 0.18) * 30)

    elif brow_down <= 0.30:
        brow_score = (80 + (brow_down - 0.25) / (0.30 - 0.25) * 20)

    else:
        brow_score = 100


    if mouth_stretch <= 0.005:
        stretch_penalty = 0

    elif mouth_stretch <= 0.05:
        stretch_penalty = ((mouth_stretch - 0.005) / (0.05 - 0.005)) * 30

    elif mouth_stretch <= 0.15:
        stretch_penalty = (30 + (mouth_stretch - 0.05) / (0.15 - 0.05) * 50)

    else:
        stretch_penalty = 80

    score = brow_score - stretch_penalty

    return max(0, min(score, 100)) / 100


def surprised(features):
    jaw_open = features["jawOpen"]

    brow_outer_up = (features["browOuterUpLeft"] + features["browOuterUpRight"]) / 2

    mouth_lower_down = (features["mouthLowerDownLeft"] + features["mouthLowerDownRight"]) / 2

    eye_wide = (features["eyeWideLeft"] + features["eyeWideRight"]) / 2

    if jaw_open <= 0.02:
        jaw_score = 0

    elif jaw_open <= 0.10:
        jaw_score = ((jaw_open - 0.02) / (0.10 - 0.02) * 30)

    elif jaw_open <= 0.20:
        jaw_score = (30 + (jaw_open - 0.10) / (0.20 - 0.10) * 25)

    elif jaw_open <= 0.30:
        jaw_score = (55 + (jaw_open - 0.20) / (0.30 - 0.20) * 25)

    elif jaw_open <= 0.40:
        jaw_score = (80 + (jaw_open - 0.30) / (0.40 - 0.30) * 20)

    else:
        jaw_score = 100


    if brow_outer_up <= 0.05:
        brow_score = 0

    elif brow_outer_up <= 0.30:
        brow_score = ((brow_outer_up - 0.05) / (0.30 - 0.05) * 65)

    elif brow_outer_up <= 0.45:
        brow_score = (65 + (brow_outer_up - 0.30) / (0.45 - 0.30) * 35)

    else:
        brow_score = 100


    if mouth_lower_down <= 0.03:
        mouth_score = 0

    elif mouth_lower_down <= 0.15:
        mouth_score = ((mouth_lower_down - 0.03) / (0.15 - 0.03) * 50)

    elif mouth_lower_down <= 0.40:
        mouth_score = (50 + (mouth_lower_down - 0.15) / (0.40 - 0.15) * 35)

    else:
        mouth_score = 85 + min((mouth_lower_down - 0.40) / 0.40 * 15, 15)


    if eye_wide <= 0.02:
        eye_score = 0

    elif eye_wide <= 0.15:
        eye_score = ((eye_wide - 0.02) / (0.15 - 0.02) * 65)

    elif eye_wide <= 0.30:
        eye_score = (65 + (eye_wide - 0.15) / (0.30 - 0.15) * 35)

    else:
        eye_score = 100

    score = ((jaw_score * 0.40) + (brow_score * 0.10) + (mouth_score * 0.45) + (eye_score * 0.05))

    return min(score, 100) / 100

    
while True:
    success, frame = camera.read()

    if not success:
        print("Could not access camera.")
        break

    elapsed = time.time() - countdown_start

    if elapsed >= 3 and game_state == "countdown":
        game_state = "playing"
        go_start = time.time()

    if game_state == "playing" and time.time() - go_start >= play_duration:
        game_state = "finished"
        final_score = current_score

        if not disregard_round:
            if final_score > high_scores[target_emotion]:
                high_scores[target_emotion] = final_score
                
    if game_state == "playing" and time.time() - go_start < 0.8:
        cv2.putText(
            frame,
            "GO!",
            (300,250),
            cv2.FONT_HERSHEY_SIMPLEX,
            3,
            (255,255,255),
            6
        )

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = landmarker.detect(mp_image)

    if result.face_blendshapes and game_state == "playing":
        features = get_features(result.face_blendshapes[0])

        if target_emotion == "HAPPY":
            current_score = happy(features)

        elif target_emotion == "SAD":
            current_score = sad(features)

        elif target_emotion == "DISGUSTED":
            current_score = disgusted(features)

        elif target_emotion == "ANGRY":
            current_score = angry(features)

        elif target_emotion == "SURPRISED":
            current_score = surprised(features)
            
        score_history.append(current_score)

        current_score = sum(score_history) / len(score_history)

        cv2.putText(
            frame,
            f"{target_emotion}: {round(current_score * 100)}%",
            (30,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2
        )

    if game_state == "menu":
        cv2.putText(
            frame,
            "EMOTION MIRROR",
            (170,100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255,255,255),
            3
        )

        cv2.putText(
            frame,
            "S - Start",
            (250,200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            "H - High Scores",
            (190,260),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2
        )

    if game_state == "high_scores":
        cv2.putText(
            frame,
            "HIGH SCORES",
            (210,100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255,255,255),
            3
        )

        cv2.putText(
            frame,
            f"HAPPY: {round(high_scores['HAPPY'] * 100)}%",
            (220,170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            f"SAD: {round(high_scores['SAD'] * 100)}%",
            (220,210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            f"DISGUSTED: {round(high_scores['DISGUSTED'] * 100)}%",
            (220,250),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            f"ANGRY: {round(high_scores['ANGRY'] * 100)}%",
            (220,290),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            f"SURPRISED: {round(high_scores['SURPRISED'] * 100)}%",
            (220,330),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            "B - Back to Menu",
            (190,400),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

    if game_state == "countdown":
        countdown = 3 - int(elapsed)

        cv2.putText(
            frame,
            f"SHOW: {target_emotion}",
            (30,50),
            cv2.FONT_HERSHEY_COMPLEX,
            1,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            str(countdown),
            (300,250),
            cv2.FONT_HERSHEY_SIMPLEX,
            4,
            (255,255,255),
            6
        )

    if game_state == "finished":
        cv2.putText(
            frame,
            "FINAL SCORE",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            f"{round(final_score * 100)}%",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255,255,255),
            3
        )

    if disregard_round:
        cv2.putText(
            frame,
            "ROUND DISREGARDED",
            (30,150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

    cv2.imshow("Emotion Mirror", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == ord("Q"):
        break

    if key == ord(" "):
        game_state = "countdown"
        countdown_start = time.time()
        score_history.clear()
        target_emotion = random.choice(["HAPPY", "SAD", "DISGUSTED", "ANGRY", "SURPRISED"])
        disregard_round = False

    if key == ord("p") or key == ord("P"):
        print("\n--- P PRESSED ---")

        if result.face_blendshapes:
            features = get_features(result.face_blendshapes[0])

            print("--- ALL FEATURES ---")
            for name, value in sorted(
                features.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"{name}: {value:.4f}")
        else:
            print("No face detected.")

    if key == ord("d") or key == ord("D"):
        disregard_round = True

    if game_state == "menu":

        if key == ord("s") or key == ord("S"):
            game_state = "countdown"
            countdown_start = time.time()
            score_history.clear()
            target_emotion = random.choice(["HAPPY", "SAD", "ANGRY", "DISGUSTED", "SURPRISED"])
            disregard_round = False

        elif key == ord("h") or key == ord("H"):
            game_state = "high_scores"


    if key == ord("b") or key == ord("B"):
        game_state = "menu"


camera.release()
cv2.destroyAllWindows()