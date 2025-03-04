import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def create_cyberpunk_theme():
    """Create a cyberpunk-themed template for plots."""
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': '#ffffff', 'family': 'Inter'},
        'scene': {
            'xaxis': {
                'gridcolor': 'rgba(255,75,75,0.1)',
                'showbackground': True,
                'backgroundcolor': 'rgba(26,26,46,0.4)'
            },
            'yaxis': {
                'gridcolor': 'rgba(255,75,75,0.1)',
                'showbackground': True,
                'backgroundcolor': 'rgba(26,26,46,0.4)'
            },
            'zaxis': {
                'gridcolor': 'rgba(255,75,75,0.1)',
                'showbackground': True,
                'backgroundcolor': 'rgba(26,26,46,0.4)'
            }
        }
    }

def create_entropy_plot(entropy_value):
    """Create a 3D entropy visualization."""
    theta = np.linspace(0, 2*np.pi, 100)
    radius = entropy_value
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = np.linspace(0, entropy_value, 100)

    fig = go.Figure(data=[
        go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(
                color='#ff4b4b',
                width=5
            ),
            name='Entropy Path'
        ),
        go.Scatter3d(
            x=[0], y=[0], z=[entropy_value],
            mode='markers+text',
            marker=dict(
                size=10,
                color='#7b2bf9',
                symbol='diamond'
            ),
            text=[f'Entropy: {entropy_value:.2f}'],
            name='Current Value'
        )
    ])

    fig.update_layout(
        title='File Entropy Visualization',
        **create_cyberpunk_theme()
    )
    return fig

def create_byte_frequency_plot(bytes_values, frequencies):
    """Create a 3D byte frequency visualization."""
    x = np.array(bytes_values)
    y = np.array(frequencies)
    z = np.zeros_like(x)

    # Create a mesh grid for surface plot
    X, Y = np.meshgrid(np.linspace(min(x), max(x), 50),
                      np.linspace(min(y), max(y), 50))
    Z = np.zeros_like(X)

    fig = go.Figure(data=[
        go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, '#1a1a2e'], [1, '#ff4b4b']],
            showscale=False,
            opacity=0.6
        ),
        go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(
                size=5,
                color=y,
                colorscale=[[0, '#ff4b4b'], [1, '#7b2bf9']],
                opacity=0.8
            ),
            name='Byte Distribution'
        )
    ])

    fig.update_layout(
        title='3D Byte Frequency Distribution',
        **create_cyberpunk_theme()
    )
    return fig

def format_hex_dump(hex_dump):
    """Format hex dump with cyberpunk styling."""
    lines = hex_dump.split('\n')
    formatted = []
    for line in lines:
        if line.strip():
            styled_line = f"""<div class="tool-output" style="margin: 2px 0">
                <pre style="margin: 0; color: #ff4b4b">{line}</pre>
            </div>"""
            formatted.append(styled_line)
    return "\n".join(formatted)

def create_detailed_view(plot_figure, title):
    """Create a detailed view layout for a plot."""
    plot_figure.update_layout(
        width=1200,
        height=800,
        title=dict(
            text=title,
            font=dict(size=24, color='#ff4b4b')
        ),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(26,26,46,0.8)',
            bordercolor='rgba(255,75,75,0.3)',
            borderwidth=1
        )
    )
    return plot_figure