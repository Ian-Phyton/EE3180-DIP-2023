from dash import html, dcc, Output, Input, callback_context, register_page, callback
import plotly.graph_objs as go
import pandas as pd
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import psycopg2
from dash.exceptions import PreventUpdate



# Function to generate options with 10-minute intervals
def generate_options_time():
    return [{'label': f'{hour:02d}:{minute:02d}', 'value': f'{hour:02d}:{minute:02d}'} for hour in range(24) for minute in range(0, 60, 10)]

### Function to collect historical temperature data
def collect_historical_data(start_datetime, end_datetime, selected_lines):
    # Separating main dataframe into individual dataframe unique to each sensor
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

    # Appending a list of traces based on selected house units into line graph
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
    
    # Customizing the layout of the line graph
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
        margin=dict(l=0, r=0, t=0, b=0)
    )
    historical_graph.update_xaxes(
        rangeslider_visible=True,
    )
    historical_graph.update_traces(
        hovertemplate='Date: %{x} <br> Temperature: %{y}'
    )
    return historical_graph


#-------------------------- Initialization --------------------------#
register_page(__name__, path="/historical-data")
connection = psycopg2.connect(
    user="dbfirenet_user", 
    password="G9Fw38n8WjMfN4zTBydkxYqZFefZSiM4", 
    host="dpg-ck0lntu3ktkc73f98tcg-a.singapore-postgres.render.com", 
    port="5432", 
    database="dbfirenet"
)
cursor = connection.cursor()


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
@callback(
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
layout = dbc.Row(
    [
        dbc.Col(historical_data_filter, width="3px"),
        dbc.Col(historical_data_datetime, id="historical-datetime-selector", width="3px"),
        dbc.Col(historical_data_unit, id="historical-unit-selector", width="3px"),
        dbc.Col(historical_data_graph, id="historical-card", width="10px"),
    ]
)


# Callback function to expand historical datetime selector after block number is selected
@callback(
    [
        Output("historical-datetime-selector", "children"),
        Output("historical-unit-selector", "children"),
        Output("historical-card", "children")
    ],
    Input("historical-input-group-dropdown-input", "value"),
)
def show_historical_selectors(block_number):
    if block_number == "Block 123":
        return historical_data_datetime, historical_data_unit, historical_data_graph
    else:
        return "", "", ""


# Callback function for generating historical data graph based on selected datetime and unit
@callback(
    Output('historical-graph', 'figure'),
    Input('date-range-picker', 'value'),
    Input('date-range-picker', 'value'),
    Input('start-time-selector', 'value'),
    Input('end-time-selector', 'value'),
    Input('historical-line-select', 'value'),
)
def update_graph(start_date, end_date, start_time, end_time, selected_lines):
    if start_date is None or end_date is None or start_time is None or end_time is None:
        raise PreventUpdate
    start_datetime = f'{start_date[0]} {str(start_time)}'
    end_datetime = f'{end_date[1]} {str(end_time)}'
    historical_graph = collect_historical_data(start_datetime, end_datetime, selected_lines)
    return historical_graph, historical_data_graph