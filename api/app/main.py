from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json
app = FastAPI()

# TODO(olshansky): Create shared constants lib between the different modules in market navigator
MAX_DELTA_PER = 0.2

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/market_state")
async def market_state():
    with open("/market_navigator_data/per_high_low.json", "r") as f:
        data = json.loads(f.read())
        top_stocks_label = f"{round(data['near_max'] * 100)}% of stocks on the market are within {round(MAX_DELTA_PER * 100)}% percent of their 52 week MAXIMUM, compared to an average of {round(data['avg_near_max'] * 100)}%."
        bottom_stocks_label = f"{round(data['near_min'] * 100)}% of stocks on the market are within {round(MAX_DELTA_PER * 100)}% percent of their 52 week MINIMUM, compared to an average of {round(data['avg_near_min'] * 100)}%."
        return {
            'top_stocks_label': top_stocks_label,
            'bottom_stocks_label': bottom_stocks_label
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
