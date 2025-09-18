"""
MLB Sabermetrics Dashboard
Interactive Streamlit application for baseball analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from sabermetrics_engine import SabermetricsEngine
    from data_collector import MLBDataCollector
except ImportError:
    st.error("Unable to import required modules. Please ensure the src/ directory is accessible.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="MLB Sabermetrics Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2d5a87);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    
    .player-comparison {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stat-highlight {
        font-size: 2rem;
        font-weight: bold;
        color: #007bff;
    }
    
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_data():
    """Load and cache sample MLB data"""
    collector = MLBDataCollector()
    return collector.generate_sample_data()

@st.cache_resource
def get_analytics_engine():
    """Get cached analytics engine instance"""
    return SabermetricsEngine()

def create_player_metrics_chart(player_stats, player_name):
    """Create radar chart for player metrics"""
    engine = get_analytics_engine()
    metrics = engine.calculate_comprehensive_player_metrics(player_stats)
    
    # Normalize metrics for radar chart (0-100 scale)
    normalized_metrics = {
        'AVG': min(100, metrics['AVG'] * 400),  # Scale batting average
        'OBP': min(100, metrics['OBP'] * 250),  # Scale OBP
        'SLG': min(100, metrics['SLG'] * 200),  # Scale slugging
        'wRC+': min(100, metrics['wRC+']),      # Already on 100 scale
        'ISO': min(100, metrics['ISO'] * 400),  # Scale ISO
        'BABIP': min(100, metrics['BABIP'] * 330)  # Scale BABIP
    }
    
    categories = list(normalized_metrics.keys())
    values = list(normalized_metrics.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=player_name,
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title=f"{player_name} - Performance Radar",
        height=400
    )
    
    return fig

def create_comparison_chart(player1_data, player2_data, player1_name, player2_name):
    """Create comparison bar chart for two players"""
    engine = get_analytics_engine()
    
    p1_metrics = engine.calculate_comprehensive_player_metrics(player1_data)
    p2_metrics = engine.calculate_comprehensive_player_metrics(player2_data)
    
    metrics_to_compare = ['AVG', 'OBP', 'SLG', 'wOBA', 'wRC+', 'BABIP', 'ISO']
    
    fig = go.Figure()
    
    # Player 1 bars
    fig.add_trace(go.Bar(
        name=player1_name,
        x=metrics_to_compare,
        y=[p1_metrics[metric] for metric in metrics_to_compare],
        marker_color='#1f77b4'
    ))
    
    # Player 2 bars
    fig.add_trace(go.Bar(
        name=player2_name,
        x=metrics_to_compare,
        y=[p2_metrics[metric] for metric in metrics_to_compare],
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title="Player Comparison - Key Metrics",
        xaxis_title="Metrics",
        yaxis_title="Value",
        barmode='group',
        height=400
    )
    
    return fig

def create_team_analysis_chart(sample_data):
    """Create team analysis visualization"""
    # Process team data from sample players
    team_stats = {}
    
    for player, info in sample_data['batters'].items():
        team = info['team']
        if team not in team_stats:
            team_stats[team] = []
        
        engine = get_analytics_engine()
        metrics = engine.calculate_comprehensive_player_metrics(info['stats'])
        team_stats[team].append({
            'player': player,
            'wRC+': metrics['wRC+'],
            'OPS': metrics['OPS'],
            'HR': info['stats']['HR']
        })
    
    # Calculate team averages
    team_averages = {}
    for team, players in team_stats.items():
        avg_wrc = np.mean([p['wRC+'] for p in players])
        avg_ops = np.mean([p['OPS'] for p in players])
        total_hr = sum([p['HR'] for p in players])
        
        team_averages[team] = {
            'wRC+': avg_wrc,
            'OPS': avg_ops,
            'HR': total_hr
        }
    
    # Create scatter plot
    teams = list(team_averages.keys())
    wrc_values = [team_averages[team]['wRC+'] for team in teams]
    ops_values = [team_averages[team]['OPS'] for team in teams]
    hr_values = [team_averages[team]['HR'] for team in teams]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=ops_values,
        y=wrc_values,
        mode='markers+text',
        text=teams,
        textposition="middle center",
        marker=dict(
            size=[hr/3 for hr in hr_values],  # Size based on HR
            color=wrc_values,
            colorscale='viridis',
            showscale=True,
            colorbar=dict(title="wRC+"),
            sizemode='diameter'
        ),
        name="Teams"
    ))
    
    fig.update_layout(
        title="Team Performance Analysis (Sample Players)",
        xaxis_title="Team OPS",
        yaxis_title="Team wRC+",
        height=500
    )
    
    return fig

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; text-align: center; margin: 0;">
            ⚾ MLB Sabermetrics Dashboard
        </h1>
        <p style="color: #cce7ff; text-align: center; margin: 0.5rem 0 0 0;">
            Advanced Baseball Analytics & Player Comparison Tool
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    try:
        sample_data = load_sample_data()
        engine = get_analytics_engine()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Sidebar
    st.sidebar.header("🎛️ Dashboard Controls")
    
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type",
        ["Player Overview", "Player Comparison", "Team Analysis", "Advanced Metrics"]
    )
    
    if analysis_type == "Player Overview":
        st.header("📊 Individual Player Analysis")
        
        # Player selection
        player_names = list(sample_data['batters'].keys())
        selected_player = st.selectbox("Select Player", player_names)
        
        if selected_player:
            player_info = sample_data['batters'][selected_player]
            player_stats = player_info['stats']
            
            # Calculate comprehensive metrics
            metrics = engine.calculate_comprehensive_player_metrics(player_stats)
            
            # Display basic info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{selected_player}</h3>
                    <p><strong>Team:</strong> {player_info['team']}</p>
                    <p><strong>Position:</strong> {player_info['position']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Traditional Stats</h4>
                    <p><strong>AVG:</strong> {metrics['AVG']:.3f}</p>
                    <p><strong>HR:</strong> {player_stats['HR']}</p>
                    <p><strong>RBI:</strong> {player_stats['RBI']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Advanced Stats</h4>
                    <p><strong>wRC+:</strong> {metrics['wRC+']:.0f}</p>
                    <p><strong>wOBA:</strong> {metrics['wOBA']:.3f}</p>
                    <p><strong>ISO:</strong> {metrics['ISO']:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed metrics table
            st.subheader("Detailed Sabermetrics")
            
            metrics_df = pd.DataFrame([{
                'Metric': 'Batting Average (AVG)',
                'Value': f"{metrics['AVG']:.3f}",
                'Description': 'Hits per at-bat'
            }, {
                'Metric': 'On-Base Percentage (OBP)',
                'Value': f"{metrics['OBP']:.3f}",
                'Description': 'Rate of reaching base safely'
            }, {
                'Metric': 'Slugging Percentage (SLG)',
                'Value': f"{metrics['SLG']:.3f}",
                'Description': 'Total bases per at-bat'
            }, {
                'Metric': 'Weighted On-Base Average (wOBA)',
                'Value': f"{metrics['wOBA']:.3f}",
                'Description': 'Overall offensive value per plate appearance'
            }, {
                'Metric': 'Weighted Runs Created Plus (wRC+)',
                'Value': f"{metrics['wRC+']:.0f}",
                'Description': 'Offensive production vs league average (100)'
            }, {
                'Metric': 'Isolated Power (ISO)',
                'Value': f"{metrics['ISO']:.3f}",
                'Description': 'Raw power measure (SLG - AVG)'
            }, {
                'Metric': 'BABIP',
                'Value': f"{metrics['BABIP']:.3f}",
                'Description': 'Batting average on balls in play'
            }])
            
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            
            # Performance radar chart
            st.subheader("Performance Radar Chart")
            radar_fig = create_player_metrics_chart(player_stats, selected_player)
            st.plotly_chart(radar_fig, use_container_width=True)
    
    elif analysis_type == "Player Comparison":
        st.header("🥊 Player Comparison")
        
        player_names = list(sample_data['batters'].keys())
        
        col1, col2 = st.columns(2)
        
        with col1:
            player1 = st.selectbox("Select Player 1", player_names, key="p1")
        
        with col2:
            player2 = st.selectbox("Select Player 2", player_names, key="p2")
        
        if player1 and player2 and player1 != player2:
            p1_info = sample_data['batters'][player1]
            p2_info = sample_data['batters'][player2]
            
            p1_stats = p1_info['stats']
            p2_stats = p2_info['stats']
            
            # Calculate metrics for comparison
            p1_metrics = engine.calculate_comprehensive_player_metrics(p1_stats)
            p2_metrics = engine.calculate_comprehensive_player_metrics(p2_stats)
            
            # Comparison header
            st.markdown(f"""
            <div class="player-comparison">
                <h3 style="text-align: center;">
                    {player1} ({p1_info['team']}) vs {player2} ({p2_info['team']})
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Side-by-side metrics
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.markdown(f"""
                **{player1}**
                - AVG: {p1_metrics['AVG']:.3f}
                - OPS: {p1_metrics['OPS']:.3f}
                - wRC+: {p1_metrics['wRC+']:.0f}
                - HR: {p1_stats['HR']}
                - RBI: {p1_stats['RBI']}
                """)
            
            with col3:
                st.markdown(f"""
                **{player2}**
                - AVG: {p2_metrics['AVG']:.3f}
                - OPS: {p2_metrics['OPS']:.3f}
                - wRC+: {p2_metrics['wRC+']:.0f}
                - HR: {p2_stats['HR']}
                - RBI: {p2_stats['RBI']}
                """)
            
            # Comparison chart
            comparison_fig = create_comparison_chart(p1_stats, p2_stats, player1, player2)
            st.plotly_chart(comparison_fig, use_container_width=True)
            
            # Winner analysis
            st.subheader("Statistical Advantages")
            
            advantages = []
            metrics_to_check = ['AVG', 'OBP', 'SLG', 'wOBA', 'wRC+', 'ISO']
            
            for metric in metrics_to_check:
                if p1_metrics[metric] > p2_metrics[metric]:
                    advantages.append(f"✅ {player1} leads in {metric}: {p1_metrics[metric]:.3f} vs {p2_metrics[metric]:.3f}")
                elif p2_metrics[metric] > p1_metrics[metric]:
                    advantages.append(f"✅ {player2} leads in {metric}: {p2_metrics[metric]:.3f} vs {p1_metrics[metric]:.3f}")
                else:
                    advantages.append(f"🤝 Tied in {metric}: {p1_metrics[metric]:.3f}")
            
            for advantage in advantages:
                st.markdown(advantage)
    
    elif analysis_type == "Team Analysis":
        st.header("🏟️ Team Performance Analysis")
        
        # Team analysis chart
        team_fig = create_team_analysis_chart(sample_data)
        st.plotly_chart(team_fig, use_container_width=True)
        
        st.markdown("""
        **Analysis Notes:**
        - Bubble size represents total home runs from sample players
        - X-axis shows team OPS (On-base Plus Slugging)
        - Y-axis shows team wRC+ (Weighted Runs Created Plus)
        - Color intensity indicates wRC+ values
        """)
        
        # Team summary table
        st.subheader("Team Summary (Sample Players)")
        
        team_summary = []
        teams_processed = set()
        
        for player, info in sample_data['batters'].items():
            team = info['team']
            if team not in teams_processed:
                teams_processed.add(team)
                
                # Get all players from this team
                team_players = [p for p, i in sample_data['batters'].items() if i['team'] == team]
                
                team_summary.append({
                    'Team': team,
                    'Players': len(team_players),
                    'Sample Players': ', '.join(team_players)
                })
        
        summary_df = pd.DataFrame(team_summary)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    elif analysis_type == "Advanced Metrics":
        st.header("📈 Advanced Sabermetrics Explained")
        
        st.markdown("""
        ### Understanding Advanced Baseball Statistics
        
        This dashboard calculates and displays various advanced baseball metrics. Here's what they mean:
        """)
        
        # Metrics explanation
        metrics_explanation = {
            'wOBA (Weighted On-Base Average)': {
                'description': 'Measures a hitter\'s overall offensive value per plate appearance',
                'scale': '~0.320 is league average, higher is better',
                'formula': 'Linear weights applied to different offensive outcomes'
            },
            'wRC+ (Weighted Runs Created Plus)': {
                'description': 'Measures offensive production compared to league average',
                'scale': '100 is average, 115 = 15% above average',
                'formula': 'Park and league adjusted offensive metric'
            },
            'ISO (Isolated Power)': {
                'description': 'Measures raw power by isolating extra-base hits',
                'scale': '~0.140 is average, 0.200+ is excellent',
                'formula': 'Slugging Percentage - Batting Average'
            },
            'BABIP': {
                'description': 'Batting Average on Balls In Play',
                'scale': '~0.300 is typical, extreme values may indicate luck',
                'formula': '(H - HR) / (AB - K - HR + SF)'
            },
            'OPS+': {
                'description': 'OPS adjusted for park and league factors',
                'scale': '100 is average, 130+ is All-Star level',
                'formula': 'Park-adjusted OBP and SLG vs league average'
            }
        }
        
        for metric, info in metrics_explanation.items():
            with st.expander(f"📊 {metric}"):
                st.write(f"**Description:** {info['description']}")
                st.write(f"**Scale:** {info['scale']}")
                st.write(f"**Calculation:** {info['formula']}")
        
        # Sample calculation demo
        st.subheader("Live Calculation Demo")
        
        selected_demo_player = st.selectbox(
            "See calculations for:", 
            list(sample_data['batters'].keys()),
            key="demo_player"
        )
        
        if selected_demo_player:
            demo_stats = sample_data['batters'][selected_demo_player]['stats']
            demo_metrics = engine.calculate_comprehensive_player_metrics(demo_stats)
            
            st.markdown(f"### {selected_demo_player} - Step-by-step Calculations")
            
            # Show raw stats
            st.markdown("**Raw Statistics:**")
            raw_stats_display = {
                'At Bats (AB)': demo_stats['AB'],
                'Hits (H)': demo_stats['H'],
                'Home Runs (HR)': demo_stats['HR'],
                'Walks (BB)': demo_stats['BB'],
                'Doubles (2B)': demo_stats['2B'],
                'Triples (3B)': demo_stats['3B']
            }
            
            for stat, value in raw_stats_display.items():
                st.write(f"- {stat}: {value}")
            
            st.markdown("**Calculated Advanced Metrics:**")
            calculated_metrics = {
                'Batting Average': f"{demo_metrics['AVG']:.3f} = {demo_stats['H']}/{demo_stats['AB']}",
                'On-Base Percentage': f"{demo_metrics['OBP']:.3f}",
                'Slugging Percentage': f"{demo_metrics['SLG']:.3f}",
                'wOBA': f"{demo_metrics['wOBA']:.3f}",
                'wRC+': f"{demo_metrics['wRC+']:.0f}",
                'ISO': f"{demo_metrics['ISO']:.3f} = {demo_metrics['SLG']:.3f} - {demo_metrics['AVG']:.3f}"
            }
            
            for metric, calculation in calculated_metrics.items():
                st.write(f"- {metric}: {calculation}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>⚾ MLB Sabermetrics Dashboard | Built with Streamlit & Advanced Baseball Analytics</p>
        <p>Data: Sample 2023 MLB Statistics | Calculations: Custom Sabermetrics Engine</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()