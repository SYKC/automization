import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go


data_path = "C:\\Users\\pchandra\\OneDrive - OneWorkplace\\Desktop\\lumi_nov2020_analysis.xlsx"
raw_df = pd.read_excel(data_path, sheet_name="time_on_page_1")
df = raw_df[raw_df['Landing Page'] != "(not set)"]
df = df.groupby(by=['Landing Page', 'Page','User Type','Default Channel Grouping'])['time_on_page'].sum().sort_values(ascending=True).to_frame().reset_index()
df = df[df['time_on_page'] != 0]
df = df[df['Landing Page'] != df['Page']]

def best_n_groupby(df,n=1000000,by="ga:userType",value="ga:transactionRevenue"):
        
        return df.groupby(by)[value]\
                .sum().sort_values(ascending=False)\
                .to_frame().reset_index()\
                .rename(columns={'index':by}).head(n)

data = []

week = best_n_groupby(df,n=10,by="Landing Page",value="time_on_page")['Landing Page'].to_list()
pages = df[df['Landing Page'].isin(week)]['Page'].value_counts().index.to_list()

df=df[df['Landing Page'].isin(week)]

for i in week:
 for j in pages:
  data.append([i,j])

data = pd.DataFrame(data,columns=["Landing Page","Page"])

utype = df['User Type'].unique()
channel = df['Default Channel Grouping'].unique()
lp = df['Landing Page'].unique()

# utype_default = df["User Type"].value_counts().index[0]
# channel_default = df["Default Channel Grouping"].value_counts().index[0]
#lp_default = df["Landing Page"].value_counts().index[0]

utype_default = 'New Visitor'
channel_default = 'Organic Search'


df_default = df[(df["User Type"] == utype_default) & (df["Default Channel Grouping"] == channel_default)]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
 html.H1('Lumi Landing Page by User Type Analysis'),
 html.Div([
 html.Div([
 html.H4('Select User Type'),
 dcc.Dropdown(
 id='utype_dropdown',
 options=[{'label': i, 'value': i} for i in utype],
 value = utype_default
 ),
 ],
 style={'width': '48%', 'display': 'inline-block'}),
 
 html.Div([
 html.H4('Select Channel'),
 dcc.Dropdown(
 id='channel_dropdown',
 value = channel_default,
 ),
 ],
 style={'width': '48%', 'float': 'right', 'display': 'inline-block'}), 
 dcc.Graph(id='heatmap', 
 figure = {
 'data': [go.Heatmap(
 x=df_default['Landing Page'],
 y=df_default['Page'],
 z=df_default['time_on_page'],
 name = 'first legend group',
 
 colorscale='Viridis')],
 'layout': go.Layout(
 xaxis = dict(title = 'Landing Page'),
 yaxis = dict( title = 'Page'),
 )})    
 ]),])


@app.callback(
    dash.dependencies.Output(component_id='channel_dropdown',component_property='options'),
    [dash.dependencies.Input(component_id='utype_dropdown',component_property='value')]
)

def update_Menu_dropdown(selected_POS):
    return [{'label': i, 'value': i} for i in df[df['User Type'] == selected_POS]['Default Channel Grouping'].unique()]

@app.callback(
    dash.dependencies.Output(component_id='heatmap',component_property='figure'),
    [dash.dependencies.Input(component_id='utype_dropdown',component_property='value'),
	 dash.dependencies.Input(component_id='channel_dropdown',component_property='value')]
)


def update_graph(utype_dropdown,channel_dropdown):
    heatmap_data = df[(df['User Type'] == utype_dropdown) & (df['Default Channel Grouping'] == channel_dropdown)]#[['Landing Page','Page','time_on_page']]
    # heatmap_data = pd.merge(data, heatmap_data, on=['Landing Page','Page'],how='outer').fillna(0)
    # heatmap_data = heatmap_data.groupby(by=['Landing Page', 'Page','User Type','Default Channel Grouping'])['time_on_page'].sum().sort_values(ascending=True).to_frame().reset_index().rename(columns={'index':['Landing Page', 'Page']})
    print (utype_dropdown,channel_dropdown)
    maxsale = heatmap_data[heatmap_data['time_on_page']==heatmap_data['time_on_page'].max()]  
    maxsale = maxsale.reset_index()
    print(maxsale)
    return {
        'data': [go.Heatmap(
                x=heatmap_data['Landing Page'],
                y=heatmap_data['Page'],
                z=heatmap_data['time_on_page'],
                xgap = 0,
                ygap = 0,
                colorscale='Viridis')],
        'layout': go.Layout(
        title = 'Majority of '+utype_dropdown+' spent time on ' + str(maxsale['Page'][0]))
    }
#+str.upper(utype_dropdown)+' IS ON '+ 
# str.upper(maxsale['Landing Page'][0])+' '+

if __name__ =='__main__':
     app.run_server(debug=True)