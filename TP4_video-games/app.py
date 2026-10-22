from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='Pokémon | Stats Lab', page_icon='🎮', layout='wide')
st.markdown('''<style>
.block-container{max-width:1220px;padding-top:1.3rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em}h1{font-size:2.5rem!important}
[data-testid="stMetric"]{background:#192333;border:1px solid #35445a;border-radius:14px;padding:14px}
[data-testid="stMetricLabel"]{font-size:.85rem}
</style>''',unsafe_allow_html=True)
COLORS=['#56C5B5','#F5A66A','#83A6F7','#E17C9D']
@st.cache_data
def load():
    d=pd.read_csv(Path(__file__).with_name('pokedex.csv'))
    nums=['pokedex_number','generation','is_sub_legendary','is_legendary','is_mythical','total_points','hp','attack','defense','sp_attack','sp_defense','speed','height_m','weight_kg','catch_rate']
    for c in nums: d[c]=pd.to_numeric(d[c],errors='coerce')
    d['type_1']=d['type_1'].fillna('Non renseigné')
    d['type_2']=d['type_2'].fillna('Aucun')
    d['statut']=d.apply(lambda r:'Mythique' if r['is_mythical']==1 else 'Légendaire' if r['is_legendary']==1 else 'Semi-légendaire' if r['is_sub_legendary']==1 else 'Ordinaire',axis=1)
    return d
raw=load()
with st.sidebar:
    st.header('Filtres')
    gens=sorted(raw.generation.dropna().astype(int).unique().tolist())
    gen=st.multiselect('Générations',gens,default=gens)
    typ=st.multiselect('Types principaux',sorted(raw.type_1.unique()),default=sorted(raw.type_1.unique()))
    status=st.multiselect('Statuts',['Ordinaire','Semi-légendaire','Légendaire','Mythique'],default=['Ordinaire','Semi-légendaire','Légendaire','Mythique'])
    st.caption('Les filtres s’appliquent aux analyses. Le comparateur reste accessible pour toutes les formes.')
df=raw[raw.generation.isin(gen)&raw.type_1.isin(typ)&raw.statut.isin(status)].copy()
st.title('POKÉMON / STATS LAB')
st.caption('Explore les statistiques de combat • Générations 1 à 8')
st.write('**Quels types dominent ? Quels profils se démarquent ?**')
if df.empty:
    st.warning('Aucune donnée pour cette sélection. Modifie les filtres à gauche.')
    st.stop()

m1,m2,m3=st.columns(3)
m1.metric('Formes sélectionnées',f'{len(df):,}'.replace(',',' '))
m2.metric('Espèces distinctes',f'{df.pokedex_number.nunique():,}'.replace(',',' '))
m3.metric('Puissance moyenne',f'{df.total_points.mean():.0f}')

vue,profils,duel=st.tabs(['Vue d’ensemble','Profils de combat','Duel Pokémon'])

def polish(fig,height=410):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#E6EDF5'),height=height,margin=dict(l=5,r=10,t=45,b=20),hoverlabel=dict(bgcolor='#273448'))
    fig.update_xaxes(showgrid=False,zeroline=False)
    fig.update_yaxes(gridcolor='#293345',zeroline=False)
    return fig

with vue:
    st.subheader('Les types les plus puissants')
    st.caption('Puissance moyenne des formes par type principal. Le nombre de formes est indiqué au survol.')
    g=df.groupby('type_1',as_index=False).agg(moyenne=('total_points','mean'),effectif=('name','size')).dropna().sort_values('moyenne')
    fig=px.bar(g,x='moyenne',y='type_1',orientation='h',text='moyenne',custom_data=['effectif'],labels={'moyenne':'Points moyens','type_1':'Type'},color_discrete_sequence=[COLORS[0]])
    fig.update_traces(texttemplate='%{text:.0f}',textposition='outside',cliponaxis=False,hovertemplate='%{y}<br>Puissance moyenne : %{x:.1f}<br>Formes : %{customdata[0]}<extra></extra>')
    fig.update_layout(xaxis_range=[0,max(750,g.moyenne.max()*1.17)],showlegend=False)
    st.plotly_chart(polish(fig,530),use_container_width=True)
    a,b=st.columns([1,1])
    with a:
        st.subheader('Combien de formes par génération ?')
        c=df.groupby('generation',as_index=False).size().rename(columns={'size':'nombre'})
        fig=px.bar(c,x='generation',y='nombre',text='nombre',labels={'generation':'Génération','nombre':'Nombre de formes'},color_discrete_sequence=[COLORS[2]])
        fig.update_traces(textposition='outside')
        fig.update_xaxes(dtick=1)
        st.plotly_chart(polish(fig,355),use_container_width=True)
    with b:
        st.subheader('Types par génération')
        st.caption('Une couleur plus claire indique davantage de formes.')
        cross=pd.crosstab(df.type_1,df.generation)
        fig=px.imshow(cross,labels={'x':'Génération','y':'Type principal','color':'Formes'},color_continuous_scale=[[0,'#1A2637'],[.5,'#377F93'],[1,'#A8E8D7']],aspect='auto')
        fig.update_layout(coloraxis_colorbar=dict(title='Formes'))
        st.plotly_chart(polish(fig,355),use_container_width=True)

