#!/usr/bin/env python3
"""
generate_dashboard.py

Launches an interactive web dashboard (bar chart, line chart, and a
data table with a dropdown filter) using Plotly + Dash. Requires
'dash' and 'plotly'.

Usage:
    python generate_dashboard.py
    python generate_dashboard.py --input data.csv --port 8050

Expected output:
    A local web server starts (default: http://127.0.0.1:8050).
    Open that URL in a browser to see an interactive dashboard:
    a dropdown to filter by category, a bar chart, and a line chart
    that update live as you change the filter. Press Ctrl+C in the
    terminal to stop the server.
"""

import argparse
import csv
import os
import sys

try:
    import pandas as pd
    from dash import Dash, dcc, html, Input, Output
    import plotly.express as px
except ImportError:
    print(
        "Missing dependency. Install requirements with: pip install dash plotly pandas",
        file=sys.stderr,
    )
    sys.exit(1)


def load_sample_dataframe():
    data = {
        "Region": ["North", "South", "East", "West", "North", "South", "East", "West"],
        "Month": ["Jan", "Jan", "Jan", "Jan", "Feb", "Feb", "Feb", "Feb"],
        "Sales": [220, 180, 260, 150, 240, 200, 280, 170],
    }
    return pd.DataFrame(data)


def load_csv_dataframe(path):
    return pd.read_csv(path)


def build_app(df):
    app = Dash(__name__)
    app.title = "Interactive Report Dashboard"

    category_col = df.columns[0]
    categories = ["All"] + sorted(df[category_col].dropna().unique().tolist())

    app.layout = html.Div(
        style={"fontFamily": "Arial, sans-serif", "maxWidth": "1000px", "margin": "0 auto", "padding": "20px"},
        children=[
            html.H2("Interactive Report Dashboard"),
            html.P(f"Filter by {category_col}:"),
            dcc.Dropdown(
                id="category-filter",
                options=[{"label": c, "value": c} for c in categories],
                value="All",
                clearable=False,
                style={"marginBottom": "20px"},
            ),
            dcc.Graph(id="bar-graph"),
            dcc.Graph(id="line-graph"),
        ],
    )

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    value_col = numeric_cols[0] if numeric_cols else df.columns[-1]

    @app.callback(
        Output("bar-graph", "figure"),
        Output("line-graph", "figure"),
        Input("category-filter", "value"),
    )
    def update_graphs(selected_category):
        filtered = df if selected_category == "All" else df[df[category_col] == selected_category]
        bar_fig = px.bar(filtered, x=category_col, y=value_col, color=category_col,
                          title=f"{value_col} by {category_col}")
        line_fig = px.line(filtered, x=category_col, y=value_col, markers=True,
                            title=f"{value_col} Trend")
        return bar_fig, line_fig

    return app


def main():
    parser = argparse.ArgumentParser(description="Launch an interactive Plotly/Dash dashboard from CSV data.")
    parser.add_argument("--input", "-i", help="Path to input CSV file. If omitted, sample data is used.")
    parser.add_argument("--port", "-p", type=int, default=8050, help="Port to run the dashboard on (default: 8050)")
    args = parser.parse_args()

    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        df = load_csv_dataframe(args.input)
    else:
        df = load_sample_dataframe()
        print("No --input provided, using built-in sample data.")

    app = build_app(df)

    print(f"Starting dashboard at: http://127.0.0.1:{args.port}")
    print("Press CTRL+C to stop the server.")
    app.run(debug=False, port=args.port)


if __name__ == "__main__":
    main()
