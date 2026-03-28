import json
from collections import Counter
from demo_data import DEMO_DATA

def load_data():
    try:
        with open("complaints.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_data(issue):
    data = load_data()
    data.append(issue)
    with open("complaints.json", "w") as f:
        json.dump(data, f)

def get_stats():
    data = DEMO_DATA + load_data()
    return Counter(data)