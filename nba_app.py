import streamlit as st
import pandas as pd
from datetime import datetime, date
from betting_analyzer import render_betting_tab, BettingAnalyzer

def run():
    """Main NBA app function"""
    
    # Try to import NBA API
    try:
        from nba_api.stats.endpoints import leaguegamefinder, playergamelogs, teamgamelogs, scoreboardv2
        from nba_api.stats.static import players, teams
        nba_api_available = True
    except ImportError:
        nba_api_available = False
    
    # Custom CSS - RotoWire Dark Theme
    st.markdown("""
    <style>
        .stApp {
            background-color: #0A0E27;
            color: #E8EAED;
        }
        
        .main h1 {
            color: #FFFFFF !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            border-bottom: 3px solid #F59E0B;
            padding-bottom: 0.5rem;
        }
        
        .main h2, .main h3 {
            color: #F59E0B !important;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D1B2A 0%, #0A0E27 100%);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #0A0E27 !important;
            color: #F59E0B !important;
            border-bottom: 3px solid #F59E0B;
        }
        
        .best-bet-card {
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
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
    
    st.sidebar.markdown("---")
    
    # Live Odds API
    with st.sidebar.expander("💰 Live Odds (Optional)"):
        st.markdown("""
        Get live odds from The Odds API
        - Sign up: [the-odds-api.com](https://the-odds-api.com/)
        - Free tier: 500 requests/month
        """)
        odds_api_key = st.text_input("API Key", type="password", key="nba_odds_key")
        
        if odds_api_key:
            st.success("✅ API key set! Check Live Odds tab")
    
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
    
    # Tabs - INCLUDING LIVE ODDS
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏆 Best Bets",
        "💰 Live Odds",
        "🛡️ Worst Defenses", 
        "🏀 Tonight's Games", 
        "🏆 Top Performers",
        "📊 Consistency",
        "🎲 Betting Tools"
    ])
    
    # TAB 1: BEST BETS DASHBOARD
    with tab1:
        st.header("🏆 Today's Best NBA Bets")
        st.markdown("Top value plays based on matchup analysis and player consistency")
        
        analyzer = BettingAnalyzer(sport="NBA")
        
        if todays_games.empty or player_logs.empty:
            st.info("Best bets will be available once the season starts and games are scheduled!")
            st.markdown("**NBA Season 2024-25 starts October 22, 2024** 🏀")
        else:
            # Analyze today's games for betting opportunities
            best_bets = []
            
            for _, game in todays_games.iterrows():
                away_team = game.get('VISITOR_TEAM_ABBREVIATION', game.get('AWAY_TEAM_ABBREVIATION', 'TBD'))
                home_team = game.get('HOME_TEAM_ABBREVIATION', 'TBD')
                
                # Find top scorers from each team
                for team, opponent in [(away_team, home_team), (home_team, away_team)]:
                    team_players = player_logs[player_logs['TEAM_ABBREVIATION'] == team]
                    
                    if not team_players.empty:
                        # Get top 3 scorers
                        top_scorers = team_players.groupby('PLAYER_NAME').agg({
                            'PTS': ['mean', 'std', 'count']
                        }).reset_index()
                        
                        top_scorers.columns = ['Player', 'PPG', 'StdDev', 'Games']
                        top_scorers = top_scorers[top_scorers['Games'] >= 5]
                        
                        if not top_scorers.empty:
                            # Calculate consistency
                            top_scorers['Consistency'] = 100 - ((top_scorers['StdDev'] / top_scorers['PPG']) * 100)
                            top_scorers = top_scorers.sort_values('PPG', ascending=False).head(3)
                            
                            for _, player in top_scorers.iterrows():
                                confidence = 'High' if player['Consistency'] > 75 else 'Medium' if player['Consistency'] > 60 else 'Low'
                                
                                if confidence in ['High', 'Medium']:
                                    best_bets.append({
                                        'player': player['Player'],
                                        'team': team,
                                        'opponent': opponent,
                                        'ppg': player['PPG'],
                                        'consistency': player['Consistency'],
                                        'confidence': confidence,
                                        'prop_suggestion': f"Over {player['PPG'] - 2:.1f} Points",
                                        'games': int(player['Games'])
                                    })
            
            # Display best bets
            if best_bets:
                best_bets_df = pd.DataFrame(best_bets)
                best_bets_df = best_bets_df.sort_values(['confidence', 'consistency'], ascending=[True, False])
                
                st.subheader(f"🔥 Top {min(10, len(best_bets))} Player Props for Today")
                
                for idx, bet in best_bets_df.head(10).iterrows():
                    confidence_emoji = "🟢" if bet['confidence'] == 'High' else "🟡"
                    
                    st.markdown(f"""
                    <div class="best-bet-card">
                        <h3>{confidence_emoji} {bet['player']} - {bet['team']}</h3>
                        <p><strong>Matchup:</strong> vs {bet['opponent']}</p>
                        <p><strong>Season Average:</strong> {bet['ppg']:.1f} PPG | <strong>Consistency:</strong> {bet['consistency']:.1f}/100</p>
                        <p><strong>Suggested Bet:</strong> {bet['prop_suggestion']}</p>
                        <p><strong>Confidence:</strong> {bet['confidence']} (Based on {bet['games']} games)</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add betting tips
                with st.expander("💡 How to Use These Bets"):
                    st.markdown("""
                    **High Confidence** 🟢
                    - Player is very consistent (low variance)
                    - Safe prop bet for points over
                    - Good for parlays
                    
                    **Medium Confidence** 🟡
                    - Player shows some variance
                    - Still a good bet but use smaller stakes
                    - Check recent form before betting
                    
                    **Tips:**
                    - Compare suggested line to actual sportsbook lines
                    - Look for 2-3 point differences for value
                    - Check injury reports before betting
                    - Consider home/away splits
                    """)
                
                # Export
                st.download_button(
                    label="📥 Download Today's Best Bets CSV",
                    data=best_bets_df.to_csv(index=False),
                    file_name=f"nba_best_bets_{date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No high-confidence bets found for today's games. Check back closer to tip-off!")
    
    # TAB 2: LIVE ODDS
    with tab2:
        st.header("💰 Live NBA Odds")
        st.markdown("Compare odds across DraftKings, FanDuel, and BetMGM")
        
        if not odds_api_key:
            st.info("👆 Enter your Odds API key in the sidebar to view live odds")
            
            st.markdown("""
            ### Why Use Live Odds?
            
            ✅ **Find Best Lines** - Compare odds across sportsbooks  
            ✅ **Spot Value** - Find +EV bets automatically  
            ✅ **Track Line Movement** - See where sharp money is going  
            ✅ **Player Props** - Get real prop lines from books  
            
            ### How to Get Started:
            
            1. Sign up at [the-odds-api.com](https://the-odds-api.com/) (FREE)
            2. Get your API key from the dashboard
            3. Enter it in the sidebar
            4. Start comparing odds!
            
            **Free Tier:** 500 requests/month
            """)
        else:
            if st.button("🔄 Fetch Live NBA Odds", key="fetch_nba_odds"):
                with st.spinner("Fetching odds from sportsbooks..."):
                    try:
                        import requests
                        
                        url = 'https://api.the-odds-api.com/v4/sports/basketball_nba/odds/'
                        params = {
                            'apiKey': odds_api_key,
                            'regions': 'us',
                            'markets': 'h2h,spreads,totals',
                            'oddsFormat': 'american',
                            'bookmakers': 'draftkings,fanduel,betmgm'
                        }
                        
                        response = requests.get(url, params=params, timeout=10)
                        response.raise_for_status()
                        
                        games = response.json()
                        
                        if games:
                            st.success(f"✅ Found odds for {len(games)} games")
                            
                            for game in games[:10]:  # Show up to 10 games
                                with st.expander(f"{game['away_team']} @ {game['home_team']}"):
                                    
                                    for bookmaker in game.get('bookmakers', []):
                                        st.markdown(f"**{bookmaker['title']}**")
                                        
                                        for market in bookmaker.get('markets', []):
                                            if market['key'] == 'h2h':
                                                st.write("Moneyline:")
                                                for outcome in market['outcomes']:
                                                    st.write(f"- {outcome['name']}: {outcome['price']:+}")
                                            
                                            elif market['key'] == 'spreads':
                                                st.write("Spread:")
                                                for outcome in market['outcomes']:
                                                    st.write(f"- {outcome['name']} {outcome['point']:+.1f}: {outcome['price']:+}")
                                            
                                            elif market['key'] == 'totals':
                                                st.write("Over/Under:")
                                                for outcome in market['outcomes']:
                                                    st.write(f"- {outcome['name']} {outcome['point']}: {outcome['price']:+}")
                                        
                                        st.markdown("---")
                        else:
                            st.info("No games with odds available right now. Check back on game days!")
                            
                    except Exception as e:
                        st.error(f"Error fetching odds: {str(e)}")
                        st.info("Make sure your API key is valid and you haven't exceeded your quota")
    
    # TAB 3: WORST DEFENSES
    with tab3:
        st.header("Which Teams Give Up The Most?")
        st.markdown("Find defensive weaknesses to exploit")
        
        if team_logs.empty:
            st.info("Team defensive data will be available once the season starts.")
        else:
            stat_category = st.selectbox(
                "Stat Category",
                ["PTS", "FG3M", "REB", "AST", "STL", "BLK"]
            )
            
            # Calculate team stats
            defense_stats = team_logs.groupby('TEAM_ABBREVIATION').agg({
                'PTS': 'mean',
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
                st.subheader("🔴 Highest Scoring Teams")
                st.caption("Teams that score the most")
                
                worst = defense_stats.nlargest(10, 'PPG')
                st.dataframe(worst[['Team', 'PPG', 'Games']], use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("🟢 Lowest Scoring Teams")
                st.caption("Teams with strongest defense")
                
                best = defense_stats.nsmallest(10, 'PPG')
                st.dataframe(best[['Team', 'PPG', 'Games']], use_container_width=True, hide_index=True)
            
            # Chart
            st.subheader("📊 League-Wide Scoring")
            chart_data = defense_stats.sort_values('PPG', ascending=False).set_index('Team')['PPG']
            st.bar_chart(chart_data)
    
    # TAB 4: TONIGHT'S GAMES
    with tab4:
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
                        st.markdown(f"**{away_team} Key Players**")
                        
                        away_players = player_logs[player_logs['TEAM_ABBREVIATION'] == away_team]
                        if not away_players.empty:
                            top_3 = away_players.groupby('PLAYER_NAME')['PTS'].mean().nlargest(3)
                            for player, ppg in top_3.items():
                                st.success(f"⭐ {player}: {ppg:.1f} PPG")
                        else:
                            st.info("Player data loading...")
                    
                    with col2:
                        st.markdown(f"**{home_team} Key Players**")
                        
                        home_players = player_logs[player_logs['TEAM_ABBREVIATION'] == home_team]
                        if not home_players.empty:
                            top_3 = home_players.groupby('PLAYER_NAME')['PTS'].mean().nlargest(3)
                            for player, ppg in top_3.items():
                                st.success(f"⭐ {player}: {ppg:.1f} PPG")
                        else:
                            st.info("Player data loading...")
    
    # TAB 5: TOP PERFORMERS
    with tab5:
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
    
    # TAB 6: CONSISTENCY
    with tab6:
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
    
    # TAB 7: BETTING TOOLS
    with tab7:
        render_betting_tab(sport="NBA", stats_df=player_logs, schedule_df=todays_games)
    
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
