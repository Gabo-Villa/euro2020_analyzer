import matplotlib.pyplot as plt
import matplotlib as mpl
import mplcyberpunk
from mplsoccer import Sbopen
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import streamlit as st

@st.cache_data
def xG_flowchart(match_id):
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

    # The lists start with 0 so the charts will start at 0
    team1_xG = [0]
    team2_xG = [0]
    team1_min = [0]
    team2_min = [0]
    team1_outcome = ['None']
    team2_outcome = ['None']

    # Append the xG, minute and outcome of the shots into the lists
    for x in range(len(df_shots['minute'])):
        if df_shots['team_name'].iloc[x] == team1:
            team1_xG.append(df_shots['shot_statsbomb_xg'].iloc[x])
            team1_min.append(df_shots['minute'].iloc[x])
            team1_outcome.append(df_shots['outcome_name'].iloc[x])
        elif df_shots['team_name'].iloc[x] == team2:
            team2_xG.append(df_shots['shot_statsbomb_xg'].iloc[x])
            team2_min.append(df_shots['minute'].iloc[x])
            team2_outcome.append(df_shots['outcome_name'].iloc[x])
    
    # It goes through the list and make the xG values be cumulative
    def nums_cumulative_sum(nums_list):
        return [sum(nums_list[:i+1]) for i in range(len(nums_list))]

    team1_cumulative_xG = nums_cumulative_sum(team1_xG)
    team2_cumulative_xG = nums_cumulative_sum(team2_xG)

    fig, ax = plt.subplots(figsize = (14,11), constrained_layout=True, tight_layout=False,)
    fig.set_facecolor('w')
    ax.patch.set_facecolor('w')

    mpl.rcParams['xtick.color'] = 'k'
    mpl.rcParams['ytick.color'] = 'k'

    # The game lasts 90 minutes if there are 2 periods, if there is a 3th period the game lasts 120 minutes
    if 3 not in df['period']:
        plt.xticks([0,15,30,45,60,75,90])
    else:
        plt.xticks([0,15,30,45,60,75,90,105,120])

    # Title and axis label
    plt.title('xG Flow Chart', fontsize=30, fontweight='bold')
    plt.xlabel('Minute', fontsize=20)
    plt.ylabel('xG', fontsize=20)

    # Plot the xG values
    ax.step(x=team1_min, y=team1_cumulative_xG, linewidth=4, where='post', color='#ba495c')
    ax.step(x=team2_min, y=team2_cumulative_xG, linewidth=4, where='post', color='#697cd4')

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Plot team 1 goals
    for x in range(len(team1_outcome)):
        if team1_outcome[x] == 'Goal':
            ax.scatter(x=team1_min[x], y=team1_cumulative_xG[x], s=1000, color='#ba495c', marker='*')
        else:
            pass

    # Plot team 2 goals
    for x in range(len(team2_outcome)):
        if team2_outcome[x] == 'Goal':
            ax.scatter(x=team2_min[x], y=team2_cumulative_xG[x], s=1000, color='#697cd4', marker='*')
        else:
            pass

    # Legend
    team1_patch = mpatches.Patch(color='#ba495c', label=f'{team1}: {str(round(team1_cumulative_xG[-1],2))} xG')
    team2_patch = mpatches.Patch(color='#697cd4', label=f'{team2}: {str(round(team2_cumulative_xG[-1],2))} xG')
    goal_marker = mlines.Line2D([], [], color='w', marker='*', markersize=40, markeredgecolor='k', label='Goal')
    ax.legend(handles=[team1_patch,team2_patch,goal_marker], fontsize=30, frameon = False)

    mplcyberpunk.add_underglow()

    return fig