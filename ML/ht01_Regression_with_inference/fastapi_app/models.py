import numpy as np
from pydantic import BaseModel

class Item(BaseModel):
    name: str = None
    year: float = np.nan
    km_driven: float = np.nan
    fuel: str = None
    seller_type: str = None
    transmission: str = None
    owner: str = None
    mileage: float = np.nan
    engine: float = np.nan
    max_power: float = np.nan
    seats: float = np.nan
