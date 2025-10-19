# NFL Matchup Analysis: Strength vs Weakness by Position
# Tracks defensive positional weaknesses and player matchups

import nflreadpy as nfl

# Load current season data
print("Loading 2024 NFL data...")
player_stats = nfl.load_player_stats([2024])
schedules = nfl.load_schedules([2024])

# Convert to pandas for easier analysis
stats_df = player_stats.to_pandas()
schedule_df = schedules.to_pandas()

print(f"Loaded {len(stats_df)} player-game records")
print(f"Loaded {len(schedule_df)} games\n")

# ============================================================
# PART 1: DEFENSE POSITIONAL WEAKNESSES (LEAGUE-WIDE)
# ============================================================

print("="*70)
print("DEFENSIVE POSITIONAL WEAKNESSES - 2024 SEASON")
print("="*70)

# Define position categories
positions = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE']
}

def analyze_defense_vs_position(stats_df, position_codes, stat_columns):
    """Analyze how each defense performs against a specific position"""
    
    # Filter for position
    pos_stats = stats_df[stats_df['position'].isin(position_codes)].copy()
    
    # Group by opponent (defense they played against)
    defense_stats = pos_stats.groupby('opponent_team').agg(stat_columns).reset_index()
    defense_stats.columns = ['Defense'] + [col[0] + '_' + col[1] for col in defense_stats.columns[1:]]
    
    # Sort by key metrics (descending = worse defense)
    return defense_stats

# Analyze each position
print("\n--- QB Stats Allowed (Worst Defenses vs QB) ---")
qb_defense = analyze_defense_vs_position(
    stats_df, 
    positions['QB'],
    {
        'passing_yards': ['sum', 'mean'],
        'passing_tds': ['sum', 'mean'],
        'interceptions': ['sum'],
        'fantasy_points_ppr': ['sum', 'mean']
    }
)
qb_defense = qb_defense.sort_values('passing_tds_sum', ascending=False)
print(qb_defense.head(10).to_string(index=False))

print("\n--- RB Stats Allowed (Worst Defenses vs RB) ---")
rb_defense = analyze_defense_vs_position(
    stats_df,
    positions['RB'],
    {
        'rushing_yards': ['sum', 'mean'],
        'rushing_tds': ['sum', 'mean'],
        'receptions': ['sum', 'mean'],
        'receiving_yards': ['sum', 'mean'],
        'receiving_tds': ['sum'],
        'fantasy_points_ppr': ['sum', 'mean']
    }
)
rb_defense = rb_defense.sort_values('fantasy_points_ppr_sum', ascending=False)
print(rb_defense.head(10).to_string(index=False))

print("\n--- WR Stats Allowed (Worst Defenses vs WR) ---")
wr_defense = analyze_defense_vs_position(
    stats_df,
    positions['WR'],
    {
        'receptions': ['sum', 'mean'],
        'receiving_yards': ['sum', 'mean'],
        'receiving_tds': ['sum', 'mean'],
        'fantasy_points_ppr': ['sum', 'mean']
    }
)
wr_defense = wr_defense.sort_values('receiving_tds_sum', ascending=False)
print(wr_defense.head(10).to_string(index=False))

print("\n--- TE Stats Allowed (Worst Defenses vs TE) ---")
te_defense = analyze_defense_vs_position(
    stats_df,
    positions['TE'],
    {
        'receptions': ['sum', 'mean'],
        'receiving_yards': ['sum', 'mean'],
        'receiving_tds': ['sum', 'mean'],
        'fantasy_points_ppr': ['sum', 'mean']
    }
)
te_defense = te_defense.sort_values('receiving_tds_sum', ascending=False)
print(te_defense.head(10).to_string(index=False))

# ============================================================
# PART 2: STRENGTH VS WEAKNESS MATCHUPS (BY GAME)
# ============================================================

print("\n\n" + "="*70)
print("UPCOMING MATCHUP ANALYSIS - Player Strength vs Defense Weakness")
print("="*70)

# Get upcoming games (week filter - adjust as needed)
current_week = 7  # Change this to current NFL week
upcoming_games = schedule_df[
    (schedule_df['week'] == current_week) & 
    (schedule_df['game_type'] == 'REG')
].copy()

print(f"\nAnalyzing Week {current_week} Matchups...\n")

# Get top performers by position (last 3 games)
recent_stats = stats_df[stats_df['week'] >= current_week - 3].copy()

