# mock_mcp_server.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/v1/context")
def get_context():
    return {
        "file": "src/example/my_code.py",
        "visible_range": [10, 25],
        "content": "def calculate_total(items):\n    total = 0\n    for item in items:\n        total += item.price\n    return total",
        "selection": "total += item.price"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)