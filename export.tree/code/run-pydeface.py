#!/usr/bin/env python
"""Run pydeface on all T1w and T2w anatomical volumes.

This script deffaces anatomical images using pydeface, archives the original
files to sourcedata/pre-deface/, and generates before/after comparison plots.

Examples:
    # Preview actions without executing
    python data/code/run-pydeface.py --dry-run

    # Process all subjects
    python data/code/run-pydeface.py

    # Process specific subjects
    python data/code/run-pydeface.py --subjects sub-sid000005 sub-sid000007
"""

import argparse
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np


def find_anatomical_files(
    bids_dir: Path, subjects: list[str] | None = None
) -> list[Path]:
    """Find all T1w and T2w NIfTI files in BIDS directory.

    Parameters
    ----------
    bids_dir : Path
        Root BIDS directory.
    subjects : list of str, optional
        List of subjects to process. If None, process all subjects.

    Returns
    -------
    list of Path
        List of anatomical NIfTI file paths.
    """
    anat_files = []

    if subjects:
        subject_dirs = [bids_dir / sub for sub in subjects if (bids_dir / sub).exists()]
    else:
        subject_dirs = sorted(bids_dir.glob("sub-*"))

    for subject_dir in subject_dirs:
        if not subject_dir.is_dir():
            continue
        # Find T1w and T2w files (excluding defaced, masks, and derivatives)
        for anat_file in subject_dir.rglob("anat/*_T1w.nii.gz"):
            if "_defaced" not in anat_file.name and "_pydeface" not in anat_file.name:
                anat_files.append(anat_file)
        for anat_file in subject_dir.rglob("anat/*_T2w.nii.gz"):
            if "_defaced" not in anat_file.name and "_pydeface" not in anat_file.name:
                anat_files.append(anat_file)

    return sorted(anat_files)


def get_defaced_path(anat_file: Path) -> Path:
    """Get path for defaced output file.

    Parameters
    ----------
    anat_file : Path
        Original anatomical file path.

    Returns
    -------
    Path
        Path with _defaced suffix before .nii.gz extension.
    """
    stem = anat_file.name.replace(".nii.gz", "")
    return anat_file.parent / f"{stem}_defaced.nii.gz"


def get_sourcedata_path(anat_file: Path, bids_dir: Path) -> Path:
    """Get sourcedata archive path for original file.

    Parameters
    ----------
    anat_file : Path
        Original anatomical file path.
    bids_dir : Path
        Root BIDS directory.

    Returns
    -------
    Path
        Path in sourcedata/pre-deface/ mirroring original structure.
    """
    # Get relative path from BIDS root (e.g., sub-sid000005/ses-1/anat/file.nii.gz)
    rel_path = anat_file.relative_to(bids_dir)
    return bids_dir / "sourcedata" / "pre-deface" / rel_path


def get_figure_path(anat_file: Path, bids_dir: Path) -> Path:
    """Get path for comparison figure.

    Parameters
    ----------
    anat_file : Path
        Original anatomical file path.
    bids_dir : Path
        Root BIDS directory.

    Returns
    -------
    Path
        Path for PNG comparison figure.
    """
    stem = anat_file.name.replace(".nii.gz", "")
    figures_dir = bids_dir / "sourcedata" / "pre-deface" / "figures"
    return figures_dir / f"{stem}_defacing-comparison.png"


