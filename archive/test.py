from dash import Dash, html, dcc, Output, Input, State, callback_context
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import psycopg2



#-------------------------- Functions --------------------------#
# Function to generate options with 10-minute intervals
def generate_options_time():
    return [{'label': f'{hour:02d}:{minute:02d}', 'value': f'{hour:02d}:{minute:02d}'} for hour in range(24) for minute in range(0, 60, 10)]


# Function to collect real time temperature data from 6 sensors
def collect_real_time_data():
    real_time_query = '''
        WITH RankedData AS (
            SELECT
                sensorid, temperature, date, level, unit,
                ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY date DESC) AS row_num
            FROM 
                data
        )
        SELECT 
            sensorid, temperature, date, level, unit 
        FROM 
            RankedData
        WHERE 
            row_num = 1 AND 
            sensorid IN ('42261f3', '42262a', '4226076', '4226087', '4226222', '42261ea');
    '''
    real_time_df = pd.read_sql_query(real_time_query, con=connection)
    real_time_df = real_time_df.sort_values(by=['level'], ascending=True)
    real_time_df['level'] = real_time_df['level'].astype(str)
    heatmap = px.density_heatmap(
        real_time_df, 
        x= "unit", 
        y= "level", 
        z="temperature", 
        range_color=[20, 60], 
        color_continuous_scale="temps", 
        text_auto=False, 
        labels={"unit": "Unit", "level": "Level", "temperature": ""},
    )
    heatmap.update_layout(
        margin=dict(l=0, r=0, t=0, b=0)
    )
    heatmap.update_traces(
        hovertemplate='Unit: %{x} <br>Level: %{y} <br>Temperature: %{z}'
    )
    heatmap.update_coloraxes(
        colorbar_orientation="h",
        colorbar_title_text="Temperature"
    )
    return heatmap


# Function to collect historical temperature data
def collect_historical_data(start_datetime, end_datetime, selected_lines):
    historical_dfs = [None] * 6
    n = 0
    for level in range(1, 4):
        for unit in range(1407, 1409):
            historical_query = '''
                SELECT 
                    date, temperature, level, unit
                FROM 
                    data
                WHERE 
                    level = '{}' AND
                    unit = '{}' AND
                    date BETWEEN '{}' AND '{}'
                ORDER BY 
                    date
            '''
            historical_df = pd.read_sql_query(historical_query.format(level, unit, start_datetime, end_datetime), con=connection)
            historical_dfs[n] = historical_df
            n += 1

    cleaned_data = {
        'date': historical_dfs[0]['date'],
        'Level: 1, Unit: 1407': historical_dfs[0]['temperature'],
        'Level: 1, Unit: 1408': historical_dfs[1]['temperature'],
        'Level: 2, Unit: 1407': historical_dfs[2]['temperature'],
        'Level: 2, Unit: 1408': historical_dfs[3]['temperature'],
        'Level: 3, Unit: 1407': historical_dfs[4]['temperature'],
        'Level: 3, Unit: 1408': historical_dfs[5]['temperature']
    }
    cleaned_historical_df = pd.DataFrame(cleaned_data)

    traces = []
    for line in selected_lines:
        trace = go.Scatter(
            x = cleaned_historical_df['date'],
            y = cleaned_historical_df[line],
            mode = 'lines',
            name = line,
            connectgaps=False
        )
        traces.append(trace)
    
    layout = go.Layout(title='',
                  xaxis=dict(title='Datetime'),
                  yaxis=dict(title='Temperature'))
    
    historical_graph = go.Figure(data=traces, layout=layout)
    historical_graph.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode="x unified"
    )
    historical_graph.update_xaxes(
        rangeslider_visible=True,
    )
    return historical_graph



#-------------------------- Initialization --------------------------#
connection = psycopg2.connect(
    user="dbfirenet_user", 
    password="G9Fw38n8WjMfN4zTBydkxYqZFefZSiM4", 
    host="dpg-ck0lntu3ktkc73f98tcg-a.singapore-postgres.render.com", 
    port="5432", 
    database="dbfirenet"
)
cursor = connection.cursor()
heatmap = collect_real_time_data()

