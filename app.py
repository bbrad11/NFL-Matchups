import streamlit as st
import nflreadpy as nfl
import pandas as pd

# Page config
st.set_page_config(
    page_title="NFL Matchup Analyzer", 
    page_icon="🏈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    /* Main title styling */
    .main h1 {
        color: #1E3A8A;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Tabs styling */
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
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #1E3A8A;
    }
    
    /* Buttons and selectbox */
    .stSelectbox, .stRadio {
        background-color: white;
        border-radius: 8px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
    }
    
    /* Cards effect for columns */
    .element-container {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Title with better styling
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0;'>🏈 NFL Matchup Analyzer</h1>
    <p style='text-align: center; color: #6B7280; font-size: 1.2rem; margin-top: 0;'>
        Data-driven insights for smarter lineup decisions
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar controls
st.sidebar.header("Settings")
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
    """Load NextGen Stats"""
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
    st.write(f"**Columns:** {stats_df.columns.tolist()}")
    if 'week' in stats_df.columns:
        st.write(f"**Available Weeks:** {sorted(stats_df['week'].unique())}")
        st.write(f"**Records in Week {current_week}:** {len(stats_df[stats_df['week'] == current_week])}")
    else:
        st.warning("No 'week' column found in data!")
    st.write(f"**Sample Data:**")
    st.dataframe(stats_df.head(3))

# Position groups
positions = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE']
}

# Analyze defense performance
def get_defense_stats(stats_df, position_codes):
    """Get how each defense performs against a position"""
    pos_stats = stats_df[stats_df['position'].isin(position_codes)].copy()
    
    # Build aggregation based on available columns
    agg_dict = {}
    for col in ['passing_tds', 'rushing_tds', 'receiving_tds', 'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']:
        if col in pos_stats.columns:
            agg_dict[col] = 'sum'
    
    if not agg_dict:
        return pd.DataFrame()
    
    defense_stats = pos_stats.groupby('opponent_team').agg(agg_dict).reset_index()
    defense_stats.columns = ['Defense'] + [col.replace('_', ' ').title() for col in defense_stats.columns[1:]]
    
    return defense_stats

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛡️ Worst Defenses", "🔥 This Week's Matchups", "🏆 Top Scorers", "📊 Consistency", "⚡ NextGen Stats"])

# ============================================================
# TAB 1: WORST DEFENSES
# ============================================================

with tab1:
    st.header("Which Defenses Give Up The Most?")
    st.markdown("Higher numbers = easier matchup for offensive players")
    
    # Add filter option
    time_filter = st.radio(
        "Show stats for:",
        ["Season Total", f"Week {current_week} Only", "Last 3 Weeks"],
        horizontal=True,
        key="def_time_filter"
    )
    
    position = st.selectbox("Position", ["QB", "RB", "WR", "TE"])
    
    # Filter data based on selection
    if time_filter == f"Week {current_week} Only":
        if 'week' in stats_df.columns:
            filtered_df = stats_df[stats_df['week'] == current_week]
            st.info(f"Showing {len(filtered_df)} records from Week {current_week}")
        else:
            filtered_df = stats_df
            st.warning("Week filtering not available - showing all data")
    elif time_filter == "Last 3 Weeks":
        if 'week' in stats_df.columns:
            filtered_df = stats_df[stats_df['week'] >= current_week - 2]
            st.info(f"Showing {len(filtered_df)} records from Weeks {current_week-2} to {current_week}")
        else:
            filtered_df = stats_df
            st.warning("Week filtering not available - showing all data")
    else:  # Season Total
        filtered_df = stats_df
        st.info(f"Showing all {len(filtered_df)} records from season")
    
    defense_stats = get_defense_stats(filtered_df, positions[position])
    
    if defense_stats.empty:
        st.warning(f"No {position} data available for {season}")
    else:
        # Sort by TDs (or first available column)
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
        
        # Chart
        st.subheader(f"Top 15 Defenses Allowing {sort_col}")
        chart_data = defense_stats.head(15).set_index('Defense')[sort_col]
        st.bar_chart(chart_data)

# ============================================================
# TAB 2: THIS WEEK'S MATCHUPS
# ============================================================

with tab2:
    st.header(f"Week {current_week} Games")
    st.markdown("Find favorable matchups where strong offenses meet weak defenses")
    
    # Get this week's games
    games = schedule_df[
        (schedule_df['week'] == current_week) & 
        (schedule_df['game_type'] == 'REG')
    ].copy()
    
    if games.empty:
        st.warning(f"No games found for Week {current_week}")
    else:
        st.subheader(f"📅 {len(games)} Games This Week")
        
        # Get weak defenses for each position
        weak_defenses = {}
        for pos_name, pos_codes in positions.items():
            defense_stats = get_defense_stats(stats_df, pos_codes)
            if not defense_stats.empty:
                # Get column with TDs
                td_cols = [col for col in defense_stats.columns if 'Td' in col]
                if td_cols:
                    defense_stats = defense_stats.sort_values(td_cols[0], ascending=False)
                    weak_defenses[pos_name] = defense_stats.head(10)['Defense'].tolist()
        
        # Show each game
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

# ============================================================
# TAB 3: TOP SCORERS
# ============================================================

with tab3:
    st.header("Season Leaders")
    
    # Add time filter
    time_filter_leaders = st.radio(
        "Show leaders for:",
        ["Season Total", "This Week Only", "Last 3 Weeks"],
        horizontal=True,
        key="leaders_time_filter"
    )
    
    sort_option = st.radio(
        "Show leaders by:",
        ["Touchdowns", "Yards", "Fantasy Points"],
        horizontal=True
    )
    
    def get_leaders(df, pos_codes):
        """Get top players at a position"""
        pos_df = df[df['position'].isin(pos_codes)].copy()
        
        if pos_df.empty:
            return pd.DataFrame()
        
        # Determine what columns exist
        has_pass_td = 'passing_tds' in pos_df.columns
        has_rush_td = 'rushing_tds' in pos_df.columns
        has_rec_td = 'receiving_tds' in pos_df.columns
        has_pass_yds = 'passing_yards' in pos_df.columns
        has_rush_yds = 'rushing_yards' in pos_df.columns
        has_rec_yds = 'receiving_yards' in pos_df.columns
        has_fantasy = 'fantasy_points_ppr' in pos_df.columns
        
        # Calculate totals
        td_cols = []
        if has_pass_td:
            pos_df['passing_tds'] = pos_df['passing_tds'].fillna(0)
            td_cols.append('passing_tds')
        if has_rush_td:
            pos_df['rushing_tds'] = pos_df['rushing_tds'].fillna(0)
            td_cols.append('rushing_tds')
        if has_rec_td:
            pos_df['receiving_tds'] = pos_df['receiving_tds'].fillna(0)
            td_cols.append('receiving_tds')
        
        yds_cols = []
        if has_pass_yds:
            pos_df['passing_yards'] = pos_df['passing_yards'].fillna(0)
            yds_cols.append('passing_yards')
        if has_rush_yds:
            pos_df['rushing_yards'] = pos_df['rushing_yards'].fillna(0)
            yds_cols.append('rushing_yards')
        if has_rec_yds:
            pos_df['receiving_yards'] = pos_df['receiving_yards'].fillna(0)
            yds_cols.append('receiving_yards')
        
        # Build aggregation
        agg_dict = {}
        
        # Add team column
        for team_col in ['recent_team', 'team', 'team_abbr']:
            if team_col in pos_df.columns:
                agg_dict[team_col] = 'last'
                break
        
        # Add stat columns
        for col in td_cols + yds_cols:
            agg_dict[col] = 'sum'
        
        if has_fantasy:
            agg_dict['fantasy_points_ppr'] = 'sum'
        
        if not agg_dict:
            return pd.DataFrame()
        
        # Group by player
        leaders = pos_df.groupby('player_display_name').agg(agg_dict).reset_index()
        
        # Calculate total TDs and yards
        if td_cols:
            leaders['Total TDs'] = leaders[td_cols].sum(axis=1)
        if yds_cols:
            leaders['Total Yards'] = leaders[yds_cols].sum(axis=1)
        
        # Rename columns for display
        rename_map = {
            'recent_team': 'Team',
            'team': 'Team',
            'team_abbr': 'Team',
            'passing_tds': 'Pass TDs',
            'rushing_tds': 'Rush TDs',
            'receiving_tds': 'Rec TDs',
            'passing_yards': 'Pass Yds',
            'rushing_yards': 'Rush Yds',
            'receiving_yards': 'Rec Yds',
            'fantasy_points_ppr': 'Fantasy Pts'
        }
        leaders = leaders.rename(columns=rename_map)
        leaders = leaders.rename(columns={'player_display_name': 'Player'})
        
        # Sort based on user preference
        if sort_option == "Touchdowns":
            sort_col = 'Total TDs' if 'Total TDs' in leaders.columns else leaders.columns[1]
        elif sort_option == "Yards":
            sort_col = 'Total Yards' if 'Total Yards' in leaders.columns else leaders.columns[1]
        else:  # Fantasy Points
            sort_col = 'Fantasy Pts' if 'Fantasy Pts' in leaders.columns else leaders.columns[1]
        
        leaders = leaders.sort_values(sort_col, ascending=False).head(15)
        
        return leaders
    
    # Filter data based on time selection
    if time_filter_leaders == "This Week Only":
        filtered_leaders_df = stats_df[stats_df['week'] == current_week]
    elif time_filter_leaders == "Last 3 Weeks":
        filtered_leaders_df = stats_df[stats_df['week'] >= current_week - 2]
    else:  # Season Total
        filtered_leaders_df = stats_df
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Quarterbacks")
        qb_leaders = get_leaders(filtered_leaders_df, positions['QB'])
        if not qb_leaders.empty:
            st.dataframe(qb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No QB data available")
        
        st.subheader("🏃 Running Backs")
        rb_leaders = get_leaders(filtered_leaders_df, positions['RB'])
        if not rb_leaders.empty:
            st.dataframe(rb_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No RB data available")
    
    with col2:
        st.subheader("📡 Wide Receivers")
        wr_leaders = get_leaders(filtered_leaders_df, positions['WR'])
        if not wr_leaders.empty:
            st.dataframe(wr_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No WR data available")
        
        st.subheader("🎣 Tight Ends")
        te_leaders = get_leaders(filtered_leaders_df, positions['TE'])
        if not te_leaders.empty:
            st.dataframe(te_leaders, use_container_width=True, hide_index=True)
        else:
            st.info("No TE data available")

# ============================================================
# TAB 4: CONSISTENCY RATINGS
# ============================================================

with tab4:
    st.header("📊 Player Consistency Ratings")
    st.markdown("Find reliable players who perform week after week")
    
    consistency_position = st.selectbox("Position", ["QB", "RB", "WR", "TE"], key="consistency_pos")
    
    # Filter for position
    pos_df = stats_df[stats_df['position'].isin(positions[consistency_position])].copy()
    
    if pos_df.empty:
        st.warning(f"No {consistency_position} data available")
    else:
        # Determine the primary stat to analyze
        if consistency_position == "QB":
            stat_col = 'passing_yards' if 'passing_yards' in pos_df.columns else 'fantasy_points_ppr'
            stat_name = "Passing Yards"
        elif consistency_position in ["RB", "WR", "TE"]:
            stat_col = 'fantasy_points_ppr' if 'fantasy_points_ppr' in pos_df.columns else 'receiving_yards'
            stat_name = "Fantasy Points"
        else:
            stat_col = pos_df.columns[0]
            stat_name = "Points"
        
        if stat_col not in pos_df.columns:
            st.warning(f"Required stat column not found")
        else:
            # Calculate consistency metrics per player
            player_consistency = pos_df.groupby('player_display_name').agg({
                stat_col: ['mean', 'std', 'count', 'min', 'max']
            }).reset_index()
            
            player_consistency.columns = ['Player', 'Avg', 'StdDev', 'Games', 'Min', 'Max']
            
            # Calculate consistency score (lower std dev relative to mean = more consistent)
            # Coefficient of Variation
            player_consistency['CV'] = (player_consistency['StdDev'] / player_consistency['Avg']) * 100
            
            # Consistency Rating (inverted CV, scaled 0-100)
            max_cv = player_consistency['CV'].max()
            player_consistency['Consistency Rating'] = 100 - ((player_consistency['CV'] / max_cv) * 100)
            
            # Filter players with at least 3 games
            player_consistency = player_consistency[player_consistency['Games'] >= 3]
            
            # Add floor and ceiling metrics
            player_consistency['Floor'] = player_consistency['Min']
            player_consistency['Ceiling'] = player_consistency['Max']
            player_consistency['Range'] = player_consistency['Max'] - player_consistency['Min']
            
            # Metrics display
            st.subheader("📈 Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                most_consistent = player_consistency.nlargest(1, 'Consistency Rating').iloc[0]
                st.metric(
                    "Most Consistent Player",
                    most_consistent['Player'],
                    f"{most_consistent['Consistency Rating']:.1f}/100"
                )
            
            with col2:
                highest_avg = player_consistency.nlargest(1, 'Avg').iloc[0]
                st.metric(
                    "Highest Average",
                    highest_avg['Player'],
                    f"{highest_avg['Avg']:.1f}"
                )
            
            with col3:
                highest_floor = player_consistency.nlargest(1, 'Floor').iloc[0]
                st.metric(
                    "Highest Floor",
                    highest_floor['Player'],
                    f"{highest_floor['Floor']:.1f}"
                )
            
            with col4:
                highest_ceiling = player_consistency.nlargest(1, 'Ceiling').iloc[0]
                st.metric(
                    "Highest Ceiling",
                    highest_ceiling['Player'],
                    f"{highest_ceiling['Ceiling']:.1f}"
                )
            
            # Sorting options
            st.subheader(f"🎯 {consistency_position} Consistency Rankings")
            
            sort_by_consistency = st.radio(
                "Sort by:",
                ["Most Consistent", "Highest Average", "Highest Floor", "Highest Ceiling"],
                horizontal=True,
                key="consistency_sort"
            )
            
            if sort_by_consistency == "Most Consistent":
                display_df = player_consistency.sort_values('Consistency Rating', ascending=False)
            elif sort_by_consistency == "Highest Average":
                display_df = player_consistency.sort_values('Avg', ascending=False)
            elif sort_by_consistency == "Highest Floor":
                display_df = player_consistency.sort_values('Floor', ascending=False)
            else:  # Highest Ceiling
                display_df = player_consistency.sort_values('Ceiling', ascending=False)
            
            # Display table
            st.dataframe(
                display_df[['Player', 'Avg', 'Consistency Rating', 'Floor', 'Ceiling', 'Games']].head(20).style.format({
                    'Avg': '{:.1f}',
                    'Consistency Rating': '{:.1f}',
                    'Floor': '{:.1f}',
                    'Ceiling': '{:.1f}',
                    'Games': '{:.0f}'
                }).background_gradient(subset=['Consistency Rating'], cmap='RdYlGn'),
                use_container_width=True,
                hide_index=True
            )
            
            # Explanation
            with st.expander("ℹ️ How Consistency is Calculated"):
                st.markdown("""
                **Consistency Rating (0-100):**
                - Higher score = more reliable week-to-week performance
                - Based on Coefficient of Variation (Standard Deviation / Mean)
                - Players with low variance relative to their average score higher
                
                **Floor:** Lowest performance in a game this season
                
                **Ceiling:** Best performance in a game this season
                
                **Range:** Difference between ceiling and floor (lower = more consistent)
                
                **Why it matters:** Consistent players reduce risk in your lineup, while high-ceiling players offer upside potential.
                """)
            
            # Weekly performance chart for top player
            st.subheader("📉 Week-by-Week Performance")
            
            top_players = display_df.head(10)['Player'].tolist()
            selected_player = st.selectbox("Select player to view weekly performance:", top_players)
            
            player_weeks = pos_df[pos_df['player_display_name'] == selected_player].copy()
            if 'week' in player_weeks.columns and not player_weeks.empty:
                player_weeks = player_weeks.sort_values('week')
                
                # Create chart data
                chart_data = player_weeks.set_index('week')[stat_col]
                
                st.line_chart(chart_data)
                
                # Show stats
                avg_val = chart_data.mean()
                st.caption(f"Average: {avg_val:.1f} | Min: {chart_data.min():.1f} | Max: {chart_data.max():.1f}")

# ============================================================
# TAB 5: NEXTGEN STATS
# ============================================================

with tab5:
    st.header("⚡ NextGen Stats")
    st.markdown("Advanced metrics from NFL's player tracking system")
    
    stat_type = st.selectbox(
        "Stat Category",
        ["rushing", "receiving", "passing"]
    )
    
    with st.spinner(f'Loading NextGen {stat_type} stats...'):
        nextgen_df = load_nextgen_data(season, stat_type)
    
    if nextgen_df.empty:
        st.warning(f"No NextGen {stat_type} data available for {season}")
        st.info("NextGen Stats are typically available for 2016+ seasons")
    else:
        st.success(f"✅ Loaded {len(nextgen_df):,} NextGen records")
        
        # Show key metrics based on stat type
        if stat_type == "rushing":
            st.subheader("🏃 Rush Efficiency Leaders")
            
            # Get available columns
            available_cols = nextgen_df.columns.tolist()
            
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'rush_yards' in available_cols:
                    st.metric("Total Rush Yards", f"{nextgen_df['rush_yards'].sum():,.0f}")
            with col2:
                if 'rush_touchdowns' in available_cols:
                    st.metric("Total Rush TDs", f"{nextgen_df['rush_touchdowns'].sum():.0f}")
            with col3:
                if 'rush_attempts' in available_cols:
                    st.metric("Total Rush Attempts", f"{nextgen_df['rush_attempts'].sum():.0f}")
            
            # Top performers table
            st.subheader("Top Rushers")
            
            # Determine sort column
            sort_options = []
            if 'rush_yards' in available_cols:
                sort_options.append('rush_yards')
            if 'rush_yards_over_expected' in available_cols:
                sort_options.append('rush_yards_over_expected')
            if 'efficiency' in available_cols:
                sort_options.append('efficiency')
            
            if sort_options:
                sort_by = st.selectbox("Sort by:", sort_options, format_func=lambda x: x.replace('_', ' ').title())
                top_df = nextgen_df.nlargest(15, sort_by)
                
                # Display columns
                display_cols = ['player_display_name']
                for col in ['team_abbr', 'rush_yards', 'rush_attempts', 'rush_touchdowns', 'efficiency', 'rush_yards_over_expected']:
                    if col in available_cols:
                        display_cols.append(col)
                
                st.dataframe(
                    top_df[display_cols].reset_index(drop=True).rename(columns={
                        'player_display_name': 'Player',
                        'team_abbr': 'Team',
                        'rush_yards': 'Rush Yds',
                        'rush_attempts': 'Attempts',
                        'rush_touchdowns': 'Rush TDs',
                        'efficiency': 'Efficiency',
                        'rush_yards_over_expected': 'Yds Over Expected'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        
        elif stat_type == "receiving":
            st.subheader("📡 Receiving Leaders")
            
            available_cols = nextgen_df.columns.tolist()
            
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'receiving_yards' in available_cols:
                    st.metric("Total Rec Yards", f"{nextgen_df['receiving_yards'].sum():,.0f}")
            with col2:
                if 'receptions' in available_cols:
                    st.metric("Total Receptions", f"{nextgen_df['receptions'].sum():.0f}")
            with col3:
                if 'targets' in available_cols:
                    st.metric("Total Targets", f"{nextgen_df['targets'].sum():.0f}")
            
            # Top performers
            st.subheader("Top Receivers")
            
            sort_options = []
            if 'receiving_yards' in available_cols:
                sort_options.append('receiving_yards')
            if 'avg_separation' in available_cols:
                sort_options.append('avg_separation')
            if 'avg_cushion' in available_cols:
                sort_options.append('avg_cushion')
            
            if sort_options:
                sort_by = st.selectbox("Sort by:", sort_options, format_func=lambda x: x.replace('_', ' ').title())
                top_df = nextgen_df.nlargest(15, sort_by)
                
                display_cols = ['player_display_name']
                for col in ['team_abbr', 'receiving_yards', 'receptions', 'targets', 'avg_separation', 'avg_cushion']:
                    if col in available_cols:
                        display_cols.append(col)
                
                st.dataframe(
                    top_df[display_cols].reset_index(drop=True).rename(columns={
                        'player_display_name': 'Player',
                        'team_abbr': 'Team',
                        'receiving_yards': 'Rec Yds',
                        'receptions': 'Rec',
                        'targets': 'Targets',
                        'avg_separation': 'Avg Separation',
                        'avg_cushion': 'Avg Cushion'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        
        elif stat_type == "passing":
            st.subheader("🎯 Passing Efficiency Leaders")
            
            available_cols = nextgen_df.columns.tolist()
            
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'pass_yards' in available_cols:
                    st.metric("Total Pass Yards", f"{nextgen_df['pass_yards'].sum():,.0f}")
            with col2:
                if 'completions' in available_cols:
                    st.metric("Total Completions", f"{nextgen_df['completions'].sum():.0f}")
            with col3:
                if 'attempts' in available_cols:
                    st.metric("Total Attempts", f"{nextgen_df['attempts'].sum():.0f}")
            
            # Top performers
            st.subheader("Top Passers")
            
            sort_options = []
            if 'pass_yards' in available_cols:
                sort_options.append('pass_yards')
            if 'completion_percentage' in available_cols:
                sort_options.append('completion_percentage')
            if 'avg_time_to_throw' in available_cols:
                sort_options.append('avg_time_to_throw')
            
            if sort_options:
                sort_by = st.selectbox("Sort by:", sort_options, format_func=lambda x: x.replace('_', ' ').title())
                top_df = nextgen_df.nlargest(15, sort_by)
                
                display_cols = ['player_display_name']
                for col in ['team_abbr', 'pass_yards', 'completions', 'attempts', 'completion_percentage', 'avg_time_to_throw']:
                    if col in available_cols:
                        display_cols.append(col)
                
                st.dataframe(
                    top_df[display_cols].reset_index(drop=True).rename(columns={
                        'player_display_name': 'Player',
                        'team_abbr': 'Team',
                        'pass_yards': 'Pass Yds',
                        'completions': 'Comp',
                        'attempts': 'Att',
                        'completion_percentage': 'Comp %',
                        'avg_time_to_throw': 'Avg Time to Throw'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        
        # Show all available columns
        with st.expander("📋 View All Available NextGen Metrics"):
            st.write("**Available columns:**")
            st.write(nextgen_df.columns.tolist())
            st.dataframe(nextgen_df.head(20), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("📊 Data: [nflverse](https://github.com/nflverse/nflreadpy) | Updated weekly during NFL season")
