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
                'backgroundcolor': 'rgba(26,26,46,0.4)',
                'showgrid': True,
                'gridwidth': 2,
                'title': {'text': ''}
            },
            'yaxis': {
                'gridcolor': 'rgba(255,75,75,0.1)',
                'showbackground': True,
                'backgroundcolor': 'rgba(26,26,46,0.4)',
                'showgrid': True,
                'gridwidth': 2,
                'title': {'text': ''}
            },
            'zaxis': {
                'gridcolor': 'rgba(255,75,75,0.1)',
                'showbackground': True,
                'backgroundcolor': 'rgba(26,26,46,0.4)',
                'showgrid': True,
                'gridwidth': 2,
                'title': {'text': ''}
            },
            'camera': {
                'eye': {'x': 1.5, 'y': 1.5, 'z': 1.5}
            }
        }
    }

def create_entropy_plot(entropy_value):
    """Create a cyberpunk 3D entropy visualization."""
    # Generate spiral helix for entropy visualization
    t = np.linspace(0, 10*np.pi, 1000)
    scale = entropy_value / 8  # Normalize to max entropy of 8

    # Create expanding spiral
    x = (t/10 * np.cos(t)) * scale
    y = (t/10 * np.sin(t)) * scale
    z = t/10 * scale

    # Create the mesh surface
    u = np.linspace(0, 2*np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    X = scale * np.outer(np.cos(u), np.sin(v))
    Y = scale * np.outer(np.sin(u), np.sin(v))
    Z = scale * np.outer(np.ones(50), np.cos(v))

    fig = go.Figure(data=[
        # Base sphere surface
        go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[[0, '#1a1a2e'], [1, '#ff4b4b']],
            opacity=0.3,
            showscale=False,
            name='Entropy Field'
        ),
        # Energy spiral
        go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(
                color='#ff4b4b',
                width=5
            ),
            name='Energy Path'
        ),
        # Particle effects
        go.Scatter3d(
            x=x[::50], y=y[::50], z=z[::50],
            mode='markers',
            marker=dict(
                size=4,
                color=z[::50],
                colorscale=[[0, '#7b2bf9'], [1, '#ff4b4b']],
                opacity=0.8
            ),
            name='Data Points'
        ),
        # Entropy value indicator
        go.Scatter3d(
            x=[0], y=[0], z=[scale*10],
            mode='markers+text',
            marker=dict(
                size=15,
                color='#7b2bf9',
                symbol='diamond'
            ),
            text=[f'Entropy: {entropy_value:.2f}'],
            textposition='top center',
            name='Current Value'
        )
    ])

    fig.update_layout(
        title='File Entropy Visualization',
        **create_cyberpunk_theme()
    )
    return fig

def create_byte_frequency_plot(bytes_values, frequencies):
    """Create a cyberpunk 3D byte frequency visualization."""
    # Normalize frequencies
    freq_norm = np.array(frequencies) / max(frequencies)
    x = np.array(bytes_values)

    # Create 3D terrain effect
    X, Y = np.meshgrid(
        np.linspace(min(x), max(x), 100),
        np.linspace(min(freq_norm), max(freq_norm), 100)
    )
    Z = np.zeros_like(X)
    for i, (bv, fn) in enumerate(zip(x, freq_norm)):
        Z += fn * np.exp(-0.01 * ((X - bv)**2 + (Y - fn)**2))

    fig = go.Figure(data=[
        # Base terrain
        go.Surface(
            x=X, y=Y, z=Z,
            colorscale=[
                [0, '#1a1a2e'],
                [0.5, '#ff4b4b'],
                [1, '#7b2bf9']
            ],
            opacity=0.8,
            name='Frequency Terrain'
        ),
        # Data points
        go.Scatter3d(
            x=x,
            y=freq_norm,
            z=np.zeros_like(x) + 0.01,  # Slightly above surface
            mode='markers',
            marker=dict(
                size=5,
                color=freq_norm,
                colorscale=[[0, '#ff4b4b'], [1, '#7b2bf9']],
                opacity=0.8
            ),
            name='Byte Frequencies'
        ),
        # Connection lines
        go.Scatter3d(
            x=x,
            y=freq_norm,
            z=np.zeros_like(x) + 0.01,
            mode='lines',
            line=dict(
                color='#ff4b4b',
                width=2
            ),
            opacity=0.3,
            name='Frequency Path'
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