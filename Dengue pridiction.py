from flask import Flask, request, render_template
import joblib
import folium
import requests


app = Flask(__name__)

# Load your saved model
model = joblib.load(r'C:\Users\sneha\Documents\project\dengue\dengue_model.pkl')

# OpenWeather API key
API_KEY = '9443f00722c1850c03bce88203f13b0b'

# Define locations (latitude, longitude) for major cities in India
locations = {
    'Delhi': (28.6139, 77.2090),
    'Mumbai': (19.0760, 72.8777),
    'Bengaluru': (12.9716, 77.5946),
    'Kolkata': (22.5726, 88.3639),
    'Chennai': (13.0827, 80.2707),
    'Hyderabad': (17.3850, 78.4867)
}

# Function to get real-time weather data
def get_weather_data(lat, lon):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        # Extract weather data
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        rainfall = data['rain']['1h'] if 'rain' in data else 0  # Rainfall in the past hour
        return temperature, humidity, rainfall, wind
    else:
        return None

@app.route('/')
def home():
    # Create a Folium map centered around India
    india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    # Loop through each location to get weather data and make predictions
    for city, (lat, lon) in locations.items():
        weather_data = get_weather_data(lat, lon)
        
        if weather_data:
            temperature, humidity, rainfall, wind = weather_data
            prediction = model.predict([[temperature, humidity, rainfall, wind]])[0]
            color = 'green' if prediction == 0 else 'red'  # Not prone: green, Prone: red
            
            # Add a circle marker to the map
            folium.CircleMarker(
                location=(lat, lon),
                radius=10,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=f'{city}: {"Prone to Dengue" if prediction == 1 else "Not Prone to Dengue"}'
            ).add_to(india_map)

# Save the map to an HTML file
# india_map.save('templates/india_map.html')

# return render_template('index.html', map_path='india_map.html')
    map_html = india_map._repr_html_()  # Get HTML representation of the map

    return render_template('index.html', map_html=map_html)

@app.route('/predict', methods=['POST'])
def predict():
    temperature = float(request.form['Temperature'])
    humidity = float(request.form['Humidity'])
    rainfall = float(request.form['Rainfall'])
    wind = float(request.form['Wind']) 
    
    prediction = model.predict([[temperature, humidity, rainfall, wind]])
    
    result = 'Prone to Dengue' if prediction[0] == 1 else 'Not Prone to Dengue'
    return render_template('index.html', prediction_text=result, map_path='india_map.html')

if __name__ == "__main__":
    app.run(debug=True)
