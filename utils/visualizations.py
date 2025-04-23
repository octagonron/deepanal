import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
import datetime
from plotly.subplots import make_subplots

def create_cyberpunk_theme():
    """Create a cyberpunk-themed template for plots."""
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': '#ff00ff', 'family': 'Inter'},
        'scene': {
            'xaxis': {
                'gridcolor': 'rgba(0,255,255,0.2)',
                'showbackground': True,
                'backgroundcolor': 'rgba(10,10,30,0.8)',
                'showgrid': True,
                'gridwidth': 2,
                'title': {'text': '', 'font': {'color': '#00ffff'}},
                'linecolor': '#00ffff',
                'linewidth': 3
            },
            'yaxis': {
                'gridcolor': 'rgba(255,0,255,0.2)',
                'showbackground': True,
                'backgroundcolor': 'rgba(10,10,30,0.8)',
                'showgrid': True,
                'gridwidth': 2,
                'title': {'text': '', 'font': {'color': '#ff00ff'}},
                'linecolor': '#ff00ff',
                'linewidth': 3
            },
            'zaxis': {
                'gridcolor': 'rgba(255,255,0,0.2)',
                'showbackground': True,
                'backgroundcolor': 'rgba(10,10,30,0.8)',
                'showgrid': True,
                'gridwidth': 2,
                'title': {'text': '', 'font': {'color': '#ffff00'}},
                'linecolor': '#ffff00',
                'linewidth': 3
            },
            'camera': {
                'eye': {'x': 1.8, 'y': 1.8, 'z': 1.8},
                'projection': {'type': 'perspective'}
            },
            'aspectratio': {'x': 1, 'y': 1, 'z': 0.8}
        },
        'margin': {'l': 0, 'r': 0, 't': 30, 'b': 0}
    }

