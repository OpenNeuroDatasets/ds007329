#!/usr/bin/env python
"""Generate visual QA figures to verify defacing was applied correctly.

This script creates orthogonal slice montages for all anatomical images across
raw BIDS, fMRIPrep, and FreeSurfer directories. The figures emphasize the face
region to allow visual verification of defacing.

Examples:
    # Preview what files would be processed
    python data/code/check-defacing.py --dry-run

    # Process all subjects
    python data/code/check-defacing.py

    # Process specific subjects
    python data/code/check-defacing.py --subjects sub-sid000005 sub-sid000007

    # Force regeneration of existing figures
    python data/code/check-defacing.py --force
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from tqdm import tqdm


def find_all_anatomicals(
    bids_dir: Path, subjects: list[str] | None = None
) -> list[dict]:
    """Find all anatomical files from raw BIDS, fMRIPrep, and FreeSurfer.

    Parameters
    ----------
    bids_dir : Path
        Root BIDS directory.
    subjects : list of str, optional
        List of subjects to process. If None, process all subjects.

    Returns
    -------
    list of dict
        List of dicts with keys: path, source, subject, label
    """
    anat_files = []

    # Determine which subjects to process
    if subjects:
        subject_ids = [s for s in subjects if (bids_dir / s).exists()]
    else:
        subject_ids = sorted([d.name for d in bids_dir.glob("sub-*") if d.is_dir()])

    for subject in subject_ids:
        # 1. Raw BIDS files
        # T1w from ses-budapest
        for t1w in (bids_dir / subject).rglob("ses-budapest/anat/*_T1w.nii.gz"):
            anat_files.append({
                "path": t1w,
                "source": "raw",
                "subject": subject,
                "label": t1w.name.replace(".nii.gz", ""),
            })

        # T2w from ses-1
        for t2w in (bids_dir / subject).rglob("ses-1/anat/*_T2w.nii.gz"):
            anat_files.append({
                "path": t2w,
                "source": "raw",
                "subject": subject,
                "label": t2w.name.replace(".nii.gz", ""),
            })

        # 2. fMRIPrep files
        fmriprep_dir = bids_dir / "derivatives" / "fmriprep" / subject

        # T1w preproc from ses-budapest
        for t1w in fmriprep_dir.rglob("ses-budapest/anat/*_desc-preproc_T1w.nii.gz"):
            anat_files.append({
                "path": t1w,
                "source": "fmriprep",
                "subject": subject,
                "label": t1w.name.replace(".nii.gz", ""),
            })

        # T2w preproc from ses-1
        for t2w in fmriprep_dir.rglob("ses-1/anat/*_desc-preproc_T2w.nii.gz"):
            anat_files.append({
                "path": t2w,
                "source": "fmriprep",
                "subject": subject,
                "label": t2w.name.replace(".nii.gz", ""),
            })

        # 3. FreeSurfer files
        fs_mri_dir = bids_dir / "derivatives" / "freesurfer" / subject / "mri"
        if fs_mri_dir.exists():
            # orig/001.mgz - original input
            orig_001 = fs_mri_dir / "orig" / "001.mgz"
            if orig_001.exists():
                anat_files.append({
                    "path": orig_001,
                    "source": "freesurfer",
                    "subject": subject,
                    "label": f"{subject}_freesurfer_orig-001",
                })

            # T1.mgz - processed T1
            t1_mgz = fs_mri_dir / "T1.mgz"
            if t1_mgz.exists():
                anat_files.append({
                    "path": t1_mgz,
                    "source": "freesurfer",
                    "subject": subject,
                    "label": f"{subject}_freesurfer_T1",
                })

            # T2.mgz - processed T2 (if exists)
            t2_mgz = fs_mri_dir / "T2.mgz"
            if t2_mgz.exists():
                anat_files.append({
                    "path": t2_mgz,
                    "source": "freesurfer",
                    "subject": subject,
                    "label": f"{subject}_freesurfer_T2",
                })

            # nu.mgz - bias-corrected
            nu_mgz = fs_mri_dir / "nu.mgz"
            if nu_mgz.exists():
                anat_files.append({
                    "path": nu_mgz,
                    "source": "freesurfer",
                    "subject": subject,
                    "label": f"{subject}_freesurfer_nu",
                })

            # brain.mgz - skull-stripped (should be safe, include for completeness)
            brain_mgz = fs_mri_dir / "brain.mgz"
            if brain_mgz.exists():
                anat_files.append({
                    "path": brain_mgz,
                    "source": "freesurfer",
                    "subject": subject,
                    "label": f"{subject}_freesurfer_brain",
                })

    return anat_files


def create_defacing_check_figure(
    filepath: Path, output_path: Path, title: str
) -> None:
    """Create orthogonal slice montage emphasizing face region.

    Layout (15 slices total):
    - Row 1: 5 sagittal slices around midline (most important for face)
    - Row 2: 5 coronal slices in anterior region
    - Row 3: 5 axial slices in inferior region

    Parameters
    ----------
    filepath : Path
        Path to the anatomical image (NIfTI or MGZ).
    output_path : Path
        Output PNG path.
    title : str
        Title for the figure.
    """
    # Load image (nibabel handles both NIfTI and MGZ)
    img = nib.load(filepath)
    data = img.get_fdata()

    # Get dimensions
    nx, ny, nz = data.shape[:3]

    # Calculate intensity scaling (0 to 99th percentile of non-zero voxels)
    nonzero_data = data[data > 0]
    if len(nonzero_data) > 0:
        vmax = np.percentile(nonzero_data, 99)
    else:
        vmax = data.max() if data.max() > 0 else 1
    vmin = 0

    # Define slice positions
    # Sagittal: 40%, 45%, 50%, 55%, 60% of x-dimension (captures both sides of face)
    sag_positions = [int(nx * p) for p in [0.40, 0.45, 0.50, 0.55, 0.60]]

    # Coronal: 60%, 65%, 70%, 75%, 80% of y-dimension (anterior face region)
    cor_positions = [int(ny * p) for p in [0.60, 0.65, 0.70, 0.75, 0.80]]

    # Axial: 15%, 25%, 35%, 45%, 55% of z-dimension (inferior head to mid-brain)
    ax_positions = [int(nz * p) for p in [0.15, 0.25, 0.35, 0.45, 0.55]]

    # Create figure (3 rows x 5 columns)
    fig, axes = plt.subplots(3, 5, figsize=(15, 10))

    # Row 1: Sagittal slices
    for i, x_pos in enumerate(sag_positions):
        x_pos = min(x_pos, nx - 1)  # Ensure within bounds
        slice_data = np.rot90(data[x_pos, :, :])
        axes[0, i].imshow(slice_data, cmap="gray", vmin=vmin, vmax=vmax)
        axes[0, i].set_title(f"Sag x={x_pos}", fontsize=9)
        axes[0, i].axis("off")

    # Row 2: Coronal slices
    for i, y_pos in enumerate(cor_positions):
        y_pos = min(y_pos, ny - 1)  # Ensure within bounds
        slice_data = np.rot90(data[:, y_pos, :])
        axes[1, i].imshow(slice_data, cmap="gray", vmin=vmin, vmax=vmax)
        axes[1, i].set_title(f"Cor y={y_pos}", fontsize=9)
        axes[1, i].axis("off")

    # Row 3: Axial slices
    for i, z_pos in enumerate(ax_positions):
        z_pos = min(z_pos, nz - 1)  # Ensure within bounds
        slice_data = np.rot90(data[:, :, z_pos])
        axes[2, i].imshow(slice_data, cmap="gray", vmin=vmin, vmax=vmax)
        axes[2, i].set_title(f"Ax z={z_pos}", fontsize=9)
        axes[2, i].axis("off")

    # Add main title
    fig.suptitle(title, fontsize=12, fontweight="bold", y=0.98)

    # Add row labels
    fig.text(0.02, 0.78, "Sagittal\n(face profile)", fontsize=10, va="center", ha="left")
    fig.text(0.02, 0.50, "Coronal\n(anterior)", fontsize=10, va="center", ha="left")
    fig.text(0.02, 0.22, "Axial\n(inferior)", fontsize=10, va="center", ha="left")

    plt.tight_layout(rect=[0.06, 0, 1, 0.96])

    # Save figure
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def get_output_filename(anat_info: dict) -> str:
    """Generate output filename for an anatomical file.

    Parameters
    ----------
    anat_info : dict
        Dictionary with keys: path, source, subject, label

    Returns
    -------
    str
        Output filename (without directory).
    """
    source = anat_info["source"]
    label = anat_info["label"]

    if source == "raw":
        # Use original filename
        return f"{label}_defacing-check.png"
    elif source == "fmriprep":
        # Prefix with fmriprep
        return f"{anat_info['subject']}_fmriprep_{label.replace(anat_info['subject'] + '_', '')}_defacing-check.png"
    else:  # freesurfer
        # Label already includes subject and source info
        return f"{label}_defacing-check.png"


def process_subject(
    subject: str,
    anat_files: list[dict],
    output_dir: Path,
    force: bool = False,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Process all anatomical files for one subject.

    Parameters
    ----------
    subject : str
        Subject ID.
    anat_files : list of dict
        List of anatomical file info dicts for this subject.
    output_dir : Path
        Base output directory.
    force : bool
        If True, regenerate existing figures.
    dry_run : bool
        If True, only preview actions.

    Returns
    -------
    tuple of int
        (processed count, skipped count)
    """
    subject_output_dir = output_dir / subject
    processed = 0
    skipped = 0

    for anat_info in anat_files:
        output_filename = get_output_filename(anat_info)
        output_path = subject_output_dir / output_filename

        # Check if output already exists
        if output_path.exists() and not force:
            if dry_run:
                print(f"    SKIP (exists): {output_filename}")
            skipped += 1
            continue

        if dry_run:
            print(f"    Would create: {output_filename}")
            print(f"      Source: {anat_info['source']}")
            print(f"      Input: {anat_info['path']}")
            processed += 1
            continue

        # Generate figure
        try:
            title = f"{anat_info['label']}\n({anat_info['source']})"
            create_defacing_check_figure(anat_info["path"], output_path, title)
            processed += 1
        except Exception as e:
            print(f"    ERROR processing {anat_info['path'].name}: {e}")
            skipped += 1

    return processed, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Generate visual QA figures to verify defacing was applied correctly.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--subjects",
        nargs="+",
        help="Subjects to process (e.g., sub-sid000005). Default: all subjects.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate existing figures.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without generating figures.",
    )
    args = parser.parse_args()

    # Determine BIDS directory (script is in data/code/)
    script_dir = Path(__file__).resolve().parent
    bids_dir = script_dir.parent

    # Output directory
    output_dir = bids_dir / "derivatives" / "qa" / "anat-defaced-check"

    print(f"BIDS directory: {bids_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Force: {args.force}")
    print(f"Dry run: {args.dry_run}")

    # Find all anatomical files
    print("\nSearching for anatomical files...")
    anat_files = find_all_anatomicals(bids_dir, args.subjects)

    if not anat_files:
        print("\nNo anatomical files found to process.")
        return

    # Group files by subject
    subjects = sorted(set(f["subject"] for f in anat_files))
    files_by_subject = {
        sub: [f for f in anat_files if f["subject"] == sub] for sub in subjects
    }

    # Print summary
    print(f"\nFound {len(anat_files)} anatomical files across {len(subjects)} subjects:")
    for sub in subjects:
        sub_files = files_by_subject[sub]
        raw_count = sum(1 for f in sub_files if f["source"] == "raw")
        fmriprep_count = sum(1 for f in sub_files if f["source"] == "fmriprep")
        fs_count = sum(1 for f in sub_files if f["source"] == "freesurfer")
        print(f"  {sub}: {raw_count} raw, {fmriprep_count} fMRIPrep, {fs_count} FreeSurfer")

    # Process each subject
    total_processed = 0
    total_skipped = 0

    if args.dry_run:
        print("\n--- DRY RUN ---")
        for subject in subjects:
            print(f"\n{subject}:")
            processed, skipped = process_subject(
                subject,
                files_by_subject[subject],
                output_dir,
                args.force,
                dry_run=True,
            )
            total_processed += processed
            total_skipped += skipped
    else:
        for subject in tqdm(subjects, desc="Processing subjects"):
            processed, skipped = process_subject(
                subject,
                files_by_subject[subject],
                output_dir,
                args.force,
                dry_run=False,
            )
            total_processed += processed
            total_skipped += skipped

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Summary: {total_processed} generated, {total_skipped} skipped")
    if args.dry_run:
        print("(Dry run - no figures created)")
    else:
        print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
