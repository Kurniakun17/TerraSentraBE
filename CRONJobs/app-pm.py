from fastapi import FastAPI
import ee
import pickle
import numpy as np
import requests
from bs4 import BeautifulSoup
import random
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

app = FastAPI()

# Enable CORS for all origins (you can restrict this if needed)
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

try:
    with open("poverty_model.pkl", "rb") as f:
        poverty_model = pickle.load(f)
except Exception as e:
    print("Error loading poverty model:", str(e))
    poverty_model = None

# List of Indonesian provinces
provinces = [
    "aceh", "sumatera utara", "sumatera barat", "riau", "jambi", "sumatera selatan", "bengkulu", "lampung",
    "bangka belitung", "kepulauan riau", "dki jakarta", "jawa barat", "jawa tengah", "di yogyakarta", "jawa timur", "banten",
    "bali", "nusa tenggara barat", "nusa tenggara timur", "kalimantan barat", "kalimantan tengah", "kalimantan selatan",
    "kalimantan timur", "kalimantan utara", "sulawesi utara", "sulawesi tengah", "sulawesi selatan", "sulawesi tenggara",
    "gorontalo", "sulawesi barat", "maluku", "maluku utara", "papua", "papua barat", "papua selatan", "papua tengah", "papua pegunungan", "sidoarjo", "bantul", "jakarta pusat"
]

# Green infrastructure & renewable energy mappings
green_infra_mapping = {
    "Roof Garden": ["roof garden", "atap hijau"],
    "Mangrove Reforestation": ["mangrove", "reforestasi"],
    "Penampungan Air Hujan": ["air hujan", "penampungan air"],
    "Bangunan Hemat Energi": ["hemat energi", "bangunan hijau"],
    "Transportasi Berkelanjutan": ["transportasi berkelanjutan", "kendaraan listrik"],
    "Biopori": ["biopori"],
    "Ekowisata": ["ekowisata", "wisata hijau"],
    "Hutan Kota": ["hutan kota"],
    "Dinding Hijau": ["dinding hijau", "vertical garden"],
    "Solar Panel": ["solar panel", "energi surya"],
    "Rekayasa Air Limbah Hijau": ["air limbah", "pengolahan limbah"],
    "Jalur Hijau": ["jalur hijau", "jalan hijau"],
    "Biofuel Plantations": ["biofuel", "energi biomassa"]
}

renewable_energy_mapping = {
    "Energi Surya": ["solar", "energi surya", "panel surya"],
    "Energi Angin": ["angin", "turbin angin"],
    "Energi Air": ["hidro", "energi air", "pembangkit listrik tenaga air"],
    "Panas Bumi": ["geotermal", "panas bumi"],
    "Biomassa": ["biomassa", "biofuel"]
}

# News sources
news_sites = ["https://www.kompas.com/tag/infrastruktur-hijau", "https://www.detik.com/tag/infrastruktur-hijau"]
energy_sites = ["https://www.kompas.com/tag/energi-terbarukan", "https://www.detik.com/tag/energi-terbarukan"]

