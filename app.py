import streamlit as st
import pandas as pd
from gensim.models.keyedvectors import KeyedVectors
import plotly.express as px
from streamlit_plotly_events import plotly_events
import re, pickle
import plotly.io as pio
pio.templates.default = 'plotly'

st.title("Ancient Greek Perseus Text Visualizer")

@st.cache(allow_output_mutation=True)
def load_d2v():
    grc_d2v = KeyedVectors.load('grc_d2v.kv')
    g_notext = pd.read_csv('grc_perseus_notext.csv')
    grc_df = pd.read_csv('grc_df.csv')
    index2title = pickle.load(open("index2title.p", "rb" ))
    title2index = pickle.load(open("title2index.p", "rb"))
    return grc_d2v, grc_df, g_notext, index2title, title2index
grc_d2v, grc_df, g_notext, index2title, title2index = load_d2v()

def get_urn_cts(fname):
    return re.search(r"(tlg\d+\.tlg\d+)",fname)[0]

options = st.multiselect(
    'Select author to visualize (listed in alphabetical order).',
    grc_df.author.sort_values().unique(),
    ['Aeschylus', 'Aristophanes', 'Euripides', 'Sophocles']
)

options = [f'^{n}$' for n in sorted(options)]
df = grc_df.loc[grc_df.author.str.contains('|'.join(options))]

fig = px.scatter(df, x='x', y='y', color='author', hover_data=['title'])
fig_selected = plotly_events(fig, select_event=True)

if st.button('Reset'):
    fig_selected = []

if len(fig_selected) > 0:
    for selected in fig_selected:
        subset = df.loc[(df.x == selected['x']) & (df.y == selected['y'])]
        selected_title = subset.title.to_list()[0]
        selected_author = subset.author.to_list()[0]
        st.write(f'#### *{selected_title.strip()}*, by {selected_author.strip()}')
        st.write('<small><b>Most similar documents</b></small>',unsafe_allow_html=True)
        res = grc_d2v.most_similar(title2index[selected_title], topn=5)
        rel = [(index2title[tup[0]], f'http://data.perseus.org/texts/urn:cts:greekLit:{get_urn_cts(g_notext.iloc[tup[0]]["filename"])}', g_notext.iloc[tup[0]]['author'],tup[1]) for tup in res]
        for i, r in enumerate(rel):       
            st.write(f'**Title**: *{r[0].strip()}*, by {r[2]} ({r[1]})')
            st.write(f'Similarity score: {round(r[3], 4)}')
            if i < len(rel)-1:
                st.markdown("<hr style='width: 75%;margin: auto;'>",unsafe_allow_html=True)
        st.markdown('<hr>',unsafe_allow_html=True)
else:
    st.write('Use the select tools in the chart above to select some works.')

st.markdown('<small>Assembled by Peter Nadel | TTS Research Technology</small>', unsafe_allow_html=True)     