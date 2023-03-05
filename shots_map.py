import matplotlib.pyplot as plt
from mplsoccer import Pitch, Sbopen
import streamlit as st
from matplotlib.patches import Circle
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea

@st.cache_data
def shots_map(match_id):
    parser = Sbopen(dataframe=True)
    events, related, freeze, tactics = parser.event(match_id)
    df = events
    # Period !=5 because the 5th period is the penalty shootout
    df_no_penalties = df[df.period != 5]
    # There are included the shots and the own goals
    df_shots = df_no_penalties[(df.type_name == 'Shot') | (df.type_name == 'Own Goal For')]
    # Replace the outcome name of the own goals to be a goal
    df_shots['outcome_name'] = df_shots['outcome_name'].apply(lambda x: str(x).replace('nan', 'Goal'))
    # Replace the null xG values with 0
    df_shots['shot_statsbomb_xg'] = df_shots['shot_statsbomb_xg'].fillna(0)
    
    team1, team2 = df.team_name.unique()
    df_team1 = df_shots[df_shots.team_name == team1]
    df_team2 = df_shots[df_shots.team_name == team2]

    # Setup the pitch
    pitch = Pitch(pitch_type='statsbomb')
    fig, ax = pitch.draw(figsize=(14, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor('w')

    # The data is collected so the attacking direction is left to right
    # We can shift the coordinates via: new_x_coordinate = right_side - old_x_coordinate
    # This is done to have one team shots on the left of the pitch and the other on the right
    df_team1['x'] = pitch.dim.right - df_team1.x

    df_team1_goals = df_team1[df_team1.outcome_name == 'Goal']
    team1_goals_count = df_team1_goals.count()[0]
    df_team1_non_goals = df_team1[df_team1.outcome_name != 'Goal']
    team1_owngoals_count = df_team1[df_team1.type_name == 'Own Goal For'].count()[0]
    team1_shots_count = df_team1_goals.count()[0] + df_team1_non_goals.count()[0] - team1_owngoals_count
    team1_xG = round(df_team1.shot_statsbomb_xg.sum(), 2)
    
    df_team2_goals = df_team2[df_team2.outcome_name == 'Goal']
    team2_goals_count = df_team2_goals.count()[0]
    df_team2_non_goals = df_team2[df_team2.outcome_name != 'Goal']
    team2_owngoals_count = df_team2[df_team2.type_name == 'Own Goal For'].count()[0]
    team2_shots_count = df_team2_goals.count()[0] + df_team2_non_goals.count()[0] - team2_owngoals_count
    team2_xG = round(df_team2.shot_statsbomb_xg.sum(), 2)

    # Plot team 1non-goal shots
    team1_non_goals = pitch.scatter(df_team1_non_goals.x, df_team1_non_goals.y,
                    s=(df_team1_non_goals.shot_statsbomb_xg * 1900) + 100,
                    edgecolors='#606060', c='None', hatch='///',
                    marker='o', ax=ax)

    # Plot team 1 goal shots
    team1_goals = pitch.scatter(df_team1_goals.x, df_team1_goals.y,
                    s=(df_team1_goals.shot_statsbomb_xg * 1900) + 100,
                    edgecolors='#606060', c='#b94b75', marker='o', ax=ax)

    # Plot team 2 non-goal shots
    team2_non_goals = pitch.scatter(df_team2_non_goals.x, df_team2_non_goals.y,
                    s=(df_team2_non_goals.shot_statsbomb_xg * 1900) + 100,
                    edgecolors='#606060', c='None', hatch='///',
                    marker='o', ax=ax)

    # Plot team 2 goal shots
    team2_goals = pitch.scatter(df_team2_goals.x, df_team2_goals.y,
                    s=(df_team2_goals.shot_statsbomb_xg * 1900) + 100,
                    edgecolors='#606060', c='#697cd4', marker='o', ax=ax)

    # Legend
    ada = AnchoredDrawingArea(40, 20, 0, 0, loc='upper left', pad=1, frameon=False)
    p1 = Circle((30, -15), 5, fc="w", ec="k")
    ada.drawing_area.add_artist(p1)
    p2 = Circle((50, -15), 10, fc="w", ec="k")
    ada.drawing_area.add_artist(p2)
    p3 = Circle((80, -15), 15, fc="w", ec="k")
    ada.drawing_area.add_artist(p3)
    p4 = Circle((35, -55), 15, fc="#ba495c", ec="k")
    ada.drawing_area.add_artist(p4)
    p5 = Circle((70, -55), 15, fc="#697cd4", ec="k")
    ada.drawing_area.add_artist(p5)
    ax.add_artist(ada)
    txt1 = ax.text(x=26, y=4.5, s='xG Value', color='k',
                    ha='center', va='center', fontsize=30)
    txt2 = ax.text(x=19, y=11.5, s='Goal', color='k',
                    ha='center', va='center', fontsize=30)

    txt3 = ax.text(x=50, y=-18, s=team1, color='#ba495c', fontweight='bold', 
                    ha='right', va='center', fontsize=30)
    txt4 = ax.text(x=70, y=-18, s=team2, color='#697cd4', fontweight='bold', 
                    ha='left', va='center', fontsize=30)
    txt5 = ax.text(x=60, y=-12, s=f'{team1_goals_count}     Goals     {team2_goals_count}',
                    ha='center', va='center', fontsize=30)
    txt6 = ax.text(x=60, y=-7, s=f'{team1_shots_count}     Shots     {team2_shots_count}',
                    ha='center', va='center', fontsize=30)
    txt7 = ax.text(x=60, y=-2, s=f'{team1_xG}       xG       {team2_xG}',
                    ha='center', va='center', fontsize=30)

    return fig
