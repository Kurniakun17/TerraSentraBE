from fastapi import FastAPI, HTTPException
import numpy as np
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json

app = FastAPI()

# Load configuration
config = {
    "routes": [
        {
            "path": "/get-infrastructure/{province}",
            "method": "GET",
            "data_file": "infrastructure_data.json",
            "param_name": "province"
        },
        {
            "path": "/green-bond/{bond_id}",
            "method": "GET",
            "data_file": "green-bond.json",
            "param_name": "bond_id"
        }
    ]
}

def get_exchange_rate():
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    if response.status_code == 200:
        return response.json().get("rates", {}).get("IDR", 16000)
    return 16000

carbon_sites = "https://www.investing.com/commodities/carbon-emissions-historical-data"
headers = {'User-Agent': 'Mozilla/5.0'}

@app.get("/get-infrastructure/{province}")
async def get_infrastructure(province: str):
    """Get infrastructure data for a specific province"""
    try:
        with open("infrastructure.json", "r") as file:
            data = json.load(file)
        # print(data)
        province = province.lower()
        for provinces in data:  # No need to access a 'bonds' key
            # print(str(provinces.get("province")).lower())
            if str(provinces.get("province")).lower() == str(province):
                # print(provinces)
                return provinces
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Infrastructure data file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing infrastructure data file")

@app.get("/green-bond/{bond_id}")
async def get_green_bond(bond_id: str):
    """Get green bond information by bond ID"""
    try:
        with open("green-bond.json", "r") as file:
            data = json.load(file)
       
        for bond in data:  # No need to access a 'bonds' key
            print(int(bond.get("id")) == int(bond_id))
            if int(bond.get("id")) == int(bond_id):
                return bond
        
        raise HTTPException(status_code=404, detail=f"Bond ID '{bond_id}' not found")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Green bond data file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing green bond data file")

@app.get("/get-umkm/{id}")
def get_umkm(id: int = None):
    try:
        with open("database/umkm.json", "r", encoding="utf-8") as file:
            umkm_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"error": "Failed to load UMKM data"}

    if id == 0: 
        return umkm_data

    for umkm in umkm_data:
        if umkm.get("id") == id:
            return umkm

    return {"error": "UMKM not found"}

@app.get("/get-carbon-offset")
def get_carbon_offset():
    response = requests.get(carbon_sites, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to retrieve data", "status_code": response.status_code}

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    exchange_rate = get_exchange_rate()
    data_list = []

    if table:
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            if len(cols) == 7:
                data_list.append({
                    "Date": cols[0],
                    "Price (IDR)": round(float(cols[1].replace(",", "")) * exchange_rate, 2),
                    "Open (IDR)": round(float(cols[2].replace(",", "")) * exchange_rate, 2),
                    "High (IDR)": round(float(cols[3].replace(",", "")) * exchange_rate, 2),
                    "Low (IDR)": round(float(cols[4].replace(",", "")) * exchange_rate, 2),
                    "Vol": cols[5],
                    "Change %": cols[6]
                })
    return data_list if data_list else {"error": "No data found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)