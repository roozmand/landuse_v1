# landuse_first/handlers/nuts.py
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import importlib.resources as pkg_resources
import landuse_v1  # the top-level package

class NUTSHandler:
    """Load, plot and query NUTS shapefiles packaged within `landuse_first/Data`.

    Example:
        nh = NUTSHandler(country_code="DE",
                         file_name="airtemp",
                         nuts_level=3,
                         year=2018)
    """

    def __init__(self, country_code, file_name, nuts_level, year):
        self.country_code = str(country_code)
        self.file_name = str(file_name)
        self.nuts_level = int(nuts_level)
        self.year = int(year)

        # resolve path to Data folder inside the installed package
        package_root = Path(pkg_resources.files(landuse_v1))
        data_root = package_root / "Data" / "Yearly"

        folder_name = f"{self.country_code}_{self.file_name}_NUTS{self.nuts_level}_{self.year}"
        folder_path = data_root / folder_name
        self.shp_file = folder_path / f"{folder_name}.shp"

        if not self.shp_file.exists():
            raise FileNotFoundError(f"Shapefile not found in package data: {self.shp_file}")

        self.gdf = gpd.read_file(self.shp_file)

    def mean_columns(self):
        return [c for c in self.gdf.columns if c.endswith("_mean")]

    def plot_mean(self, mean_column=None, cmap="Blues", vmin=None, vmax=None, figsize=(10, 10)):
        if mean_column is None:
            mean_cols = self.mean_columns()
            if not mean_cols:
                raise ValueError("No *_mean column found.")
            mean_column = mean_cols[0]

        fig, ax = plt.subplots(figsize=figsize)
        self.gdf.plot(
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
        ax.set_title(f"{self.country_code} NUTS{self.nuts_level} - {mean_column} ({self.year})")
        ax.axis("off")
        plt.show()

    def get_district_value(self, nuts_id, mean_column=None):
        if mean_column is None:
            mean_cols = self.mean_columns()
            if not mean_cols:
                raise ValueError("No *_mean column found.")
            mean_column = mean_cols[0]

        district = self.gdf[self.gdf["NUTS_ID"] == nuts_id]
        if district.empty:
            raise KeyError(f"District {nuts_id} not found in NUTS{self.nuts_level}.")
        return district.iloc[0][mean_column]

    def __repr__(self):
        return f"<NUTSHandler {self.country_code} NUTS{self.nuts_level} {self.year} ({len(self.gdf)} features)>"
