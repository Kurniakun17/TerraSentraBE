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

# Add subdistrict coordinates for Bantul regency
bantul_subdistricts = {
    "srandakan": (-7.9599944, 110.1975521),
    "sanden": (-7.9811811, 110.1881439),
    "kretek": (-7.9923989, 110.266404),
    "pundong": (-7.9713209, 110.3009071),
    "bambang lipuro": (-7.9445142, 110.2380219),
    "pandak": (-7.924187, 110.243655),
    "bantul": (-7.8913955, 110.295007),
    "jetis": (-7.9098564, 110.3251626),
    "imogiri": (-7.9375405, 110.3550834),
    "dlingo": (-7.919252, 110.4111034),
    "pleret": (-7.8773835, 110.3946772),
    "piyungan": (-7.845006, 110.4297405),
    "banguntapan": (-7.823617, 110.361653),
    "sewon": (-7.8558584, 110.3108565),
    "kasihan": (-7.8145279, 110.2754565),
    "pajangan": (-7.8720351, 110.248431),
    "sedayu": (-7.8239625, 110.2148165)
}

# Function to fetch air quality data and calculate environmental score for a subdistrict
def fetch_environmental_score(subdistrict):
    if subdistrict not in bantul_subdistricts:
        return {"error": "Invalid subdistrict name"}
    
    lat, lon = bantul_subdistricts[subdistrict]
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
        
        # Carbon Monoxide (CO) from Sentinel-5P
        co_image = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_CO") \
            .filterDate(start_date, end_date) \
            .select("CO_column_number_density") \
            .map(lambda img: img.updateMask(img.gt(0))) \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=1000, bestEffort=True)
        
        # Sulfur Dioxide (SO2) from Sentinel-5P
        so2_image = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_SO2") \
            .filterDate(start_date, end_date) \
            .select("SO2_column_number_density") \
            .map(lambda img: img.updateMask(img.gt(0))) \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=1000, bestEffort=True)
        
        # Get the values and convert to appropriate units
        no2_value = round(no2_image.getInfo().get("NO2_column_number_density", 0) * 1000000, 3)  # Convert to μmol/m²
        co_value = round(co_image.getInfo().get("CO_column_number_density", 0) * 1000, 3)  # Convert to mol/m²
        so2_value = round(so2_image.getInfo().get("SO2_column_number_density", 0) * 1000000, 3)  # Convert to μmol/m²
        
        # Print the values for the subdistrict
        print(f"Subdistrict: {subdistrict.title()}")
        print(f"  NO2: {no2_value} μmol/m²")
        print(f"  CO: {co_value} mol/m²")
        print(f"  SO2: {so2_value} μmol/m²")
        
        # Define maximum expected values based on your example data
        # These should be adjusted if you have more representative data
        no2_max = 100.0  # μmol/m²
        co_max = 60.0    # mol/m²
        so2_max = 400.0  # μmol/m²
        
        # Calculate normalized scores (0-100 scale, higher is better/cleaner)
        # Using an inverse linear scale:
        # 0 pollutant value = 100 score
        # max pollutant value = 0 score
        no2_score = max(0, 100 * (1 - (no2_value / no2_max)))
        co_score = max(0, 100 * (1 - (co_value / co_max)))
        so2_score = max(0, 100 * (1 - (so2_value / so2_max)))
        
        # Calculate weighted environmental score
        # Giving equal weights to each pollutant
        env_score = round((no2_score + co_score + so2_score) / 3, 1)
        
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
        
        return {
            "subdistrict": subdistrict.title(),
            "environmental_score": env_score,
            "environmental_rating": rating,
            "pollutant_data": {
                "no2": {
                    "value": no2_value,
                    "unit": "μmol/m²",
                    "score": round(no2_score, 1)
                },
                "co": {
                    "value": co_value,
                    "unit": "mol/m²",
                    "score": round(co_score, 1)
                },
                "so2": {
                    "value": so2_value,
                    "unit": "μmol/m²",
                    "score": round(so2_score, 1)
                }
            }
        }
            
    except Exception as e:
        print(f"Error fetching air quality data for {subdistrict}: {str(e)}")
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
    for subdistrict in bantul_subdistricts.keys():
        results[subdistrict] = fetch_environmental_score(subdistrict)
    return results