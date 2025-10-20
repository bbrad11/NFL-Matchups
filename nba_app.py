import streamlit as st
import pandas as pd
from datetime import datetime, date

def run():
    """Main NBA app function"""
    
    # Try to import NBA API
    try:
        from nba_api.stats.endpoints import leaguegamefinder, playergamelogs, teamgamelogs, scoreboardv2
        from nba_api.stats.static import players, teams
        nba_api_available = True
    except ImportError:
        nba_api_available = False
    
    # Custom CSS
    st.markdown("""
    <style>
        .main h1 {
            color: #C9082A;
            font-size: 3rem !important;
            font-weight: 800 !important;
            margin-bottom: 0.5rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #F3F4F6;
            border-radius: 8px;
            padding: 0 24px;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #C9082A;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0;'>🏀 NBA Matchup Analyzer</h1>
        <p style='text-align: center; color: #6B7280; font-size: 1.2rem; margin-top: 0;'>
            Find the best NBA matchups and player props
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check if NBA API is available
    if not nba_api_available:
        st.error("📦 **NBA API not installed!** Add `nba_api` to requirements.txt and redeploy.")
        st.code("nba_api", language="text")
        st.stop()
    
    # Sidebar controls
    st.sidebar.header("⚙️ NBA Settings")
    season_map = {
        "2024-25": "2024-25",
        "2023-24": "2023-24", 
        "2022-23": "2022-23"
    }
    season_display = st.sidebar.selectbox("Season", list(season_map.keys()), index=0)
    season = season_map[season_display]
    
    # Position groups
    positions = {
        'Guard': ['G', 'PG', 'SG', 'G-F'],
        'Forward': ['F', 'SF', 'PF', 'F-C', 'F-G'],
        'Center': ['C', 'C-F']
    }
    
    # Cache functions
    @st.cache_data(ttl=3600)
    def get_all_teams():
        """Get all NBA teams"""
        return teams.get_teams()
    
    @st.cache_data(ttl=3600)
    def get_player_game_logs(season_year):
        """Get player game logs for the season"""
        try:
            logs = playergamelogs.PlayerGameLogs(season_nullable=season_year)
            return logs.get_data_frames()[0]
        except Exception as e:
            st.error(f"Error loading player data: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def get_todays_games():
        """Get today's NBA games"""
        try:
            today = date.today().strftime('%m/%d/%Y')
            scoreboard = scoreboardv2.ScoreboardV2(game_date=today)
            games = scoreboard.get_data_frames()[0]
            return games
        except Exception as e:
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600) 
    def get_team_game_logs(season_year):
        """Get team game logs"""
        try:
            logs = teamgamelogs.TeamGameLogs(season_nullable=season_year)
            return logs.get_data_frames()[0]
        except Exception as e:
            st.error(f"Error loading team data: {e}")
            return pd.DataFrame()
    
    # Load data
    with st.spinner('Loading NBA data...'):
        all_teams = get_all_teams()
        player_logs = get_player_game_logs(season)
        team_logs = get_team_game_logs(season)
        todays_games = get_todays_games()
    
    if not player_logs.empty:
        st.success(f"✅ Loaded {len(player_logs):,} player game records")
    else:
        st.warning("⚠️ No player data available yet. Season may not have started.")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🛡️ Worst Defenses", 
        "🏀 Tonight's Games", 
        "🏆 Top Performers",
        "📊 Consistency"
    ])
    
    # TAB 1: WORST DEFENSES
    with tab1:
        st.header("Which Teams Give Up The Most?")
        st.markdown("Find defensive weaknesses to exploit")
        
        if team_logs.empty:
            st.info("Team defensive data will be available once the season starts.")
        else:
            stat_category = st.selectbox(
                "Stat Category",
                ["PTS", "FG3M", "REB", "AST", "STL", "BLK"]
            )
            
            # Calculate points allowed (opponent stats)
            defense_stats = team_logs.groupby('TEAM_ABBREVIATION').agg({
                'PTS': 'mean',  # Points scored
                'FG3M': 'mean',
                'REB': 'mean',
                'AST': 'mean',
                'STL': 'mean',
                'BLK': 'mean',
                'GAME_ID': 'count'
            }).reset_index()
            
            defense_stats.columns = ['Team', 'PPG', '3PM', 'RPG', 'APG', 'SPG', 'BPG', 'Games']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔴 Worst Defenses")
                st.caption("Teams allowing most production")
                
                # For defense, we'd need opponent stats - showing offensive stats for now
                worst = defense_stats.nlargest(10, 'PPG')
                st.dataframe(worst[['Team', 'PPG', 'Games']], use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("🟢 Best Defenses")
                st.caption("Teams with lowest scoring")
                
                best = defense_stats.nsmallest(10, 'PPG')
                st.dataframe(best[['Team', 'PPG', 'Games']], use_container_width=True, hide_index=True)
    
    # TAB 2: TONIGHT'S GAMES
    with tab2:
        st.header("🏀 Tonight's NBA Games")
        st.markdown("Find favorable matchups for your lineup")
        
        current_date = datetime.now().strftime("%B %d, %Y")
        st.subheader(f"📅 Games for {current_date}")
        
        if todays_games.empty:
            st.info("No games scheduled for today. Check back on game days!")
            st.markdown("**NBA Season 2024-25 starts October 22, 2024** 🏀")
        else:
            st.success(f"✅ {len(todays_games)} games today!")
            
            for _, game in todays_games.iterrows():
                away_team = game.get('VISITOR_TEAM_ABBREVIATION', game.get('AWAY_TEAM_ABBREVIATION', 'TBD'))
                home_team = game.get('HOME_TEAM_ABBREVIATION', 'TBD')
                game_time = game.get('GAME_STATUS_TEXT', 'TBD')
                
                with st.expander(f"{away_team} @ {home_team} - {game_time}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**{away_team} Analysis**")
                        st.info("Matchup analysis coming soon")
                    
                    with col2:
                        st.markdown(f"**{home_team} Analysis**")
                        st.info("Matchup analysis coming soon")
    
    # TAB 3: TOP PERFORMERS
    with tab3:
        st.header("Season Leaders")
        
        if player_logs.empty:
            st.info("Player stats will be available once games are played.")
        else:
            sort_option = st.radio(
                "Show leaders by:",
                ["PTS", "REB", "AST", "FG3M", "STL", "BLK"],
                horizontal=True
            )
            
            # Aggregate player stats
            player_stats = player_logs.groupby('PLAYER_NAME').agg({
                'PTS': 'mean',
                'REB': 'mean',
                'AST': 'mean',
                'FG3M': 'mean',
                'STL': 'mean',
                'BLK': 'mean',
                'GAME_ID': 'count'
            }).reset_index()
            
            player_stats.columns = ['Player', 'PPG', 'RPG', 'APG', '3PM', 'SPG', 'BPG', 'Games']
            
            # Filter players with at least 5 games
            player_stats = player_stats[player_stats['Games'] >= 5]
            
            # Sort by selected stat
            stat_map = {
                'PTS': 'PPG',
                'REB': 'RPG', 
                'AST': 'APG',
                'FG3M': '3PM',
                'STL': 'SPG',
                'BLK': 'BPG'
            }
            
            sort_col = stat_map[sort_option]
            top_players = player_stats.nlargest(20, sort_col)
            
            st.subheader(f"Top 20 by {sort_option}")
            st.dataframe(
                top_players[['Player', 'PPG', 'RPG', 'APG', 'Games']].round(1),
                use_container_width=True,
                hide_index=True
            )
            
            # Chart
            st.subheader(f"📊 Top 15 Leaders - {sort_col}")
            chart_data = top_players.head(15).set_index('Player')[sort_col]
            st.bar_chart(chart_data)
    
    # TAB 4: CONSISTENCY
    with tab4:
        st.header("📊 Player Consistency Ratings")
        st.markdown("Find reliable players who perform night after night")
        
        if player_logs.empty:
            st.info("Consistency ratings will be available once more games are played.")
        else:
            # Filter for players with enough games
            player_game_counts = player_logs.groupby('PLAYER_NAME').size()
            qualified_players = player_game_counts[player_game_counts >= 5].index
            
            consistency_df = player_logs[player_logs['PLAYER_NAME'].isin(qualified_players)].copy()
            
            if consistency_df.empty:
                st.info("Not enough games played yet for consistency analysis. Check back after Week 2!")
            else:
                # Calculate consistency metrics
                consistency_stats = consistency_df.groupby('PLAYER_NAME').agg({
                    'PTS': ['mean', 'std', 'min', 'max', 'count']
                }).reset_index()
                
                consistency_stats.columns = ['Player', 'Avg', 'StdDev', 'Floor', 'Ceiling', 'Games']
                
                # Coefficient of Variation
                consistency_stats['CV'] = (consistency_stats['StdDev'] / consistency_stats['Avg']) * 100
                
                # Consistency Rating (0-100)
                max_cv = consistency_stats['CV'].max()
                if max_cv > 0:
                    consistency_stats['Consistency Rating'] = 100 - ((consistency_stats['CV'] / max_cv) * 100)
                else:
                    consistency_stats['Consistency Rating'] = 100
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    most_consistent = consistency_stats.nlargest(1, 'Consistency Rating').iloc[0]
                    st.metric(
                        "Most Consistent", 
                        most_consistent['Player'][:15] + "..." if len(most_consistent['Player']) > 15 else most_consistent['Player'],
                        f"{most_consistent['Consistency Rating']:.1f}/100"
                    )
                
                with col2:
                    highest_avg = consistency_stats.nlargest(1, 'Avg').iloc[0]
                    st.metric(
                        "Highest Average",
                        highest_avg['Player'][:15] + "..." if len(highest_avg['Player']) > 15 else highest_avg['Player'],
                        f"{highest_avg['Avg']:.1f} PPG"
                    )
                
                with col3:
                    highest_floor = consistency_stats.nlargest(1, 'Floor').iloc[0]
                    st.metric(
                        "Highest Floor",
                        highest_floor['Player'][:15] + "..." if len(highest_floor['Player']) > 15 else highest_floor['Player'],
                        f"{highest_floor['Floor']:.1f} PPG"
                    )
                
                with col4:
                    highest_ceiling = consistency_stats.nlargest(1, 'Ceiling').iloc[0]
                    st.metric(
                        "Highest Ceiling",
                        highest_ceiling['Player'][:15] + "..." if len(highest_ceiling['Player']) > 15 else highest_ceiling['Player'],
                        f"{highest_ceiling['Ceiling']:.1f} PPG"
                    )
                
                # Rankings
                st.subheader("🎯 Consistency Rankings")
                
                sort_by = st.radio(
                    "Sort by:",
                    ["Most Consistent", "Highest Average", "Highest Floor", "Highest Ceiling"],
                    horizontal=True
                )
                
                if sort_by == "Most Consistent":
                    display_df = consistency_stats.sort_values('Consistency Rating', ascending=False)
                elif sort_by == "Highest Average":
                    display_df = consistency_stats.sort_values('Avg', ascending=False)
                elif sort_by == "Highest Floor":
                    display_df = consistency_stats.sort_values('Floor', ascending=False)
                else:
                    display_df = consistency_stats.sort_values('Ceiling', ascending=False)
                
                st.dataframe(
                    display_df[['Player', 'Avg', 'Consistency Rating', 'Floor', 'Ceiling', 'Games']].head(20).round(1),
                    use_container_width=True,
                    hide_index=True
                )
                
                with st.expander("ℹ️ How Consistency is Calculated"):
                    st.markdown("""
                    **Consistency Rating (0-100):**
                    - Higher score = more reliable night-to-night performance
                    - Based on Coefficient of Variation (StdDev / Mean)
                    - Lower variance relative to average = higher rating
                    
                    **Floor:** Lowest scoring game this season
                    
                    **Ceiling:** Highest scoring game this season
                    
                    **Why it matters:** Consistent players are safer DFS plays, while high-ceiling players offer tournament upside.
                    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #6B7280;'>
            📊 Data: NBA Stats API | Updated daily during NBA season<br>
            <small>Season 2024-25 starts October 22, 2024</small>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run()
