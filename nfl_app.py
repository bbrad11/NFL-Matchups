import streamlit as st
import nflreadpy as nfl
import pandas as pd
import polars as pl
from datetime import datetime

def run():
    """Main NFL app function"""

    # Custom CSS
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
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0;'>🏈 NFL Matchup Analyzer</h1>
        <p style='text-align: center; color: #6B7280; font-size: 1.2rem; margin-top: 0;'>
            Find the best fantasy football matchups and betting opportunities
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
        schedule = nfl.load_schedules([season])
        
        # Convert Polars DataFrames to Pandas if needed
        if hasattr(player_stats, 'to_pandas'):
            player_stats = player_stats.to_pandas()
        if hasattr(schedule, 'to_pandas'):
            schedule = schedule.to_pandas()
            
        return player_stats, schedule

    # Load data
    with st.spinner('Loading NFL data...'):
        stats_df, schedule_df = load_nfl_data(season)

    st.success(f"✅ Loaded {len(stats_df):,} player games")
    
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
    
    def get_leaders(df, pos_codes, sort_option):
        pos_df = df[df['position'].isin(pos_codes)].copy()
        if pos_df.empty:
            return pd.DataFrame()
        
        agg_dict = {}
        for team_col in ['recent_team', 'team', 'team_abbr']:
            if team_col in pos_df.columns:
                agg_dict[team_col] = 'last'
                break
        
        for col in ['passing_tds', 'rushing_tds', 'receiving_tds', 'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']:
            if col in pos_df.columns:
                pos_df[col] = pos_df[col].fillna(0)
                agg_dict[col] = 'sum'
        
        if not agg_dict:
            return pd.DataFrame()
        
        leaders = pos_df.groupby('player_display_name').agg(agg_dict).reset_index()
        
        # Calculate totals
        td_cols = [c for c in ['passing_tds', 'rushing_tds', 'receiving_tds'] if c in leaders.columns]
        yds_cols = [c for c in ['passing_yards', 'rushing_yards', 'receiving_yards'] if c in leaders.columns]
        
        if td_cols:
            leaders['Total TDs'] = leaders[td_cols].sum(axis=1)
        if yds_cols:
            leaders['Total Yards'] = leaders[yds_cols].sum(axis=1)
        
        # Rename columns
        rename_map = {
            'recent_team': 'Team', 'team': 'Team', 'team_abbr': 'Team',
            'passing_tds': 'Pass TDs', 'rushing_tds': 'Rush TDs', 'receiving_tds': 'Rec TDs',
            'passing_yards': 'Pass Yds', 'rushing_yards': 'Rush Yds', 'receiving_yards': 'Rec Yds',
            'fantasy_points_ppr': 'Fantasy Pts'
        }
        leaders = leaders.rename(columns=rename_map)
        leaders = leaders.rename(columns={'player_display_name': 'Player'})
        
        # Sort by selected option
        if sort_option == "Touchdowns":
            sort_col = 'Total TDs' if 'Total TDs' in leaders.columns else leaders.columns[1]
        elif sort_option == "Yards":
            sort_col = 'Total Yards' if 'Total Yards' in leaders.columns else leaders.columns[1]
        else:
            sort_col = 'Fantasy Pts' if 'Fantasy Pts' in leaders.columns else leaders.columns[1]
        
        return leaders.sort_values(sort_col, ascending=False).head(15)

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛡️ Worst Defenses", 
        "🔥 This Week's Matchups", 
        "🏆 Top Scorers",
        "📊 Consistency",
        "⚡ NextGen Stats",
        "💰 Player Props"
    ])

    # TAB 1: WORST DEFENSES
    with tab1:
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
        if time_filter == f"Week {current_week} Only" and 'week' in stats_df.columns:
            filtered_df = stats_df[stats_df['week'] == current_week]
        elif time_filter == "Last 3 Weeks" and 'week' in stats_df.columns:
            filtered_df = stats_df[stats_df['week'] >= current_week - 2]
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
                st.dataframe(defense_stats.head(10).reset_index(drop=True), use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader(f"🟢 Best {position} Defenses")
                st.caption("These defenses shut down opponents")
                st.dataframe(defense_stats.tail(10).iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
            
            st.subheader(f"Top 15 Defenses Allowing {sort_col}")
            chart_data = defense_stats.head(15).set_index('Defense')[sort_col]
            st.bar_chart(chart_data)
    
    # TAB 2: THIS WEEK'S MATCHUPS
    with tab2:
        st.header(f"Week {current_week} Games")
        st.markdown("Find favorable matchups where strong offenses meet weak defenses")
        
        games = schedule_df[(schedule_df['week'] == current_week) & (schedule_df['game_type'] == 'REG')].copy()
        
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
    
    # TAB 3: TOP SCORERS
    with tab3:
        st.header("Season Leaders")
        
        time_filter_leaders = st.radio(
            "Show leaders for:",
            ["Season Total", f"Week {current_week} Only", "Last 3 Weeks"],
            horizontal=True,
            key="leaders_time_filter"
        )
        
        sort_option = st.radio(
            "Show leaders by:",
            ["Touchdowns", "Yards", "Fantasy Points"],
            horizontal=True,
            key="leaders_sort"
        )
        
        # Filter data
        if time_filter_leaders == f"Week {current_week} Only" and 'week' in stats_df.columns:
            filtered_leaders_df = stats_df[stats_df['week'] == current_week]
        elif time_filter_leaders == "Last 3 Weeks" and 'week' in stats_df.columns:
            filtered_leaders_df = stats_df[stats_df['week'] >= current_week - 2]
        else:
            filtered_leaders_df = stats_df
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Quarterbacks")
            qb_leaders = get_leaders(filtered_leaders_df, positions['QB'], sort_option)
            if not qb_leaders.empty:
                st.dataframe(qb_leaders, use_container_width=True, hide_index=True)
            else:
                st.info("No QB data available")
            
            st.subheader("🏃 Running Backs")
            rb_leaders = get_leaders(filtered_leaders_df, positions['RB'], sort_option)
            if not rb_leaders.empty:
                st.dataframe(rb_leaders, use_container_width=True, hide_index=True)
            else:
                st.info("No RB data available")
        
        with col2:
            st.subheader("📡 Wide Receivers")
            wr_leaders = get_leaders(filtered_leaders_df, positions['WR'], sort_option)
            if not wr_leaders.empty:
                st.dataframe(wr_leaders, use_container_width=True, hide_index=True)
            else:
                st.info("No WR data available")
            
            st.subheader("🎣 Tight Ends")
            te_leaders = get_leaders(filtered_leaders_df, positions['TE'], sort_option)
            if not te_leaders.empty:
                st.dataframe(te_leaders, use_container_width=True, hide_index=True)
            else:
                st.info("No TE data available")
    
    # TAB 4: CONSISTENCY
    with tab4:
        st.header("📊 Player Consistency Ratings")
        st.markdown("Find reliable players who perform week after week")
        
        consistency_position = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="consistency_pos")
        
        pos_df = stats_df[stats_df['position'].isin(positions[consistency_position])].copy()
        
        if pos_df.empty:
            st.warning(f"No {consistency_position} data available")
        else:
            # Determine stat column
            if consistency_position == "QB":
                stat_col = 'passing_yards' if 'passing_yards' in pos_df.columns else 'fantasy_points_ppr'
            else:
                stat_col = 'fantasy_points_ppr' if 'fantasy_points_ppr' in pos_df.columns else 'receiving_yards'
            
            if stat_col in pos_df.columns:
                player_consistency = pos_df.groupby('player_display_name').agg({
                    stat_col: ['mean', 'std', 'count', 'min', 'max']
                }).reset_index()
                
                player_consistency.columns = ['Player', 'Avg', 'StdDev', 'Games', 'Min', 'Max']
                player_consistency['CV'] = (player_consistency['StdDev'] / player_consistency['Avg']) * 100
                max_cv = player_consistency['CV'].max()
                player_consistency['Consistency Rating'] = 100 - ((player_consistency['CV'] / max_cv) * 100)
                player_consistency = player_consistency[player_consistency['Games'] >= 3]
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    most_consistent = player_consistency.nlargest(1, 'Consistency Rating').iloc[0]
                    st.metric("Most Consistent", most_consistent['Player'], f"{most_consistent['Consistency Rating']:.1f}/100")
                
                with col2:
                    highest_avg = player_consistency.nlargest(1, 'Avg').iloc[0]
                    st.metric("Highest Average", highest_avg['Player'], f"{highest_avg['Avg']:.1f}")
                
                with col3:
                    highest_floor = player_consistency.nlargest(1, 'Min').iloc[0]
                    st.metric("Highest Floor", highest_floor['Player'], f"{highest_floor['Min']:.1f}")
                
                with col4:
                    highest_ceiling = player_consistency.nlargest(1, 'Max').iloc[0]
                    st.metric("Highest Ceiling", highest_ceiling['Player'], f"{highest_ceiling['Max']:.1f}")
                
                st.subheader(f"🎯 {consistency_position} Consistency Rankings")
                display_df = player_consistency.sort_values('Consistency Rating', ascending=False)
                st.dataframe(display_df[['Player', 'Avg', 'Consistency Rating', 'Min', 'Max', 'Games']].head(20), use_container_width=True, hide_index=True)

    # TAB 5: NEXTGEN STATS
    with tab5:
        st.header("⚡ NextGen Stats")
        st.markdown("Advanced metrics from NFL's player tracking system")
        
        stat_type = st.selectbox("Stat Category", ["rushing", "receiving", "passing"])
        
        @st.cache_data
        def load_nextgen_data(season, stat_type):
            try:
                nextgen_df = nfl.load_nextgen_stats([season], stat_type=stat_type)
                if hasattr(nextgen_df, 'to_pandas'):
                    nextgen_df = nextgen_df.to_pandas()
                return nextgen_df
            except Exception as e:
                return pd.DataFrame()
        
        with st.spinner(f'Loading NextGen {stat_type} stats...'):
            nextgen_df = load_nextgen_data(season, stat_type)
        
        if nextgen_df.empty:
            st.warning(f"No NextGen {stat_type} data available for {season}")
        else:
            st.success(f"✅ Loaded {len(nextgen_df):,} NextGen records")
            
            if stat_type == "rushing" and 'rush_yards' in nextgen_df.columns:
                st.subheader("Top Rushers")
                top_df = nextgen_df.nlargest(15, 'rush_yards')
                display_cols = ['player_display_name', 'team_abbr', 'rush_yards', 'rush_attempts']
                display_cols = [c for c in display_cols if c in nextgen_df.columns]
                st.dataframe(top_df[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
            
            elif stat_type == "receiving" and 'receiving_yards' in nextgen_df.columns:
                st.subheader("Top Receivers")
                top_df = nextgen_df.nlargest(15, 'receiving_yards')
                display_cols = ['player_display_name', 'team_abbr', 'receiving_yards', 'receptions']
                display_cols = [c for c in display_cols if c in nextgen_df.columns]
                st.dataframe(top_df[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
            
            elif stat_type == "passing" and 'pass_yards' in nextgen_df.columns:
                st.subheader("Top Passers")
                top_df = nextgen_df.nlargest(15, 'pass_yards')
                display_cols = ['player_display_name', 'team_abbr', 'pass_yards', 'completions', 'attempts']
                display_cols = [c for c in display_cols if c in nextgen_df.columns]
                st.dataframe(top_df[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
            
            with st.expander("📋 View All Available NextGen Metrics"):
                st.write("**Available columns:**")
                st.write(nextgen_df.columns.tolist())
                st.dataframe(nextgen_df.head(20), use_container_width=True)
    
    # TAB 6: PLAYER PROPS
    with tab6:
        st.header("💰 Player Props & Parlay Builder")
        st.markdown("Analyze player stats to build winning parlays")
        
        # Get current week's games
        if not schedule_df.empty and 'week' in schedule_df.columns:
            week_games = schedule_df[schedule_df['week'] == current_week]
            
            if not week_games.empty:
                st.subheader(f"🎯 Week {current_week} Player Props")
                
                # Analyze each game for prop opportunities
                for _, game in week_games.iterrows():
                    away_team = game.get('away_team', 'TBD')
                    home_team = game.get('home_team', 'TBD')
                    
                    with st.expander(f"🏈 {away_team} @ {home_team}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**{away_team} Props:**")
                            
                            # Get away team's offensive players
                            away_players = stats_df[stats_df['recent_team'] == away_team].copy()
                            if not away_players.empty:
                                # QB Props
                                qb_players = away_players[away_players['position'] == 'QB']
                                if not qb_players.empty:
                                    qb_stats = qb_players.groupby('player_display_name').agg({
                                        'passing_yards': 'mean',
                                        'passing_tds': 'mean'
                                    }).round(1)
                                    qb_stats = qb_stats.sort_values('passing_yards', ascending=False).head(2)
                                    
                                    st.write("**QB Props:**")
                                    for player, stats in qb_stats.iterrows():
                                        st.write(f"• {player}: {stats['passing_yards']:.0f} pass yds avg")
                                
                                # RB Props
                                rb_players = away_players[away_players['position'].isin(['RB', 'FB'])]
                                if not rb_players.empty:
                                    rb_stats = rb_players.groupby('player_display_name').agg({
                                        'rushing_yards': 'mean',
                                        'receiving_yards': 'mean'
                                    }).round(1)
                                    rb_stats = rb_stats.sort_values('rushing_yards', ascending=False).head(2)
                                    
                                    st.write("**RB Props:**")
                                    for player, stats in rb_stats.iterrows():
                                        st.write(f"• {player}: {stats['rushing_yards']:.0f} rush yds avg")
                                
                                # WR Props
                                wr_players = away_players[away_players['position'] == 'WR']
                                if not wr_players.empty:
                                    wr_stats = wr_players.groupby('player_display_name').agg({
                                        'receiving_yards': 'mean',
                                        'receptions': 'mean'
                                    }).round(1)
                                    wr_stats = wr_stats.sort_values('receiving_yards', ascending=False).head(2)
                                    
                                    st.write("**WR Props:**")
                                    for player, stats in wr_stats.iterrows():
                                        st.write(f"• {player}: {stats['receiving_yards']:.0f} rec yds avg")
                        
                        with col2:
                            st.markdown(f"**{home_team} Props:**")
                            
                            # Get home team's offensive players
                            home_players = stats_df[stats_df['recent_team'] == home_team].copy()
                            if not home_players.empty:
                                # QB Props
                                qb_players = home_players[home_players['position'] == 'QB']
                                if not qb_players.empty:
                                    qb_stats = qb_players.groupby('player_display_name').agg({
                                        'passing_yards': 'mean',
                                        'passing_tds': 'mean'
                                    }).round(1)
                                    qb_stats = qb_stats.sort_values('passing_yards', ascending=False).head(2)
                                    
                                    st.write("**QB Props:**")
                                    for player, stats in qb_stats.iterrows():
                                        st.write(f"• {player}: {stats['passing_yards']:.0f} pass yds avg")
                                
                                # RB Props
                                rb_players = home_players[home_players['position'].isin(['RB', 'FB'])]
                                if not rb_players.empty:
                                    rb_stats = rb_players.groupby('player_display_name').agg({
                                        'rushing_yards': 'mean',
                                        'receiving_yards': 'mean'
                                    }).round(1)
                                    rb_stats = rb_stats.sort_values('rushing_yards', ascending=False).head(2)
                                    
                                    st.write("**RB Props:**")
                                    for player, stats in rb_stats.iterrows():
                                        st.write(f"• {player}: {stats['rushing_yards']:.0f} rush yds avg")
                                
                                # WR Props
                                wr_players = home_players[home_players['position'] == 'WR']
                                if not wr_players.empty:
                                    wr_stats = wr_players.groupby('player_display_name').agg({
                                        'receiving_yards': 'mean',
                                        'receptions': 'mean'
                                    }).round(1)
                                    wr_stats = wr_stats.sort_values('receiving_yards', ascending=False).head(2)
                                    
                                    st.write("**WR Props:**")
                                    for player, stats in wr_stats.iterrows():
                                        st.write(f"• {player}: {stats['receiving_yards']:.0f} rec yds avg")
            else:
                st.warning(f"No games found for Week {current_week}")
        else:
            st.warning("Schedule data not available")
        
        # Parlay Tips
        st.subheader("🎲 Parlay Building Tips")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**High-Probability Props:**")
            st.write("✅ QB passing yards")
            st.write("✅ RB rushing yards")
            st.write("✅ WR receptions")
            st.write("✅ Kicker field goals")
        
        with col2:
            st.write("**Avoid These Props:**")
            st.write("❌ Defensive TDs")
            st.write("❌ Special teams TDs")
            st.write("❌ Exact yardage props")
            st.write("❌ Weather-dependent props")
        
        # Show defense rankings for prop targeting
        st.subheader("🎯 Target These Defenses")
        
        defense_tips = st.selectbox("Select position to see worst defenses:", ["QB", "RB", "WR", "TE"])
        
        if defense_tips in positions:
            defense_stats = get_defense_stats(stats_df, positions[defense_tips])
            if not defense_stats.empty:
                td_cols = [col for col in defense_stats.columns if 'Td' in col]
                if td_cols:
                    defense_stats = defense_stats.sort_values(td_cols[0], ascending=False)
                    st.write(f"**Worst {defense_tips} Defenses (Target for Props):**")
                    worst_defenses = defense_stats.head(5)['Defense'].tolist()
                    for i, team in enumerate(worst_defenses, 1):
                        st.write(f"{i}. {team}")
                    st.caption("Target offensive players against these teams!")

    st.markdown("---")
    st.caption("Data from nflverse (via nflreadpy). Created with Streamlit.")


if __name__ == "__main__":
    run()
