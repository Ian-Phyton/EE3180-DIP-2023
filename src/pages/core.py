from dash import html
import dash_bootstrap_components as dbc

### This file contains all elements used for the main layout of the website

# Website Header
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


# Website Navbar
# Navigation bar buttons linking with other pages
nav_buttons = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    dbc.Button("Live Heatmap", className="me-md-2", color='danger', id='live-heatmap-button1', href="/live-heatmap"),
                    dbc.Button("Historical Data", className="me-md-2", color='danger', id='historical-data-button1', href="/historical-data")
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
                href="/",
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
