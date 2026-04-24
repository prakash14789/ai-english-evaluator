import plotly.graph_objects as go
import pandas as pd

def create_wpm_gauge(wpm):
    """
    Creates a Plotly Gauge chart for WPM.
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = wpm,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Speaking Pace (WPM)", 'font': {'size': 24, 'color': "#4F8BF9"}},
        gauge = {
            'axis': {'range': [None, 200], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#4F8BF9"},
            'bgcolor': "#1e222d",
            'borderwidth': 2,
            'bordercolor': "#8892b0",
            'steps': [
                {'range': [0, 80], 'color': '#3b1c1c'},
                {'range': [80, 130], 'color': '#0e4b25'},
                {'range': [130, 200], 'color': '#1a1f2e'}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 120}
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"},
        height=300,
        margin=dict(l=30, r=30, t=50, b=20)
    )
    return fig

def create_fluency_line_chart(timeline):
    """
    Creates a Line Chart for WPM over time.
    """
    if not timeline:
        return None
        
    df = pd.DataFrame(timeline)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time'], 
        y=df['wpm'],
        mode='lines+markers',
        name='Pace',
        line=dict(color='#4F8BF9', width=3),
        marker=dict(size=8, color='#2ecc71'),
        hovertemplate='Time: %{x}s<br>WPM: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title="Speaking Flow & Consistency",
        xaxis_title="Time (seconds)",
        yaxis_title="Words Per Minute",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(14, 17, 23, 0.5)',
        font={'color': "white"},
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#2e3440'),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def create_vocabulary_sack(word_count, unique_words):
    """
    A simple visualization for 'Word Sack'.
    """
    # Using a Bar chart to represent 'Fullness' vs 'Variety'
    variety_ratio = (unique_words / max(1, word_count)) * 100
    
    fig = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = variety_ratio,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Vocabulary Richness %", 'font': {'size': 20, 'color': "#f1c40f"}},
        gauge = {
            'shape': "bullet",
            'axis': {'range': [None, 100]},
            'bar': {'color': "#f1c40f"},
            'steps': [
                {'range': [0, 30], 'color': "#3b1c1c"},
                {'range': [30, 70], 'color': "#1a1f2e"}],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.75,
                'value': 60}
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"},
        height=150,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_history_chart(history_data):
    """
    Creates a line chart showing progress over sessions.
    """
    if not history_data:
        return None
        
    df = pd.DataFrame(history_data)
    if df.empty:
        return None
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['score'],
        mode='lines+markers',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=10, color='#4F8BF9'),
        name="Grammar Score"
    ))

    fig.update_layout(
        title="Your Progress Over Time",
        xaxis_title="Date",
        yaxis_title="Score (0-10)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(14, 17, 23, 0.5)',
        font={'color': "white"},
        yaxis=dict(range=[0, 10.5]),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig
