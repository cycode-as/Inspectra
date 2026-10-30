
from pathlib import Path
from collections import defaultdict
from predict import predict

BASE = Path(__file__).resolve().parent

folders = {
    "NORMAL": BASE / "datasets/metal_nut/test/good",
    "SCRATCH": BASE / "datasets/metal_nut/test/scratch",
    "BENT": BASE / "datasets/metal_nut/test/bent",
    "COLOR": BASE / "datasets/metal_nut/test/color",
    "FLIP": BASE / "datasets/metal_nut/test/flip",
}

print("\nINSPECTRA - FULL DATASET EVALUATION")
print("=" * 50)

summary = defaultdict(lambda: {
    "total": 0,
    "pass": 0,
    "review": 0,
    "reject": 0
})

for category, folder in folders.items():

    images = sorted(folder.glob("*.png"))

    print(f"\nTesting {category}: {len(images)} images")

    for image in images:
        result = predict(image)

        status = result["status"]

        summary[category]["total"] += 1
        summary[category][status.lower()] += 1

        print(
            f"{image.name}: "
            f"{result['anomaly_score']:.4f} | {status}"
        )

print("\n" + "=" * 50)
print("FINAL SUMMARY")
print("=" * 50)

for category, data in summary.items():
    print(
        f"{category:10} | "
        f"Total: {data['total']:3} | "
        f"PASS: {data['pass']:3} | "
        f"REVIEW: {data['review']:3} | "
        f"REJECT: {data['reject']:3}"
    )

print("\nEvaluation completed.")