def create_entropy_plot(entropy_value):
    """Create a cyberpunk 3D entropy visualization."""
    # Generate more complex patterns for visualization
    t = np.linspace(0, 16*np.pi, 2000)
    scale = entropy_value / 8  # Normalize to max entropy of 8
    
    # Create expanding double spiral with modulation
    x1 = (t/8 * np.cos(t) + 0.3*np.sin(3*t)) * scale
    y1 = (t/8 * np.sin(t) + 0.3*np.cos(3*t)) * scale
    z1 = (t/10 + 0.2*np.sin(5*t)) * scale
    
    # Second spiral path (offset)
    x2 = (t/8 * np.cos(t + np.pi) + 0.3*np.sin(3*t)) * scale
    y2 = (t/8 * np.sin(t + np.pi) + 0.3*np.cos(3*t)) * scale
    z2 = (t/10 + 0.2*np.sin(5*t + np.pi)) * scale
    
    # Create holographic cube effect
    cube_size = scale * 1.5
    edges_x = []
    edges_y = []
    edges_z = []
    
    # Generate cube corners
    corners = [
        [-cube_size, -cube_size, -cube_size],
        [cube_size, -cube_size, -cube_size],
        [cube_size, cube_size, -cube_size],
        [-cube_size, cube_size, -cube_size],
        [-cube_size, -cube_size, cube_size],
        [cube_size, -cube_size, cube_size],
        [cube_size, cube_size, cube_size],
        [-cube_size, cube_size, cube_size]
    ]
    
    # Connect cube edges (12 edges total)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
        (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
        (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
    ]
    
    for edge in edges:
        c1, c2 = corners[edge[0]], corners[edge[1]]
        # Create points along the edge
        for i in range(20):
            t = i / 19.0
            edges_x.append(c1[0] * (1-t) + c2[0] * t)
            edges_y.append(c1[1] * (1-t) + c2[1] * t)
            edges_z.append(c1[2] * (1-t) + c2[2] * t)
    
    # Create voxel-like points inside the cube
    voxel_points = 800
    voxel_x = np.random.uniform(-cube_size, cube_size, voxel_points)
    voxel_y = np.random.uniform(-cube_size, cube_size, voxel_points)
    voxel_z = np.random.uniform(-cube_size, cube_size, voxel_points)
    voxel_colors = np.sqrt(
        (voxel_x/cube_size)**2 + 
        (voxel_y/cube_size)**2 + 
        (voxel_z/cube_size)**2
    )
    
    # Create the pulsating sphere
    u = np.linspace(0, 2*np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    sphere_x = scale * 0.8 * np.outer(np.cos(u), np.sin(v))
    sphere_y = scale * 0.8 * np.outer(np.sin(u), np.sin(v))
    sphere_z = scale * 0.8 * np.outer(np.ones(50), np.cos(v))
    
    # Create ripple effect on sphere
    for i in range(len(u)):
        for j in range(len(v)):
            ripple = 0.1 * np.sin(8 * u[i]) * np.sin(8 * v[j])
            sphere_x[i, j] += ripple * np.cos(u[i]) * np.sin(v[j])
            sphere_y[i, j] += ripple * np.sin(u[i]) * np.sin(v[j])
            sphere_z[i, j] += ripple * np.cos(v[j])
    
    # Create circular rings around center
    rings = []
    for radius in np.linspace(0.2, 1.0, 5):
        ring_t = np.linspace(0, 2*np.pi, 200)
        ring_x = radius * scale * np.cos(ring_t)
        ring_y = radius * scale * np.sin(ring_t)
        ring_z = np.zeros_like(ring_t) + (radius * 0.1 * scale)
        rings.append((ring_x, ring_y, ring_z))
    
    # Combine all visualizations into figure
    fig = go.Figure()
    
    # 1. Add core sphere with ripple effect
    fig.add_trace(go.Surface(
        x=sphere_x, y=sphere_y, z=sphere_z,
        colorscale=[
            [0, '#00ffff'], 
            [0.5, '#ff00ff'],
            [1, '#ffff00']
        ],
        opacity=0.6,
        showscale=False,
        hoverinfo='none',
        name='Entropy Core'
    ))
    
    # 2. Add primary data spiral
    fig.add_trace(go.Scatter3d(
        x=x1, y=y1, z=z1,
        mode='lines',
        line=dict(
            color='#ff00ff',
            width=4
        ),
        hoverinfo='none',
        name='Data Flow'
    ))
    
    # 3. Add secondary data spiral
    fig.add_trace(go.Scatter3d(
        x=x2, y=y2, z=z2,
        mode='lines',
        line=dict(
            color='#00ffff',
            width=4
        ),
        hoverinfo='none',
        name='Mirror Flow'
    ))
    
    # 4. Add data points along spirals
    fig.add_trace(go.Scatter3d(
        x=x1[::100], y=y1[::100], z=z1[::100],
        mode='markers',
        marker=dict(
            size=6,
            color=z1[::100],
            colorscale=[[0, '#ff00ff'], [1, '#00ffff']],
            opacity=0.8,
            symbol='circle'
        ),
        hoverinfo='none',
        name='Energy Nodes'
    ))
    
    # 5. Add cube framework
    fig.add_trace(go.Scatter3d(
        x=edges_x, y=edges_y, z=edges_z,
        mode='markers',
        marker=dict(
            size=3,
            color='#ffff00',
            opacity=0.7
        ),
        hoverinfo='none',
        name='Data Boundary'
    ))
    
    # 6. Add voxel points inside the cube
    fig.add_trace(go.Scatter3d(
        x=voxel_x, y=voxel_y, z=voxel_z,
        mode='markers',
        marker=dict(
            size=2,
            color=voxel_colors,
            colorscale=[[0, '#00ffff'], [0.5, '#ff00ff'], [1, '#ffff00']],
            opacity=0.3
        ),
        hoverinfo='none',
        name='Data Cloud'
    ))
    
    # 7. Add circular rings
    for i, (ring_x, ring_y, ring_z) in enumerate(rings):
        fig.add_trace(go.Scatter3d(
            x=ring_x, y=ring_y, z=ring_z,
            mode='lines',
            line=dict(
                color='#ffff00' if i % 2 == 0 else '#00ffff',
                width=3
            ),
            opacity=0.7,
            hoverinfo='none',
            name=f'Data Ring {i+1}'
        ))
    
    # 8. Add entropy value indicator
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[scale*1.8],
        mode='markers+text',
        marker=dict(
            size=16,
            color='#ff00ff',
            symbol='diamond',
            line=dict(color='#00ffff', width=2)
        ),
        text=[f'Entropy: {entropy_value:.2f}'],
        textposition='top center',
        textfont=dict(
            color='#ffff00',
            size=14
        ),
        name='Entropy Value'
    ))
    
    # Add small holographic info panels
    panel_offsets = [
        [cube_size*1.2, 0, 0],
        [-cube_size*1.2, 0, 0],
        [0, cube_size*1.2, 0]
    ]
    
    panel_texts = [
        f"ENTROPY: {entropy_value:.4f}",
        f"NORM: {entropy_value/8:.2f}",
        f"STATUS: {'HIGH' if entropy_value > 7 else 'NORMAL' if entropy_value > 5 else 'LOW'}"
    ]
    
    for i, (offset, text) in enumerate(zip(panel_offsets, panel_texts)):
        fig.add_trace(go.Scatter3d(
            x=[offset[0]], y=[offset[1]], z=[offset[2]],
            mode='text',
            text=[text],
            textfont=dict(
                color='#00ffff' if i == 0 else '#ff00ff' if i == 1 else '#ffff00',
                size=12
            ),
            name=f'Info Panel {i+1}'
        ))
    
    # Layout configuration
    fig.update_layout(
        title={
            'text': 'ENTROPY VISUALIZATION MATRIX',
            'font': {'color': '#00ffff', 'size': 24}
        },
        showlegend=True,
        legend=dict(
            font=dict(color='#00ffff', size=10),
            bgcolor='rgba(0,0,10,0.7)',
            bordercolor='#ff00ff',
            borderwidth=1
        ),
        **create_cyberpunk_theme()
    )
    
    # Make animation more smooth
    fig.update_layout(
        scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.8, y=1.8, z=0.8)
        )
    )
    
    return fig

