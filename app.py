import streamlit as st
from mplsoccer import Sbopen
import os.path
from pathlib import Path
import base64
from shots_map import shots_map
from heatmap_passes import heatmap_passes
from xG_flowchart import xG_flowchart
from goals import goals
from xT_players import xT_players
from pass_network import pass_network
from players_statistics import players_statistics


st.set_page_config(page_title='Euro 2020 Analyzer', page_icon='⚽')
st.title('Euro 2020 Analyzer')

# Convert the image to bytes so that it can be displayed using an <img> HTML element
# Code snippet from: pmbaumgartner.github.io/streamlitopedia/sizing-and-images.html
@st.cache_data
def img_to_bytes(img_path):
    path = os.path.dirname(__file__)
    euro_image = path + '/euro_2020.png'
    img_bytes = Path(euro_image).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


st.sidebar.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=140 height=140>](https://www.uefa.com/uefaeuro/history/seasons/2020/)'''.format(img_to_bytes("euro_2020.png")), unsafe_allow_html=True)

categories = st.sidebar.selectbox(
    'Select the category:',
    ['Matches', 'Players'])

if categories == 'Matches':
    parser = Sbopen(dataframe=True)
    matches = parser.match(competition_id = 55, season_id = 43)
    matches = matches.sort_values('match_date')
    matches['match'] = matches.home_team_name + ' vs. ' + matches.away_team_name

    stages_unique = matches['competition_stage_name'].unique().tolist()

    competition_stage = st.sidebar.selectbox(
    'Select a stage of the tournament:',
    stages_unique)

    match = st.sidebar.selectbox(
    'Select a match:',
    matches['match'].loc[matches['competition_stage_name'] == competition_stage])

    match_id = int(matches['match_id'].loc[matches['match'] == match])

    visualizations = st.sidebar.selectbox(
    'Select a visualization:',
    ['Shots Map', 'Heatmap (Passes locations)', 'xG Flow Chart', 'Goals', 'xT Players Performance', 'Pass Network'])
    if visualizations == 'Shots Map':
        st.pyplot(shots_map(match_id))
    elif visualizations == 'Heatmap (Passes locations)':
        st.pyplot(heatmap_passes(match_id))
    elif visualizations == 'xG Flow Chart':
        st.pyplot(xG_flowchart(match_id))
        st.sidebar.write('[What are Expected Goals (xG)?](https://theanalyst.com/eu/2021/07/what-are-expected-goals-xg/)')
    elif visualizations == 'Goals':
        st.pyplot(goals(match_id))
    elif visualizations == 'xT Players Performance':
        st.pyplot(xT_players(match_id))
        st.sidebar.write('[What is Expected Threat (xT)?](https://karun.in/blog/expected-threat.html)')
    elif visualizations == 'Pass Network':
        st.pyplot(pass_network(match_id))

elif categories == 'Players':
    tables = st.sidebar.selectbox(
        'Select a table:',
        ['Goals', 'Assists', 'Red cards', 'Saves'])
    
    st.pyplot(players_statistics(tables))

with st.sidebar.expander('About the project'):
    st.write('Data visualization app to analyze the Euro 2020. All the data is provided by [Statsbomb](https://statsbomb.com/).')
