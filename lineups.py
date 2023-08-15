from mplsoccer import VerticalPitch, Sbopen
import pandas as pd
import streamlit as st


@st.cache_data
def lineups(match_id):
    parser = Sbopen(dataframe=True)
    events, related, freeze, tactics = parser.event(match_id)
    lineup = parser.lineup(match_id)
    lineup.drop(
        [
            "match_id",
            "team_id",
            "country_id",
            "country_name",
            "jersey_number",
            "player_name",
        ],
        axis=1,
        inplace=True,
    )

    df_tactics = pd.merge(tactics, lineup, how="left", on="player_id")
    df_tactics["player_id"] = df_tactics["player_id"].astype(int)

    team1, team2 = events.team_name.unique()

    starting_xi_event_1 = events.loc[
        ((events["type_name"] == "Starting XI") & (events["team_name"] == team1)),
        ["id", "tactics_formation"],
    ]
    starting_xi_event_2 = events.loc[
        ((events["type_name"] == "Starting XI") & (events["team_name"] == team2)),
        ["id", "tactics_formation"],
    ]

    starting_xi_1 = df_tactics.merge(starting_xi_event_1, on="id")
    starting_xi_2 = df_tactics.merge(starting_xi_event_2, on="id")

    formation_1 = events.tactics_formation.iloc[0]
    formation_2 = events.tactics_formation.iloc[1]

    pitch = VerticalPitch()
    fig, axs = pitch.grid(
        ncols=2, axis=False, endnote_height=0.01, title_height=0.01, figheight=13
    )

    # Team 1
    txt1 = axs["title"].text(
        x=0.23,
        y=0,
        s=team1,
        fontsize=30,
        color="#ba495c",
        fontweight="bold",
        ha="center",
        va="center",
    )
    ax_text1 = pitch.formation(
        formation_1,
        positions=starting_xi_1.position_id,
        kind="text",
        text=starting_xi_1.player_nickname.str.replace(" ", "\n"),
        va="center",
        ha="center",
        fontsize=16,
        ax=axs["pitch"][0],
    )
    ax_scatter1 = pitch.formation(
        formation_1,
        positions=starting_xi_1.position_id,
        kind="scatter",
        c="#ba495c",
        linewidth=3,
        s=500,
        xoffset=-8,
        edgecolors="black",
        ax=axs["pitch"][0],
    )

    # Team 2
    txt2 = axs["title"].text(
        x=0.77,
        y=0,
        s=team2,
        fontsize=30,
        color="#697cd4",
        fontweight="bold",
        ha="center",
        va="center",
    )
    ax_text2 = pitch.formation(
        formation_2,
        positions=starting_xi_2.position_id,
        kind="text",
        text=starting_xi_2.player_nickname.str.replace(" ", "\n"),
        va="center",
        ha="center",
        fontsize=16,
        ax=axs["pitch"][1],
    )
    ax_scatter2 = pitch.formation(
        formation_2,
        positions=starting_xi_2.position_id,
        kind="scatter",
        c="#697cd4",
        linewidth=3,
        s=500,
        xoffset=-8,
        edgecolors="black",
        ax=axs["pitch"][1],
    )

    return fig
