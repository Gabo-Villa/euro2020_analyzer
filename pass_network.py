import pandas as pd
from mplsoccer import Pitch, Sbopen
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
import matplotlib.lines as mlines
import streamlit as st


def pass_network(match_id):
    parser = Sbopen(dataframe=True)
    events, related, freeze, tactics = parser.event(match_id)
    lineup = parser.lineup(match_id)
    lineup.drop(['match_id', 'team_id', 'country_id', 'country_name'], axis=1, inplace=True)

    df_event = pd.merge(events, lineup[['player_id', 'player_nickname', 'jersey_number']], on = 'player_id')
    df_event['player_id'] = df_event['player_id'].astype(int)
    
    team1, team2 = df_event.team_name.unique()
    
    team = st.sidebar.selectbox(
    'Select a team:',
    df_event['team_name'].loc[df_event['match_id'] == match_id].unique()
    )

    rival_team = list(set(df_event.team_name.unique()) - {team})[0]
    first_sub_minute = df_event[(df_event.type_name == "Substitution") & (df_event.team_name == team)].minute.min()

    # Only the passes until the minute when the first substitution was made
    df_passes = df_event[(df_event.type_name == "Pass") &
                      (df_event.outcome_name.isnull()) &
                      (df_event.team_name == team) &
                      (df_event.minute < first_sub_minute)]

    # Average locations for players
    average_locs_and_count = df_passes.groupby('player_nickname').agg({'x': ['mean'], 'y': ['mean', 'count']})
    average_locs_and_count.columns = ['x', 'y', 'pass_count']
    average_locs_and_count = average_locs_and_count.sort_values('pass_count', ascending=False)

    lineup_dict = lineup[['player_name', 'player_nickname']].set_index('player_name').to_dict()

    df_passes['pass_recipient'] = df_passes.pass_recipient_name.apply(lambda x: lineup_dict['player_nickname'][x] if lineup_dict['player_nickname'][x] else x)

    # Combination of passes between the players
    passes_between = df_passes.groupby(['player_nickname', 'pass_recipient']).id.count().reset_index()
    passes_between.rename({'id': 'combination_pass_count'}, axis='columns', inplace=True)
    passes_between = passes_between[passes_between['combination_pass_count'] > 1]

    df_passes_plot = pd.merge(passes_between, average_locs_and_count, left_on='player_nickname', right_index=True)
    df_passes_plot = df_passes_plot.merge(average_locs_and_count, left_on='pass_recipient', right_index=True, suffixes=['', '_end'])
    df_passes_plot = df_passes_plot.sort_values('combination_pass_count', ascending=False)
    
    # Line width and marker size
    MAX_LINE_WIDTH = 10
    MAX_MARKER_SIZE = 2000
    df_passes_plot['width'] = (df_passes_plot.combination_pass_count / df_passes_plot.combination_pass_count.max() *
                           MAX_LINE_WIDTH)
    df_passes_plot['marker_size'] = (df_passes_plot['pass_count']
                                    / df_passes_plot['pass_count'].max() * MAX_MARKER_SIZE)
    
    # The colors for each team
    if team == team1:
        team_color = '#ba495c'
    elif team == team2:
        team_color = '#697cd4'
    
    # Transparency for the lines, less transparent = more passes and more transparent = less passes
    MIN_TRANSPARENCY = 0.2
    color = np.array(to_rgba(team_color))
    color = np.tile(color, (len(df_passes_plot), 1))
    c_transparency = df_passes_plot.combination_pass_count / df_passes_plot.combination_pass_count.max()
    c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency

    # Setup the pitch
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(14, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor('w')

    # Plot lines and nodes
    pass_lines = pitch.lines(df_passes_plot.x, df_passes_plot.y,
                             df_passes_plot.x_end, df_passes_plot.y_end, lw=df_passes_plot.width,
                             color=color, zorder=1, ax=ax)
    pass_nodes = pitch.scatter(df_passes_plot.x, df_passes_plot.y,
                               s=df_passes_plot.marker_size,
                               color='white', edgecolors=color, linewidth=2, alpha=1, ax=ax)
    for index, row in df_passes_plot.iterrows():
        pitch.annotate(row.player_nickname, xy=(row.x, row.y), va='center',
                       ha='center', size=16, weight='bold', ax=ax)

    # Title
    ax.set_title(f"{team} Pass Network vs. {rival_team}\n Until First Sub - {first_sub_minute}'", fontsize=30, color="black", fontweight='bold', pad=-20)

    # Legend
    line_width = mlines.Line2D([], [], color=team_color, label='Width: Number of passes between the players')
    circle_size = mlines.Line2D([], [], color='w', marker='o', markersize=20, markeredgecolor=team_color, label='Size: Number of passes')
    ax.legend(handles=[line_width, circle_size], fontsize=15, loc = 'lower left', frameon = False, borderaxespad=-1.5)

    st.markdown('__Statistics until the minute of the first substitution:__')
    st.write(f'Passes completed by {team}: {len(df_passes.id)}')
    st.write(f'Player with most passes: {average_locs_and_count.index[0]} ({average_locs_and_count.pass_count[0]})')
    st.write(f'Most frequent pass combination: {df_passes_plot.player_nickname.iloc[0]} - {df_passes_plot.pass_recipient.iloc[0]} ({df_passes_plot.combination_pass_count.iloc[0]})')

    return fig
