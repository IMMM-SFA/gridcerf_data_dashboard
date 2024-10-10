import dash
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        id="expandable-box",
        style={
            "width": "20px",
            "height": "20px",
            "backgroundColor": "lightgray",
            "cursor": "pointer",
            "transition": "width 0.3s, height 0.3s",
            "border": "1px solid black",
            "position": "relative"  # Position relative for the close button
        },
        n_clicks=0,
        children=[
            # Close button will be added here
            html.Button("X", id="close-button", style={
                "position": "absolute",
                "top": "5px",
                "right": "5px",
                "backgroundColor": "red",
                "color": "white",
                "border": "none",
                "cursor": "pointer",
                "display": "none"  # Hidden initially
            })
        ]
    ),
    html.Div("Click the box to expand!", style={"margin-top": "10px"})
])

@app.callback(
    Output("expandable-box", "style"),
    Output("expandable-box", "children"),
    Input("expandable-box", "n_clicks"),
    Input("close-button", "n_clicks"),
)
def toggle_expand(expand_clicks, close_clicks):
    # If the close button is clicked
    if close_clicks:
        return (
            {
                "width": "20px",
                "height": "20px",
                "backgroundColor": "lightgray",
                "cursor": "pointer",
                "transition": "width 0.3s, height 0.3s",
                "border": "1px solid black",
                "position": "relative"
            },
            [html.Button("X", id="close-button", style={
                "position": "absolute",
                "top": "5px",
                "right": "5px",
                "backgroundColor": "red",
                "color": "white",
                "border": "none",
                "cursor": "pointer",
                "display": "none"  # Hidden when collapsed
            })]  # Keep the button but hidden
        )

    # If the box is clicked to expand
    if expand_clicks:
        return (
            {
                "width": "200px",
                "height": "100px",
                "backgroundColor": "lightgray",
                "cursor": "pointer",
                "transition": "width 0.3s, height 0.3s",
                "border": "1px solid black",
                "position": "relative"
            },
            [html.Button("X", id="close-button", style={
                "position": "absolute",
                "top": "5px",
                "right": "5px",
                "backgroundColor": "red",
                "color": "white",
                "border": "none",
                "cursor": "pointer",
                "display": "block"  # Show the close button when expanded
            })]  # Close button in expanded state
        )

    # Keep the small size if not clicked
    return (
        {
            "width": "20px",
            "height": "20px",
            "backgroundColor": "lightgray",
            "cursor": "pointer",
            "transition": "width 0.3s, height 0.3s",
            "border": "1px solid black",
            "position": "relative"
        },
        [html.Button("X", id="close-button", style={
            "position": "absolute",
            "top": "5px",
            "right": "5px",
            "backgroundColor": "red",
            "color": "white",
            "border": "none",
            "cursor": "pointer",
            "display": "none"  # Hidden when collapsed
        })]  # Keep the button but hidden
    )

if __name__ == "__main__":
    app.run_server(port=8070, debug=True)
