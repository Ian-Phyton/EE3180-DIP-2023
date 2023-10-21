from dash import html, register_page
import dash_bootstrap_components as dbc

register_page(__name__, path="/")

layout = html.Div(
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
                        dbc.Button("Check now", color="danger", id="live-heatmap-button2", href="/live-heatmap"),
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
                        dbc.Button("Access here", color="danger", id="historical-data-button2", href="/historical-data"),
                    ]
                ),
            ],
            style={"width": "50%", "margin": "20px"},
        )
    ],
    className="d-grid gap-2 d-md-flex mx-auto",
)