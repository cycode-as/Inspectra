
from pathlib import Path

from anomalib.data import MVTecAD
from anomalib.models import Patchcore
from anomalib.engine import Engine


def main():
    print("=" * 55)
    print("INSPECTRA - METAL NUT ANOMALY DETECTION")
    print("=" * 55)

    # Dataset configuration
    datamodule = MVTecAD(
        root="./datasets",
        category="metal_nut",
        train_batch_size=4,
        eval_batch_size=4,
        num_workers=0,
    )

    # PatchCore model
    model = Patchcore(
        backbone="wide_resnet50_2",
        layers=["layer2", "layer3"],
        pre_trained=True,
        coreset_sampling_ratio=0.1,
        num_neighbors=9,
        precision="float32",
    )

    # CPU training engine
    engine = Engine(
        default_root_dir="results",
        max_epochs=1,
        accelerator="cpu",
        devices=1,
    )

    print("\nStarting PatchCore training...")
    print("Training uses normal images from train/good.")
    print("Please wait; CPU training may take some time.\n")

    engine.fit(
        model=model,
        datamodule=datamodule,
    )

    print("\nTraining completed!")

    # Display checkpoint location
    checkpoint_callback = engine.trainer.checkpoint_callback

    if checkpoint_callback is not None:
        checkpoint_path = checkpoint_callback.best_model_path

        if checkpoint_path:
            print("\nModel checkpoint saved at:")
            print(checkpoint_path)
        else:
            print("\nTraining finished, but no checkpoint path was reported.")

    print("\nINSPECTRA model training stage finished.")


if __name__ == "__main__":
    main()
