#!/usr/bin/env python3
"""
Compute a PCA‑based UMAP embedding for the Heart Cell Atlas (HCA) subsampled
dataset, after filtering out lowly expressed genes, and save the plot coloured
by cell type.

Output
------
A PNG image is saved to
    pred_results/hca_cell_type_pca.png
"""

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

# Scanpy provides convenient single‑cell utilities built on AnnData
import scanpy as sc


def main():
    # ---------------------------------------------------------------------
    # 1. Load the data
    # ---------------------------------------------------------------------
    data_path = Path("benchmark/datasets/hca/hca_subsampled_20k.h5ad")
    if not data_path.exists():
        sys.exit(f"Dataset not found at {data_path.absolute()}")

    adata = sc.read_h5ad(data_path)

    # ---------------------------------------------------------------------
    # 2. Filter out lowly expressed genes
    #    (genes detected in fewer than 3 cells are removed)
    # ---------------------------------------------------------------------
    sc.pp.filter_genes(adata, min_cells=3)

    # ---------------------------------------------------------------------
    # 3. Basic normalisation & log‑transform
    # ---------------------------------------------------------------------
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # (Optional) keep only highly variable genes for speed/clarity
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat", subset=True)

    # ---------------------------------------------------------------------
    # 4. Scale, PCA (30 components), neighbours & UMAP
    # ---------------------------------------------------------------------
    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=30, svd_solver="arpack")
    sc.pp.neighbors(adata, n_pcs=30, n_neighbors=15)
    sc.tl.umap(adata)

    # ---------------------------------------------------------------------
    # 5. Determine which obs column contains the cell‑type annotation
    # ---------------------------------------------------------------------
    preferred_keys = [
        "cell_type",
        "celltype",
        "cell_ontology_class",
        "cell_type_ontology_term_id",
        "cellType",
        "CellType",
    ]
    cell_type_key = None
    for key in preferred_keys:
        if key in adata.obs:
            cell_type_key = key
            break
    # Fallback: first categorical / string column
    if cell_type_key is None:
        for key in adata.obs.columns:
            if adata.obs[key].dtype.name == "category" or adata.obs[key].dtype == object:
                cell_type_key = key
                break
    # Final fallback: just use the first obs column
    if cell_type_key is None:
        cell_type_key = adata.obs.columns[0]

    # ---------------------------------------------------------------------
    # 6. Plot & save
    # ---------------------------------------------------------------------
    out_dir = Path("pred_results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "hca_cell_type_pca.png"

    # Generate a matplotlib figure without displaying to screen
    sc.pl.umap(
        adata,
        color=cell_type_key,
        title=f"HCA UMAP coloured by '{cell_type_key}'",
        show=False,
        frameon=False,
    )
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()

    print(f"UMAP figure successfully saved to: {out_file.resolve()}")


if __name__ == "__main__":
    main()
