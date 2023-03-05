import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from urllib.request import urlopen


@st.cache_data
def players_statistics(tables):
    if tables == 'Goals':
        df = pd.read_html('https://fbref.com/en/share/r2L00', header=1)[0]
        df = df.loc[df['Gls'] >= 4]
        df = df.sort_values('Gls', ascending=True)
        columns = ['Player', 'Team_img', 'Min', 'Sh', 'xG', 'Gls']
        column_names = ['Player', 'Team', 'Minutes', 'Shots', 'xG', 'Goals']
        color = '#697cd4'
        title = 'Top scorers'
    elif tables == 'Red cards':
        df = pd.read_html('https://fbref.com/en/share/RRl8O', header=1)[0]
        df = df.loc[df['CrdR'] >= 1]
        df.drop('2CrdY', axis=1, inplace=True)
        df = df.sort_values('CrdY', ascending=True)
        columns = ['Player', 'Team_img', 'Min', 'Fls', 'CrdY', 'CrdR']
        column_names = ['Player', 'Team', 'Minutes', 'Fouls', 'Yellow cards', 'Red cards']
        color = '#ba495c'
        title = 'Players with red card'
    elif tables == 'Assists':
        df = pd.read_html('https://fbref.com/en/share/vAHVp', header=1)[0]
        df = df.loc[df['Ast'] >= 3]
        columns = ['Player', 'Team_img', 'Min', 'Cmp%', 'xA', 'Ast']
        column_names = ['Player', 'Team', 'Minutes', 'Completed passes %', 'xA', 'Assists']
        color = '#697cd4'
        title = 'Top assists'
    elif tables == 'Saves':
        df = pd.read_html('https://fbref.com/en/share/1g75s', header=1)[0]
        df = df.loc[df['Saves'] >= 14]
        df = df.sort_values('Saves', ascending=True)
        columns = ['Player', 'Team_img', 'Min', 'GA', 'Save%', 'Saves']
        column_names = ['Player', 'Team', 'Minutes', 'Goals against', 'Save %', 'Saves']
        color = '#ba495c'
        title = 'Goalkeepers with most saves'

    df['Min'] = df['90s'].mul(90).astype(int)
    df.drop('90s', axis=1,inplace=True)
    df['Flag_code'] = df['Squad'].apply(lambda x: x.split(' ')[0])
    df.drop('Squad', axis=1, inplace=True)
    uk_countries = ['eng', 'nir', 'sct', 'wls']
    df['Team_img'] = df['Flag_code'].apply(lambda x: f'https://countryflagsapi.com/png/{x}' if x not in uk_countries else f'https://countryflagsapi.com/png/gb-{x}')
    df.drop('Flag_code', axis=1, inplace=True)
    bold_columns = ['Gls', 'CrdR', 'Ast', 'Saves']

    fig = plt.figure(figsize=(11,9))
    ax = plt.subplot()

    color = color
    ncolumns = len(df.columns)
    nrows = df.shape[0]

    ax.set_xlim(0, ncolumns + 0.5)
    ax.set_ylim(0, nrows + 0.5)

    positions = [0.25, 2, 3, 4, 5, 6]

    datacoord_to_figurecoord = ax.transData.transform
    figurecoord_to_normalizedfigurecoord = fig.transFigure.inverted().transform
    # Data coordinates to normalized figure coordinates
    datacoord_to_normalizedfigurecoord = lambda x: figurecoord_to_normalizedfigurecoord(datacoord_to_figurecoord(x))
    # Flag axes
    ax_point_1 = datacoord_to_normalizedfigurecoord([2.25, 0.25])
    ax_point_2 = datacoord_to_normalizedfigurecoord([2.75, 0.75])
    ax_width = abs(ax_point_1[0] - ax_point_2[0])
    ax_height = abs(ax_point_1[1] - ax_point_2[1])

    # Content of the table (rows)
    for i in range(nrows):
        for index_row, column in enumerate(columns):
            if index_row == 0:
                ha = 'left'
            else:
                ha = 'center'
            if column in bold_columns:
                text_label = f'{df[column].iloc[i]}'
                weight = 'bold'
            else:
                text_label = f'{df[column].iloc[i]}'
                weight = 'normal'
            if column == 'Team_img':
                ax_coords = datacoord_to_normalizedfigurecoord([1.75, i + .25])
                flag_ax = fig.add_axes([ax_coords[0], ax_coords[1], ax_width, ax_height])
                image = Image.open(urlopen(df['Team_img'].iloc[i]))
                flag_ax.imshow(image)
                flag_ax.axis('off')
            else:
                ax.annotate(
                    xy = (positions[index_row], i + 0.5),
                    text = text_label,
                    ha = ha,
                    va = 'center',
                    weight = weight)

    # Column names
    for index_column, c in enumerate(column_names):
        if index_column == 0:
            ha = 'left'
        else:
            ha = 'center'
        ax.annotate(
            xy = (positions[index_column], nrows + 0.1),
            text = column_names[index_column],
            ha = ha,
            va = 'bottom',
            weight = 'bold',
            color = color)

    # Dividing lines
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [nrows, nrows], lw = 1.5, color = color, marker = '', zorder = 4)
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], lw = 1.5, color = color, marker = '', zorder = 4)
    for x in range(1, nrows):
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [x, x], lw = 1.15, color = color, ls = ':', zorder = 3 , marker = '')

    ax.fill_between(
        x = [5.5,6.5],
        y1 = nrows,
        y2 = 0,
        color = color,
        alpha = 0.5,
        ec = 'None'
    )

    ax.set_title(title, loc = 'center', fontsize = 25, weight= 'bold', color = color)
    ax.set_axis_off()

    return fig
