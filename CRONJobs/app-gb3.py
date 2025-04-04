from fastapi import FastAPI
import ee
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authenticate and initialize Google Earth Engine (GEE)
try:
    ee.Initialize(project='ee-steviaanlenaa')
except Exception as e:
    print("Error initializing Earth Engine:", str(e))

# Add subdistrict coordinates for Jakarta Pusat
jakarta_pusat_subdistricts = {
    "gambir": (-6.1768, 106.8215),
    "tanah abang": (-6.2053, 106.8179),
    "menteng": (-6.1970, 106.8304),
    "senen": (-6.1737, 106.8414),
    "cempaka putih": (-6.1714, 106.8702),
    "johar baru": (-6.1788, 106.8595),
    "kemayoran": (-6.1619, 106.8494),
    "sawah besar": (-6.1641, 106.8267)
}

# Function to fetch environmental data and calculate environmental score for a subdistrict
def fetch_environmental_score(subdistrict):
    if subdistrict not in jakarta_pusat_subdistricts:
        return {"error": "Invalid subdistrict name"}
    
    lat, lon = jakarta_pusat_subdistricts[subdistrict]
    point = ee.Geometry.Point(lon, lat)
    
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    try:
        # Nitrogen Dioxide (NO2) from Sentinel-5P
        no2_image = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2") \
            .filterDate(start_date, end_date) \
            .select("NO2_column_number_density") \
            .map(lambda img: img.updateMask(img.gt(0))) \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=1000, bestEffort=True)
        
        # Land Surface Temperature (LST) from MODIS
        lst_image = ee.ImageCollection("MODIS/006/MOD11A1") \
            .filterDate(start_date, end_date) \
            .select("LST_Day_1km") \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=1000, bestEffort=True)
        
    
        # Get the values and convert to appropriate units
        no2_value = round(no2_image.getInfo().get("NO2_column_number_density", 0) * 1000000, 3)  # Convert to μmol/m²
        lst_value = round(lst_image.getInfo().get("LST_Day_1km", 0) * 0.02 - 273.15, 2)  # Convert to Celsius
        
        # Print the values for the subdistrict
        print(f"Subdistrict: {subdistrict.title()}")
        print(f"  NO2: {no2_value} μmol/m²")
        print(f"  LST: {lst_value} °C")
        
        # Define maximum expected values
        no2_max = 100.0    # μmol/m²
        lst_max = 40.0     # °C (adjust based on Jakarta's climate)
        solar_min = 150.0  # W/m² - minimum threshold for good solar potential
        solar_max = 350.0  # W/m² - excellent solar potential
        
        # Calculate normalized scores (0-100 scale, higher is better)
        # For NO2: Lower is better (cleaner air)
        no2_score = max(0, 100 * (1 - (no2_value / no2_max)))
        
        # For temperature: optimal temp for solar panels is 25°C, efficiency drops as temperature rises
        # Score decreases as temperature deviates from optimal
        lst_score = max(0, 100 - (abs(lst_value - 25) * 6.67))  # 6.67 = 100/15 (15°C deviation from ideal)
        
        # Calculate weighted environmental score
        # Giving higher weight to solar radiation for solar panel context
        env_score = round((0.3 * no2_score + 0.3 * lst_score), 1)
        
        # Create a qualitative rating based on the score
        if env_score >= 80:
            rating = "Excellent"
        elif env_score >= 60:
            rating = "Good"
        elif env_score >= 40:
            rating = "Moderate"
        elif env_score >= 20:
            rating = "Poor"
        else:
            rating = "Very Poor"
        
        # Add solar panel specific insights
        solar_panel_efficiency = None
        if lst_value > 35:
            solar_panel_efficiency = "Reduced due to high temperatures"
        elif no2_value > 60:
            solar_panel_efficiency = "May be affected by air pollution deposits"
        else:
            solar_panel_efficiency = "Favorable conditions"
        
        return {
            "subdistrict": subdistrict.title(),
            "environmental_score": env_score,
            "environmental_rating": rating,
            "solar_panel_efficiency": solar_panel_efficiency,
            "environmental_data": {
                "no2": {
                    "value": no2_value,
                    "unit": "μmol/m²",
                    "score": round(no2_score, 1),
                    "impact": "Air pollution can reduce panel efficiency through particle deposition"
                },
                "lst": {
                    "value": lst_value,
                    "unit": "°C",
                    "score": round(lst_score, 1),
                    "impact": "Higher temperatures reduce solar panel efficiency by ~0.5% per °C above 25°C"
                }
            }
        }
            
    except Exception as e:
        print(f"Error fetching environmental data for {subdistrict}: {str(e)}")
        return {
            "error": f"Failed to fetch environmental data: {str(e)}",
            "subdistrict": subdistrict.title(),
            "environmental_score": 0,
            "environmental_rating": "Unknown"
        }

# API Endpoint to get environmental score for a specific subdistrict
@app.get("/environmental-score/{subdistrict}")
def get_environmental_score(subdistrict: str):
    subdistrict = subdistrict.strip().lower()
    return fetch_environmental_score(subdistrict)

# API Endpoint to get scores for all subdistricts
@app.get("/all-environmental-scores")
def get_all_environmental_scores():
    results = {}
    for subdistrict in jakarta_pusat_subdistricts.keys():
        results[subdistrict] = fetch_environmental_score(subdistrict)
    return results