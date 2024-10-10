import dash
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        id="toggle-switch",
        style={
            "width": "50px",         # Width set to 30px
            "height": "20px",        # Height set to 20px
            "borderRadius": "10px",  # Border radius set to 10px
            "position": "relative",
            "backgroundColor": "#ccc",
            "cursor": "pointer",
            "display": "flex",
            "alignItems": "center",
            "padding": "2px",        # Padding adjusted for smaller size
            "transition": "background-color 0.3s"
        },
        n_clicks=0,
        children=[
            html.Div(id="icon", style={
                "width": "16px",        # Circle width set to fit
                "height": "16px",       # Circle height set to fit
                "borderRadius": "50%",  # Circular shape
                "backgroundColor": "white",
                "boxShadow": "0 0 2px rgba(0,0,0,0.5)",
                "position": "absolute",
                "transition": "transform 0.3s"
            }, children=[
                html.Span("🌙", id="moon-icon", style={"display": "block"}),  # Moon icon
                html.Span("☀️", id="sun-icon", style={"display": "none"})   # Sun icon
            ])
        ]
    ),
    html.Div(id="output", style={"margin-top": "20px"})
])

@app.callback(
    Output("toggle-switch", "style"),
    Output("icon", "style"),
    Output("moon-icon", "style"),
    Output("sun-icon", "style"),
    Input("toggle-switch", "n_clicks"),
)
def toggle_switch(n_clicks):
    if n_clicks % 2 == 1:  # Odd clicks mean switch is "on"
        return (
            {"backgroundColor": "#ffdd57",
                        "height": "20px",        # Height set to 20px
            "borderRadius": "10px",  # Border radius set to 10px
            "position": "relative",
            "cursor": "pointer",
            "display": "flex",
            "alignItems": "center",
            "padding": "2px",        # Padding adjusted for smaller size
            "transition": "background-color 0.3s",
            "width": "50px"},  # Background color when "on"
            {"transform": "translateX(14px)"},  # Move the circle to the right
            {"display": "none"},  # Hide moon icon
            {"display": "block"}  # Show sun icon
        )
    else:  # Even clicks mean switch is "off"
        return (
            {"backgroundColor": "#ccc",
                        "height": "20px",        # Height set to 20px
            "borderRadius": "10px",  # Border radius set to 10px
            "position": "relative",
            "cursor": "pointer",
            "display": "flex",
            "alignItems": "center",
            "padding": "2px",        # Padding adjusted for smaller size
            "transition": "background-color 0.3s",
            "width": "50px"},  # Background color when "off"
            {"transform": "translateX(0)"},  # Move the circle to the left
            {"display": "block"},  # Show moon icon
            {"display": "none"}   # Hide sun icon
        )

if __name__ == "__main__":
    app.run_server(port=8070, debug=True)
