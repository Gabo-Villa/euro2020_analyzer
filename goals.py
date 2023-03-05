import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch, Sbopen
import streamlit as st

def goals(match_id):
    parser = Sbopen(dataframe=True)
    events, related, freeze, tactics = parser.event(match_id)
    lineup = parser.lineup(match_id)
    lineup.drop(['player_name', 'match_id', 'team_id', 'country_id', 'country_name'], axis=1, inplace=True)

    df_event = pd.merge(events, lineup[['player_id', 'player_nickname', 'jersey_number']], on = 'player_id')
    df_event['player_id'] = df_event['player_id'].astype(int)

    # Period !=5 because the 5th period is the penalty shootout
    df_goals = df_event.loc[df_event['outcome_name'] == 'Goal'][df_event['period'] != 5]
    df_goals = df_goals.sort_values('minute')

    if len(df_goals) == 0:
        st.text('There are no goals in this match')
    else:
        goals = st.sidebar.selectbox(
        'Select a goal:',
        df_goals['player_nickname'].loc[df_goals['match_id'] == match_id] + ' ' + df_goals['minute'].astype(str).loc[df_goals['match_id'] == match_id]
                 + ':' + df_goals['second'].astype(str).loc[df_goals['match_id'] == match_id]
        )

        shot_id = df_goals['id'].loc[df_goals['player_nickname'] + ' ' + df_goals['minute'].astype(str) + ':' + df_goals['second'].astype(str) == goals]
        shot_id = shot_id.to_string(index=False)

        df_shot_event = df_event[df_event['id'] == shot_id].dropna(axis=1, how='all')
        df_freeze_frame = freeze[freeze['id'] == shot_id]
        df_freeze_frame = df_freeze_frame.merge(lineup, how='left', on='player_id')

        team1 = df_shot_event.team_name.iloc[0]
        team2 = list(set(df_event.team_name.unique()) - {team1})[0]
        
        df_shot_event = df_shot_event.reset_index(drop=True)
        shooter = df_shot_event['player_nickname'].to_string(index=False)

        df_team1 = df_freeze_frame[df_freeze_frame['team_name'] == team1]
        df_team2_goalkeeper = df_freeze_frame.loc[df_freeze_frame['team_name'] == team2][df_freeze_frame['position_name'] == 'Goalkeeper']
        df_team2_other = df_freeze_frame.loc[df_freeze_frame['team_name'] == team2][df_freeze_frame['position_name'] != 'Goalkeeper']

        # Setup the pitch
        pitch = VerticalPitch(half=True, goal_type='box', pad_bottom=-20)

        # Mplsoccer's grid function to plot a pitch with a title axis.
        fig, axs = pitch.draw(figsize=(14, 11), constrained_layout=True, tight_layout=False)
                      
        # Plot the players
        sc1 = pitch.scatter(df_team1['x'], df_team1['y'], s=700, c='#ba495c', label=team1, ax=axs)
        sc2 = pitch.scatter(df_team2_other['x'], df_team2_other['y'], s=700, c='#697cd4', label=team2, ax=axs)
        sc4 = pitch.scatter(df_team2_goalkeeper['x'], df_team2_goalkeeper['y'], s=700, ax=axs, c='#5ba965', label='Goalkeeper')

        # Plot the shot
        sc3 = pitch.scatter(df_shot_event['x'], df_shot_event['y'], marker='football', s=700, ax=axs, label=shooter, zorder=1.2)
        line = pitch.lines(df_shot_event['x'], df_shot_event['y'], df_shot_event['end_x'], df_shot_event['end_y'], comet=True, 
                           label='Shot', color='#cb5a4c', ax=axs)

        # Plot the angle to the goal
        pitch.goal_angle(df_shot_event['x'], df_shot_event['y'], ax=axs, alpha=0.2, zorder=1.1, color='#cb5a4c', goal='right')

        # Plot the jersey numbers
        for i, label in enumerate(df_freeze_frame['jersey_number']):
            pitch.annotate(label, (df_freeze_frame['x'][i], df_freeze_frame['y'][i]), va='center', ha='center', 
                                   color='white', fontsize=15, ax=axs)

        axs.legend(fontsize = 20, loc = 'upper left', labelspacing=0.5)

        minute_goal = df_shot_event.minute.astype(str).iloc[0]
        second_goal = df_shot_event.second.astype(str).iloc[0]
        xG_goal = round(df_shot_event.shot_statsbomb_xg.iloc[0], 2)
        body_part_goal = df_shot_event['body_part_name'][0]
        play_pattern_goal = df_shot_event['play_pattern_name'][0]
        
        axs.set_title(f'{shooter} {minute_goal}:{second_goal}\nBody part: {body_part_goal}\n{play_pattern_goal}\nxG: {xG_goal}', ha='center', fontsize=25)

        return fig