def create_byte_frequency_plot(bytes_values, frequencies):
    """Create a cyberpunk 3D byte frequency visualization matching the reference image."""
    # Normalize frequencies
    freq_norm = np.array(frequencies) / max(frequencies)
    x = np.array(bytes_values)
    
    # Create heightmap data for primary visualization
    X, Y = np.meshgrid(
        np.linspace(0, 255, 100),  # Use full byte range (0-255)
        np.linspace(0, 1, 100)
    )
    
    # Create complex terrain with multiple peaks
    Z = np.zeros_like(X)
    for i, (bv, fn) in enumerate(zip(x, freq_norm)):
        # Use more complex function to create sharper peaks
        Z += fn * np.exp(-0.005 * ((X - bv)**2 + (Y - fn*5)**2))
    
    # Amplify the terrain for more dramatic effect
    Z = Z * 1.5
    
    # Create city-like grid layout for the visualization
    city_x = []
    city_y = []
    city_z = []
    city_colors = []
    
    # Generate vertical bars ("buildings") based on frequency data
    for i, (bv, fn) in enumerate(zip(x, freq_norm)):
        if fn > 0.01:  # Only plot significant frequencies
            # Create building with height proportional to frequency
            height = fn * 1.5
            
            # Base of building
            base_size = 0.8
            base_x = [bv-base_size, bv+base_size, bv+base_size, bv-base_size, bv-base_size]
            base_y = [0, 0, 1, 1, 0]
            base_z = [0, 0, 0, 0, 0]
            
            # Top of building
            top_x = [bv-base_size, bv+base_size, bv+base_size, bv-base_size, bv-base_size]
            top_y = [0, 0, 1, 1, 0]
            top_z = [height, height, height, height, height]
            
            # Vertical lines
            for j in range(4):
                city_x.extend([base_x[j], top_x[j], None])
                city_y.extend([base_y[j], top_y[j], None])
                city_z.extend([base_z[j], top_z[j], None])
                # Assign color based on position in spectrum
                color_val = (bv / 255)
                city_colors.extend([color_val, color_val, color_val])
    
    # Create holographic data cube (3D grid)
    grid_size = 4
    grid_x, grid_y, grid_z = [], [], []
    
    # Create 3D grid lines
    for i in range(grid_size + 1):
        # Normalized coordinates (0 to 1)
        coord = i / grid_size
        
        # Lines along X-axis
        for j in range(grid_size + 1):
            jcoord = j / grid_size
            grid_x.extend([coord, coord, None])
            grid_y.extend([jcoord, jcoord, None])
            grid_z.extend([0, 1, None])
            
            grid_x.extend([coord, coord, None])
            grid_y.extend([0, 1, None])
            grid_z.extend([jcoord, jcoord, None])
        
        # Lines along Y-axis
        for j in range(grid_size + 1):
            jcoord = j / grid_size
            grid_x.extend([0, 1, None])
            grid_y.extend([coord, coord, None])
            grid_z.extend([jcoord, jcoord, None])
    
    # Create primary visualization with multiple components
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{'type': 'scene'}]],
        subplot_titles=["BYTE FREQUENCY MATRIX"]
    )
    
    # 1. Main terrain surface (uses custom colorscale for cyberpunk look)
    fig.add_trace(
        go.Surface(
            x=X, 
            y=Y, 
            z=Z,
            colorscale=[
                [0, '#000000'],
                [0.2, '#00ffff'],
                [0.4, '#0000ff'],
                [0.6, '#ff00ff'],
                [0.8, '#ff0000'],
                [1, '#ffff00']
            ],
            opacity=0.8,
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                specular=0.8,
                roughness=0.5,
                fresnel=0.8
            ),
            hoverinfo='none',
            name='Frequency Terrain'
        )
    )
    
    # 2. Add "city" buildings for each frequency peak
    fig.add_trace(
        go.Scatter3d(
            x=city_x, 
            y=city_y, 
            z=city_z,
            mode='lines',
            line=dict(
                color=city_colors,
                colorscale=[
                    [0, '#00ffff'],
                    [0.5, '#ff00ff'],
                    [1, '#ffff00']
                ],
                width=2
            ),
            hoverinfo='none',
            name='Byte Buildings'
        )
    )
    
    # 3. Add grid overlay
    fig.add_trace(
        go.Scatter3d(
            x=grid_x,
            y=grid_y,
            z=grid_z,
            mode='lines',
            line=dict(
                color='#00ffff',
                width=1
            ),
            opacity=0.3,
            hoverinfo='none',
            name='Data Grid'
        )
    )
    
    # 4. Add data points
    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=np.full_like(x, 0.5),  # Center Y
            z=freq_norm * 1.5,  # Scale Z 
            mode='markers',
            marker=dict(
                size=4,
                color=x,  # Color by byte value
                colorscale=[
                    [0, '#00ffff'],
                    [0.5, '#ff00ff'],
                    [1, '#ffff00']
                ],
                opacity=0.8,
                symbol='circle'
            ),
            hoverinfo='none',
            name='Data Points'
        )
    )
    
    # 5. Add connecting lines for data points (neon circuit look)
    significant_indices = freq_norm > 0.05
    if any(significant_indices):
        sig_x = x[significant_indices]
        sig_z = freq_norm[significant_indices] * 1.5
        
        # Sort by byte value to create path
        sort_idx = np.argsort(sig_x)
        sorted_x = sig_x[sort_idx]
        sorted_z = sig_z[sort_idx]
        
        fig.add_trace(
            go.Scatter3d(
                x=sorted_x,
                y=np.full_like(sorted_x, 0.5),  # Center Y
                z=sorted_z,
                mode='lines',
                line=dict(
                    color='#ff00ff',
                    width=3
                ),
                opacity=0.8,
                hoverinfo='none',
                name='Frequency Circuit'
            )
        )
    
    # 6. Add highlight points for anomalies (high frequencies)
    anomaly_threshold = 0.7
    anomaly_indices = freq_norm > anomaly_threshold
    if any(anomaly_indices):
        anomaly_x = x[anomaly_indices]
        anomaly_z = freq_norm[anomaly_indices] * 1.5
        
        fig.add_trace(
            go.Scatter3d(
                x=anomaly_x,
                y=np.full_like(anomaly_x, 0.5),
                z=anomaly_z + 0.1,  # Slightly above
                mode='markers',
                marker=dict(
                    size=8,
                    color='#ffff00',
                    symbol='diamond',
                    line=dict(
                        color='#ff00ff',
                        width=2
                    )
                ),
                hoverinfo='none',
                name='Anomalies'
            )
        )
    
    # 7. Add informational panel text
    # Calculate some statistics
    freq_avg = np.mean(freq_norm)
    freq_std = np.std(freq_norm)
    freq_max = np.max(freq_norm)
    max_byte = x[np.argmax(freq_norm)]
    
    # Information panels
    panel_texts = [
        f"MAX BYTE: {int(max_byte)} ({max_byte:02X}h)",
        f"FREQ STD: {freq_std:.4f}",
        f"ENTROPY INDEX: {freq_std/freq_avg:.2f}"
    ]
    
    # Place text panels in 3D space
    for i, text in enumerate(panel_texts):
        fig.add_trace(
            go.Scatter3d(
                x=[255 * 1.1],  # Right side
                y=[0.5],        # Center Y
                z=[1.5 - i*0.2],  # Stacked vertically
                mode='text',
                text=[text],
                textfont=dict(
                    color='#00ffff' if i == 0 else '#ff00ff' if i == 1 else '#ffff00',
                    size=12
                ),
                hoverinfo='none',
                name=f'Info {i+1}'
            )
        )
    
    # 8. Add background glowing effect with small particles
    particles_n = 200
    particles_x = np.random.uniform(0, 255, particles_n)
    particles_y = np.random.uniform(0, 1, particles_n)
    particles_z = np.random.uniform(0, 1.8, particles_n) 
    
    fig.add_trace(
        go.Scatter3d(
            x=particles_x,
            y=particles_y,
            z=particles_z,
            mode='markers',
            marker=dict(
                size=1.5,
                color=particles_z,
                colorscale=[
                    [0, '#00ffff'],
                    [0.5, '#ff00ff'],
                    [1, '#ffff00']
                ],
                opacity=0.5
            ),
            hoverinfo='none',
            name='Data Particles'
        )
    )
    
    # Configure layout for cyberpunk aesthetic
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title=dict(
                    text="BYTE VALUE (HEX)",
                    font=dict(family="monospace", size=12, color="#00ffff")
                ),
                range=[0, 255],
                tickvals=[0, 32, 64, 96, 128, 160, 192, 224, 255],
                ticktext=['00h', '20h', '40h', '60h', '80h', 'A0h', 'C0h', 'E0h', 'FFh'],
                tickfont=dict(color="#00ffff"),
                gridcolor='rgba(0,255,255,0.2)',
                showbackground=True,
                backgroundcolor='rgba(0,0,20,0.8)',
            ),
            yaxis=dict(
                title=dict(
                    text="DATA DIMENSION",
                    font=dict(family="monospace", size=12, color="#ff00ff")
                ),
                showticklabels=False,
                gridcolor='rgba(255,0,255,0.2)',
                showbackground=True,
                backgroundcolor='rgba(0,0,20,0.8)',
            ),
            zaxis=dict(
                title=dict(
                    text="FREQUENCY FACTOR",
                    font=dict(family="monospace", size=12, color="#ffff00")
                ),
                range=[0, 2],
                tickfont=dict(color="#ffff00"),
                gridcolor='rgba(255,255,0,0.2)',
                showbackground=True,
                backgroundcolor='rgba(0,0,20,0.8)',
            ),
            camera=dict(
                eye=dict(x=1.8, y=1.2, z=1.5),
                up=dict(x=0, y=0, z=1)
            ),
        ),
        title=dict(
            text="BYTE FREQUENCY ANALYSIS MATRIX",
            font=dict(size=24, color="#00ffff", family="monospace"),
            x=0.5,
            y=0.95
        ),
        showlegend=True,
        legend=dict(
            font=dict(color="#00ffff", family="monospace"),
            bgcolor="rgba(0,0,20,0.7)",
            bordercolor="#ff00ff",
            borderwidth=1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    
    return fig

def format_hex_dump(hex_dump):
    """Format hex dump with cyberpunk styling."""
    lines = hex_dump.split('\n')
    formatted = []
    
    # Add cyberpunk header
    formatted.append(f"""
    <div style="border: 1px solid #00ffff; border-radius: 5px; padding: 10px; margin-bottom: 15px; 
                background-color: rgba(0,0,20,0.8); color: #ff00ff;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span style="color: #00ffff; font-family: monospace; font-weight: bold;">DEEP ANAL</span>
            <span style="color: #ffff00; font-family: monospace;">HEX MATRIX</span>
            <span style="color: #ff00ff; font-family: monospace;">{datetime.datetime.now().strftime("%H:%M:%S")}</span>
        </div>
        <div style="height: 2px; background: linear-gradient(90deg, #00ffff, #ff00ff, #ffff00); margin-bottom: 10px;"></div>
    """)
    
    # Add each line with advanced styling
    for i, line in enumerate(lines):
        if line.strip():
            # Split line to get address and hex data
            parts = line.split(':') if ':' in line else [f"{i:08x}", line]
            
            if len(parts) >= 2:
                addr = parts[0].strip()
                data = parts[1].strip()
                
                # Format address with cyan color
                addr_formatted = f'<span style="color: #00ffff; font-weight: bold;">{addr}</span>'
                
                # Format hex bytes with color gradients
                bytes_formatted = ""
                ascii_formatted = ""
                
                # Process hex bytes to add color and extract ASCII
                hex_bytes = data.split()
                for j, byte in enumerate(hex_bytes):
                    if len(byte) == 2:  # Ensure it's a hex byte
                        # Color based on value (higher bytes more magenta, lower more cyan)
                        try:
                            byte_val = int(byte, 16)
                            # Calculate color based on byte value 
                            r = min(255, byte_val * 2)
                            g = max(0, 80 - byte_val // 3)
                            b = min(255, 255 - byte_val // 2)
                            
                            color = f"#{r:02x}{g:02x}{b:02x}"
                            
                            # Add colored byte
                            bytes_formatted += f'<span style="color: {color};">{byte}</span> '
                            
                            # Add ASCII representation if it's a printable character
                            if 32 <= byte_val <= 126:  # Printable ASCII range
                                char = chr(byte_val)
                                # Escape special HTML characters
                                if char == '<': char = '&lt;'
                                elif char == '>': char = '&gt;'
                                elif char == '&': char = '&amp;'
                                
                                ascii_formatted += f'<span style="color: {color};">{char}</span>'
                            else:
                                ascii_formatted += '<span style="color: #555;">.</span>'
                                
                        except ValueError:
                            bytes_formatted += f'<span style="color: #ff00ff;">{byte}</span> '
                            ascii_formatted += '<span style="color: #555;">.</span>'
                
                # Combine everything with proper spacing and styling
                styled_line = f"""
                <div style="font-family: monospace; margin: 3px 0; display: flex; background: rgba(0,10,30,0.3); 
                            padding: 3px; border-left: 2px solid #00ffff;">
                    <div style="width: 90px; padding-right: 10px; text-align: right; border-right: 1px solid #ff00ff;
                               margin-right: 10px;">{addr_formatted}</div>
                    <div style="flex-grow: 1;">{bytes_formatted}</div>
                    <div style="margin-left: 10px; padding-left: 10px; border-left: 1px solid #ffff00;">
                        {ascii_formatted}
                    </div>
                </div>"""
                formatted.append(styled_line)
            else:
                # Handle lines without clear structure
                styled_line = f"""
                <div style="font-family: monospace; margin: 3px 0; color: #ff00ff; background: rgba(0,10,30,0.3);
                            padding: 3px; border-left: 2px solid #ff00ff;">
                    {line}
                </div>"""
                formatted.append(styled_line)
    
    # Add cyberpunk footer
    formatted.append(f"""
        <div style="height: 2px; background: linear-gradient(90deg, #ffff00, #ff00ff, #00ffff); margin-top: 10px;"></div>
        <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 0.8em;">
            <span style="color: #00ffff; font-family: monospace;">SECTOR: {len(lines)}</span>
            <span style="color: #ffff00; font-family: monospace;">TYPE: BINARY</span>
            <span style="color: #ff00ff; font-family: monospace;">DEEP ANAL v1.0</span>
        </div>
    </div>
    """)
    
    return "\n".join(formatted)

def create_detailed_view(plot_figure, title):
    """Create a detailed view layout for a plot with enhanced cyberpunk aesthetics."""
    # Update the figure to be larger and more detailed
    plot_figure.update_layout(
        width=1200,
        height=800,
        title=dict(
            text=title.upper(),
            font=dict(
                size=28, 
                color='#00ffff',
                family='monospace'
            ),
            x=0.5,
            y=0.98
        ),
        showlegend=True,
        legend=dict(
            font=dict(
                color='#00ffff',
                family='monospace',
                size=12
            ),
            bgcolor='rgba(0,0,20,0.8)',
            bordercolor='#ff00ff',
            borderwidth=2,
            orientation='h',
            yanchor='bottom',
            y=0.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        
        # Add annotations and custom styling elements
        annotations=[
            # Add corner markers to give it a targeting/scanning look
            dict(
                x=0.02, y=0.98,
                xref='paper', yref='paper',
                text='⌜',
                showarrow=False,
                font=dict(size=24, color='#00ffff')
            ),
            dict(
                x=0.98, y=0.98,
                xref='paper', yref='paper',
                text='⌝',
                showarrow=False,
                font=dict(size=24, color='#00ffff')
            ),
            dict(
                x=0.02, y=0.02,
                xref='paper', yref='paper',
                text='⌞',
                showarrow=False,
                font=dict(size=24, color='#00ffff')
            ),
            dict(
                x=0.98, y=0.02,
                xref='paper', yref='paper',
                text='⌟',
                showarrow=False,
                font=dict(size=24, color='#00ffff')
            ),
            
            # Add timestamp and analysis marking
            dict(
                x=0.98, y=0.94,
                xref='paper', yref='paper',
                text=f'T:{datetime.datetime.now().strftime("%H:%M:%S")}',
                showarrow=False,
                font=dict(size=14, color='#ff00ff', family='monospace'),
                align='right'
            ),
            dict(
                x=0.02, y=0.94,
                xref='paper', yref='paper',
                text='DEEP ANAL MATRIX',
                showarrow=False,
                font=dict(size=14, color='#ffff00', family='monospace'),
                align='left'
            ),
            
            # Add scanning line annotation
            dict(
                x=0.5, y=0.94,
                xref='paper', yref='paper',
                text='[ DETAILED ANALYSIS MODE ]',
                showarrow=False,
                font=dict(size=14, color='#00ffff', family='monospace'),
                align='center'
            )
        ],
        
        # Update 3D scene configuration for better visualization
        scene=dict(
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=0.8),
                projection=dict(type='perspective')
            ),
            aspectratio=dict(x=1, y=1, z=0.7)
        )
    )
    
    # Add shapes for cyberpunk border effect
    plot_figure.update_layout(
        shapes=[
            # Horizontal lines (top and bottom)
            dict(
                type="line", xref="paper", yref="paper",
                x0=0.01, y0=0.99, x1=0.99, y1=0.99,
                line=dict(color="#00ffff", width=2)
            ),
            dict(
                type="line", xref="paper", yref="paper",
                x0=0.01, y0=0.01, x1=0.99, y1=0.01,
                line=dict(color="#00ffff", width=2)
            ),
            
            # Vertical lines (left and right)
            dict(
                type="line", xref="paper", yref="paper",
                x0=0.01, y0=0.01, x1=0.01, y1=0.99,
                line=dict(color="#ff00ff", width=2)
            ),
            dict(
                type="line", xref="paper", yref="paper",
                x0=0.99, y0=0.01, x1=0.99, y1=0.99,
                line=dict(color="#ff00ff", width=2)
            ),
        ]
    )
    
    return plot_figure