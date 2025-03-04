import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def create_entropy_plot(entropy_value):
    """Create an entropy gauge plot."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = entropy_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "File Entropy"},
        gauge = {
            'axis': {'range': [0, 8]},
            'bar': {'color': "rgb(255, 75, 75)"},
            'steps': [
                {'range': [0, 4], 'color': "rgb(38, 39, 48)"},
                {'range': [4, 6], 'color': "rgb(58, 59, 68)"},
                {'range': [6, 8], 'color': "rgb(78, 79, 88)"}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"}
    )
    return fig

def create_byte_frequency_plot(bytes_values, frequencies):
    """Create a byte frequency distribution plot."""
    df = pd.DataFrame({
        'Byte': bytes_values,
        'Frequency': frequencies
    })
    
    fig = px.bar(df, x='Byte', y='Frequency',
                 title='Byte Frequency Distribution')
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"},
        xaxis={'gridcolor': "rgba(255,255,255,0.1)"},
        yaxis={'gridcolor': "rgba(255,255,255,0.1)"}
    )
    return fig

def format_hex_dump(hex_dump):
    """Format hex dump for display."""
    lines = hex_dump.split('\n')
    formatted = []
    for line in lines:
        if line.strip():
            formatted.append(f"<pre style='margin: 0'>{line}</pre>")
    return "\n".join(formatted)
