from datetime import date, datetime

from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output

def create_app(dash_kwargs: dict = None) -> Dash:

    dash_kwargs = dash_kwargs or {}

    app = Dash(
        name=__name__,
        **dash_kwargs,
    )

    app.layout = html.Div(
        children=[
            html.H1(children="Hello World!"),
            html.Div(
                [
                    html.H2("How many days are you old?"),
                    html.P("Select your Birthdate: "),
                    dcc.DatePickerSingle(
                        id="birthdate-picker",
                        date=date(1993, 1, 1),
                        display_format="DD.MM.YYYY",
                    ),
                    html.P(id="birthdate-output"),
                ]
            ),
        ],
    )

    return app

@callback(
    Output("birthdate-output", "children"),
    Input("birthdate-picker", "date"),
    prevent_initial_call=True,
)
def calculate_days_since_birth(birthday_iso_string):

    now = datetime.now().date()
    birthday = date.fromisoformat(birthday_iso_string)

    age_in_days = (now - birthday).days
    output = ["You're ", html.Strong(age_in_days), " days young!"]
    return output

if __name__ == "__main__":
    create_app().run(debug=False)
