"""
Burn‑scar assessment from multi‑temporal satellite imagery.

This script:
1. Reads 2014 (pre‑fire) and 2015 (post‑fire) GeoTIFFs in
   benchmark/datasets/BurnScar/.
2. Computes the Normalized Burn Ratio (NBR) for each image.
3. Calculates the differenced NBR (dNBR = NBR_pre − NBR_post).
4. Extracts burn‑scar polygons from dNBR using a severity threshold.
5. Saves:
      • A PNG map with dNBR backdrop + burn polygons
        → pred_results/burn_scar_analysis.png
      • (If GeoPandas available) the polygons as a GeoPackage
        → pred_results/burn_scar_polygons.gpkg
"""

import os
import numpy as np
import rasterio
from rasterio import features
from rasterio.plot import show
import matplotlib.pyplot as plt

try:
    import geopandas as gpd
    from shapely.geometry import shape
except ImportError:  # geopandas might be unavailable; fall back to shapely only
    gpd = None
    from shapely.geometry import shape


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def pick_bands(count):
    """Return (nir_idx, swir2_idx) using 1‑based indexing for rasterio."""
    if count >= 7:                  # Landsat‑8 style
        return 5, 7
    if count >= 12:                 # Sentinel‑2 style
        return 8, 12
    if count == 1:                  # already NBR
        return None, None
    return count - 1, count         # fallback


def compute_nbr(ds):
    """
    Compute NBR = (NIR − SWIR2) / (NIR + SWIR2).
    If ds has a single band, assume it is already NBR.
    """
    if ds.count == 1:
        arr = ds.read(1).astype("float32")
        mask = ds.read_masks(1) == 0
        arr[mask] = np.nan
        return arr

    nir_idx, swir_idx = pick_bands(ds.count)
    if nir_idx is None:
        raise ValueError("Cannot infer NBR bands.")

    nir  = ds.read(nir_idx).astype("float32")
    swir = ds.read(swir_idx).astype("float32")

    mask = (ds.read_masks(nir_idx) == 0) | (ds.read_masks(swir_idx) == 0)
    nir[mask]  = np.nan
    swir[mask] = np.nan

    denom = nir + swir
    nbr = np.where(np.abs(denom) < 1e-6, np.nan, (nir - swir) / denom)
    return nbr


def extract_burn_polygons(dnbr, transform, threshold=0.27, min_pixels=20):
    """Return list of Shapely polygons where dNBR > threshold."""
    burn = dnbr > threshold
    burn = np.nan_to_num(burn).astype(np.uint8)

    polys = []
    for geom, val in features.shapes(burn, mask=burn, transform=transform):
        if val == 1:
            poly = shape(geom)
            if poly.is_valid and poly.area >= min_pixels:
                polys.append(poly)
    return polys


def save_plot(dnbr, polygons, out_png, transform):
    """Plot dNBR with burn polygons and save PNG."""
    plt.figure(figsize=(10, 8))
    show(
        dnbr,
        transform=transform,
        cmap="RdYlGn_r",
        vmin=-1,
        vmax=1,
        title="Burn‑scar analysis (dNBR)",
    )
    for poly in polygons:
        x, y = poly.exterior.xy
        plt.plot(x, y, color="black", linewidth=0.8)
    plt.axis("off")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main():
    data_dir = os.path.join("benchmark", "datasets", "BurnScar")
    pre_raster = os.path.join(data_dir, "G_2014.tif")
    post_raster = os.path.join(data_dir, "G_2015.tif")

    out_dir  = "pred_results"
    out_png  = os.path.join(out_dir, "burn_scar_analysis.png")
    out_gpkg = os.path.join(out_dir, "burn_scar_polygons.gpkg")

    # Ensure output directory exists BEFORE any write attempts
    os.makedirs(out_dir, exist_ok=True)

    with rasterio.open(pre_raster) as pre_ds, rasterio.open(post_raster) as post_ds:
        if pre_ds.transform != post_ds.transform or pre_ds.shape != post_ds.shape:
            raise ValueError("Input rasters are not aligned.")

        nbr_pre  = compute_nbr(pre_ds)
        nbr_post = compute_nbr(post_ds)
        dnbr = nbr_pre - nbr_post

        polygons = extract_burn_polygons(
            dnbr, transform=pre_ds.transform, threshold=0.27, min_pixels=20
        )

        # Export polygons if GeoPandas available
        if gpd is not None and polygons:
            gdf = gpd.GeoDataFrame(
                {"dnbr_thresh": [0.27] * len(polygons)}, geometry=polygons, crs=pre_ds.crs
            )
            gdf.to_file(out_gpkg, driver="GPKG")

        save_plot(dnbr, polygons, out_png, transform=pre_ds.transform)

    print(f"PNG saved  : {out_png}")
    if gpd is not None and polygons:
        print(f"Polygons saved: {out_gpkg}")


if __name__ == "__main__":
    main()
