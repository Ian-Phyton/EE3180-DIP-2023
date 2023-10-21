from dash import html, dcc, Output, Input, State, callback_context, register_page, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import pandas as pd


def collect_real_time_data():
    real_time_df = pd.read_csv('./pages/heatmap_demo_data.csv')
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

register_page(__name__, path="/demo-heatmap")
demo_heatmap = collect_real_time_data()

### Live Heatmap Page Content ###
# Dropdown menu items for block number selection
demo_heatmap_dropdown_menu_items = [
    dbc.DropdownMenuItem("Block 123", id="demo-heatmap-dropdown-menu-item-1"),
    dbc.DropdownMenuItem("Block 124", id="demo-heatmap-dropdown-menu-item-2"),
    dbc.DropdownMenuItem("Block 125", id="demo-heatmap-dropdown-menu-item-3"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Clear", id="demo-heatmap-dropdown-menu-item-clear"),
]

# Dropdown menu for block number selection
demo_heatmap_filter_dropdown =  dbc.InputGroup(
    [
        dbc.DropdownMenu(demo_heatmap_dropdown_menu_items, label="Select"),
        dbc.Input(id="demo-heatmap-input-group-dropdown-input", placeholder="Block Number", disabled=True),
    ],
    size="sm"
)

# Callback function for dropdown menu
@callback(
    Output("demo-heatmap-input-group-dropdown-input", "value"),
    [
        Input("demo-heatmap-dropdown-menu-item-1", "n_clicks"),
        Input("demo-heatmap-dropdown-menu-item-2", "n_clicks"),
        Input("demo-heatmap-dropdown-menu-item-3", "n_clicks"),
        Input("demo-heatmap-dropdown-menu-item-clear", "n_clicks"),
    ],
)
def on_button_click(n1, n2, n3, n_clear):
    if not callback_context.triggered:
        return ""
    else:
        button_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if button_id == "demo-heatmap-dropdown-menu-item-clear":
        return ""
    elif button_id == "demo-heatmap-dropdown-menu-item-1":
        return "Block 123"
    elif button_id == "demo-heatmap-dropdown-menu-item-2":
        return "Block 124"
    else:
        return "Block 125"

# Live heatmap block number selector layout
demo_heatmap_filter = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Select building block number", className="card-title"),
            demo_heatmap_filter_dropdown,
            dbc.Button("Check now", color="danger", id="open-live-demo-heatmap-modal", style={"margin-top": "10px"})
        ]
    )
)

# Live heatmap graph layout
demo_heatmap_graph = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Live Heatmap", className="card-title"),
            html.P(
                "For Block 123"
            ),
            dcc.Graph(
                id='block-demo-heatmap',
                figure=demo_heatmap,
                config={'displayModeBar': False}
            ),
            dcc.Interval(
                id='demo-interval-component',
                interval=5*1000, # in milliseconds
                n_intervals=0
            )
        ]
    )
)

# Live heatmap page layout
layout = dbc.Row(
    [
        dbc.Col(demo_heatmap_filter, width="3px"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Live Heatmap")),
                dbc.ModalBody(dbc.Col(id="demo-heatmap-card", children=demo_heatmap_graph)),
            ],
            id="live-demo-heatmap-modal",
            fullscreen=True,
        ),
        
    ]
)

# Callback function to update the live heatmap graph periodically
@callback(
    Output('block-demo-heatmap', 'figure'),
    Input('demo-interval-component', 'n_intervals')
)
def update_heatmap(n_intervals):
    heatmap = collect_real_time_data()
    return heatmap

# Callback function to expand live heatmap graph after block number is selected
@callback(
    Output("live-demo-heatmap-modal", "is_open"),
    Input("open-live-demo-heatmap-modal", "n_clicks"),
    State("live-demo-heatmap-modal", "is_open"),
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open

# Callback function to allow access to only to buildings affected by fire
@callback(
    Output("open-live-demo-heatmap-modal", "disabled"),
    Input("demo-heatmap-input-group-dropdown-input", "value")
)
def show_heatmap(block_number):
    if block_number == "Block 123":
        return False
    else:
        return True
