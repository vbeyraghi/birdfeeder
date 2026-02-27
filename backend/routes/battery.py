import csv
import os
from typing import List

from config import LATEST_BATTERY_CSV
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/battery", tags=["battery"])


class BatteryData(BaseModel):
    timestamp: str
    percentage: float
    solar_radiation_Wm2: float


@router.get("/status", response_model=List[BatteryData])
def get_battery_data():
    """Returns the latest battery data from the CSV file."""
    if not os.path.exists(LATEST_BATTERY_CSV):
        return []

    data = []
    try:
        with open(LATEST_BATTERY_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(BatteryData(
                    timestamp=row["timestamp"],
                    percentage=float(row["percentage"]),
                    solar_radiation_Wm2=float(row["solar_radiation_Wm2"])
                ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading battery data: {e}")

    return data