def get_top_players_by_position(df, position_list, metric, top_n=5):
    """Get top performing players at a position"""
    pos_df = df[df['position'].isin(position_list)].copy()
    top_players = pos_df.groupby('player_display_name').agg({
        metric: 'mean',
        'recent_team': 'last',
        'position': 'first'
    }).reset_index()
    top_players = top_players.sort_values(metric, ascending=False).head(top_n)
    return top_players

def find_favorable_matchups(top_players, weak_defenses, position_name):
    """Match top players against weak defenses"""
    print(f"\n--- {position_name} Favorable Matchups ---")
    
    weak_def_teams = weak_defenses.head(10)['Defense'].tolist()
    
    for _, game in upcoming_games.iterrows():
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Check if any top player's team is playing against a weak defense
        for _, player in top_players.iterrows():
            player_team = player['recent_team']
            
            if player_team == home_team and away_team in weak_def_teams:
                print(f"🔥 {player['player_display_name']} ({player_team}) vs {away_team}")
                print(f"   Defense Rank: {weak_def_teams.index(away_team) + 1} (worst against {position_name})")
                
            elif player_team == away_team and home_team in weak_def_teams:
                print(f"🔥 {player['player_display_name']} ({player_team}) @ {home_team}")
                print(f"   Defense Rank: {weak_def_teams.index(home_team) + 1} (worst against {position_name})")

# Find favorable matchups for each position
print("\n" + "="*70)

top_qbs = get_top_players_by_position(recent_stats, positions['QB'], 'passing_tds', 10)
find_favorable_matchups(top_qbs, qb_defense, "QB")

top_rbs = get_top_players_by_position(recent_stats, positions['RB'], 'fantasy_points_ppr', 15)
find_favorable_matchups(top_rbs, rb_defense, "RB")

top_wrs = get_top_players_by_position(recent_stats, positions['WR'], 'receiving_tds', 20)
find_favorable_matchups(top_wrs, wr_defense, "WR")

top_tes = get_top_players_by_position(recent_stats, positions['TE'], 'receiving_tds', 10)
find_favorable_matchups(top_tes, te_defense, "TE")

# ============================================================
# PART 3: TOUCHDOWN SCORERS - SEASON LEADERS
# ============================================================

print("\n\n" + "="*70)
print("2024 TOUCHDOWN LEADERS BY POSITION")
print("="*70)

def get_td_leaders(df, position_list, position_name):
    pos_df = df[df['position'].isin(position_list)].copy()
    
    # Calculate total TDs
    if position_name == "QB":
        pos_df['total_tds'] = pos_df['passing_tds'].fillna(0) + pos_df['rushing_tds'].fillna(0)
        sort_col = 'passing_tds'
    else:
        pos_df['total_tds'] = pos_df['rushing_tds'].fillna(0) + pos_df['receiving_tds'].fillna(0)
        sort_col = 'total_tds'
    
    leaders = pos_df.groupby('player_display_name').agg({
        'rushing_tds': 'sum',
        'receiving_tds': 'sum',
        'passing_tds': 'sum',
        'total_tds': 'sum',
        'recent_team': 'last',
        'position': 'first'
    }).reset_index()
    
    leaders = leaders.sort_values(sort_col, ascending=False).head(10)
    return leaders

print("\n--- QB Touchdown Leaders ---")
qb_tds = get_td_leaders(stats_df, positions['QB'], "QB")
print(qb_tds[['player_display_name', 'recent_team', 'passing_tds', 'rushing_tds']].to_string(index=False))

print("\n--- RB Touchdown Leaders ---")
rb_tds = get_td_leaders(stats_df, positions['RB'], "RB")
print(rb_tds[['player_display_name', 'recent_team', 'rushing_tds', 'receiving_tds', 'total_tds']].to_string(index=False))

print("\n--- WR Touchdown Leaders ---")
wr_tds = get_td_leaders(stats_df, positions['WR'], "WR")
print(wr_tds[['player_display_name', 'recent_team', 'receiving_tds', 'rushing_tds', 'total_tds']].to_string(index=False))

print("\n--- TE Touchdown Leaders ---")
te_tds = get_td_leaders(stats_df, positions['TE'], "TE")
print(te_tds[['player_display_name', 'recent_team', 'receiving_tds', 'total_tds']].to_string(index=False))

print("\n" + "="*70)
print("Analysis Complete!")
print("="*70)