with profils:
    st.subheader('Attaque et défense')
    st.caption('Chaque point représente une forme. Survole-le pour afficher son nom. La couleur distingue les formes légendaires/mythiques des autres.')
    p=df.dropna(subset=['attack','defense']).copy()
    p['groupe']=p.statut.apply(lambda x:'Légendaire ou mythique' if x in ['Légendaire','Mythique'] else 'Autre')
    fig=px.scatter(p,x='attack',y='defense',color='groupe',hover_name='name',hover_data={'generation':True,'total_points':True,'groupe':False},color_discrete_map={'Autre':COLORS[2],'Légendaire ou mythique':COLORS[1]},opacity=.68,labels={'attack':'Attaque','defense':'Défense','groupe':'Statut','generation':'Génération','total_points':'Puissance'})
    fig.update_traces(marker_size=8)
    fig.update_layout(legend=dict(orientation='h',y=1.12,x=0))
    st.plotly_chart(polish(fig,440),use_container_width=True)
    a,b=st.columns(2)
    with a:
        st.subheader('Distribution des vitesses')
        med=df.speed.median()
        fig=px.histogram(df,x='speed',nbins=22,color_discrete_sequence=[COLORS[0]],labels={'speed':'Vitesse'})
        fig.add_vline(x=med,line_dash='dash',line_color=COLORS[1],annotation_text=f'Médiane : {med:.0f}',annotation_position='top right')
        fig.update_yaxes(title='Nombre de formes')
        st.plotly_chart(polish(fig,370),use_container_width=True)
    with b:
        st.subheader('Puissance selon le statut')
        order=['Ordinaire','Semi-légendaire','Légendaire','Mythique']
        fig=px.box(df.dropna(subset=['total_points']),x='statut',y='total_points',category_orders={'statut':order},color='statut',color_discrete_sequence=COLORS,labels={'statut':'Statut','total_points':'Puissance totale'},points=False)
        fig.update_layout(showlegend=False)
        st.plotly_chart(polish(fig,370),use_container_width=True)
    st.caption('La puissance totale est la somme des six statistiques de base : elle ne prédit pas automatiquement l’issue d’un combat.')

with duel:
    st.subheader('Deux Pokémon, six statistiques')
    st.caption('Compare deux formes précises, y compris les Méga-évolutions.')
    names=sorted(raw.name.dropna().astype(str).unique())
    a,b=st.columns(2)
    p1=a.selectbox('Pokémon A',names,index=names.index('Charizard') if 'Charizard' in names else 0)
    p2=b.selectbox('Pokémon B',names,index=names.index('Blastoise') if 'Blastoise' in names else 1)
    cols=['hp','attack','defense','sp_attack','sp_defense','speed']
    labels=['PV','Attaque','Défense','Attaque spé.','Défense spé.','Vitesse']
    r1=raw.loc[raw.name==p1].iloc[0];r2=raw.loc[raw.name==p2].iloc[0]
    fig=go.Figure()
    for r,n,c in [(r1,p1,COLORS[0]),(r2,p2,COLORS[1])]:
        fig.add_trace(go.Bar(name=n,x=labels,y=[r[k] for k in cols],marker_color=c,text=[int(r[k]) if pd.notna(r[k]) else '' for k in cols],textposition='outside'))
    fig.update_layout(barmode='group',yaxis_title='Points',legend=dict(orientation='h',y=1.13),uniformtext_minsize=10)
    st.plotly_chart(polish(fig,460),use_container_width=True)
    a,b=st.columns(2)
    for container,r,n in [(a,r1,p1),(b,r2,p2)]:
        with container:
            st.markdown(f'**{n}** · {r.type_1}'+(f' / {r.type_2}' if r.type_2!='Aucun' else ''))
            st.metric('Puissance totale',f'{r.total_points:.0f}' if pd.notna(r.total_points) else 'Non disponible')
            best=max(cols,key=lambda k:r[k] if pd.notna(r[k]) else -1)
            st.caption(f'Point fort : {labels[cols.index(best)]} ({r[best]:.0f})')

with st.expander('Données et méthode'):
    st.write(f'**Source :** pokedex.csv — {len(raw)} formes et {raw.pokedex_number.nunique()} numéros Pokédex distincts. Les Méga-évolutions et variantes peuvent partager un numéro.')
    st.write('**Préparation :** conversion des colonnes de statistiques en valeurs numériques, conservation des valeurs manquantes et regroupement des statuts. Les moyennes excluent les valeurs absentes.')
    st.write('**Limites :** les comparaisons concernent les statistiques des formes, et non la popularité, les ventes ou les performances techniques du jeu. Les groupes de tailles différentes doivent être interprétés avec prudence.')
    st.dataframe(df[['name','generation','type_1','type_2','statut','total_points','hp','attack','defense','sp_attack','sp_defense','speed']].sort_values('total_points',ascending=False),hide_index=True,use_container_width=True)
    st.download_button('Exporter les données filtrées',df.to_csv(index=False).encode('utf-8-sig'),'pokemon_selection.csv','text/csv')