# Function to scrape news articles
def scrape_news(sites):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for site in sites:
        try:
            response = requests.get(site, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles.extend([article.text.strip().lower() for article in soup.find_all('h2')])
        except Exception as e:
            print(f"Error scraping {site}: {e}")
    return articles if articles else ["No relevant news found"]

# Categorize articles based on keywords
def get_category(title, mapping):
    title_lower = title.lower()
    for category, keywords in mapping.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    return random.choice(list(mapping.keys()))

# Scrape and categorize infrastructure & renewable energy news
articles = scrape_news(news_sites)
energy_articles = scrape_news(energy_sites)

infra_results = {province: get_category(random.choice(articles), green_infra_mapping) for province in provinces}
renewable_results = {province: get_category(random.choice(energy_articles), renewable_energy_mapping) for province in provinces}

province_coords = {
    "aceh": (4.6951, 96.7494),
    "sumatera utara": (2.1154, 99.5451),
    "sumatera barat": (-0.7399, 100.8000),
    "riau": (0.5071, 101.4478),
    "jambi": (-1.4852, 102.4381),
    "sumatera selatan": (-3.3194, 103.9144),
    "bengkulu": (-3.7928, 102.2601),
    "lampung": (-4.5586, 105.4068),
    "bangka belitung": (-2.7410, 106.4406),
    "kepulauan riau": (3.9457, 108.1429),
    "dki jakarta": (-6.2088, 106.8456),
    "jawa barat": (-6.8894, 107.6405),
    "jawa tengah": (-7.1500, 110.1403),
    "di yogyakarta": (-7.7956, 110.3695),
    "jawa timur": (-7.2504, 112.7688),
    "banten": (-6.4058, 106.0640),
    "bali": (-8.3405, 115.0920),
    "nusa tenggara barat": (-8.6529, 117.3616),
    "nusa tenggara timur": (-8.6574, 121.0794),
    "kalimantan barat": (0.1326, 111.0966),
    "kalimantan tengah": (-1.6815, 113.3824),
    "kalimantan selatan": (-3.0926, 115.2838),
    "kalimantan timur": (1.6407, 116.4194),
    "kalimantan utara": (3.5071, 117.4991),
    "sulawesi utara": (1.4025, 124.9831),
    "sulawesi tengah": (-1.4305, 120.7655),
    "sulawesi selatan": (-3.6688, 119.9741),
    "sulawesi tenggara": (-4.1461, 122.1743),
    "gorontalo": (0.6994, 122.4467),
    "sulawesi barat": (-2.8440, 119.2321),
    "maluku": (-3.2385, 130.1453),
    "maluku utara": (0.6348, 127.9721),
    "papua": (-4.2699, 138.0804),
    "papua barat": (-1.3361, 133.1747),
    "papua selatan": (-7.6710, 138.7648),
    "papua tengah": (-3.9917, 136.2804),
    "papua pegunungan": (-4.5415, 138.1185),
    "sidoarjo": (-7.4545375,112.5005207),
    "bantul": (-7.902243,110.2863846),
    "jakarta pusat": (-6.1822261,106.7952647)
}

# Function to fetch NDVI, precipitation, and soil moisture data
def fetch_environmental_data(province):
    if province not in province_coords:
        return {"error": "Invalid province"}

    lat, lon = province_coords[province]
    point = ee.Geometry.Point(lon, lat)

    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    try:
        # Vegetation index (NDVI)
        ndvi_image = ee.ImageCollection("MODIS/061/MOD13Q1") \
            .filterDate(start_date, end_date) \
            .select("NDVI") \
            .map(lambda img: img.updateMask(img.gt(0))) \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=250, bestEffort=True)

        # Precipitation
        precipitation_image = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterDate(start_date, end_date) \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=500, bestEffort=True)

        # Soil moisture (using Sentinel-1 VV polarization as proxy)
        soil_moisture_image = ee.ImageCollection("COPERNICUS/S1_GRD") \
            .filterBounds(point) \
            .filterDate(start_date, end_date) \
            .select("VV") \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=500, bestEffort=True)
        
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
        
        # Ozone (O3) from Sentinel-5P
        o3_image = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_O3") \
            .filterDate(start_date, end_date) \
            .select("O3_column_number_density") \
            .map(lambda img: img.updateMask(img.gt(0))) \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=1000, bestEffort=True)
        
        # Particulate Matter - using MODIS Aerosol Optical Depth as proxy for PM2.5
        # MAIAC AOD Collection
        aod_image = ee.ImageCollection("MODIS/006/MCD19A2_GRANULES") \
            .filterDate(start_date, end_date) \
            .select("Optical_Depth_055") \
            .map(lambda img: img.updateMask(img.gt(0))) \
            .mean() \
            .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=1000, bestEffort=True)
        
        # Convert AOD to estimated PM2.5 using a simplified linear model
        # This is a rough approximation; actual conversion depends on regional factors
        aod_value = aod_image.getInfo().get("Optical_Depth_055", 0)
        estimated_pm25 = aod_value * 10  # Simple scaling factor, adjust based on regional calibration
        
        # Alternative: GEOS PM2.5 data if available
        try:
            pm_image = ee.ImageCollection("NASA/GEOS-CF/v1/rpl/htf") \
                .filterDate(start_date, end_date) \
                .select("PM25") \
                .mean() \
                .reduceRegion(reducer=ee.Reducer.mean(), geometry=point.buffer(10000), scale=1000, bestEffort=True)
            pm25_value = pm_image.getInfo().get("PM25", estimated_pm25)
        except:
            pm25_value = estimated_pm25  # Fallback to AOD-based estimate

        return {
            "ndvi": round(ndvi_image.getInfo().get("NDVI", 0) * 0.0001, 2),
            "precipitation": round(precipitation_image.getInfo().get("precipitation", 0), 1),
            "sentinel": round(soil_moisture_image.getInfo().get("VV", 0), 3),
            "no2": round(no2_image.getInfo().get("NO2_column_number_density", 0) * 1000000, 3),  # Convert to μmol/m²
            "co": round(co_image.getInfo().get("CO_column_number_density", 0) * 1000, 3),  # Convert to mol/m²
            "so2": round(so2_image.getInfo().get("SO2_column_number_density", 0) * 1000000, 3),  # Convert to μmol/m²
            "o3": round(o3_image.getInfo().get("O3_column_number_density", 0) / 2241.15, 3),  # Convert to DU (Dobson Units)
            "pm25": round(pm25_value, 1)  # PM2.5 in μg/m³
        }
    except Exception as e:
        print("Error fetching environmental data:", str(e))
        return {"error": "Failed to fetch environmental data"}
    
    
