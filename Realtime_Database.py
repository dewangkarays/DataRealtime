import firebase_admin
from firebase_admin import credentials, db
import requests
import time

# ---- Firebase Setup ----
# Path ke file kredensial Firebase (sesuaikan dengan lokasi file Anda)
FIREBASE_CREDENTIALS_PATH = r"E:\Machine Learning TA\data-iradiasi-realtime-firebase.json"

# Inisialisasi Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://data-iradiasi-realtime-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

print("Firebase initialized successfully.")

# ---- API Setup ----
API_URL = 'https://api.open-meteo.com/v1/forecast?latitude=6.6247&longitude=110.641&minutely_15=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,is_day,shortwave_radiation,diffuse_radiation&wind_speed_unit=ms&timezone=auto&past_minutely_15=1&forecast_days=1&forecast_minutely_15=4&models=best_match'

# Fungsi untuk mengambil data dari API
def fetch_api_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            minute_data = data.get('minutely_15', {})
            parsed_data = [
                {
                    'time': minute_data.get('time', [])[i],
                    'temperature_2m': minute_data.get('temperature_2m', [])[i],
                    'relative_humidity_2m': minute_data.get('relative_humidity_2m', [])[i],
                    'wind_speed_10m': minute_data.get('wind_speed_10m', [])[i],
                    'wind_direction_10m': minute_data.get('wind_direction_10m', [])[i],
                    'is_day': minute_data.get('is_day', [])[i],
                    'shortwave_radiation': minute_data.get('shortwave_radiation', [])[i],
                    'diffuse_radiation': minute_data.get('diffuse_radiation', [])[i]
                }
                for i in range(len(minute_data.get('time', [])))
            ]
            return parsed_data
        else:
            print(f"Error fetching data: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error occurred while fetching API data: {e}")
        return []

# Fungsi untuk menyimpan data ke Firebase
def save_to_firebase(data):
    try:
        ref = db.reference('weather_data')  # Lokasi data di Realtime Database
        for entry in data:
            ref.child(entry['time']).set(entry)  # Gunakan `time` sebagai key unik
        print(f"Data saved to Firebase: {len(data)} entries.")
    except Exception as e:
        print(f"Error saving data to Firebase: {e}")

# ---- Main Loop ----
if __name__ == "__main__":
    while True:
        print("Fetching data from API...")
        api_data = fetch_api_data()
        if api_data:
            print("Saving data to Firebase...")
            save_to_firebase(api_data)
        else:
            print("No data to save.")
        
        print("Sleeping for 15 minutes...")
        time.sleep(900)  # Tunggu selama 15 menit sebelum mengambil data lagi
