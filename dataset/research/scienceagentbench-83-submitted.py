"""
Urban Heat‑Island Analysis with Kriging Interpolation

The script:
1. Loads point temperature measurements and census block polygons.
2. Performs Ordinary Kriging to interpolate temperatures over the whole city.
3. Aggregates the interpolated temperatures to an average value for each census
   block group.
4. Creates a choropleth map of the average temperature per block group and
   highlights neighbourhoods with a high proportion of residents aged 65+.
5. Saves the result to  pred_results/interpolated_urban_heat.png
"""

import os
import warnings

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Point

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
DATA_DIR = "benchmark/datasets/UrbanHeat"
TEMP_FILE = os.path.join(DATA_DIR, "Temperature.geojson")
BLOCK_FILE = os.path.join(DATA_DIR, "block.geojson")
OUTPUT_DIR = "pred_results"
OUTPUT_FIG = os.path.join(OUTPUT_DIR, "interpolated_urban_heat.png")

# Grid resolution (number of cells in x and y directions for Kriging)
GRID_NX, GRID_NY = 200, 200  # adjust if memory issues occur

# ---------------------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------------------
def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------------------
print("Loading datasets...")
temp_gdf = gpd.read_file(TEMP_FILE)
block_gdf = gpd.read_file(BLOCK_FILE)

# Harmonise CRS (if not already identical)
if temp_gdf.crs != block_gdf.crs:
    temp_gdf = temp_gdf.to_crs(block_gdf.crs)

# Extract numpy arrays for Kriging
x = temp_gdf.geometry.x.values
y = temp_gdf.geometry.y.values
z = temp_gdf["TemperatureF"].values

# ---------------------------------------------------------------------------
# 2. KRIGING INTERPOLATION
# ---------------------------------------------------------------------------
print("Performing Kriging interpolation (this may take a minute)...")
try:
    from pykrige.ok import OrdinaryKriging
except ImportError as e:
    raise ImportError(
        "pykrige is required for Kriging interpolation but is not installed "
        "in this environment.") from e

# Prepare grid covering the entire study area
minx, miny, maxx, maxy = block_gdf.total_bounds
grid_x = np.linspace(minx, maxx, GRID_NX)
grid_y = np.linspace(miny, maxy, GRID_NY)

# Run Ordinary Kriging
with warnings.catch_warnings():
    warnings.simplefilter("ignore")  # silence sill/range optimization warnings
    ok = OrdinaryKriging(
        x,
        y,
        z,
        variogram_model="linear",
        verbose=False,
        enable_plotting=False,
    )
    z_pred, _ = ok.execute("grid", grid_x, grid_y)

# ---------------------------------------------------------------------------
# 3. CONVERT GRID TO POINTS & AGGREGATE BY CENSUS BLOCK
# ---------------------------------------------------------------------------
print("Aggregating interpolated surface to census block groups...")
# Build GeoDataFrame from grid
xx, yy = np.meshgrid(grid_x, grid_y)
flat_coords = np.column_stack([xx.ravel(), yy.ravel()])
flat_z = z_pred.ravel()

grid_points_gdf = gpd.GeoDataFrame(
    {"temp_pred": flat_z},
    geometry=[Point(xy) for xy in flat_coords],
    crs=block_gdf.crs,
)

# Spatial join points -> blocks
joined = gpd.sjoin(grid_points_gdf, block_gdf[["OBJECTID", "geometry"]], predicate="within", how="left")

# Compute mean predicted temperature per block
mean_temp_per_block = (
    joined.dropna(subset=["OBJECTID"])
    .groupby("OBJECTID")["temp_pred"]
    .mean()
    .rename("MeanTempF")
)

# Attach to block_gdf
block_gdf = block_gdf.merge(mean_temp_per_block, on="OBJECTID", how="left")

# ---------------------------------------------------------------------------
# 4. VISUALISATION
# ---------------------------------------------------------------------------
print("Creating choropleth map...")
ensure_dir(OUTPUT_DIR)

fig, ax = plt.subplots(figsize=(10, 10))

# Plot mean temperature
block_gdf.plot(
    column="MeanTempF",
    cmap="inferno",
    linewidth=0.3,
    edgecolor="black",
    legend=True,
    legend_kwds={"label": "Average Temperature (°F)"},
    ax=ax,
)

# Highlight top‑quartile elder density areas
if "Block_Groups_Over65Density" in block_gdf.columns:
    q75 = block_gdf["Block_Groups_Over65Density"].quantile(0.75)
    high_elder = block_gdf[block_gdf["Block_Groups_Over65Density"] >= q75]
    high_elder.boundary.plot(
        ax=ax,
        color="cyan",
        linewidth=1.2,
        label="Top 25% Over‑65 Density",
    )
    ax.legend()

ax.set_title("Urban Heat‑Island Surface (Kriging) and Elderly Population Hotspots")
ax.set_axis_off()

plt.tight_layout()
plt.savefig(OUTPUT_FIG, dpi=300, bbox_inches="tight")
plt.close()
print(f"Map saved to {OUTPUT_FIG}")