# Function to fetch Night_Lights and Daylight_Duration
def fetch_geospatial_data(province):
    if province not in province_coords:
        return {"error": "Invalid province"}

    lat, lon = province_coords[province]
    point = ee.Geometry.Point(lon, lat).buffer(5000)

    end_date = ee.Date("2024-01-01")
    start_date = end_date.advance(-60, "day")

    buffered_point = point.buffer(1000)

    try:
        # Fetch Nighttime Lights (VIIRS)
        # Using a different VIIRS collection that's more reliably available
        viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")\
            .filterDate(start_date, end_date)\
            .select("avg_rad")\
            .mean()
        
        night_lights_result = viirs.reduceRegion(
            reducer=ee.Reducer.mean(), 
            geometry=buffered_point, 
            scale=500, 
            bestEffort=True
        )
        
        night_lights = night_lights_result.getInfo().get("avg_rad")
        
        # Fetch a different solar radiation metric that's more consistently available
        solar = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY")\
            .filterDate(start_date, end_date)\
            .select("surface_solar_radiation_downwards_sum")\
            .mean()
            
        daylight_result = solar.reduceRegion(
            reducer=ee.Reducer.mean(), 
            geometry=buffered_point, 
            scale=1000, 
            bestEffort=True
        )
        
        daylight_duration = daylight_result.getInfo().get("surface_solar_radiation_downwards_sum")
        
        # Add debugging statements
        print(f"Province: {province}, Night Lights: {night_lights}, Daylight: {daylight_duration}")
        
        # Check if either value is None and substitute a default value
        if night_lights is None:
            print(f"Warning: Night lights data unavailable for {province}")
            night_lights = 0.0
            
        if daylight_duration is None:
            print(f"Warning: Daylight duration data unavailable for {province}")
            daylight_duration = 0.0
            
        return float(night_lights), float(daylight_duration)
        
    except Exception as e:
        print(f"Error fetching geospatial data for {province}: {str(e)}")
        # Return default values instead of NaN
        return 0.0, 0.0

# Function to predict Poverty Index
def predict_poverty_index(province):
    if poverty_model is None:
        return "Model not available"

    try:
        night_lights, daylight_duration = fetch_geospatial_data(province)
        
        # Use default values if data is missing
        if isinstance(night_lights, dict) and "error" in night_lights:
            print(f"Error for {province}: {night_lights['error']}")
            return "Data unavailable"
        
        features = np.array([[night_lights, daylight_duration]])
        predicted_poverty = poverty_model.predict(features)[0]
        
        return round(predicted_poverty, 2)
    except Exception as e:
        print(f"Error predicting poverty index for {province}: {str(e)}")
        return "Prediction error"

# API Endpoint
@app.get("/get-infrastructure/{province}")
def get_infrastructure(province: str):
    province = province.strip().lower()
    if province not in province_coords:
        return {"error": "Invalid province name"}
    environmental_data = fetch_environmental_data(province)
    poverty_index = predict_poverty_index(province)
    return {
        "province": province.title(),
        "infrastructure": infra_results.get(province, "Not Available"),
        "renewable_energy": renewable_results.get(province, "Not Available"),
        "poverty_index": poverty_index,
        **environmental_data
    }
