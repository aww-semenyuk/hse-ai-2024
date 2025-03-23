import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
import datetime
from pathlib import Path

from utils import test_api_call, analyze_temperature, forecast_temperature, get_current_weather, season_months_map, ARIMA_NUM_PERIODS

st.title('Temperature data analyzer')

api_key = st.text_input(r'$\large{\text{Enter your OpenWeather API key for getting current weather}}$', type='password')
if api_key is not None and st.button('Click to test API key'):
    response = test_api_call(api_key)
    if response.status_code==200:
        st.success('API test successful')
    else:
        st.warning(f'API test failed with code {response.status_code}, response={response.text}')

uploaded_file = st.file_uploader(r'$\large{\text{Upload historical temperature data. Otherwise sample data will be used.}}$')

if 'button' not in st.session_state:
    st.session_state['button'] = False

def click_button():
    st.session_state['button'] = not st.session_state['button']

st.button('Process data', on_click=click_button)

if st.session_state['button']:
    if not uploaded_file:
        data = pd.read_csv(Path(__file__).parent / 'temperature_data.csv', parse_dates=['timestamp'])
    else:
        data = pd.read_csv(uploaded_file, parse_dates=['timestamp'])

    if 'curr_weather_dict' not in st.session_state:
        st.session_state['curr_weather_dict'] = {}

    with st.spinner('Data is being processed...'):
        cities = data['city'].unique().tolist()
        data_w_anomaly, data_season_profiles = analyze_temperature(data)
        data_w_fc = forecast_temperature(data, num_periods=ARIMA_NUM_PERIODS)
        curr_weather_dict = asyncio.run(get_current_weather(cities, api_key))

    st.success('Data processing finished')

    city_choice = st.selectbox(r'$\large{\text{Choose a city to analyze}}$', options=cities, index=None, placeholder='...')
    if city_choice is not None:
        st.header('Historical data overview')

        time_range_options = pd.to_datetime(data_w_anomaly.loc[lambda df: df['city']==city_choice]['timestamp'].to_numpy().astype('datetime64[M]')).unique()
        time_from, time_to = st.select_slider(r'$\large{\text{Select time range to plot historical data}}$', 
                                              options=time_range_options, 
                                              value=(time_range_options.min(), time_range_options.max()))

        tmp_df = data_w_anomaly.loc[lambda df: (df['city']==city_choice) & (df['timestamp'] >= time_from) & (df['timestamp'] <= time_to)]

        fig, ax = plt.subplots(figsize=(14, 4))

        ax.plot('timestamp', 'temperature', data=tmp_df, lw=0.5, alpha=0.7, label='temperature')
        ax.scatter('timestamp', 'temperature', data=tmp_df[tmp_df['is_anomaly_temp']], marker='.', color='tab:red', s=20, label='anomalies')
        ax.fill_between(x=tmp_df['timestamp'],
                        y1=tmp_df['mean_30d']+2*tmp_df['std_30d'],
                        y2=tmp_df['mean_30d']-2*tmp_df['std_30d'],
                        alpha=0.2, color='skyblue', label='mean$\pm$2*std (30d rolling)')

        ax.legend()

        ax.set_title(f'Historical temperature data for {city_choice}')
        ax.legend()

        st.pyplot(fig)

        trend_act = data_w_fc.loc[lambda df: (df['city']==city_choice)].tail(2*ARIMA_NUM_PERIODS).head(ARIMA_NUM_PERIODS)['temperature'].mean()
        trend_fc = data_w_fc.loc[lambda df: (df['city']==city_choice)].tail(ARIMA_NUM_PERIODS)['temperature'].mean()
        st.info(f'The temperature is likely to {"decline" if (trend_fc-trend_act)<0 else "increase"} in the next {ARIMA_NUM_PERIODS} days')

        st.header('Current weather overview')
        if city_choice not in curr_weather_dict:
            st.warning(f'Weather for {city_choice} not found, please check the spelling or your API key')
        else:
            st.markdown(
            f'''**Weather overview in {city_choice}, {curr_weather_dict[city_choice]['country']}. Data actual for {curr_weather_dict[city_choice]['datetime']}:**\\
                {curr_weather_dict[city_choice]['main']}, temperature is {curr_weather_dict[city_choice]['temp']:.1f}&deg;C, feels like {curr_weather_dict[city_choice]['feels_like']:.1f}&deg;C
            ''')

            st.write('Season profile (based on past data):')
            data_season_profile_tmp = data_season_profiles.loc[lambda df: (df['season']==season_months_map[str(datetime.datetime.fromisoformat(curr_weather_dict[city_choice]['datetime']).month)]) & 
                                                                          (df['city']==city_choice)]
            st.table(data_season_profile_tmp)

            mean_tmp, std_tmp = data_season_profile_tmp.T.loc['mean'].values[0], data_season_profile_tmp.T.loc['std'].values[0]
            if (curr_weather_dict[city_choice]['temp'] < mean_tmp-2*std_tmp) or (curr_weather_dict[city_choice]['temp'] > mean_tmp+2*std_tmp):
                st.info('Current temperature is NOT normal judging by season profile')
            else:
                st.info('Current temperature is normal judging by season profile')
