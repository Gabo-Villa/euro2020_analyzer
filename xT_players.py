import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mplsoccer import Sbopen
import os.path
import streamlit as st

@st.cache_data
def xT_players(match_id):
    parser = Sbopen(dataframe=True)
    events, related, freeze, tactics = parser.event(match_id)
    lineup = parser.lineup(match_id)
    lineup.drop(['player_name', 'match_id', 'team_name','team_id', 'country_id', 'country_name'], axis=1, inplace=True)

    df_event = pd.merge(events, lineup, on = 'player_id')
    df_event['player_id'] = df_event['player_id'].astype(int)

    # The xT is calculated using passes and carries
    df_xT = df_event.loc[(df_event['type_name'] == 'Pass') | (df_event['type_name'] == 'Carry')][df_event['outcome_name'].isnull()]
    path = os.path.dirname(__file__)
    # xT grid from: github.com/mckayjohns/xT/blob/main/xT_Grid.csv
    xT_grid = path +'/xT_Grid.csv'
    
    xT_grid = pd.read_csv(xT_grid, header=None)
    xT_grid = np.array(xT_grid)
    xT_rows, xT_cols = xT_grid.shape

    df_xT['x1_bin'] = pd.cut(df_xT['x'], bins = xT_cols, labels = False)
    df_xT['y1_bin'] = pd.cut(df_xT['y'], bins = xT_rows, labels = False)
    df_xT['x2_bin'] = pd.cut(df_xT['end_x'], bins = xT_cols, labels = False)
    df_xT['y2_bin'] = pd.cut(df_xT['end_y'], bins = xT_rows, labels = False)
    df_xT['start_zone_value'] = df_xT[['x1_bin', 'y1_bin']].apply(lambda x: xT_grid[x[1]][x[0]], axis=1)
    df_xT['end_zone_value'] = df_xT[['x2_bin', 'y2_bin']].apply(lambda x: xT_grid[x[1]][x[0]], axis=1)
    df_xT['xT'] = df_xT['end_zone_value'] - df_xT['start_zone_value']
    df_xT['xT_player'] = df_xT['player_nickname'].apply(lambda x: df_xT['xT'].loc[df_xT['player_nickname'] == x].sum())

    player_list = []
    xT_list = []
    team_list = []

    # Append the xT value and the team of the players into the lists
    for x in df_xT['player_nickname'].unique():
        player_xT = df_xT.loc[df_xT['player_nickname'] == x]
        sum_xT = player_xT['xT'].sum()
        team = player_xT['team_name'].iloc[0]
        player_list.append(x)
        xT_list.append(sum_xT)
        team_list.append(team)
    
    df_plot = pd.DataFrame({
    'player' : player_list,
    'xT' : xT_list,
    'team' : team_list
    })
    df_plot = df_plot.sort_values(by='xT', ascending=True)

    team1, team2 = df_event.team_name.unique()

    fig, ax = plt.subplots(figsize = (14,11), constrained_layout=True, tight_layout=False,)
    # Plot the xT values
    barlist = ax.barh(df_plot['player'], df_plot['xT'])
    # Title and axis label
    ax.set_title('xT Players Performance', ha='center', fontsize=30, fontweight='bold')
    plt.xlabel('xT', fontsize=15)

    for label in ax.get_yticklabels():
        label.set(fontsize=15)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.axvline(x=0, color='k', linestyle='--')

    # Change the color depending of the team
    i = 0
    for team in df_plot['team']:
        if team == team1:
            barlist[i].set_color('#ba495c')
            i += 1
        elif team == team2:
            barlist[i].set_color('#697cd4')
            i += 1

    #Legend
    team1_patch = mpatches.Patch(color='#ba495c', label=team1)
    team2_patch = mpatches.Patch(color='#697cd4', label=team2)
    ax.legend(handles=[team1_patch, team2_patch], fontsize=30, frameon = False)

    return fig
