import os
import base64
import cv2
import numpy as np
from video_utils import extract_frames, merge_3d_frames

# Vertex AI integration (optional, env-driven)
VERTEX_ENABLED = os.getenv('VERTEX_ENABLED', 'false').lower() == 'true'
VERTEX_PROJECT_ID = os.getenv('VERTEX_PROJECT_ID')
VERTEX_LOCATION = os.getenv('VERTEX_LOCATION')  # e.g., us-central1, europe-west4
VERTEX_ENDPOINT_ID = os.getenv('VERTEX_ENDPOINT_ID')  # numeric id
VERTEX_ENDPOINT = os.getenv('VERTEX_ENDPOINT')  # full resource name optional


def _get_vertex_endpoint_resource() -> str:
    if VERTEX_ENDPOINT:
        return VERTEX_ENDPOINT
    if VERTEX_PROJECT_ID and VERTEX_LOCATION and VERTEX_ENDPOINT_ID:
        return f"projects/{VERTEX_PROJECT_ID}/locations/{VERTEX_LOCATION}/endpoints/{VERTEX_ENDPOINT_ID}"
    return ''


def _vertex_predict_frame(frame: np.ndarray) -> np.ndarray:
    """
    Send a single frame to Vertex AI Endpoint and expect an image-like prediction back.
    This function assumes the deployed model accepts base64-encoded PNG via instances=[{"content": "..."}]
    and returns a base64-encoded image in predictions[0].
    """
    endpoint_res = _get_vertex_endpoint_resource()
    if not endpoint_res:
        return frame
    try:
        # Encode frame to PNG bytes
        ok, buf = cv2.imencode('.png', frame)
        if not ok:
            return frame
        image_bytes = buf.tobytes()
        b64 = base64.b64encode(image_bytes).decode('utf-8')

        # Lazy import to avoid requiring package when not enabled
        from google.cloud.aiplatform.gapic import PredictionServiceClient

        client = PredictionServiceClient()
        instances = [{"content": b64}]
        parameters = {}
        response = client.predict(endpoint=endpoint_res, instances=instances, parameters=parameters)
        preds = getattr(response, 'predictions', None)
        if not preds:
            return frame
        # Try multiple common keys
        pred0 = preds[0]
        if isinstance(pred0, dict):
            for key in ("content", "image", "output", "data"):
                val = pred0.get(key)
                if isinstance(val, str):
                    try:
                        out_bytes = base64.b64decode(val)
                        out_arr = np.frombuffer(out_bytes, dtype=np.uint8)
                        out_img = cv2.imdecode(out_arr, cv2.IMREAD_COLOR)
                        if out_img is not None:
                            return out_img
                    except Exception:
                        pass
        # If prediction is a plain string
        if isinstance(pred0, str):
            try:
                out_bytes = base64.b64decode(pred0)
                out_arr = np.frombuffer(out_bytes, dtype=np.uint8)
                out_img = cv2.imdecode(out_arr, cv2.IMREAD_COLOR)
                if out_img is not None:
                    return out_img
            except Exception:
                pass
    except Exception as e:
        print(f"Vertex prediction failed: {e}")
    return frame


def convert_frame_2d_to_3d(frame: np.ndarray) -> np.ndarray:
    """
    2D→3D conversion.
    - If Vertex AI is enabled and configured, call the endpoint per frame.
    - Otherwise return the original frame (placeholder).
    """
    if VERTEX_ENABLED:
        return _vertex_predict_frame(frame)
    return frame


def process_video(video_path: str) -> str:
    frames = extract_frames(video_path, fps=24)
    frames_3d = [convert_frame_2d_to_3d(f) for f in frames]

    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    output_path = os.path.join(static_dir, 'output.mp4')

    merge_3d_frames(frames_3d, output_path=output_path)

    bucket = os.getenv('GCS_BUCKET_NAME', '')
    if bucket:
        try:
            from google.cloud import storage
            client = storage.Client()
            blob_name = 'outputs/output.mp4'
            bucket_obj = client.bucket(bucket)
            blob = bucket_obj.blob(blob_name)
            blob.upload_from_filename(output_path, content_type='video/mp4')
            if os.getenv('MAKE_PUBLIC', 'false').lower() == 'true':
                blob.make_public()
                return f'https://storage.googleapis.com/{bucket}/{blob_name}'
            else:
                url = blob.generate_signed_url(expiration=3600)
                return url
        except Exception as e:
            print(f'GCS upload failed: {e}')
    return '/static/output.mp4'