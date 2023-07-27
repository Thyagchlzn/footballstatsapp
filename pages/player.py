import dash
from dash import  dcc, html, Input, Output    # pip install dash
import dash_bootstrap_components as dbc
from .utils import  *
import sqlite3


#fetching player names
con = sqlite3.connect("fbref.db")
cur = con.cursor()
cur.execute("select DISTINCT(pid),markstatsplayer from ( select a.pid,p.markstatsplayer  from astats as a ,playerkey as p where a.min>1000 and trim(p.fbrefplayer)=trim(a.player));")
records = cur.fetchall()
records=[x[1] for x in records]
cur.close()

dash.register_page(__name__,order=2)

layout=html.Div([html.Div(
    dbc.Row([ dbc.Col([
        dcc.Dropdown(records, id='demo-dropdown',value="Lionel Messi", placeholder="Select a player",className="drop",style={"background-color":"#ea39b8","color":"black","font-family":"Consolas"}),
        ],width=12)]),style={"margin-bottom":"20px","margin-top":"20px","width":"25%","margin-left":"auto","margin-right":"auto"}) ,#1st row

    html.Div(dbc.Row([
        dbc.Col([html.Div("Category:",style={"font-weight":"bold","padding-right":"100px","text-align":"right","margin-bottom":"10px","color":"#F5EFE7","font-family":"Rockwell"})]),
        dbc.Col([html.Div("Similar Players:",style={"font-weight":"bold","padding-left":"50px","text-align":"left","color":"#F5EFE7","font-family":"Rockwell"})])
                        ])),

    html.Div(children=[dbc.Row(children=[html.Div(children=[dbc.Col(children=[dcc.Markdown(id='sim-players1')])],style={"text-align":"right","width":"45%","padding-right":"1.5%","font-family":"Rockwell"}),

        html.Div(children=[dbc.Col(children=[dcc.Markdown(id='sim-players2')]),dbc.Col(children=[html.Div(dcc.Markdown(id='sim-players3'))]),html.Div(dbc.Col(children=[dcc.Markdown(id='sim-players4')]))],
                 style={"width":"25%","text-align":"center","font-family":"Rockwell"}),

        ])]),



    html.Div(children=[dbc.Row([dbc.Col([dcc.Graph(id='player-style')],className='col-6')],className='row-10')],style={"width":"60%","margin-left":"auto","margin-right":"auto","margin-bottom":"10px"}),
    html.Div(children=[dbc.Row([dbc.Col([dcc.Graph(id='plot1')],className='col-6')],className='row-10')],style={"width":"60%","margin-left":"auto","margin-right":"auto","margin-bottom":"10px"}),
    html.Div(children=[dbc.Row([dbc.Col([dcc.Graph(id='plot2')],className='col-6')],className='row-10')],style={"width":"60%","margin-left":"auto","margin-right":"auto","margin-bottom":"10px"}),



])

@dash.callback([Output('sim-players1', 'children'),Output('sim-players2', 'children'),Output('sim-players3', 'children'),Output('sim-players4', 'children'),Output('player-style', 'figure'),Output('plot1', 'figure'),Output('plot2', 'figure')],
               [Input('demo-dropdown', 'value')])
def update_graph(value):
    if value not in records:
        print(value)
        raise dash.exceptions.PreventUpdate
    else:
        con = sqlite3.connect('fbref.db')
        c = con.cursor()
        #extracting player id and position from name
        c.execute(
            "select pid,position from astats where playedfull >10 and player=(select fbrefplayer from playerkey where markstatsplayer=  '{}')".format(
                value))
        rec = c.fetchall()[0]
        playerid = rec[0]
        position = rec[1]

        print(playerid, position)

        data,titles=graph_matcher(c,playerid,position)

        fig2=plotone(c,playerid,position)
        fig3=plottwo(c,playerid,position)
        # category def
        categories = ["Poacher/No.9-Tier 1", "Attacking-Fullback-Tier 2", "Ball Playing Centre Back -Tier 2",
                      "No.10-Tier 2", "Solid and Physical Centre Back-Tier 1", "Ball Playing Centre Back -Tier 1",
                      "No.8-Tier 2", "Defensive Midfielder-Tier 1", "Poacher/No.9-Tier 2", "Winger-Tier 1",
                      "Attacking-Fullback-Tier 1", "Orchestrator-Tier 1", "Defensive Midfielder-Tier 2",
                      "No.8-Tier 1", "Winger-Tier 2", "Solid and Physical Centre Back-Tier 2", "Complete Forward",
                      "Orchestrator-Tier 2", "Conventional FullBack", "No.10-Tier 1", "Goalkeeper"]

        # picking similar players
        similarplayers = []
        if position != 'GK':
            c.execute("select cluster from clusterinfo where pid= {} ".format(playerid))
            clusterid = c.fetchall()[0][0]

            c.execute(
                "select sFirst,sSecond,sThird from similarplayers where pid=  '{}'".format(playerid))

            rec = c.fetchall()[0]
            print(rec)
            for x in rec:
                c.execute(
                    "select player from astats where pid=  '{}'".format(x))
                temp = c.fetchall()[0][0]
                print("similar players", temp)
                similarplayers.append(temp)
        else:
            clusterid = len(categories) - 1
            c.execute("select player from totgk where pid<> {}  order by random() Limit 3;".format(playerid))
            rec = c.fetchall()
            for x in rec:
                print("similar players", x[0])
                similarplayers.append(x[0])

        c.close()
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=data,
            theta=titles,name='',
            fill='toself',fillcolor='#660000',line=dict(color="#cc0000"),
        ))

        fig.update_layout(
            margin=dict(l=20, r=20, t=25, b=35),
            title={
                'text': 'Player Wheel', 'x': 0.07, 'y': 0.97,
            }, font=fontdict,
            width=1000, height=700,
            polar=dict(
                radialaxis=dict(
                    visible=True
                ),
            ), template='plotly_dark',
            showlegend=False
        )
        fig.update_layout(
            polar={"radialaxis": {"tickvals": [i for i in range(0, 101, 20)], 'range': [0, 100]}})

        fig2.update_layout(
            margin=dict(l=20, r=5, t=30, b=25),
            title={
                'x': 0.07, 'y': 0.97,
            }, font=fontdict,
            width=1000, height=500, template='plotly_dark',

        )
        fig3.update_layout(
            margin=dict(l=20, r=5, t=25, b=25),
            title={
                'x': 0.07, 'y': 0.97,
            }, font=fontdict,
            width=1000, height=500, template='plotly_dark',

        )
        return categories[clusterid],similarplayers[0],similarplayers[1],similarplayers[2],fig,fig2,fig3