app = Dash(external_stylesheets=[dbc.themes.LITERA])
app.config.suppress_callback_exceptions=True
server = app.server



#-------------------------- HTML Elements --------------------------#
### Website Header ###
header = dbc.Row(
    [
        dbc.Col(
            html.Img(src='https://www.nhb.gov.sg/-/media/nhb/images/resources/national-symbols/resources_lionhead_hires.gif', height='16px'),
            width='auto'
        ),
        dbc.Col(
            html.Div(dbc.Button('A Singapore Government Agency Website', color='light', size='sm', disabled=True)),
            width='auto'
        )
    ]
)


### Website Navbar ###
# Navigation bar buttons linking with other pages
nav_buttons = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    dbc.Button("Live Heatmap", className="me-md-2", color='danger', id='live-heatmap-button1'),
                    dbc.Button("Historical Data", className="me-md-2", color='danger', id='historical-data-button1')
                ],
                className="d-grid gap-2 d-md-flex justify-content-md-end"
            )
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

# Navigation bar layout with collapsible buttons
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='https://www.scdf.gov.sg/images/default-source/media/scdf-logo.jpg', height="40px")),
                        dbc.Col(dbc.NavbarBrand("FireNet", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                id="home-button",
                href="#",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                nav_buttons,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="light",
    dark=False,
)

# Callback function for collapsible buttons
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


### Home Page Content ###
# Informative cards to briefly introduce the function of the website and system
card = html.Div(
    [
        dbc.Card(
            [
                dbc.CardImg(src="https://www.facilitiesnet.com/resources/editorial/2019/18432-Building-Controls.jpg", top=True),
                dbc.CardBody(
                    [
                        html.H4("Live Heatmap", className="card-title"),
                        html.P(
                            "Check the live temperature data of buildings affected by fire. Powered by FireNet sensors.",
                            className="card-text",
                        ),
                        dbc.Button("Check now", color="danger", id="live-heatmap-button2"),
                    ]
                ),
            ],
            style={"width": "50%", "margin": "20px"},
        ),
        dbc.Card(
            [
                dbc.CardImg(src="https://learn.g2.com/hubfs/Imported%20sitepage%20images/1ZB5giUShe0gw9a6L69qAgsd7wKTQ60ZRoJC5Xq3BIXS517sL6i6mnkAN9khqnaIGzE6FASAusRr7w=w1439-h786.png", top=True),
                dbc.CardBody(
                    [
                        html.H4("Historical Data", className="card-title"),
                        html.P(
                            "Publicly accessible temperature data for post-fire analysis.",
                            className="card-text",
                        ),
                        dbc.Button("Access here", color="warning", id="historical-data-button2"),
                    ]
                ),
            ],
            style={"width": "50%", "margin": "20px"},
        )
    ],
    className="d-grid gap-2 d-md-flex mx-auto",
)


### Live Heatmap Page Content ###
# Dropdown menu items for block number selection
heatmap_dropdown_menu_items = [
    dbc.DropdownMenuItem("Block 123", id="heatmap-dropdown-menu-item-1"),
    dbc.DropdownMenuItem("Block 124", id="heatmap-dropdown-menu-item-2"),
    dbc.DropdownMenuItem("Block 125", id="heatmap-dropdown-menu-item-3"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Clear", id="heatmap-dropdown-menu-item-clear"),
]

# Dropdown menu for block number selection
live_heatmap_filter_dropdown =  dbc.InputGroup(
    [
        dbc.DropdownMenu(heatmap_dropdown_menu_items, label="Select"),
        dbc.Input(id="heatmap-input-group-dropdown-input", placeholder="Block Number", disabled=True),
    ],
    size="sm"
)

# Callback function for dropdown menu
@app.callback(
    Output("heatmap-input-group-dropdown-input", "value"),
    [
        Input("heatmap-dropdown-menu-item-1", "n_clicks"),
        Input("heatmap-dropdown-menu-item-2", "n_clicks"),
        Input("heatmap-dropdown-menu-item-3", "n_clicks"),
        Input("heatmap-dropdown-menu-item-clear", "n_clicks"),
    ],
)
def on_button_click(n1, n2, n3, n_clear):
    if not callback_context.triggered:
        return ""
    else:
        button_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if button_id == "heatmap-dropdown-menu-item-clear":
        return ""
    elif button_id == "heatmap-dropdown-menu-item-1":
        return "Block 123"
    elif button_id == "heatmap-dropdown-menu-item-2":
        return "Block 124"
    else:
        return "Block 125"

# Live heatmap block number selector layout
live_heatmap_filter = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Select building block number", className="card-title"),
            live_heatmap_filter_dropdown,
        ]
    )
)

