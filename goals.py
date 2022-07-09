import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch
from mplsoccer.statsbomb import read_event, read_lineup, EVENT_SLUG, LINEUP_SLUG
import streamlit as st

def goals(match_id):
    dict_event = read_event(f'{EVENT_SLUG}/{match_id}.json', related_event_df=False, tactics_lineup_df=False, warn=False)
    df_event = dict_event['event']
    df_freeze = dict_event['shot_freeze_frame']
    df_lineup = read_lineup(f'{LINEUP_SLUG}/{match_id}.json', warn=False)
    df_lineup1 = df_lineup[['player_id', 'player_nickname', 'player_jersey_number']]

    df_event = pd.merge(df_event, df_lineup1, on = 'player_id')
    df_event['player_id'] = df_event['player_id'].astype(int)
    # If available, use player's nickname instead of full name
    df_event['player'] = df_event[['player_nickname', 'player_name']].apply(lambda x: x[0] if x[0] else x[1], axis=1)

    # Period !=5 because the 5th period is the penalty shootout
    df_goals = df_event.loc[df_event['outcome_name']=='Goal'][df_event['period'] != 5]
    df_goals = df_goals.sort_values('minute')

    if len(df_goals) == 0:
        st.text('There are no goals in this match')
    else:
        goals = st.sidebar.selectbox(
        'Select a goal:',
        df_goals['player'].loc[df_goals['match_id']==match_id] + ' ' + df_goals['minute'].astype(str).loc[df_goals['match_id']==match_id]
                 + ':' + df_goals['second'].astype(str).loc[df_goals['match_id']==match_id]
        )

        shot_id = df_goals['id'].loc[df_goals['player'] + ' ' + df_goals['minute'].astype(str) + ':' + df_goals['second'].astype(str) == goals]
        shot_id = shot_id.to_string(index=False)

        df_shot_event = df_event[df_event['id'] == shot_id].dropna(axis=1, how='all')
        df_freeze_frame = df_freeze[df_freeze['id'] == shot_id]
        df_lineup2 = df_lineup[['player_id', 'player_name', 'player_nickname','player_jersey_number', 'team_name']].copy()
        # If available, use player's nickname instead of full name
        df_lineup2['player'] = df_lineup2[['player_nickname', 'player_name']].apply(lambda x: x[0] if x[0] else x[1], axis=1)
        df_freeze_frame = df_freeze_frame.merge(df_lineup2, how='left', on='player_id')

        team1 = df_shot_event.team_name.iloc[0]
        team2 = list(set(df_event.team_name.unique()) - {team1})[0]

        df_shot_event = df_shot_event.reset_index(drop=True)
        shooter = df_shot_event['player'].to_string(index=False)
        shooter_team = df_shot_event['team_name'][0]

        df_team1 = df_freeze_frame[df_freeze_frame['team_name'] == shooter_team]
        df_team2_goalkeeper = df_freeze_frame.loc[df_freeze_frame['team_name'] != shooter_team][df_freeze_frame['player_position_name'] == 'Goalkeeper']
        df_team2_other = df_freeze_frame.loc[df_freeze_frame['team_name'] != shooter_team][df_freeze_frame['player_position_name'] != 'Goalkeeper']

        # Setup the pitch
        pitch = VerticalPitch(half=True, goal_type='box', pad_bottom=-20)

        # Mplsoccer's grid function to plot a pitch with a title axis.
        fig, axs = pitch.grid(figheight=8, endnote_height=0,
                        title_height=0.1, title_space=0.02,
                        axis=False,
                        grid_height=0.83)
        
        # Set font
        plt.rcParams['font.family'] = 'Franklin Gothic Medium'
                      
        # Plot the players
        sc1 = pitch.scatter(df_team1['x'], df_team1['y'], s=700, c='#ba495c', label=team1, ax=axs['pitch'])
        sc2 = pitch.scatter(df_team2_other['x'], df_team2_other['y'], s=700,
                        c='#697cd4', label=team2, ax=axs['pitch'])
        sc4 = pitch.scatter(df_team2_goalkeeper['x'], df_team2_goalkeeper['y'], s=700,
                        ax=axs['pitch'], c='#5ba965', label='Goalkeeper')

        # Plot the shot
        sc3 = pitch.scatter(df_shot_event['x'], df_shot_event['y'], marker='football',
                        s=700, ax=axs['pitch'], label=shooter, zorder=1.2)
        line = pitch.lines(df_shot_event['x'], df_shot_event['y'],
                        df_shot_event['end_x'], df_shot_event['end_y'], comet=True,
                        label='Shot', color='#cb5a4c', ax=axs['pitch'])

        # Plot the angle to the goal
        pitch.goal_angle(df_shot_event['x'], df_shot_event['y'], ax=axs['pitch'], alpha=0.2, zorder=1.1,
                        color='#cb5a4c', goal='right')

        # Plot the jersey numbers
        for i, label in enumerate(df_freeze_frame['player_jersey_number']):
            pitch.annotate(label, (df_freeze_frame['x'][i], df_freeze_frame['y'][i]),
                        va='center', ha='center', color='white',
                        fontsize=15, ax=axs['pitch'])

        # Legend
        legend = axs['pitch'].legend(loc='upper left', labelspacing=1.5)
        for text in legend.get_texts():
            text.set_fontsize(25)
            text.set_va('center')

        # Title
        axs['title'].text(0.5, 0.5, f'{shooter} \n{df_shot_event.minute.astype(str).iloc[0]}:{df_shot_event.second.astype(str).iloc[0]}\nxG: {round(df_shot_event.shot_statsbomb_xg.iloc[0], 2)}',
                        va='center', ha='center', color='black',
                        fontsize=30)

        st.pyplot(fig)