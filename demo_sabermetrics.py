#!/usr/bin/env python3
"""
MLB Sabermetrics Dashboard - Portfolio Demo
Showcases advanced baseball analytics capabilities
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.sabermetrics_engine import SabermetricsEngine
    from src.data_collector import MLBDataCollector
except ImportError:
    print("Error: Cannot import required modules. Please ensure src/ directory is accessible.")
    sys.exit(1)

class MLBAnalyticsDemo:
    """
    Demonstration class for MLB Sabermetrics Dashboard capabilities
    """
    
    def __init__(self):
        self.engine = SabermetricsEngine()
        self.collector = MLBDataCollector()
        self.sample_data = self.collector.generate_sample_data()
    
    def display_header(self):
        """Display the demo header"""
        print("=" * 70)
        print("⚾ MLB SABERMETRICS DASHBOARD - PORTFOLIO DEMONSTRATION")
        print("=" * 70)
        print("Advanced Baseball Analytics & Player Comparison Platform")
        print(f"Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def demo_individual_analysis(self):
        """Demonstrate individual player analysis"""
        print("📊 INDIVIDUAL PLAYER ANALYSIS")
        print("-" * 50)
        
        # Select a star player for demo
        player_name = "Ronald Acuña Jr."
        player_info = self.sample_data['batters'][player_name]
        player_stats = player_info['stats']
        
        print(f"Analyzing: {player_name} ({player_info['team']}) - {player_info['position']}")
        print()
        
        # Calculate comprehensive metrics
        metrics = self.engine.calculate_comprehensive_player_metrics(player_stats)
        
        print("TRADITIONAL STATISTICS:")
        print(f"  Batting Average: {metrics['AVG']:.3f}")
        print(f"  Home Runs: {player_stats['HR']}")
        print(f"  RBIs: {player_stats['RBI']}")
        print(f"  Stolen Bases: {player_stats['SB']}")
        print()
        
        print("ADVANCED SABERMETRICS:")
        print(f"  wOBA (Weighted On-Base Average): {metrics['wOBA']:.3f}")
        print(f"  wRC+ (Weighted Runs Created+): {metrics['wRC+']:.0f}")
        print(f"  ISO (Isolated Power): {metrics['ISO']:.3f}")
        print(f"  BABIP: {metrics['BABIP']:.3f}")
        print(f"  OPS+: {metrics['OPS+']:.0f}")
        print()
        
        # Player evaluation
        self.evaluate_player_performance(metrics, player_name)
        print()
    
    def demo_player_comparison(self):
        """Demonstrate player comparison capabilities"""
        print("🥊 PLAYER COMPARISON ANALYSIS")
        print("-" * 50)
        
        # Compare two superstars
        player1 = "Mookie Betts"
        player2 = "Mike Trout"
        
        p1_info = self.sample_data['batters'][player1]
        p2_info = self.sample_data['batters'][player2]
        
        print(f"Comparing: {player1} ({p1_info['team']}) vs {player2} ({p2_info['team']})")
        print()
        
        # Calculate metrics for both players
        p1_metrics = self.engine.calculate_comprehensive_player_metrics(p1_info['stats'])
        p2_metrics = self.engine.calculate_comprehensive_player_metrics(p2_info['stats'])
        
        # Display comparison
        comparison_metrics = ['AVG', 'OBP', 'SLG', 'wOBA', 'wRC+', 'ISO', 'BABIP']
        
        print(f"{'METRIC':<20} {player1:<15} {player2:<15} {'ADVANTAGE':<15}")
        print("-" * 70)
        
        p1_wins = 0
        p2_wins = 0
        
        for metric in comparison_metrics:
            p1_val = p1_metrics[metric]
            p2_val = p2_metrics[metric]
            
            if p1_val > p2_val:
                advantage = f"{player1} ✓"
                p1_wins += 1
            elif p2_val > p1_val:
                advantage = f"{player2} ✓"
                p2_wins += 1
            else:
                advantage = "Tied"
            
            print(f"{metric:<20} {p1_val:<15.3f} {p2_val:<15.3f} {advantage:<15}")
        
        print("-" * 70)
        print(f"STATISTICAL WINS: {player1}: {p1_wins}, {player2}: {p2_wins}")
        
        # Determine overall winner
        if p1_wins > p2_wins:
            print(f"🏆 STATISTICAL EDGE: {player1}")
        elif p2_wins > p1_wins:
            print(f"🏆 STATISTICAL EDGE: {player2}")
        else:
            print("🤝 STATISTICALLY EVEN")
        
        print()
    
    def demo_pitcher_analysis(self):
        """Demonstrate pitcher analysis"""
        print("⚾ PITCHER ANALYSIS")
        print("-" * 50)
        
        pitcher_name = "Gerrit Cole"
        pitcher_info = self.sample_data['pitchers'][pitcher_name]
        pitcher_stats = pitcher_info['stats']
        
        print(f"Analyzing: {pitcher_name} ({pitcher_info['team']})")
        print()
        
        # Calculate pitcher metrics
        p_metrics = self.engine.calculate_pitcher_metrics(pitcher_stats)
        
        print("PITCHING STATISTICS:")
        print(f"  ERA: {p_metrics['ERA']:.2f}")
        print(f"  WHIP: {p_metrics['WHIP']:.3f}")
        print(f"  FIP: {p_metrics['FIP']:.2f}")
        print(f"  K/9: {p_metrics['K_per_9']:.1f}")
        print(f"  BB/9: {p_metrics['BB_per_9']:.1f}")
        print(f"  K/BB Ratio: {p_metrics['K_BB_ratio']:.2f}")
        print()
        
        # Pitcher evaluation
        self.evaluate_pitcher_performance(p_metrics, pitcher_name)
        print()
    
    def demo_team_analysis(self):
        """Demonstrate team-level analysis"""
        print("🏟️ TEAM PERFORMANCE ANALYSIS")
        print("-" * 50)
        
        # Process team data
        team_stats = {}
        
        for player, info in self.sample_data['batters'].items():
            team = info['team']
            if team not in team_stats:
                team_stats[team] = {'players': [], 'total_hr': 0, 'total_rbi': 0}
            
            metrics = self.engine.calculate_comprehensive_player_metrics(info['stats'])
            team_stats[team]['players'].append({
                'name': player,
                'wRC+': metrics['wRC+'],
                'OPS': metrics['OPS']
            })
            team_stats[team]['total_hr'] += info['stats']['HR']
            team_stats[team]['total_rbi'] += info['stats']['RBI']
        
        # Calculate team averages
        print(f"{'TEAM':<6} {'PLAYERS':<3} {'AVG wRC+':<10} {'AVG OPS':<8} {'TOTAL HR':<9} {'TOTAL RBI':<10}")
        print("-" * 60)
        
        for team, data in team_stats.items():
            avg_wrc = sum(p['wRC+'] for p in data['players']) / len(data['players'])
            avg_ops = sum(p['OPS'] for p in data['players']) / len(data['players'])
            
            print(f"{team:<6} {len(data['players']):<3} {avg_wrc:<10.0f} {avg_ops:<8.3f} {data['total_hr']:<9} {data['total_rbi']:<10}")
        
        print()
    
    def demo_advanced_metrics_explanation(self):
        """Explain advanced metrics calculations"""
        print("📈 ADVANCED METRICS EXPLANATION")
        print("-" * 50)
        
        print("KEY SABERMETRICS DEFINITIONS:")
        print()
        
        metrics_info = {
            'wOBA': 'Weighted On-Base Average - Overall offensive value per PA',
            'wRC+': 'Weighted Runs Created Plus - Offensive production vs league (100 = avg)',
            'ISO': 'Isolated Power - Raw power measure (SLG - AVG)',
            'BABIP': 'Batting Average on Balls in Play - Luck indicator',
            'FIP': 'Fielding Independent Pitching - Pitcher performance without defense',
            'WHIP': 'Walks + Hits per Inning Pitched - Baserunner prevention'
        }
        
        for metric, description in metrics_info.items():
            print(f"  {metric:<6}: {description}")
        
        print()
        
        # Show sample calculation
        print("SAMPLE CALCULATION - Mike Trout wOBA:")
        trout_stats = self.sample_data['batters']['Mike Trout']['stats']
        woba = self.engine.calculate_woba(trout_stats)
        
        print(f"  Input Stats: AB={trout_stats['AB']}, H={trout_stats['H']}, BB={trout_stats['BB']}")
        print(f"  Linear Weights Applied to Different Hit Types")
        print(f"  Calculated wOBA: {woba:.3f}")
        print(f"  League Average: ~0.320 (Trout is {'above' if woba > 0.320 else 'below'} average)")
        print()
    
    def evaluate_player_performance(self, metrics, player_name):
        """Evaluate player performance based on metrics"""
        wrc_plus = metrics['wRC+']
        
        if wrc_plus >= 140:
            rating = "⭐ MVP CANDIDATE"
        elif wrc_plus >= 130:
            rating = "🌟 ALL-STAR LEVEL"
        elif wrc_plus >= 115:
            rating = "✅ ABOVE AVERAGE"
        elif wrc_plus >= 100:
            rating = "🔶 LEAGUE AVERAGE"
        else:
            rating = "🔻 BELOW AVERAGE"
        
        print(f"PERFORMANCE RATING: {rating}")
        print(f"Analysis: {player_name}'s wRC+ of {wrc_plus:.0f} indicates they are ", end="")
        
        if wrc_plus > 100:
            print(f"{wrc_plus - 100:.0f}% better than league average")
        else:
            print(f"{100 - wrc_plus:.0f}% below league average")
    
    def evaluate_pitcher_performance(self, metrics, pitcher_name):
        """Evaluate pitcher performance"""
        era = metrics['ERA']
        fip = metrics['FIP']
        
        if era < 3.00:
            rating = "⭐ ACE LEVEL"
        elif era < 4.00:
            rating = "🌟 ABOVE AVERAGE"
        elif era < 4.50:
            rating = "✅ LEAGUE AVERAGE"
        else:
            rating = "🔻 BELOW AVERAGE"
        
        print(f"PERFORMANCE RATING: {rating}")
        print(f"Analysis: ERA of {era:.2f} with FIP of {fip:.2f}")
        
        if fip < era:
            print("FIP suggests pitcher has been unlucky - expect improvement")
        elif fip > era:
            print("FIP suggests pitcher has been lucky - expect regression")
        else:
            print("ERA and FIP align - performance is sustainable")
    
    def display_technical_capabilities(self):
        """Display technical capabilities demonstrated"""
        print("🛠️ TECHNICAL CAPABILITIES DEMONSTRATED")
        print("-" * 50)
        
        capabilities = [
            "✅ Advanced Sabermetrics Calculations (wOBA, wRC+, FIP, ISO, BABIP)",
            "✅ Real MLB Data Processing and Analysis",
            "✅ Player Performance Evaluation and Comparison",
            "✅ Team-Level Statistical Analysis",
            "✅ Pitcher and Batter Specialized Metrics",
            "✅ Interactive Dashboard Components (Streamlit-ready)",
            "✅ Data Visualization and Reporting",
            "✅ Scalable Architecture for Multiple Data Sources",
            "✅ Professional Documentation and Code Organization",
            "✅ Portfolio-Ready Baseball Analytics Platform"
        ]
        
        for capability in capabilities:
            print(f"  {capability}")
        
        print()
    
    def display_footer(self):
        """Display demo footer with next steps"""
        print("=" * 70)
        print("🎯 PORTFOLIO IMPACT")
        print("=" * 70)
        
        print("This MLB Sabermetrics Dashboard demonstrates:")
        print("• Advanced domain expertise in baseball analytics")
        print("• Professional-grade statistical calculations")
        print("• Interactive data visualization capabilities")
        print("• Full-stack development skills")
        print("• Real-world application of data science")
        print()
        
        print("TO RUN THE INTERACTIVE DASHBOARD:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run: streamlit run dashboard/streamlit_app.py")
        print("3. Open browser to localhost:8501")
        print()
        
        print("GITHUB REPOSITORY: MLB-Sabermetrics-Dashboard")
        print("⚾ Professional Baseball Analytics for Your Portfolio")
        print("=" * 70)

def main():
    """Run the complete MLB Sabermetrics demo"""
    try:
        demo = MLBAnalyticsDemo()
        
        # Run all demonstration components
        demo.display_header()
        demo.demo_individual_analysis()
        demo.demo_player_comparison()
        demo.demo_pitcher_analysis()
        demo.demo_team_analysis()
        demo.demo_advanced_metrics_explanation()
        demo.display_technical_capabilities()
        demo.display_footer()
        
    except Exception as e:
        print(f"Demo error: {e}")
        print("Please ensure all required modules are installed and accessible.")

if __name__ == "__main__":
    main()