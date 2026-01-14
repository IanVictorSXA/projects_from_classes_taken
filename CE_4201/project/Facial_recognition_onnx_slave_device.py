# Author: Yongming Mai (MYM929)
# This scripts waits for the command from Master device. It expects 2 types of message: "register" and "recogntion"
# Register will make it add a new person to database
# Recogntion will make it do the facial recognition

import paho.mqtt.client as mqtt
import ssl
import threading
import time
import os
import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp
from picamera2 import Picamera2
from collections import deque

# ==================================================
# AWS IoT Config
# ==================================================
AWS_ENDPOINT = "a3ot19o41mukgz-ats.iot.us-east-1.amazonaws.com"
CA_PATH = "certs/rootCA.pem"
CERT_PATH = "certs/device.pem.crt"
KEY_PATH = "certs/private.pem.key"
SUB_TOPIC = "raspi/face_recog/send_from_master"  # master → Pi
PUB_TOPIC = "raspi/face_recog/send_from_slave"   # Pi → master

# ==================================================
# MQTT Setup
# ==================================================
def on_connect(client, userdata, flags, reason_code, properties):
    print("✅ Connected to AWS IoT Core with result code:", reason_code)
    client.subscribe(SUB_TOPIC)
    print(f"📡 Subscribed to topic: {SUB_TOPIC}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip().lower()
    print(f"\n📥 Message received:")
    print(f"   Topic: {msg.topic}")
    print(f"   Payload: {payload}")

    if payload == "register":
        print("🪪 Switching to register mode...")
        threading.Thread(target=run_register_mode, daemon=True).start()
    elif payload == "recognition":
        print("🔍 Switching to recognition mode...")
        threading.Thread(target=run_recognition_mode, daemon=True).start()
    else:
        print("⚠️ Unknown command, ignoring.")


client = mqtt.Client(
    client_id="1",
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(
    ca_certs=CA_PATH,
    certfile=CERT_PATH,
    keyfile=KEY_PATH,
    tls_version=ssl.PROTOCOL_TLSv1_2
)

try:
    print("🔌 Connecting to AWS IoT Core...")
    client.connect(AWS_ENDPOINT, 8883, 60)
    client.loop_start()
    print("🚀 Connection initiated, waiting for messages...")
except Exception as e:
    print(f"❌ Connection failed: {e}")


def register_publish(name):
    try:
        client.publish(PUB_TOPIC, name)
        print(f"📡 Published '{name}' to topic '{PUB_TOPIC}'")
    except Exception as e:
        print(f"⚠️ Failed to publish name: {e}")


def recognition_publish(name):
    try:
        result = client.publish(PUB_TOPIC, name)
        print(result.rc)
        print(f"📡 Published '{name}' to topic '{PUB_TOPIC}'")
    except Exception as e:
        print(f"⚠️ Failed to publish name: {e}")


# ==================================================
# Face Recognition Setup
# ==================================================
MODEL_PATH = "model/arcface.onnx"
EMB_DIR = "embeddings"
THRESHOLD = 0.50
DETECT_MIN_CONF = 0.70
REG_MAX_SAMPLES = 30
SMOOTH_WINDOW = 5
MARGIN = 0.15
SAVE_DEBUG_FRAMES = False

os.makedirs(EMB_DIR, exist_ok=True)
if SAVE_DEBUG_FRAMES:
    os.makedirs("frames", exist_ok=True)
    os.makedirs("crops", exist_ok=True)

ARC_TEMPLATE = np.array([
    [38.2946, 51.6963],
    [73.5318, 51.5014],
    [56.0252, 71.7366],
    [41.5493, 92.3655],
    [70.7299, 92.2041]
], dtype=np.float32)

print("🧠 Loading ArcFace model...")
session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
print("✅ Model loaded")


def preprocess(img_bgr):
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (112, 112), interpolation=cv2.INTER_LINEAR)
    img = img.astype(np.float32) / 255.0
    img = (img - 0.5) / 0.5
    img = np.transpose(img, (2, 0, 1))
    return np.expand_dims(img, 0)


def l2_normalize(x, eps=1e-9):
    n = np.linalg.norm(x)
    return x / (n if n > eps else eps)


def get_embedding(face_img_bgr):
    x = preprocess(face_img_bgr)
    emb = session.run(None, {input_name: x})[0][0]
    return l2_normalize(emb.astype(np.float32))


def cosine_sim(a, b):
    return float(np.dot(a, b))


def save_embedding(name, embedding):
    path = os.path.join(EMB_DIR, f"{name}.npy")
    np.save(path, embedding)
    print(f"💾 Saved embedding: {path}")


def load_database():
    db = {}
    for f in os.listdir(EMB_DIR):
        if f.endswith(".npy"):
            name = f[:-4]
            db[name] = np.load(os.path.join(EMB_DIR, f))
    return db


def find_best_match(embedding, db):
    best_name, best_sim = None, -1.0
    for name, emb in db.items():
        sim = cosine_sim(embedding, emb)
        if sim > best_sim:
            best_name, best_sim = name, sim
    return best_name, best_sim


def expand_bbox(x1, y1, x2, y2, w_img, h_img, margin=MARGIN):
    w = x2 - x1
    h = y2 - y1
    dx = int(w * margin)
    dy = int(h * margin)
    return max(0, x1 - dx), max(0, y1 - dy), min(w_img, x2 + dx), min(h_img, y2 + dy)


# ==================================================
# Face Alignment / Detection
# ==================================================
FM_LEFT_EYE = (33, 133)
FM_RIGHT_EYE = (263, 362)
FM_NOSE = 1
FM_MOUTH_L = 61
FM_MOUTH_R = 291


def landmarks_to_5pts(landmarks, w, h):
    def avg_pts(idx_pair):
        i, j = idx_pair
        xi, yi = landmarks[i].x * w, landmarks[i].y * h
        xj, yj = landmarks[j].x * w, landmarks[j].y * h
        return np.array([(xi + xj) / 2, (yi + yj) / 2], dtype=np.float32)

    p_left_eye = avg_pts(FM_LEFT_EYE)
    p_right_eye = avg_pts(FM_RIGHT_EYE)
    p_nose = np.array([landmarks[FM_NOSE].x * w, landmarks[FM_NOSE].y * h], np.float32)
    p_mouth_l = np.array([landmarks[FM_MOUTH_L].x * w, landmarks[FM_MOUTH_L].y * h], np.float32)
    p_mouth_r = np.array([landmarks[FM_MOUTH_R].x * w, landmarks[FM_MOUTH_R].y * h], np.float32)
    return np.vstack([p_left_eye, p_right_eye, p_nose, p_mouth_l, p_mouth_r])


def align_face(frame_bgr, five_points):
    src, dst = five_points.astype(np.float32), ARC_TEMPLATE
    M, _ = cv2.estimateAffinePartial2D(src, dst, method=cv2.LMEDS)
    if M is None:
        M = cv2.getAffineTransform(src[:3], dst[:3])
    return cv2.warpAffine(frame_bgr, M, (112, 112), flags=cv2.INTER_LINEAR)


mp_face_det = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
detector = mp_face_det.FaceDetection(model_selection=0, min_detection_confidence=DETECT_MIN_CONF)
mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ==================================================
# Camera Setup
# ==================================================
cam = Picamera2()
config = cam.create_video_configuration(main={"size": (640, 480)}, controls={"FrameRate": 30})
cam.configure(config)
cam.start()
time.sleep(1)
print("📸 Camera ready")


def lock_auto_controls():
    try:
        cam.set_controls({"AeEnable": False, "AwbEnable": False})
    except Exception:
        pass


def detect_faces_and_landmarks(frame_bgr):
    h, w, _ = frame_bgr.shape
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    dets = detector.process(frame_rgb).detections
    results = []
    if not dets:
        return results
    mesh_res = mesh.process(frame_rgb)
    mesh_faces = mesh_res.multi_face_landmarks if mesh_res and mesh_res.multi_face_landmarks else []
    centers = []
    for f in mesh_faces:
        xs = [lm.x for lm in f.landmark]
        ys = [lm.y for lm in f.landmark]
        centers.append((np.mean(xs) * w, np.mean(ys) * h))
    for det in dets:
        score = float(det.score[0]) if det.score else 0.0
        if score < DETECT_MIN_CONF:
            continue
        rb = det.location_data.relative_bounding_box
        x1, y1 = int(rb.xmin * w), int(rb.ymin * h)
        x2, y2 = int((rb.xmin + rb.width) * w), int((rb.ymin + rb.height) * h)
        x1, y1, x2, y2 = expand_bbox(x1, y1, x2, y2, w, h, MARGIN)
        five_pts = None
        if centers:
            cxb, cyb = (x1 + x2) / 2, (y1 + y2) / 2
            idx = int(np.argmin([(cx - cxb) ** 2 + (cy - cyb) ** 2 for (cx, cy) in centers]))
            try:
                five_pts = landmarks_to_5pts(mesh_faces[idx].landmark, w, h)
            except Exception:
                five_pts = None
        results.append({"bbox": (x1, y1, x2, y2), "score": score, "five": five_pts})
    return results


# ==================================================
# Register Mode
# ==================================================
def register_mode():
    name = input("Enter name to register: ").strip()
    print(f"📷 Waiting for face to start registration for {name}...")

    while True:
        frame = cam.capture_array()
        faces = detect_faces_and_landmarks(frame)
        if not faces:
            print("❌ No face detected.")
            time.sleep(0.25)
            continue
        print("🧍 Face detected — locking exposure and capturing 30 samples.")
        lock_auto_controls()
        break

    samples = []
    while len(samples) < REG_MAX_SAMPLES:
        frame = cam.capture_array()
        faces = detect_faces_and_landmarks(frame)
        if not faces:
            print(f"⚠️ Lost face... waiting ({len(samples)}/{REG_MAX_SAMPLES})")
            time.sleep(0.2)
            continue
        best = faces[0]
        x1, y1, x2, y2 = best["bbox"]
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        aligned = align_face(frame, best["five"]) if best["five"] is not None else cv2.resize(crop, (112, 112))
        emb = get_embedding(aligned)
        samples.append(emb)
        print(f"✅ Captured sample {len(samples)}/{REG_MAX_SAMPLES}")

    mean_emb = l2_normalize(np.mean(samples, axis=0))
    save_embedding(name, mean_emb)
    print(f"✅ Registered {name} successfully with 30 samples.")
    register_publish(name)


# ==================================================
# Recognition Mode
# ==================================================
def recognition_mode():
    print("🔍 Starting recognition... Press Ctrl+C to quit.")
    prev_time = time.time()
    emb_smooth = deque(maxlen=SMOOTH_WINDOW)
    recent_labels = deque(maxlen=10)
    exposure_locked = False
    db = load_database()

    if not db:
        print("ℹ️ No registered faces found in embeddings folder.")

    while True:
        frame = cam.capture_array()
        faces = detect_faces_and_landmarks(frame)
        curr = time.time()
        fps = 1.0 / (curr - prev_time)
        prev_time = curr

        if not faces:
            print("❌ No face detected.")
            time.sleep(0.25)
            continue

        if not exposure_locked:
            lock_auto_controls()
            exposure_locked = True

        best = faces[0]
        x1, y1, x2, y2 = best["bbox"]
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        aligned = align_face(frame, best["five"]) if best["five"] is not None else cv2.resize(crop, (112, 112))
        emb = get_embedding(aligned)
        emb_smooth.append(emb)
        emb_use = l2_normalize(np.mean(emb_smooth, axis=0)) if len(emb_smooth) > 1 else emb

        label, score = "Unknown", 0.0
        if db:
            name, sim = find_best_match(emb_use, db)
            score = sim
            if sim >= THRESHOLD:
                label = name

        recent_labels.append(label)
        if len(recent_labels) == 10:
            final_label = max(set(recent_labels), key=recent_labels.count)
            if final_label == "Unknown":
                print(f"🧍 FINAL: Unknown (majority of last 10)")
            else:
                print(f"🧍 FINAL: {final_label} ✅ (majority of last 10)")

            recognition_publish(final_label)
            return

        print(f"Frame: {label} — cos={score:.3f} — FPS={fps:.1f}")


# ==================================================
# Thread Wrappers
# ==================================================
def run_register_mode():
    register_mode()
    print("✅ Register mode finished.")
    print("🕓 Waiting for master command...")


def run_recognition_mode():
    recognition_mode()
    print("✅ Recognition mode finished.")
    print("🕓 Waiting for master command...")


# ==================================================
# Main Loop
# ==================================================
if __name__ == "__main__":
    print("🕓 Waiting for master command...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
        cam.stop()
        client.loop_stop()
        client.disconnect()
