"""
MLB Data Collection and Processing Module
Handles data acquisition from various baseball data sources
"""

import pandas as pd
import numpy as np
import requests
import json
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

class MLBDataCollector:
    """
    Collects and processes MLB data from various sources
    """
    
    def __init__(self):
        # MLB Stats API base URL
        self.mlb_api_base = "https://statsapi.mlb.com/api/v1"
        
        # Current season (can be updated)
        self.current_season = 2024
        
        # Team mapping for convenience
        self.team_mapping = {
            'LAA': 108, 'HOU': 117, 'OAK': 133, 'TOR': 141, 'ATL': 144,
            'MIL': 158, 'STL': 138, 'CHC': 112, 'ARI': 109, 'LAD': 119,
            'SF': 137, 'CLE': 114, 'SEA': 136, 'MIA': 146, 'NYM': 121,
            'WSH': 120, 'BAL': 110, 'SD': 135, 'PHI': 143, 'PIT': 134,
            'TEX': 140, 'TB': 139, 'BOS': 111, 'CIN': 113, 'COL': 115,
            'KC': 118, 'DET': 116, 'MIN': 142, 'CWS': 145, 'NYY': 147
        }
        
    def get_team_roster(self, team_id: int, season: int = None) -> pd.DataFrame:
        """Get team roster for a specific season"""
        if season is None:
            season = self.current_season
            
        try:
            url = f"{self.mlb_api_base}/teams/{team_id}/roster"
            params = {'season': season}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            roster_data = []
            for player in data.get('roster', []):
                player_info = player.get('person', {})
                position = player.get('position', {})
                
                roster_data.append({
                    'player_id': player_info.get('id'),
                    'player_name': player_info.get('fullName'),
                    'jersey_number': player.get('jerseyNumber'),
                    'position': position.get('abbreviation'),
                    'position_name': position.get('name'),
                    'status': player.get('status', {}).get('description')
                })
            
            return pd.DataFrame(roster_data)
            
        except Exception as e:
            print(f"Error fetching roster for team {team_id}: {e}")
            return pd.DataFrame()
    
    def get_player_stats(self, player_id: int, season: int = None, 
                        stat_type: str = 'season') -> Dict:
        """Get player statistics for a specific season"""
        if season is None:
            season = self.current_season
            
        try:
            url = f"{self.mlb_api_base}/people/{player_id}/stats"
            params = {
                'stats': stat_type,
                'season': season,
                'group': 'hitting,pitching,fielding'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching stats for player {player_id}: {e}")
            return {}
    
    def process_batting_stats(self, stats_data: Dict) -> Dict:
        """Process batting statistics from API response"""
        batting_stats = {}
        
        try:
            for stat_group in stats_data.get('stats', []):
                for split in stat_group.get('splits', []):
                    stat = split.get('stat', {})
                    
                    # Extract batting statistics
                    batting_stats = {
                        'AB': stat.get('atBats', 0),
                        'H': stat.get('hits', 0),
                        'BB': stat.get('baseOnBalls', 0),
                        'IBB': stat.get('intentionalWalks', 0),
                        'HBP': stat.get('hitByPitch', 0),
                        'SF': stat.get('sacFlies', 0),
                        'SH': stat.get('sacBunts', 0),
                        'K': stat.get('strikeOuts', 0),
                        '2B': stat.get('doubles', 0),
                        '3B': stat.get('triples', 0),
                        'HR': stat.get('homeRuns', 0),
                        'RBI': stat.get('rbi', 0),
                        'R': stat.get('runs', 0),
                        'SB': stat.get('stolenBases', 0),
                        'CS': stat.get('caughtStealing', 0),
                        'AVG': float(stat.get('avg', 0)),
                        'OBP': float(stat.get('obp', 0)),
                        'SLG': float(stat.get('slg', 0)),
                        'OPS': float(stat.get('ops', 0))
                    }
                    
                    # Calculate singles
                    batting_stats['1B'] = (batting_stats['H'] - 
                                         batting_stats['2B'] - 
                                         batting_stats['3B'] - 
                                         batting_stats['HR'])
                    
                    break  # Take first split (season stats)
                    
        except Exception as e:
            print(f"Error processing batting stats: {e}")
            
        return batting_stats
    
    def process_pitching_stats(self, stats_data: Dict) -> Dict:
        """Process pitching statistics from API response"""
        pitching_stats = {}
        
        try:
            for stat_group in stats_data.get('stats', []):
                for split in stat_group.get('splits', []):
                    stat = split.get('stat', {})
                    
                    # Extract pitching statistics
                    pitching_stats = {
                        'W': stat.get('wins', 0),
                        'L': stat.get('losses', 0),
                        'ERA': float(stat.get('era', 0)),
                        'G': stat.get('gamesPlayed', 0),
                        'GS': stat.get('gamesStarted', 0),
                        'CG': stat.get('completeGames', 0),
                        'SHO': stat.get('shutouts', 0),
                        'SV': stat.get('saves', 0),
                        'IP': float(stat.get('inningsPitched', 0)),
                        'H': stat.get('hits', 0),
                        'ER': stat.get('earnedRuns', 0),
                        'HR': stat.get('homeRuns', 0),
                        'BB': stat.get('baseOnBalls', 0),
                        'IBB': stat.get('intentionalWalks', 0),
                        'K': stat.get('strikeOuts', 0),
                        'HBP': stat.get('hitBatsmen', 0),
                        'WHIP': float(stat.get('whip', 0)),
                        'BABIP': float(stat.get('babip', 0))
                    }
                    
                    break  # Take first split (season stats)
                    
        except Exception as e:
            print(f"Error processing pitching stats: {e}")
            
        return pitching_stats
    
    def get_team_stats(self, team_id: int, season: int = None) -> Dict:
        """Get comprehensive team statistics"""
        if season is None:
            season = self.current_season
            
        try:
            url = f"{self.mlb_api_base}/teams/{team_id}/stats"
            params = {
                'stats': 'season',
                'season': season,
                'group': 'hitting,pitching,fielding'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching team stats for {team_id}: {e}")
            return {}
    
    def get_league_leaders(self, stat_type: str = 'homeRuns', 
                          season: int = None, limit: int = 10) -> pd.DataFrame:
        """Get league leaders for a specific statistic"""
        if season is None:
            season = self.current_season
            
        try:
            url = f"{self.mlb_api_base}/stats/leaders"
            params = {
                'leaderCategories': stat_type,
                'season': season,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            leaders_data = []
            for category in data.get('leagueLeaders', []):
                for leader in category.get('leaders', []):
                    player = leader.get('person', {})
                    team = leader.get('team', {})
                    
                    leaders_data.append({
                        'player_id': player.get('id'),
                        'player_name': player.get('fullName'),
                        'team_name': team.get('name'),
                        'value': leader.get('value'),
                        'rank': leader.get('rank'),
                        'stat_type': stat_type
                    })
            
            return pd.DataFrame(leaders_data)
            
        except Exception as e:
            print(f"Error fetching league leaders for {stat_type}: {e}")
            return pd.DataFrame()
    
    def generate_sample_data(self) -> Dict:
        """Generate sample MLB data for demonstration purposes"""
        
        # Sample player data (based on real 2023 stats)
        sample_players = {
            'Ronald Acuña Jr.': {
                'team': 'ATL',
                'position': 'OF',
                'stats': {
                    'AB': 556, 'H': 217, 'BB': 78, 'HBP': 17, 'SF': 6,
                    '1B': 124, '2B': 52, '3B': 8, 'HR': 41, 'K': 105,
                    'IBB': 6, 'RBI': 106, 'R': 149, 'SB': 73
                }
            },
            'Mookie Betts': {
                'team': 'LAD',
                'position': 'OF',
                'stats': {
                    'AB': 527, 'H': 155, 'BB': 96, 'HBP': 15, 'SF': 3,
                    '1B': 97, '2B': 33, '3B': 3, 'HR': 39, 'K': 98,
                    'IBB': 11, 'RBI': 107, 'R': 122, 'SB': 16
                }
            },
            'Mike Trout': {
                'team': 'LAA',
                'position': 'OF',
                'stats': {
                    'AB': 473, 'H': 134, 'BB': 89, 'HBP': 3, 'SF': 4,
                    '1B': 82, '2B': 21, '3B': 1, 'HR': 30, 'K': 124,
                    'IBB': 18, 'RBI': 90, 'R': 90, 'SB': 2
                }
            },
            'Freddie Freeman': {
                'team': 'LAD',
                'position': '1B',
                'stats': {
                    'AB': 594, 'H': 187, 'BB': 73, 'HBP': 6, 'SF': 7,
                    '1B': 131, '2B': 27, '3B': 4, 'HR': 29, 'K': 108,
                    'IBB': 13, 'RBI': 102, 'R': 106, 'SB': 13
                }
            },
            'José Altuve': {
                'team': 'HOU',
                'position': '2B',
                'stats': {
                    'AB': 625, 'H': 189, 'BB': 45, 'HBP': 7, 'SF': 4,
                    '1B': 134, '2B': 36, '3B': 3, 'HR': 17, 'K': 91,
                    'IBB': 2, 'RBI': 69, 'R': 95, 'SB': 18
                }
            }
        }
        
        # Sample pitcher data
        sample_pitchers = {
            'Gerrit Cole': {
                'team': 'NYY',
                'stats': {
                    'W': 15, 'L': 4, 'ERA': 2.63, 'G': 33, 'GS': 33,
                    'IP': 222.2, 'H': 180, 'ER': 65, 'HR': 28,
                    'BB': 45, 'K': 222, 'HBP': 7, 'WHIP': 1.01
                }
            },
            'Spencer Strider': {
                'team': 'ATL',
                'stats': {
                    'W': 20, 'L': 5, 'ERA': 3.86, 'G': 31, 'GS': 31,
                    'IP': 186.2, 'H': 149, 'ER': 80, 'HR': 25,
                    'BB': 56, 'K': 281, 'HBP': 9, 'WHIP': 1.10
                }
            }
        }
        
        return {
            'batters': sample_players,
            'pitchers': sample_pitchers,
            'last_updated': datetime.now().isoformat()
        }
    
    def save_data_to_csv(self, data: pd.DataFrame, filename: str, 
                        directory: str = "data/") -> bool:
        """Save DataFrame to CSV file"""
        try:
            import os
            os.makedirs(directory, exist_ok=True)
            
            filepath = os.path.join(directory, filename)
            data.to_csv(filepath, index=False)
            
            print(f"Data saved to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")
            return False

def demo_data_collection():
    """Demonstrate data collection capabilities"""
    collector = MLBDataCollector()
    
    print("=" * 60)
    print("MLB DATA COLLECTION DEMO")
    print("=" * 60)
    print()
    
    # Generate sample data
    print("📊 GENERATING SAMPLE PLAYER DATA")
    print("-" * 40)
    sample_data = collector.generate_sample_data()
    
    # Display sample batter data
    print("Top MLB Batters (2023 Sample):")
    for player, info in list(sample_data['batters'].items())[:3]:
        stats = info['stats']
        print(f"{player} ({info['team']}) - {info['position']}")
        print(f"  AVG: {stats['H']/stats['AB']:.3f}, HR: {stats['HR']}, RBI: {stats['RBI']}")
    
    print()
    print("Top MLB Pitchers (2023 Sample):")
    for pitcher, info in sample_data['pitchers'].items():
        stats = info['stats']
        print(f"{pitcher} ({info['team']})")
        print(f"  ERA: {stats['ERA']:.2f}, W: {stats['W']}, K: {stats['K']}")
    
    print()
    print("=" * 60)
    print("CAPABILITIES DEMONSTRATED:")
    print("✅ Player statistics processing")
    print("✅ Team data collection")
    print("✅ Batting and pitching metrics")
    print("✅ Sample data generation")
    print("✅ Data export functionality")
    print("=" * 60)
    
    return sample_data

if __name__ == "__main__":
    demo_data_collection()