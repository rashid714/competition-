"""Generate reproducible demo donation data used for testing and Kaggle runner.

Creates a session JSON file under `session_data/` with sample donations.
"""
import os
import json
import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'session_data')


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def generate_demo(session_id=None, num_donations=20):
    ensure_data_dir()
    if not session_id:
        session_id = f"daily_{datetime.date.today().strftime('%Y%m%d')}"

    donations = []
    stores = ['FreshMart', 'GreenBite', 'SunFarm', 'CityGrocer']
    items = ['Apples', 'Carrots', 'Bread', 'Milk', 'Salad']

    for i in range(num_donations):
        donation = {
            'store': stores[i % len(stores)],
            'item': items[i % len(items)],
            'weight': round(5 + (i * 2.3) % 50, 1),
            'location': 'Testville',
            'timestamp': datetime.datetime.now().isoformat(),
            'session_id': session_id
        }
        donations.append(donation)

    session_path = os.path.join(DATA_DIR, f"{session_id}.json")
    with open(session_path, 'w') as f:
        json.dump({'donations': donations}, f, indent=2)

    print(f"Demo data written to {session_path}")


if __name__ == '__main__':
    generate_demo()
