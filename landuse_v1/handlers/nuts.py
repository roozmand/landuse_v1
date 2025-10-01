# landuse_first/handlers/nuts.py
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import importlib.resources as pkg_resources
import landuse_v1  # top-level package

class NUTSHandler:
    """
    NUTSHandler is a stateless handler for NUTS and crop landuse shapefiles.
    
    Constructor takes no parameters; all parameters go to the methods.
    """

    def __init__(self):
        pass

    # ---------------- NUTS functions ----------------
    def mean_columns(self, country_code="DE", file_name="airtemp", nuts_level=2, year=2022):
        gdf = self._read_nuts(country_code, file_name, nuts_level, year)
        return [c for c in gdf.columns if c.endswith("_mean")]

    def plot_mean(self, country_code="DE", file_name="airtemp", nuts_level=2, year=2022,
                  mean_column=None, cmap="Blues", vmin=None, vmax=None, figsize=(10,10)):
        gdf = self._read_nuts(country_code, file_name, nuts_level, year)

        if mean_column is None:
            mean_cols = [c for c in gdf.columns if c.endswith("_mean")]
            if not mean_cols:
                raise ValueError("No *_mean column found.")
            mean_column = mean_cols[0]

        fig, ax = plt.subplots(figsize=figsize)
        gdf.plot(
            ax=ax,
            column=mean_column,
            cmap=cmap,
            edgecolor="black",
            linewidth=0.5,
            legend=True,
            vmin=vmin,
            vmax=vmax,
            missing_kwds={"color": "lightgrey", "label": "No data"}
        )
        ax.set_title(f"{country_code} NUTS{nuts_level} - {mean_column} ({year})")
        ax.axis("off")
        plt.show()

    def get_district_value(self, nuts_id, country_code="DE", file_name="airtemp",
                           nuts_level=2, year=2022, mean_column=None):
        gdf = self._read_nuts(country_code, file_name, nuts_level, year)

        if mean_column is None:
            mean_cols = [c for c in gdf.columns if c.endswith("_mean")]
            if not mean_cols:
                raise ValueError("No *_mean column found.")
            mean_column = mean_cols[0]

        district = gdf[gdf["NUTS_ID"] == nuts_id]
        if district.empty:
            raise KeyError(f"District {nuts_id} not found in NUTS{nuts_level}.")
        return district.iloc[0][mean_column]

    # ---------------- Crop landuse functions ----------------
    def plot_crop_landuse(self, crop_name, nuts_level=2, year=2022,
                          column="v_mean", cmap="viridis", figsize=(10,10)):
        gdf_crop = self._read_crop(crop_name, nuts_level, year)

        if column not in gdf_crop.columns:
            raise ValueError(f"Column {column} not found in crop shapefile.")

        fig, ax = plt.subplots(figsize=figsize)
        gdf_crop.plot(
            ax=ax,
            column=column,
            cmap=cmap,
            edgecolor="black",
            linewidth=0.5,
            legend=True,
            missing_kwds={"color": "lightgrey", "label": "No data"}
        )
        ax.set_title(f"{crop_name} NUTS{nuts_level} ({year}) - {column}")
        ax.axis("off")
        plt.show()

    def get_crop_mean(self, crop_name, nuts_level=2, year=2022, column="v_mean"):
        gdf_crop = self._read_crop(crop_name, nuts_level, year)

        if column not in gdf_crop.columns:
            raise ValueError(f"Column {column} not found in crop shapefile.")

        return gdf_crop[column].mean()

    # ---------------- New utility functions ----------------
    def get_nuts_names(self, nuts_level, country_code="DE", file_name="airtemp", year=2022):
        """
        Return a list of district names for a given NUTS level.
        """
        gdf = self._read_nuts(country_code, file_name, nuts_level, year)
        return gdf["NUTS_NAME"].tolist()

    def get_crop_mean_per_district(self, crop_name, nuts_level=2, year=2022, column="v_mean"):
        """
        Return a dictionary with mean values per district for a given crop shapefile.
        """
        gdf_crop = self._read_crop(crop_name, nuts_level, year)

        if column not in gdf_crop.columns:
            raise ValueError(f"Column {column} not found in crop shapefile.")

        if "NUTS_NAME" not in gdf_crop.columns:
            raise KeyError("Column 'NUTS_NAME' not found in crop shapefile.")

        means = gdf_crop.groupby("NUTS_NAME")[column].mean().to_dict()
        return means

    # ---------------- Internal helpers ----------------
    def _read_nuts(self, country_code, file_name, nuts_level, year):
        package_root = Path(pkg_resources.files(landuse_v1))
        data_root = package_root / "Data" / "Yearly"
        folder_name = f"{country_code}_{file_name}_NUTS{nuts_level}_{year}"
        shp_file = data_root / folder_name / f"{folder_name}.shp"

        if not shp_file.exists():
            raise FileNotFoundError(f"NUTS shapefile not found: {shp_file}")

        return gpd.read_file(shp_file)

    def _read_crop(self, crop_name, nuts_level, year):
        crop_name_clean = str(crop_name).replace(" ", "_")
        package_root = Path(pkg_resources.files(landuse_v1))
        data_root = package_root / "Data" / "Yearly"
        folder_name = f"DE_landuse_{crop_name_clean}_NUTS{nuts_level}_{year}"
        shp_file = data_root / folder_name / f"{folder_name}.shp"

        if not shp_file.exists():
            raise FileNotFoundError(f"Crop shapefile not found: {shp_file}")

        return gpd.read_file(shp_file)

    def __repr__(self):
        return "<NUTSHandler (stateless)>"
