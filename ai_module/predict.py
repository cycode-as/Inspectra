from pathlib import Path
from time import perf_counter
from uuid import uuid4

import numpy as np
import torch
from anomalib.data import PredictDataset
from anomalib.engine import Engine
from anomalib.models import Patchcore
from anomalib.visualization import visualize_anomaly_map


# Project paths
BASE_DIR = Path(__file__).resolve().parent
CHECKPOINT = (
    BASE_DIR
    / "results"
    / "Patchcore"
    / "MVTecAD"
    / "metal_nut"
    / "v0"
    / "weights"
    / "lightning"
    / "model.ckpt"
)

HEATMAP_DIR = BASE_DIR / "results" / "heatmaps"

# Load the model only once
_MODEL = None
_ENGINE = None


def load_model():
    global _MODEL, _ENGINE

    if _MODEL is None:
        if not CHECKPOINT.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found: {CHECKPOINT}"
            )

        print("Loading INSPECTRA PatchCore model...")

        _MODEL = Patchcore.load_from_checkpoint(
            str(CHECKPOINT),
            map_location="cpu",
        )

        _MODEL.eval()

        _ENGINE = Engine(
            accelerator="cpu",
            devices=1,
        )

        print("Model loaded successfully.")

    return _MODEL, _ENGINE


def to_number(value):
    if isinstance(value, torch.Tensor):
        return float(value.detach().cpu().item())

    return float(value)


def predict(image_path):
    """
    Analyze one metal-nut image.

    Returns:
        anomaly_score
        status
        heatmap_path
        inference_time_ms
    """

    image_path = Path(image_path).resolve()

    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    start_time = perf_counter()

    model, engine = load_model()

    dataset = PredictDataset(
        path=str(image_path),
        image_size=(256, 256),
    )

    predictions = engine.predict(
        model=model,
        dataset=dataset,
        return_predictions=True,
    )

    if not predictions:
        raise RuntimeError("The model did not return predictions.")
    prediction = predictions[0]
        
    

    # Extract prediction values
    score = to_number(prediction.pred_score)
    label = to_number(prediction.pred_label)

    anomaly_map = prediction.anomaly_map

    if isinstance(anomaly_map, torch.Tensor):
        anomaly_map = anomaly_map.detach().cpu().numpy()

    anomaly_map = np.squeeze(anomaly_map)

    if anomaly_map.ndim != 2:
        raise ValueError(
            f"Unexpected anomaly map shape: {anomaly_map.shape}"
        )

    # Save a uniquely named heatmap for every request
    HEATMAP_DIR.mkdir(parents=True, exist_ok=True)

    heatmap_path = HEATMAP_DIR / f"{uuid4().hex}.png"

    heatmap_image = visualize_anomaly_map(
        anomaly_map,
        normalize=True,
        colormap=True,
    )

    heatmap_image.save(heatmap_path)

    # Use the model's predicted label
    if score >= 0.55:
    	status = "REJECT"
    elif score >= 0.45:
    	status = "REVIEW"
    else:
    	status = "PASS"

    inference_time = (perf_counter() - start_time) * 1000

    return {
        "anomaly_score": score,
        "status": status,
        "heatmap_path": str(heatmap_path),
        "inference_time_ms": round(inference_time, 2),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            'Usage: python predict.py "path_to_image"'
        )
        sys.exit(1)

    try:
        result = predict(sys.argv[1])

        print("\nINSPECTRA PREDICTION RESULT")
        print("-" * 40)

        for key, value in result.items():
            print(f"{key}: {value}")

    except Exception as error:
        print(f"\nPrediction failed: {error}")
        raise
