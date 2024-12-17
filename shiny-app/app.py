import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shiny import App, render, ui, reactive
import folium
from folium import Marker
from pathlib import Path

here = Path(__file__).parent

# Load the vacancy data from shp file
vacancy_gdf = gpd.read_file("vacant_gdf.shp")

# create the UI
page1 = ui.navset_card_underline(
ui.nav_panel(
    "Map Toggles",
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_radio_buttons("area_measure", "Area Measure:", ["zcta", "tract"]),
            ui.input_radio_buttons("wealth_measure", "Wealth Measure:", ["income", "value"])
        ),
        ui.output_image("map_image"),
        fill=True,
        border=True,
        gap="10px")
    
    ),
    title="Total Reported Vacant Lots 2011 - 2024"
)

page2 = ui.navset_card_underline(
    ui.nav_panel("Interactive Map",
        ui.input_slider(
            "year",
            "Select Year",
            min=2011,
            max=2024,
            value=2011,
            step=1
        ),
        ui.output_ui("map")
    ),
    title="Vacancy Data Map"
)

app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel("Aggregate Wealth and Area Divisions", page1),
    ui.nav_panel("Yearly Reports Interactive Map", page2),
    title="A Closer Look at Chicago Vacancies"
)

def server(input, output, session):
    @output
    @render.image
    def map_image():
        area_measure = input.area_measure()
        wealth_measure = input.wealth_measure()
        image_path = here / f"{area_measure}_{wealth_measure}.png"
        return {"src": image_path, "alt": f"Map showing {wealth_measure} for {area_measure}", "width": "50%"}

    def create_map(year):
        filtered_gdf = vacancy_gdf[vacancy_gdf['year'] == year]
        m = folium.Map(location=[41.85, -87.65], zoom_start=10)
        for _, row in filtered_gdf.iterrows():
            if not row['geometry'].is_empty:
                Marker(
                    location=[row['geometry'].y, row['geometry'].x],
                    popup=row['property_a']
                ).add_to(m)
        return m

    @output
    @render.ui
    @reactive.event(input.year)
    def map():
        selected_year = input.year()
        m = create_map(selected_year)
        map_html = m._repr_html_()
        return ui.HTML(map_html)

app = App(app_ui, server)

