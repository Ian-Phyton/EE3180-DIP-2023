from dash import Output, Input, State, Dash, page_container
import dash_bootstrap_components as dbc

# Import core app components
from pages import core

# Initialize app
app = Dash(
    __name__, 
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LITERA]
)
server = app.server

# Main app layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(core.header),
        dbc.Row(core.navbar),
        dbc.Row(page_container),
    ]
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


if __name__ == '__main__':
    app.run_server(debug=True)