# Live heatmap graph layout
live_heatmap_graph = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Live Heatmap", className="card-title"),
            html.P(
                "For Block 123"
            ),
            dcc.Graph(
                id='block-heatmap',
                figure=heatmap,
                config={'displayModeBar': False}
            ),
            dcc.Interval(
                id='interval-component',
                interval=5*1000, # in milliseconds
                n_intervals=0
            )
        ]
    )
)

# Live heatmap page layout
live_heatmap_page = dbc.Row(
    [
        dbc.Col(live_heatmap_filter, width="3px"),
        dbc.Col(id="heatmap-card", width="10px"),
    ]
)

# Callback function to update the live heatmap graph periodically
@app.callback(
    Output('block-heatmap', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_heatmap(n_intervals):
    heatmap = collect_real_time_data()
    return heatmap

# Callback function to expand live heatmap graph after block number is selected
@app.callback(
    Output("heatmap-card", "children"),
    Input("heatmap-input-group-dropdown-input", "value")
)
def show_heatmap(block_number):
    if block_number == "Block 123":
        return live_heatmap_graph
    else:
        return ""


### Historical Data Page Content ###
# Dropdown menu items for block number selection
historical_dropdown_menu_items = [
    dbc.DropdownMenuItem("Block 123", id="historical-dropdown-menu-item-1"),
    dbc.DropdownMenuItem("Block 124", id="historical-dropdown-menu-item-2"),
    dbc.DropdownMenuItem("Block 125", id="historical-dropdown-menu-item-3"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Clear", id="historical-dropdown-menu-item-clear"),
]

# Dropdown menu for block number selection
historical_data_filter_dropdown =  dbc.InputGroup(
    [
        dbc.DropdownMenu(historical_dropdown_menu_items, label="Select"),
        dbc.Input(id="historical-input-group-dropdown-input", placeholder="Block Number", disabled=True),
    ],
    size="sm"
)

# Callback function for dropdown menu
@app.callback(
    Output("historical-input-group-dropdown-input", "value"),
    [
        Input("historical-dropdown-menu-item-1", "n_clicks"),
        Input("historical-dropdown-menu-item-2", "n_clicks"),
        Input("historical-dropdown-menu-item-3", "n_clicks"),
        Input("historical-dropdown-menu-item-clear", "n_clicks"),
    ],
)
def on_button_click(n1, n2, n3, n_clear):
    if not callback_context.triggered:
        return ""
    else:
        button_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if button_id == "historical-dropdown-menu-item-clear":
        return ""
    elif button_id == "historical-dropdown-menu-item-1":
        return "Block 123"
    elif button_id == "historical-dropdown-menu-item-2":
        return "Block 124"
    else:
        return "Block 125"

# Historical data block number selector layout
historical_data_filter = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Select building block number", className="card-title"),
            historical_data_filter_dropdown,
        ]
    )
)

