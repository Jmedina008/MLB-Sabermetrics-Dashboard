"""
MLB Sabermetrics Analytics Engine
Advanced baseball metrics calculations and player analysis tools
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SabermetricsEngine:
    """
    Core engine for calculating advanced baseball statistics and sabermetrics
    """
    
    def __init__(self):
        # League average constants (2023 MLB season approximations)
        self.league_constants = {
            'wOBA_scale': 1.255,
            'wOBA_league': 0.320,
            'R_per_game_league': 4.65,
            'wRC_league': 100,
            'FIP_constant': 3.10,
            'park_factor_neutral': 1.000
        }
        
        # Linear weights for wOBA calculation (2023)
        self.woba_weights = {
            'uBB': 0.690,  # Unintentional walks
            'HBP': 0.722,  # Hit by pitch
            '1B': 0.888,   # Singles
            '2B': 1.271,   # Doubles
            '3B': 1.616,   # Triples
            'HR': 2.101    # Home runs
        }
        
    def calculate_basic_stats(self, stats: Dict) -> Dict:
        """Calculate basic baseball statistics"""
        ab = stats.get('AB', 0)
        h = stats.get('H', 0)
        bb = stats.get('BB', 0)
        sf = stats.get('SF', 0)
        hbp = stats.get('HBP', 0)
        
        # Avoid division by zero
        pa = ab + bb + sf + hbp
        
        basic_stats = {}
        
        # Batting Average
        basic_stats['AVG'] = h / ab if ab > 0 else 0
        
        # On-Base Percentage
        basic_stats['OBP'] = (h + bb + hbp) / pa if pa > 0 else 0
        
        # Slugging Percentage
        singles = stats.get('1B', h - stats.get('2B', 0) - stats.get('3B', 0) - stats.get('HR', 0))
        total_bases = singles + (2 * stats.get('2B', 0)) + (3 * stats.get('3B', 0)) + (4 * stats.get('HR', 0))
        basic_stats['SLG'] = total_bases / ab if ab > 0 else 0
        
        # OPS
        basic_stats['OPS'] = basic_stats['OBP'] + basic_stats['SLG']
        
        return basic_stats
    
    def calculate_woba(self, stats: Dict) -> float:
        """Calculate Weighted On-Base Average (wOBA)"""
        bb = stats.get('BB', 0) - stats.get('IBB', 0)  # Unintentional walks
        hbp = stats.get('HBP', 0)
        singles = stats.get('1B', 0)
        doubles = stats.get('2B', 0)
        triples = stats.get('3B', 0)
        hr = stats.get('HR', 0)
        
        ab = stats.get('AB', 0)
        sf = stats.get('SF', 0)
        
        # wOBA calculation
        numerator = (self.woba_weights['uBB'] * bb + 
                    self.woba_weights['HBP'] * hbp + 
                    self.woba_weights['1B'] * singles + 
                    self.woba_weights['2B'] * doubles + 
                    self.woba_weights['3B'] * triples + 
                    self.woba_weights['HR'] * hr)
        
        denominator = ab + bb + sf + hbp
        
        return numerator / denominator if denominator > 0 else 0
    
    def calculate_wrc_plus(self, stats: Dict, park_factor: float = 1.0) -> float:
        """Calculate Weighted Runs Created Plus (wRC+)"""
        woba = self.calculate_woba(stats)
        
        # wRC+ calculation
        wrc_plus = ((woba - self.league_constants['wOBA_league']) / 
                   self.league_constants['wOBA_scale'] + 
                   self.league_constants['R_per_game_league']) * 100 / park_factor
        
        return wrc_plus
    
    def calculate_babip(self, stats: Dict) -> float:
        """Calculate Batting Average on Balls in Play"""
        h = stats.get('H', 0)
        hr = stats.get('HR', 0)
        ab = stats.get('AB', 0)
        k = stats.get('K', 0)
        sf = stats.get('SF', 0)
        
        balls_in_play = ab - k - hr + sf
        hits_in_play = h - hr
        
        return hits_in_play / balls_in_play if balls_in_play > 0 else 0
    
    def calculate_iso(self, stats: Dict) -> float:
        """Calculate Isolated Power (ISO)"""
        basic = self.calculate_basic_stats(stats)
        return basic['SLG'] - basic['AVG']
    
    def calculate_pitcher_fip(self, stats: Dict) -> float:
        """Calculate Fielding Independent Pitching (FIP)"""
        hr = stats.get('HR', 0)
        bb = stats.get('BB', 0)
        hbp = stats.get('HBP', 0)
        k = stats.get('K', 0)
        ip = stats.get('IP', 0)
        
        if ip <= 0:
            return 0
            
        fip = ((13 * hr + 3 * (bb + hbp) - 2 * k) / ip) + self.league_constants['FIP_constant']
        return fip
    
    def calculate_pitcher_whip(self, stats: Dict) -> float:
        """Calculate Walks plus Hits per Inning Pitched (WHIP)"""
        bb = stats.get('BB', 0)
        h = stats.get('H', 0)
        ip = stats.get('IP', 0)
        
        return (bb + h) / ip if ip > 0 else 0
    
    def calculate_ops_plus(self, stats: Dict, park_factor: float = 1.0, 
                          league_obp: float = 0.320, league_slg: float = 0.425) -> float:
        """Calculate OPS+ (park and league adjusted)"""
        basic = self.calculate_basic_stats(stats)
        
        obp_ratio = basic['OBP'] / league_obp if league_obp > 0 else 1
        slg_ratio = basic['SLG'] / league_slg if league_slg > 0 else 1
        
        ops_plus = 100 * (obp_ratio + slg_ratio - 1) / park_factor
        return ops_plus
    
    def calculate_comprehensive_player_metrics(self, batting_stats: Dict, 
                                             park_factor: float = 1.0) -> Dict:
        """Calculate comprehensive set of player metrics"""
        metrics = {}
        
        # Basic stats
        basic = self.calculate_basic_stats(batting_stats)
        metrics.update(basic)
        
        # Advanced metrics
        metrics['wOBA'] = self.calculate_woba(batting_stats)
        metrics['wRC+'] = self.calculate_wrc_plus(batting_stats, park_factor)
        metrics['BABIP'] = self.calculate_babip(batting_stats)
        metrics['ISO'] = self.calculate_iso(batting_stats)
        metrics['OPS+'] = self.calculate_ops_plus(batting_stats, park_factor)
        
        # Additional derived metrics
        metrics['BB_Rate'] = batting_stats.get('BB', 0) / (batting_stats.get('AB', 0) + batting_stats.get('BB', 0)) if (batting_stats.get('AB', 0) + batting_stats.get('BB', 0)) > 0 else 0
        metrics['K_Rate'] = batting_stats.get('K', 0) / (batting_stats.get('AB', 0) + batting_stats.get('BB', 0)) if (batting_stats.get('AB', 0) + batting_stats.get('BB', 0)) > 0 else 0
        
        return metrics
    
    def calculate_pitcher_metrics(self, pitching_stats: Dict) -> Dict:
        """Calculate comprehensive pitcher metrics"""
        metrics = {}
        
        # Basic pitcher stats
        ip = pitching_stats.get('IP', 0)
        er = pitching_stats.get('ER', 0)
        h = pitching_stats.get('H', 0)
        bb = pitching_stats.get('BB', 0)
        k = pitching_stats.get('K', 0)
        
        # ERA
        metrics['ERA'] = (er * 9) / ip if ip > 0 else 0
        
        # WHIP
        metrics['WHIP'] = self.calculate_pitcher_whip(pitching_stats)
        
        # FIP
        metrics['FIP'] = self.calculate_pitcher_fip(pitching_stats)
        
        # K/9, BB/9, HR/9
        metrics['K_per_9'] = (k * 9) / ip if ip > 0 else 0
        metrics['BB_per_9'] = (bb * 9) / ip if ip > 0 else 0
        metrics['HR_per_9'] = (pitching_stats.get('HR', 0) * 9) / ip if ip > 0 else 0
        
        # K/BB ratio
        metrics['K_BB_ratio'] = k / bb if bb > 0 else k if k > 0 else 0
        
        return metrics
    
    def compare_players(self, player1_stats: Dict, player2_stats: Dict, 
                       metrics: List[str] = None) -> Dict:
        """Compare two players across specified metrics"""
        if metrics is None:
            metrics = ['AVG', 'OBP', 'SLG', 'OPS', 'wOBA', 'wRC+', 'BABIP', 'ISO']
        
        p1_metrics = self.calculate_comprehensive_player_metrics(player1_stats)
        p2_metrics = self.calculate_comprehensive_player_metrics(player2_stats)
        
        comparison = {}
        for metric in metrics:
            if metric in p1_metrics and metric in p2_metrics:
                comparison[metric] = {
                    'player1': p1_metrics[metric],
                    'player2': p2_metrics[metric],
                    'difference': p1_metrics[metric] - p2_metrics[metric],
                    'player1_better': p1_metrics[metric] > p2_metrics[metric]
                }
        
        return comparison
    
    def calculate_war_approximation(self, batting_stats: Dict, fielding_stats: Dict = None, 
                                  position: str = 'OF') -> float:
        """
        Simplified WAR approximation calculation
        Note: This is a simplified version. Actual WAR is much more complex.
        """
        # This is a very simplified WAR calculation for demonstration
        # Real WAR involves complex defensive metrics, replacement level, etc.
        
        wrc_plus = self.calculate_wrc_plus(batting_stats)
        pa = batting_stats.get('AB', 0) + batting_stats.get('BB', 0) + batting_stats.get('SF', 0) + batting_stats.get('HBP', 0)
        
        # Offensive value (simplified)
        offensive_value = ((wrc_plus - 100) / 100) * (pa / 700) * 20  # Very rough approximation
        
        # Position adjustment (simplified)
        position_adjustments = {
            'C': 12.5, '1B': -12.5, '2B': 2.5, '3B': 2.5, 
            'SS': 7.5, 'LF': -7.5, 'CF': 2.5, 'RF': -7.5, 'DH': -17.5
        }
        
        position_adj = position_adjustments.get(position, 0) * (pa / 700)
        
        # Replacement level
        replacement_level = 2.0 * (pa / 700)
        
        war_approx = offensive_value + position_adj + replacement_level
        
        return max(0, war_approx)  # WAR shouldn't be negative for basic calculation

# Example usage and testing
def demo_sabermetrics():
    """Demonstrate sabermetrics calculations"""
    engine = SabermetricsEngine()
    
    # Example player stats (Mike Trout-like numbers)
    trout_stats = {
        'AB': 473, 'H': 134, 'BB': 89, 'HBP': 3, 'SF': 4,
        '1B': 82, '2B': 21, '3B': 1, 'HR': 30, 'K': 124,
        'IBB': 18
    }
    
    # Calculate comprehensive metrics
    metrics = engine.calculate_comprehensive_player_metrics(trout_stats)
    
    print("Mike Trout 2023 Sabermetrics:")
    print(f"AVG: {metrics['AVG']:.3f}")
    print(f"OBP: {metrics['OBP']:.3f}")
    print(f"SLG: {metrics['SLG']:.3f}")
    print(f"OPS: {metrics['OPS']:.3f}")
    print(f"wOBA: {metrics['wOBA']:.3f}")
    print(f"wRC+: {metrics['wRC+']:.1f}")
    print(f"BABIP: {metrics['BABIP']:.3f}")
    print(f"ISO: {metrics['ISO']:.3f}")
    print(f"BB%: {metrics['BB_Rate']:.1%}")
    print(f"K%: {metrics['K_Rate']:.1%}")
    
    return metrics

if __name__ == "__main__":
    demo_sabermetrics()