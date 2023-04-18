import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title='Azur Lane eHP',
    initial_sidebar_state='collapsed',
    layout='wide',
    menu_items={
        'About': '''
            ##### Azur Lane eHP

            Data and calculations from Mebot#6604 and website made by Risbiantotri#9712.
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
st.caption('Data is colored by armor type. (Green: Light, Orange: Medium, Heavy: Red)')

def ordinal_suffix(n):
    if n % 100 in (11, 12, 13):
        return 'th'
    else:
        return { 1: 'st', 2: 'nd', 3: 'rd' }.get(n % 10, 'th')

df = pd.read_csv('vg.csv', index_col=[0])

armor_colors = {
    'light': '#86b341',
    'medium': '#e3a949',
    'heavy': '#ff5858',
}

col1, col2 = st.columns(2)
armor_type = col1.selectbox('Armor Type:', ['All', 'Light', 'Medium', 'Heavy'])
hull_type = col2.selectbox('Hull Type:', ['All', 'DD', 'CL', 'CA', 'CB', 'AE'])

if armor_type != 'All':
    df = df[df['armor'] == armor_type]
if hull_type != 'All':
    df = df[df['hull'] == hull_type]

if len(df) >= 10:
    height = round(len(df) * 21.5)
elif len(df) <= 9 and len(df) >= 2:
    height = round(len(df) * 50)
elif len(df) == 1:
    height = 75

if len(df) > 0:
	counter = len(df)
	fig = go.Figure()

	for row in df.iterrows():
		name = row[1]['name']
		ehp = row[1]['ehp']
		armor = row[1]['armor'].lower()
		hull = row[1]['hull'].lower()

		fig.add_trace(
			go.Bar(
				x=[ehp],
				y=[name],
				orientation='h',
				text=ehp,
				textposition='outside',
				hovertemplate=f'{counter}{ordinal_suffix(counter)}, {name}, {ehp}',
				marker=dict(color=armor_colors[armor]),
				showlegend=False,
				name=''
			)
		)

		counter -= 1

	fig.update_layout(
		legend=dict(x=1, xanchor='right', y=0),
		margin=dict(l=0, r=0, t=50, b=0),
		height=height,
		xaxis=dict(visible=False, range=[0, 35000])
	)

	fig.update_xaxes(fixedrange=True)

	cols = st.columns([1, 3, 1])
	cols[1].plotly_chart(fig, use_container_width=True)
else:
     st.text('No data available.')
