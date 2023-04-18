import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title='Azur Lane eHP',
    initial_sidebar_state='collapsed',
    layout='wide',
    menu_items={
        'About': '''
            ##### lorem ipsum

            Lorem ipsum
        '''
    }
)

st.markdown(
    '''
    <style>
        ul[aria-activedescendant] ul[role="option"]:nth-child(n+3):nth-child(-n+7),
        ul[aria-activedescendant] div:nth-child(n+1):nth-child(-n+5),
        div[data-testid="stDecoration"], iframe, footer {
            display: none !important;
        }
        .main .block-container {
            padding-top: 40px;
        }
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
            display: none !important;
        }
    </style>
    ''',
    unsafe_allow_html=True
)

st.markdown('<h4>Vanguard eHP</h4>', unsafe_allow_html=True)
st.caption('Lorem ipsum dolor sit amet')

df = pd.read_csv('vg.csv', index_col=[0])

armor_colors = {
    'light': '#86b341',
    'medium': '#e3a949',
    'heavy': '#ff5858',
}

fig = go.Figure()

for row in df.iterrows():
    name = row[1]['name']
    ehp = row[1]['ehp']
    armor = row[1]['armor'].lower()

    fig.add_trace(
        go.Bar(
            x=[ehp],
            y=[name],
            orientation='h',
            text=ehp,
            textposition='outside',
            hovertemplate=f'{name}, {ehp}',
            marker=dict(color=armor_colors[armor]),
            showlegend=False,
            name=''
        )
    )

fig.update_layout(
    legend=dict(x=1, xanchor='right', y=0),
    margin=dict(l=0, r=0, t=50, b=0),
    height=9000,
    xaxis=dict(visible=False, range=[0, 35000])
)

fig.update_xaxes(fixedrange=True)

cols = st.columns([1, 3, 1])
cols[1].plotly_chart(fig, use_container_width=True)