# Historical data datetime selector layout
historical_data_datetime = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Select date and time", className="card-title"),
            dmc.DateRangePicker(
                id='date-range-picker',
                label="Date Range",
                placeholder="YYYY-MM-DD",
                allowSingleDateInRange=True,
                style={'width': '310px'}
            ),
            dmc.Select(
                id='start-time-selector',
                data=generate_options_time(),
                label="Start Time",
                placeholder="Start",
                style={'width': '150px', 'display': 'inline-block', "margin-right": "10px"}
            ),
            dmc.Select(
                id='end-time-selector',
                data=generate_options_time(),
                label="End Time",
                placeholder="End",
                style={'width': '150px', 'display': 'inline-block', "margin-right": "10px"}
            )
        ]
    )
)

# Historical data unit selector layout
historical_data_unit = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Select unit", className="card-title"),
            dcc.Checklist(
                id='historical-line-select',
                options=[
                    {'label': 'Level: 1, Unit: 1407', 'value': 'Level: 1, Unit: 1407'},
                    {'label': 'Level: 1, Unit: 1408', 'value': 'Level: 1, Unit: 1408'},
                    {'label': 'Level: 2, Unit: 1407', 'value': 'Level: 2, Unit: 1407'},
                    {'label': 'Level: 2, Unit: 1408', 'value': 'Level: 2, Unit: 1408'},
                    {'label': 'Level: 3, Unit: 1407', 'value': 'Level: 3, Unit: 1407'},
                    {'label': 'Level: 3, Unit: 1408', 'value': 'Level: 3, Unit: 1408'}
                ],
                value=['Level: 1, Unit: 1407', 'Level: 1, Unit: 1408', 'Level: 2, Unit: 1407', 'Level: 2, Unit: 1408', 'Level: 3, Unit: 1407', 'Level: 3, Unit: 1408']
            )
        ]
    )
)

# Historical data graph layout
historical_data_graph = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Historical Temperature Data", className="card-title"),
            html.P(
                "For Block 123"
            ),
            dcc.Graph(
                id='historical-graph',
                config={'displayModeBar': False}
            )
        ]
    )
)

# Historical data page layout
historical_data_page = dbc.Row(
    [
        dbc.Col(historical_data_filter, width="3px"),
        dbc.Col(historical_data_datetime, width="3px"),
        dbc.Col(historical_data_unit, width="3px"),
        dbc.Col(historical_data_graph, width="10px"),
    ]
)

# Callback function for generating historical data graph based on selected datetime and unit
@app.callback(
    Output('historical-graph', 'figure'),
    [
        Input('date-range-picker', 'value'),
        Input('date-range-picker', 'value'),
        Input('start-time-selector', 'value'),
        Input('end-time-selector', 'value'),
        Input('historical-line-select', 'value'),
        Input("historical-input-group-dropdown-input", "value")
    ]
)
def update_graph(start_date, end_date, start_time, end_time, selected_lines, block_number):
    if start_date[0] != None and end_date[1] != None and start_time != None and end_time != None:
        start_datetime = f'{start_date[0]} {str(start_time)}'
        end_datetime = f'{end_date[1]} {str(end_time)}'
    if block_number == "Block 123":
        historical_graph = collect_historical_data(start_datetime, end_datetime, selected_lines)
        return historical_graph
    else:
        return ""



#-------------------------- App Layout --------------------------#
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(header),
        dbc.Row(navbar),
        dbc.Row(html.Div(id='page-content')),
    ]
)



#-------------------------- Global Callback Functions --------------------------#
### Callback function to update content page based on clicked navbar buttons ###
@app.callback(
    Output("page-content", "children"),
    [
        Input("home-button", "n_clicks"),
        Input("live-heatmap-button1", "n_clicks"),
        Input("historical-data-button1", "n_clicks"),
    ]
)
def update_page_content(button1, button2, button3):
    if not callback_context.triggered_id:
        button_id = None
    else:
        button_id = callback_context.triggered_id.split(".")[0]

    if button_id == "home-button":
        return card
    elif button_id == "live-heatmap-button1":
        return live_heatmap_page
    elif button_id == "historical-data-button1":
        return historical_data_page
    else:
        return card



if __name__ == '__main__':
    app.run(debug=True)