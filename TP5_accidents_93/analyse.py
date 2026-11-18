"""TP DataViz: carte autonome (aucun serveur de tuiles requis)."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from contour_93 import CONTOUR_93, VILLES

root = Path(__file__).resolve().parent
(root / 'images').mkdir(exist_ok=True)
d = pd.read_csv(root / 'accidents_93_2024.csv', encoding='utf-8-sig')
d['lat'] = pd.to_numeric(d['lat'], errors='coerce')
d['long'] = pd.to_numeric(d['long'], errors='coerce')
d = d.dropna(subset=['lat', 'long'])
d = d[d['lat'].between(48.75, 49.10) & d['long'].between(2.20, 2.70)]

counts = d['luminosite'].value_counts()
fig, ax = plt.subplots(figsize=(10, 4.6))
bars = ax.barh(counts.index[::-1], counts.values[::-1], color='#2176ae')
ax.bar_label(bars, padding=5)
ax.set_xlim(0, counts.max()*1.16)
ax.set_xlabel("Nombre d'accidents corporels")
ax.set_title('Accidents selon la luminosité — Seine-Saint-Denis, 2024', loc='left', weight='bold')
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.grid(axis='x', alpha=.13)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(root / 'images' / 'luminosite.png', dpi=160, bbox_inches='tight')
plt.close(fig)

# Vue géographique sur axes GPS, sans fond cartographique distant.
# Le facteur cos(latitude) garde des proportions géographiques approximatives.
colors = {'Plein jour':'#2563eb', 'Nuit avec éclairage allumé':'#f59e0b',
          'Nuit sans éclairage public':'#7c3aed', 'Crépuscule / aube':'#0d9488',
          'Nuit avec éclairage éteint':'#dc2626'}
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[p[0] for p in CONTOUR_93], y=[p[1] for p in CONTOUR_93],
    mode='lines', fill='toself', fillcolor='rgba(59,130,246,0.045)',
    line={'color':'#334155','width':2.5}, name='Contour du 93 (simplifié)',
    hoverinfo='skip', showlegend=False
))
for ville,(lon,lat) in VILLES.items():
    fig.add_annotation(x=lon,y=lat,text=ville,showarrow=False,
        font={'size':10,'color':'#475569'},bgcolor='rgba(255,255,255,.75)',
        borderpad=2,opacity=.92)
for label in counts.index:
    s = d[d['luminosite'] == label]
    fig.add_trace(go.Scattergl(
        x=s['long'], y=s['lat'], mode='markers', name=f'{label} ({len(s)})',
        marker={'size':6, 'color':colors.get(label, '#64748b'), 'opacity':0.42},
        customdata=s[['date','hrmn','Num_Acc']].astype(str).values,
        hovertemplate='<b>Accident %{customdata[2]}</b><br>Date : %{customdata[0]}<br>Heure : %{customdata[1]}<br>Longitude : %{x:.4f}<br>Latitude : %{y:.4f}<extra>'+label+'</extra>'
    ))
fig.update_layout(
    title={'text':'Accidents corporels dans le 93 · 2024', 'x':0.04},
    paper_bgcolor='white', plot_bgcolor='#f5f8fc', font={'family':'Arial','color':'#17233c'},
    legend={'title':'Luminosité · cliquer pour filtrer', 'orientation':'h', 'y':-0.15, 'x':0},
    margin={'l':60,'r':30,'t':80,'b':115}, height=700,
    annotations=[{'text':'Contour du 93 simplifié · noms des villes = repères approximatifs · zoom et survol interactifs',
                  'xref':'paper','yref':'paper','x':0,'y':1.04,'showarrow':False,'font':{'size':12,'color':'#52637a'}}]
)
fig.update_xaxes(title='Longitude (° Est)', range=[2.27,2.63], showgrid=True, gridcolor='#dce5f0', zeroline=False)
fig.update_yaxes(title='Latitude (° Nord)', range=[48.79,49.03], showgrid=True, gridcolor='#dce5f0', zeroline=False,
                 scaleanchor='x', scaleratio=1.51)
fig.write_html(root / 'carte_accidents_93.html', include_plotlyjs=True, full_html=True)

fig2, ax = plt.subplots(figsize=(9,7))
ax.fill([p[0] for p in CONTOUR_93], [p[1] for p in CONTOUR_93], facecolor='#e8eff9',edgecolor='#334155',linewidth=1.5)
ax.scatter(d['long'], d['lat'], s=8, alpha=.27, color='#2176ae', rasterized=True)
for ville,(lon,lat) in VILLES.items():
    ax.text(lon,lat,ville,fontsize=6.8,color='#334155',bbox={'facecolor':'white','alpha':.65,'edgecolor':'none','pad':1})
ax.set(xlabel='Longitude (° Est)', ylabel='Latitude (° Nord)', title='Accidents corporels — Seine-Saint-Denis, 2024')
ax.set_aspect(1.51)
ax.grid(alpha=.15)
fig2.tight_layout()
fig2.savefig(root/'images'/'carte_apercu.png',dpi=150)
plt.close(fig2)
print('Carte autonome et graphiques générés pour',len(d),'accidents')
