from fastapi import FastAPI, HTTPException
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

@app.get("/get-infrastructure/{province}")
async def get_infrastructure(province: str):
    """Get infrastructure data for a specific province"""
    try:
        with open("infrastructure.json", "r") as file:
            data = json.load(file)
        print(data)
        province = province.lower()
        for provinces in data:  # No need to access a 'bonds' key
            # print(str(provinces.get("province")).lower())
            if str(provinces.get("province")).lower() == str(province):
                print(provinces)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)