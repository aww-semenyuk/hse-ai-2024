import pandas as pd
import streamlit as st
import datetime
import httpx
import requests
import asyncio
from aiocache import Cache, cached
from statsmodels.tsa.arima.model import ARIMA
from scipy.constants import convert_temperature
from functools import reduce
from copy import deepcopy

OPENWEATHERAPI_BASEURL = 'https://api.openweathermap.org/data/2.5/weather'
ARIMA_NUM_PERIODS = 7

season_months = {'winter': [12, 1, 2], 
                 'spring': [3, 4, 5],
                 'summer': [6, 7, 8],
                 'autumn': [9, 10, 11]}
season_months_map = reduce(lambda a, b: {**a, **b}, [{str(month): season for month in months} for season, months in season_months.items()])

@st.cache_data(ttl=3600, show_spinner=False)
def analyze_temperature(data):
    """
    Returns 2 DataFrames:
        - copy of 'data' with 30 days rolling mean and std + anomaly flag
        - season profile for each city-season pair
    """
    data_w_anomaly_ = data \
        .pipe(lambda df: pd.concat((
            df,
            df.groupby('city', sort=False) \
              .rolling(datetime.timedelta(days=30), on='timestamp', closed='left')['temperature'] \
              .agg({'mean_30d': 'mean', 'std_30d': 'std'}) \
              .reset_index(drop=True)), axis=1)) \
        .assign(is_anomaly_temp=lambda df: (df['temperature'] < df['mean_30d']-2*df['std_30d']) | (df['temperature'] > df['mean_30d']+2*df['std_30d']))

    data_season_profiles_ = data \
        .groupby(['city', 'season'], as_index=False)['temperature'] \
        .agg(['mean', 'std', 'min', 'max'])

    return data_w_anomaly_, data_season_profiles_

@st.cache_data(ttl=3600, show_spinner=False)
def forecast_temperature(data, num_periods):
    """
    Return copy of 'data' DataFrame with 'num_periods' periods forecast appended
    """
    data_w_fc = deepcopy(data)

    for city in data['city'].unique():
        tmp_data = data[data['city']==city].set_index('timestamp')
        tmp_data.index.freq = 'D'

        arima = ARIMA(tmp_data['temperature'], order=(5, 1, 0), freq='D').fit()

        tmp_forecast = pd.DataFrame.from_dict(
            {'timestamp': pd.date_range(start=tmp_data.index.values[-1] + pd.Timedelta(days=1), periods=num_periods, freq='D').values,
             'temperature': arima.forecast(steps=num_periods).values}) \
             .assign(city=city, season=lambda df: df['timestamp'].dt.month.astype('str').map(season_months_map))
        
        data_w_fc = pd.concat((data_w_fc, tmp_forecast))

    return data_w_fc.reset_index(drop=True)

@st.cache_data(ttl=3600, show_spinner=False)
def test_api_call(api_key):
    """
    Test API for supplied key
    """
    response = requests.get(OPENWEATHERAPI_BASEURL, params={'q': 'New York', 'appid': api_key})
    return response

@cached(ttl=3600, cache=Cache.MEMORY)
async def fetch_data(url, params_list):
    """
    Fetch several http requests using async client 
    """
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url, params=params) for params in params_list]
        responses = await asyncio.gather(*tasks)

    results = {}
    for params, response in zip(params_list, responses):
        if response.status_code==200:
            results[params['q']] = response.json()

    return results

@cached(ttl=3600, cache=Cache.MEMORY)
async def get_current_weather(list_cities, api_key):
    """
    Send async requests to OpenWeatherAPI
    """
    params_list = [{'q': city, 'appid': api_key} for city in list_cities]

    results = await fetch_data(OPENWEATHERAPI_BASEURL, params_list)

    curr_weather_dict = {}
    for key, val in results.items():
        curr_weather_dict[key] = {'main': val['weather'][0]['main'], 
                                  'temp': convert_temperature(val['main']['temp'], 'Kelvin', 'Celsius'),
                                  'feels_like': convert_temperature(val['main']['feels_like'], 'Kelvin', 'Celsius'),
                                  'country': val['sys']['country'],
                                  'datetime': datetime.datetime.fromtimestamp(val['dt']).isoformat()}

    return curr_weather_dict
