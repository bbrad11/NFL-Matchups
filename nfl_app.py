import streamlit as st
import nflreadpy as nfl
import pandas as pd
from betting_analyzer import render_betting_tab, BettingAnalyzer

def run():
    """Main NFL app function"""
    
    # Custom CSS for modern look
    st.markdown("""
    <style>
        .main h1 {
            color: #1E3A8A;
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
            background-color: #1E3A8A;
            color: white;
        }
        
        .best-bet-card {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        
        .best-bet-card h3 {
            color: white;
            margin: 0 0 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0;'>🏈 NFL Matchup Analyzer</h1>
        <p style='text-align: center; color: #6B7280; font-size: 1.2rem; margin-top: 0;'>
            Data-driven insights for smarter lineup decisions
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar controls
    st.sidebar.header("⚙️ NFL Settings")
    season = st.sidebar.selectbox("Season", [2025, 2024, 2023], index=0)
    current_week = st.sidebar.slider("Week", 1, 18, 7)
    
    # Cache data loading
    @st.cache_data
    def load_nfl_data(season):
        player_stats = nfl.load_player_stats([season])
        schedules = nfl.load_schedules([season])
        return player_stats.to_pandas(), schedules.to_pandas()
    
    @st.cache_data
    def load_nextgen_data(season, stat_type):
        try:
            nextgen = nfl.load_nextgen_stats(stat_type=stat_type, seasons=[season])
            return nextgen.to_pandas()
        except Exception as e:
            return pd.DataFrame()
    
    # Load data
    with st.spinner('Loading NFL data...'):
        stats_df, schedule_df = load_nfl_data(season)
    
    st.success(f"✅ Loaded {len(stats_df):,} player games")
    
    # Debug info in sidebar
    with st.sidebar.expander("🔍 Debug Info"):
        st.write(f"**Data Shape:** {stats_df.shape}")
        if 'week' in stats_df.columns:
            st.write(f"**Available Weeks:** {sorted(stats_df['week'].unique())}")
            st.write(f"**Records in Week {current_week}:** {len(stats_df[stats_df['week'] == current_week])}")
    
    # Position groups
    positions = {
        'QB': ['QB'],
        'RB': ['RB', 'FB'],
        'WR': ['WR'],
        'TE': ['TE']
    }
    
    # Analyze defense performance
    def get_defense_stats(stats_df, position_codes):
        pos_stats = stats_df[stats_df['position'].isin(position_codes)].copy()
        
        agg_dict = {}
        for col in ['passing_tds', 'rushing_tds', 'receiving_tds', 'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']:
            if col in pos_stats.columns:
                agg_dict[col] = 'sum'
        
        if not agg_dict:
            return pd.DataFrame()
        
        defense_stats = pos_stats.groupby('opponent_team').agg(agg_dict).reset_index()
        defense_stats.columns = ['Defense'] + [col.replace('_', ' ').title() for col in defense_stats.columns[1:]]
        
        return defense_stats
    
    # Tabs - NOW INCLUDING BETTING AND BEST BETS
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏆 Best Bets",
        "🛡️ Worst Defenses", 
        "🔥 This Week's Matchups", 
        "🏆 Top Scorers",
        "📊 Consistency",
        "⚡ NextGen Stats",
        "💰 Betting Tools"
    ])
    
    # TAB 1: BEST BETS DASHBOARD
    with tab1:
        st.header("🏆 Today's Best Bets")
        st.markdown("Top value plays based on matchup analysis and consistency ratings")
        
        analyzer = BettingAnalyzer(sport="NFL")
        
        # Get this week's games
        games = schedule_df[
            (schedule_df['week'] == current_week) & 
            (schedule_df['game_type'] == 'REG')
        ].copy()
        
        if games.empty:
            st.info(f"No games found for Week {current_week}")
        else:
            # Get defense rankings
            weak_defenses = {}
            for pos_name, pos_codes in positions.items():
                defense_stats = get_defense_stats(stats_df, pos_codes)
                if not defense_stats.empty:
                    td_cols = [col for col in defense_stats.columns if 'Td' in col]
                    if td_cols:
                        defense_stats = defense_stats.sort_values(td_cols[0], ascending=False)
                        weak_defenses[pos_name] = defense_stats.head(10)['Defense'].tolist()
            
            # Find best bet opportunities
            best_bets = []
            
            for _, game in games.iterrows():
                away = game['away_team']
                home = game['home_team']
                
                # Check for favorable matchups
                for pos, weak_teams in weak_defenses.items():
                    # Away team players vs weak home defense
                    if home in weak_teams:
                        rank = weak_teams.index(home) + 1
                        
                        # Get top player from away team at this position
                        # Find the team column (could be 'recent_team', 'team', or 'team_abbr')
                        team_col = None
                        for col in ['recent_team', 'team', 'team_abbr']:
                            if col in stats_df.columns:
                                team_col = col
                                break
                        
                        if team_col is None:
                            continue
                        
                        away_players = stats_df[
                            (stats_df[team_col] == away) & 
                            (stats_df['position'].isin(positions[pos]))
                        ]
                        
                        if not away_players.empty:
                            # Get player with most consistent recent performance
                            if 'fantasy_points_ppr' in away_players.columns:
                                top_player = away_players.groupby('player_display_name').agg({
                                    'fantasy_points_ppr': 'mean'
                                }).nlargest(1, 'fantasy_points_ppr')
                                
                                if not top_player.empty:
                                    player_name = top_player.index[0]
                                    avg_points = top_player['fantasy_points_ppr'].values[0]
                                    
                                    best_bets.append({
                                        'player': player_name,
                                        'team': away,
                                        'position': pos,
                                        'opponent': home,
                                        'def_rank': rank,
                                        'avg_points': avg_points,
                                        'matchup_type': 'Favorable',
                                        'confidence': 'High' if rank <= 5 else 'Medium'
                                    })
                    
                    # Home team players vs weak away defense
                    if away in weak_teams:
                        rank = weak_teams.index(away) + 1
                        
                        # Find the team column
                        team_col = None
                        for col in ['recent_team', 'team', 'team_abbr']:
                            if col in stats_df.columns:
                                team_col = col
                                break
                        
                        if team_col is None:
                            continue
                        
                        home_players = stats_df[
                            (stats_df[team_col] == home) & 
                            (stats_df['position'].isin(positions[pos]))
                        ]
                        
                        if not home_players.empty:
                            if 'fantasy_points_ppr' in home_players.columns:
                                top_player = home_players.groupby('player_display_name').agg({
                                    'fantasy_points_ppr': 'mean'
                                }).nlargest(1, 'fantasy_points_ppr')
                                
                                if not top_player.empty:
                                    player_name = top_player.index[0]
                                    avg_points = top_player['fantasy_points_ppr'].values[0]
                                    
                                    best_bets.append({
                                        'player': player_name,
                                        'team': home,
                                        'position': pos,
                                        'opponent': away,
                                        'def_rank': rank,
                                        'avg_points': avg_points,
                                        'matchup_type': 'Favorable',
                                        'confidence': 'High' if rank <= 5 else 'Medium'
                                    })
            
            # Display best bets
            if best_bets:
                st.subheader(f"🔥 Top {min(10, len(best_bets))} Plays for Week {current_week}")
                
                # Sort by defense rank and avg points
                best_bets_df = pd.DataFrame(best_bets)
                best_bets_df = best_bets_df.sort_values(['def_rank', 'avg_points'], ascending=[True, False])
                
                for idx, bet in best_bets_df.head(10).iterrows():
                    confidence_color = "🟢" if bet['confidence'] == 'High' else "🟡"
                    
                    st.markdown(f"""
                    <div class="best-bet-card">
                        <h3>{confidence_color} {bet['player']} ({bet['position']}) - {bet['team']}</h3>
                        <p><strong>Matchup:</strong> vs {bet['opponent']} (#{bet['def_rank']} worst {bet['position']} defense)</p>
                        <p><strong>Avg Fantasy Points:</strong> {bet['avg_points']:.1f} | <strong>Confidence:</strong> {bet['confidence']}</p>
                        <p><strong>Bet Type:</strong> Player Props (Over Points/Yards/TDs)</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export bets
                st.download_button(
                    label="📥 Download Best Bets CSV",
                    data=best_bets_df.to_csv(index=False),
                    file_name=f"nfl_best_bets_week_{current_week}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No strong bet opportunities found this week. Check back closer to game time!")
    
    # TAB 2: WORST DEFENSES
    with tab2:
        st.header("Which Defenses Give Up The Most?")
        st.markdown("Higher numbers = easier matchup for offensive players")
        
        time_filter = st.radio(
            "Show stats for:",
            ["Season Total", f"Week {current_week} Only", "Last 3 Weeks"],
            horizontal=True,
            key="def_time_filter"
        )
        
        position = st.selectbox("Position", ["QB", "RB", "WR", "TE"])
        
        # Filter data
        if time_filter == f"Week {current_week} Only":
            if 'week' in stats_df.columns:
                filtered_df = stats_df[stats_df['week'] == current_week]
                st.info(f"Showing {len(filtered_df)} records from Week {current_week}")
            else:
                filtered_df = stats_df
        elif time_filter == "Last 3 Weeks":
            if 'week' in stats_df.columns:
                filtered_df = stats_df[stats_df['week'] >= current_week - 2]
                st.info(f"Showing {len(filtered_df)} records from Weeks {current_week-2} to {current_week}")
            else:
                filtered_df = stats_df
        else:
            filtered_df = stats_df
            st.info(f"Showing all {len(filtered_df)} records from season")
        
        defense_stats = get_defense_stats(filtered_df, positions[position])
        
        if defense_stats.empty:
            st.warning(f"No {position} data available")
        else:
            td_cols = [col for col in defense_stats.columns if 'Td' in col]
            sort_col = td_cols[0] if td_cols else defense_stats.columns[1]
            defense_stats = defense_stats.sort_values(sort_col, ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"🔴 Worst {position} Defenses")
                st.caption("These defenses allow the most production")
                st.dataframe(
                    defense_stats.head(10).reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                st.subheader(f"🟢 Best {position} Defenses")
                st.caption("These defenses shut down opponents")
                st.dataframe(
                    defense_stats.tail(10).iloc[::-1].reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True
                )
            
            st.subheader(f"Top 15 Defenses Allowing {sort_col}")
            chart_data = defense_stats.head(15).set_index('Defense')[sort_col]
            st.bar_chart(chart_data)
    
    # TAB 3: THIS WEEK'S MATCHUPS
    with tab3:
        st.header(f"Week {current_week} Games")
        st.markdown("Find favorable matchups where strong offenses meet weak defenses")
        
        games = schedule_df[
            (schedule_df['week'] == current_week) & 
            (schedule_df['game_type'] == 'REG')
        ].copy()
        
        if games.empty:
            st.warning(f"No games found for Week {current_week}")
        else:
            st.subheader(f"📅 {len(games)} Games This Week")
            
            weak_defenses = {}
            for pos_name, pos_codes in positions.items():
                defense_stats = get_defense_stats(stats_df, pos_codes)
                if not defense_stats.empty:
                    td_cols = [col for col in defense_stats.columns if 'Td' in col]
                    if td_cols:
                        defense_stats = defense_stats.sort_values(td_cols[0], ascending=False)
                        weak_defenses[pos_name] = defense_stats.head(10)['Defense'].tolist()
            
            for _, game in games.iterrows():
                away = game['away_team']
                home = game['home_team']
                
                with st.expander(f"{away} @ {home} - {game['gameday']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**{away} Offense**")
                        for pos, weak_teams in weak_defenses.items():
                            if home in weak_teams:
                                rank = weak_teams.index(home) + 1
                                st.success(f"✅ {pos}: Good matchup (vs #{rank} worst defense)")
                    
                    with col2:
                        st.markdown(f"**{home} Offense**")
                        for pos, weak_teams in weak_defenses.items():
                            if away in weak_teams:
                                rank = weak_teams.index(away) + 1
                                st.success(f"✅ {pos}: Good matchup (vs #{rank} worst defense)")
    
    # TAB 4: TOP SCORERS (keeping your original code - truncated for space)
    with tab4:
        st.header("Season Leaders")
        # ... (keep your existing top scorers code)
        st.info("Top scorers code here (same as before)")
    
    # TAB 5: CONSISTENCY (keeping your original code - truncated for space)
    with tab5:
        st.header("📊 Player Consistency Ratings")
        # ... (keep your existing consistency code)
        st.info("Consistency code here (same as before)")
    
    # TAB 6: NEXTGEN STATS (keeping your original code - truncated for space)
    with tab6:
        st.header("⚡ NextGen Stats")
        # ... (keep your existing NextGen code)
        st.info("NextGen stats code here (same as before)")
    
    # TAB 7: BETTING TOOLS
    with tab7:
        render_betting_tab(sport="NFL", stats_df=stats_df, schedule_df=schedule_df)
    
    # Footer
    st.markdown("---")
    st.markdown("📊 Data: [nflverse](https://github.com/nflverse/nflreadpy) | Updated weekly during NFL season")

if __name__ == "__main__":
    run()
