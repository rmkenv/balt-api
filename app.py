from flask import Flask
from flask import request
from flask import jsonify

import requests
import json

app = Flask(__name__)

@app.route('/iaqi-score', methods=['GET'])
def get_iaqi_score():
    # Fetching AQI for PM & O3
    airnow_api = requests.get('https://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=21202&distance=10&API_KEY=9FCE9356-FF6B-4ADF-863E-0C4D9FFAA8BB')
    airnow_data = json.loads(airnow_api.text)
    if len(airnow_data) < 2:
        return "AQI API Result Incomplete !", "500"
    aqi_pm = airnow_data[0]["AQI"]
    aqi_o3 = airnow_data[1]["AQI"]
    # print("Status Code: ", airnow_api.status_code)
    # print("\nData: ", airnow_data)

    # Fetching the HeatIndex using KBWI Station
    heatindex_api = requests.get('https://api.weather.gov/stations/kbwi/observations?limit=1')
    heatindex_data = json.loads(heatindex_api.text)
    # return heatindex_data
    heatindex_data = heatindex_data['features'][0]['properties']['heatIndex']

    heatindex_val = heatindex_data['value']

    if heatindex_val != None:
        iaqi_score = aqi_pm + aqi_o3 + heatindex_val
    else:
        return "HeatIndex is null. Please try  again later !", 500

    if iaqi_score > 430:
        iaqi_desc1 = 'Hazardous'
        iaqi_desc2 = ''
        display_color = 'Pink'
    elif iaqi_score >= 321 and iaqi_score <= 430:
        iaqi_desc1 = 'Very Unhealthy'
        iaqi_desc2 = 'Extreme Danger'
        display_color = 'Purple'
    elif iaqi_score >= 251 and iaqi_score <= 320:
        iaqi_desc1 = 'Unhealthy'
        iaqi_desc2 = 'Danger'
        display_color = 'Red'
    elif iaqi_score >= 191 and iaqi_score <= 250:
        iaqi_desc1 = 'Unhealthy for Sensitive Groups'
        iaqi_desc2 = 'Extreme Caution'
        display_color = 'Orange'
    elif iaqi_score >= 135 and iaqi_score <= 190:
        iaqi_desc1 = 'Moderate'
        iaqi_desc2 = 'Caution'
        display_color = 'Yellow'
    elif iaqi_score < 135:
        iaqi_desc1 = 'Good'
        iaqi_desc2 = ''
        display_color = 'Green'



    return jsonify({'AQI PM2.5': aqi_pm, 'AQI O3': aqi_o3, 'Heat Index': heatindex_val, 'IAQI Score': iaqi_score, 'Description 1': iaqi_desc1, 'Description 2': iaqi_desc2, 'Display Color': display_color})

@app.route('/test/')
def test():
    return jsonify({'status':'ok', 'code':'200'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, use_reloader=True)
