from dash import Dash, html

def create_app(dash_kwargs: dict = None) -> Dash:

    dash_kwargs = dash_kwargs or {}

    app = Dash(
        name=__name__,
        **dash_kwargs,
    )

    app.layout = html.Div(
        children=[
            html.H1(children="Hello World!"),
        ],
    )

    return app

if __name__ == "__main__":
    create_app().run(debug=False)