def run_pydeface(input_file: Path, output_file: Path, dry_run: bool = False) -> bool:
    """Run pydeface on an anatomical image.

    Parameters
    ----------
    input_file : Path
        Input NIfTI file.
    output_file : Path
        Output defaced NIfTI file.
    dry_run : bool
        If True, only print the command without executing.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    cmd = ["pydeface", str(input_file), "--outfile", str(output_file)]

    if dry_run:
        print(f"    Would run: {' '.join(cmd)}")
        return True

    print("    Running pydeface...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"    ERROR: pydeface failed: {result.stderr}")
        return False

    return True


def create_comparison_plot(
    original_file: Path, defaced_file: Path, output_path: Path, dry_run: bool = False
) -> None:
    """Create side-by-side sagittal comparison plot.

    Parameters
    ----------
    original_file : Path
        Original (pre-deface) NIfTI file.
    defaced_file : Path
        Defaced NIfTI file.
    output_path : Path
        Output PNG path.
    dry_run : bool
        If True, only print action without executing.
    """
    if dry_run:
        print(f"    Would create comparison plot: {output_path.name}")
        return

    # Load images
    orig_img = nib.load(original_file)
    deface_img = nib.load(defaced_file)

    orig_data = orig_img.get_fdata()
    deface_data = deface_img.get_fdata()

    # Get mid-sagittal slice (x dimension)
    mid_x = orig_data.shape[0] // 2
    orig_slice = np.rot90(orig_data[mid_x, :, :])
    deface_slice = np.rot90(deface_data[mid_x, :, :])

    # Calculate common intensity range
    vmin = 0
    vmax = np.percentile(orig_data[orig_data > 0], 99)

    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(10, 6))

    axes[0].imshow(orig_slice, cmap="gray", vmin=vmin, vmax=vmax)
    axes[0].set_title("Before (Original)", fontsize=12)
    axes[0].axis("off")

    axes[1].imshow(deface_slice, cmap="gray", vmin=vmin, vmax=vmax)
    axes[1].set_title("After (Defaced)", fontsize=12)
    axes[1].axis("off")

    # Add suptitle with filename info
    stem = defaced_file.name.replace(".nii.gz", "")
    fig.suptitle(stem, fontsize=14, fontweight="bold")

    plt.tight_layout()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"    Saved comparison plot: {output_path.name}")


def cleanup_pydeface_artifacts(anat_file: Path, dry_run: bool = False) -> None:
    """Remove pydeface intermediate files.

    Parameters
    ----------
    anat_file : Path
        Original anatomical file path.
    dry_run : bool
        If True, only print actions without executing.
    """
    stem = anat_file.name.replace(".nii.gz", "")
    artifacts = [
        anat_file.parent / f"{stem}_pydeface_mask.nii.gz",
        anat_file.parent / f"{stem}_pydeface.mat",
    ]

    for artifact in artifacts:
        if artifact.exists():
            if dry_run:
                print(f"    Would remove: {artifact.name}")
            else:
                artifact.unlink()
                print(f"    Removed: {artifact.name}")


def process_file(anat_file: Path, bids_dir: Path, dry_run: bool = False) -> bool:
    """Process a single anatomical file.

    Parameters
    ----------
    anat_file : Path
        Anatomical NIfTI file to process.
    bids_dir : Path
        Root BIDS directory.
    dry_run : bool
        If True, only print actions without executing.

    Returns
    -------
    bool
        True if processed successfully, False if skipped or failed.
    """
    defaced_path = get_defaced_path(anat_file)
    sourcedata_path = get_sourcedata_path(anat_file, bids_dir)
    figure_path = get_figure_path(anat_file, bids_dir)

    print(f"\n  Processing: {anat_file.name}")

    # Check if already processed (original archived to sourcedata)
    if sourcedata_path.exists():
        print("    SKIP: Already processed (found in sourcedata)")
        return False

    # Check if defaced version already exists (mid-processing state)
    if defaced_path.exists():
        print(f"    WARNING: Defaced already exists, skipping: {defaced_path.name}")
        return False

    # Step 1: Run pydeface
    if not run_pydeface(anat_file, defaced_path, dry_run):
        return False

    # Step 2: Archive original to sourcedata
    if dry_run:
        print(f"    Would archive original to: {sourcedata_path}")
    else:
        sourcedata_path.parent.mkdir(parents=True, exist_ok=True)
        # Copy with follow_symlinks=True to resolve datalad/git-annex links
        shutil.copy2(anat_file, sourcedata_path, follow_symlinks=True)
        print("    Archived original to: sourcedata/pre-deface/...")

    # Step 3: Generate comparison plot (before removing original)
    create_comparison_plot(anat_file, defaced_path, figure_path, dry_run)

    # Step 4: Remove original and rename defaced
    if dry_run:
        print(f"    Would remove original: {anat_file.name}")
        print(f"    Would rename defaced to: {anat_file.name}")
    else:
        anat_file.unlink()
        defaced_path.rename(anat_file)
        print("    Replaced original with defaced version")

    # Step 5: Cleanup pydeface artifacts
    cleanup_pydeface_artifacts(anat_file, dry_run)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Run pydeface on T1w and T2w anatomical volumes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--subjects",
        nargs="+",
        help="Subjects to process (e.g., sub-sid000005). Default: all subjects.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without executing.",
    )
    args = parser.parse_args()

    # Determine BIDS directory (script is in data/code/)
    script_dir = Path(__file__).resolve().parent
    bids_dir = script_dir.parent

    print(f"BIDS directory: {bids_dir}")
    print(f"Dry run: {args.dry_run}")

    # Find anatomical files
    anat_files = find_anatomical_files(bids_dir, args.subjects)

    if not anat_files:
        print("\nNo anatomical files found to process.")
        return

    print(f"\nFound {len(anat_files)} anatomical file(s) to process:")
    for f in anat_files:
        print(f"  - {f.relative_to(bids_dir)}")

    # Process each file
    processed = 0
    skipped = 0

    for anat_file in anat_files:
        if process_file(anat_file, bids_dir, args.dry_run):
            processed += 1
        else:
            skipped += 1

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Summary: {processed} processed, {skipped} skipped")
    if args.dry_run:
        print("(Dry run - no changes made)")


if __name__ == "__main__":
    main()
