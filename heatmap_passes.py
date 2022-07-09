from mplsoccer import VerticalPitch
from mplsoccer.statsbomb import read_event, EVENT_SLUG
import streamlit as st

def heatmap_passes(match_id):
    event_dict = read_event(f'{EVENT_SLUG}/{match_id}.json', related_event_df=False, tactics_lineup_df=False, warn=False)
    df = event_dict['event']
    df_passes = df[df.type_name == 'Pass']
    team1, team2 = df.team_name.unique()
    df_team1 = df_passes[df_passes.team_name == team1]
    df_team2 = df_passes[df_passes.team_name == team2]

    pitch = VerticalPitch(line_color='#000009', line_zorder=2)
    fig, axs = pitch.grid(ncols=2, axis=False, endnote_height=0.01)


    # Team 1 heatmap
    kde_team1 = pitch.kdeplot(df_team1.x, df_team1.y, ax=axs['pitch'][0],
                           shade=True, levels=100, shade_lowest=True,
                           cut=4, cmap='Reds')

    # Team 2 heatmap
    kde_team2 = pitch.kdeplot(df_team2.x, df_team2.y, ax=axs['pitch'][1],
                          shade=True, levels=100, shade_lowest=True,
                          cut=4, cmap='Blues')

    # Title and team names
    title = axs['title'].text(x=0.5, y=0.6, s='Heatmap\n(Passes locations)', fontsize=30, color='#000009',
                                fontname='Franklin Gothic Medium',
                                ha='center', va='center')
    txt1 = axs['title'].text(x=0.23, y=0, s=team1, fontsize=30, color='#ba495c',
                                fontname='DejaVu Sans', fontweight='bold',
                                ha='center', va='center')
    txt2 = axs['title'].text(x=0.77, y=0, s=team2, fontsize=30, color='#697cd4',
                                fontname='DejaVu Sans', fontweight='bold',
                                ha='center', va='center')

    st.pyplot(fig)