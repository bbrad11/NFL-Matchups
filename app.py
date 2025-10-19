import streamlit as st
import nflreadpy as nfl
import pandas as pd

# Page config
st.set_page_config(page_title="NFL Matchup Analyzer", page_icon="🏈", layout="wide")

# Title
st.title("🏈 NFL Matchup & Defense Weakness Analyzer")
st.markdown("Track strength-vs-weakness matchups and defensive positional weaknesses")

# Sidebar controls
st.sidebar.header("Settings")
season = st.sidebar.selectbox("Season", [2025, 2024, 2023], index=0)
current_week = st.sidebar.slider("Current Week", 1, 18, 7)

# Cache data loading
@st.cache_data
def load_nfl_data(season):
    player_stats = nfl.load_player_stats([season])
    schedules = nfl.load_schedules([season])
    return player_stats.to_pandas(), schedules.to_pandas()

# Load data
with st.spinner('Loading NFL data...'):
    stats_df, schedule_df = load_nfl_data(season)

st.success(f"✅ Loaded {len(stats_df):,} player-game records")

# Position mapping
positions = {
    'QB': ['QB'],
    'RB': ['RB', 'FB'],
    'WR': ['WR'],
    'TE': ['TE']
}

# Function to analyze defense vs position
def analyze_defense_vs_position(stats_df, position_codes, stat_columns):
    pos_stats = stats_df[stats_df['position'].isin(position_codes)].copy()
    defense_stats = pos_stats.groupby('opponent_team').agg(stat_columns).reset_index()
    defense_stats.columns = ['Defense'] + [col[0] + '_' + col[1] for col in defense_stats.columns[1:]]
    return defense_stats

# ============================================================
# TAB 1: DEFENSE WEAKNESSES
# ============================================================

tab1, tab2, tab3 = st.tabs(["🛡️ Defense Weaknesses", "🔥 Matchup Analysis", "🏆 TD Leaders"])

with tab1:
    st.header("Defensive Positional Weaknesses")
    
    position_select = st.selectbox("Select Position", ["QB", "RB", "WR", "TE"])
    
    if position_select == "QB":
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
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs QB (by TDs)")
            st.dataframe(qb_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs QB (by TDs)")
            st.dataframe(qb_defense.tail(10).iloc[::-1], use_container_width=True)
        
        # Chart
        st.bar_chart(qb_defense.head(15).set_index('Defense')['passing_tds_sum'])
    
    elif position_select == "RB":
        rb_defense = analyze_defense_vs_position(
            stats_df,
            positions['RB'],
            {
                'rushing_yards': ['sum', 'mean'],
                'rushing_tds': ['sum', 'mean'],
                'receiving_tds': ['sum'],
                'fantasy_points_ppr': ['sum', 'mean']
            }
        )
        rb_defense['total_tds'] = rb_defense['rushing_tds_sum'] + rb_defense['receiving_tds_sum']
        rb_defense = rb_defense.sort_values('total_tds', ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs RB")
            st.dataframe(rb_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs RB")
            st.dataframe(rb_defense.tail(10).iloc[::-1], use_container_width=True)
        
        st.bar_chart(rb_defense.head(15).set_index('Defense')['total_tds'])
    
    elif position_select == "WR":
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
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs WR")
            st.dataframe(wr_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs WR")
            st.dataframe(wr_defense.tail(10).iloc[::-1], use_container_width=True)
        
        st.bar_chart(wr_defense.head(15).set_index('Defense')['receiving_tds_sum'])
    
    else:  # TE
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
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Worst Defenses vs TE")
            st.dataframe(te_defense.head(10), use_container_width=True)
        with col2:
            st.subheader("Best Defenses vs TE")
            st.dataframe(te_defense.tail(10).iloc[::-1], use_container_width=True)
        
        st.bar_chart(te_defense.head(15).set_index('Defense')['receiving_tds_sum'])

# ============================================================
# TAB 2: MATCHUP ANALYSIS
# ============================================================

with tab2:
    st.header(f"Week {current_week} Matchup Analysis")
    
    upcoming_games = schedule_df[
        (schedule_df['week'] == current_week) & 
        (schedule_df['game_type'] == 'REG')
    ].copy()
    
    st.subheader(f"📅 {len(upcoming_games)} Games This Week")
    
    # Recent form (last 3 weeks)
    recent_stats = stats_df[stats_df['week'] >= current_week - 3].copy()
    
    # Calculate defense rankings
    qb_defense = analyze_defense_vs_position(stats_df, positions['QB'], {'passing_tds': ['sum']})
    rb_defense = analyze_defense_vs_position(stats_df, positions['RB'], {'rushing_tds': ['sum'], 'receiving_tds': ['sum']})
    wr_defense = analyze_defense_vs_position(stats_df, positions['WR'], {'receiving_tds': ['sum']})
    te_defense = analyze_defense_vs_position(stats_df, positions['TE'], {'receiving_tds': ['sum']})
    
    qb_weak = qb_defense.sort_values('passing_tds_sum', ascending=False).head(10)['Defense'].tolist()
    rb_defense['total_tds'] = rb_defense['rushing_tds_sum'] + rb_defense['receiving_tds_sum']
    rb_weak = rb_defense.sort_values('total_tds', ascending=False).head(10)['Defense'].tolist()
    wr_weak = wr_defense.sort_values('receiving_tds_sum', ascending=False).head(10)['Defense'].tolist()
    te_weak = te_defense.sort_values('receiving_tds_sum', ascending=False).head(10)['Defense'].tolist()
    
    # Show matchups
    for _, game in upcoming_games.iterrows():
        with st.expander(f"{game['away_team']} @ {game['home_team']} - {game['gameday']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{game['away_team']} Offense**")
                if game['home_team'] in qb_weak:
                    st.success(f"✅ QB favorable matchup (vs weak pass D)")
                if game['home_team'] in rb_weak:
                    st.success(f"✅ RB favorable matchup (vs weak run D)")
                if game['home_team'] in wr_weak:
                    st.success(f"✅ WR favorable matchup (vs weak pass D)")
                if game['home_team'] in te_weak:
                    st.success(f"✅ TE favorable matchup (vs weak TE D)")
            
            with col2:
                st.markdown(f"**{game['home_team']} Offense**")
                if game['away_team'] in qb_weak:
                    st.success(f"✅ QB favorable matchup (vs weak pass D)")
                if game['away_team'] in rb_weak:
                    st.success(f"✅ RB favorable matchup (vs weak run D)")
                if game['away_team'] in wr_weak:
                    st.success(f"✅ WR favorable matchup (vs weak pass D)")
                if game['away_team'] in te_weak:
                    st.success(f"✅ TE favorable matchup (vs weak TE D)")

# ============================================================
# TAB 3: TD LEADERS
# ============================================================

with tab3:
    st.header("🏆 Touchdown Leaders")
    
    def get_td_leaders(df, position_list, position_name):
        pos_df = df[df['position'].isin(position_list)].copy()
        
        # Check which columns exist
        has_passing = 'passing_tds' in pos_df.columns
        has_rushing = 'rushing_tds' in pos_df.columns
        has_receiving = 'receiving_tds' in pos_df.columns
        
        # Build aggregation dict based on available columns
        agg_dict = {}
        
        if has_rushing:
            agg_dict['rushing_tds'] = 'sum'
            pos_df['rushing_tds'] = pos_df['rushing_tds'].fillna(0)
        
        if has_receiving:
            agg_dict['receiving_tds'] = 'sum'
            pos_df['receiving_tds'] = pos_df['receiving_tds'].fillna(0)
        
        if has_passing:
            agg_dict['passing_tds'] = 'sum'
            pos_df['passing_tds'] = pos_df['passing_tds'].fillna(0)
        
        # Add team column (try different possible names)
        team_col = None
        for col in ['recent_team', 'team', 'team_abbr']:
            if col in pos_df.columns:
                team_col = col
                agg_dict[col] = 'last'
                break
        
        if not agg_dict:
            st.error(f"No TD columns found for {position_name}")
            return pd.DataFrame()
        
        # Calculate total TDs
        if position_name == "QB":
            if has_passing and has_rushing:
                pos_df['total_tds'] = pos_df['passing_tds'] + pos_df['rushing_tds']
            elif has_passing:
                pos_df['total_tds'] = pos_df['passing_tds']
            else:
                pos_df['total_tds'] = 0
            sort_col = 'passing_tds' if has_passing else 'total_tds'
        else:
            tds = []
            if has_rushing:
                tds.append(pos_df['rushing_tds'])
            if has_receiving:
                tds.append(pos_df['receiving_tds'])
            pos_df['total_tds'] = sum(tds) if tds else 0
            sort_col = 'total_tds'
        
        agg_dict['total_tds'] = 'sum'
        
        try:
            leaders = pos_df.groupby('player_display_name').agg(agg_dict).reset_index()
            leaders = leaders.sort_values(sort_col, ascending=False).head(15)
            return leaders
        except Exception as e:
            st.error(f"Error processing {position_name}: {str(e)}")
            return pd.DataFrame()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 QB Leaders")
        qb_tds = get_td_leaders(stats_df, positions['QB'], "QB")
        if not qb_tds.empty:
            display_cols = ['player_display_name']
            for col in ['recent_team', 'team', 'team_abbr']:
                if col in qb_tds.columns:
                    display_cols.append(col)
                    break
            for col in ['passing_tds', 'rushing_tds']:
                if col in qb_tds.columns:
                    display_cols.append(col)
            st.dataframe(qb_tds[display_cols], use_container_width=True)
        
        st.subheader("🏃 RB Leaders")
        rb_tds = get_td_leaders(stats_df, positions['RB'], "RB")
        if not rb_tds.empty:
            display_cols = ['player_display_name']
            for col in ['recent_team', 'team', 'team_abbr']:
                if col in rb_tds.columns:
                    display_cols.append(col)
                    break
            for col in ['rushing_tds', 'receiving_tds', 'total_tds']:
                if col in rb_tds.columns:
                    display_cols.append(col)
            st.dataframe(rb_tds[display_cols], use_container_width=True)
    
    with col2:
        st.subheader("📡 WR Leaders")
        wr_tds = get_td_leaders(stats_df, positions['WR'], "WR")
        if not wr_tds.empty:
            display_cols = ['player_display_name']
            for col in ['recent_team', 'team', 'team_abbr']:
                if col in wr_tds.columns:
                    display_cols.append(col)
                    break
            for col in ['receiving_tds', 'total_tds']:
                if col in wr_tds.columns:
                    display_cols.append(col)
            st.dataframe(wr_tds[display_cols], use_container_width=True)
        
        st.subheader("🎣 TE Leaders")
        te_tds = get_td_leaders(stats_df, positions['TE'], "TE")
        if not te_tds.empty:
            display_cols = ['player_display_name']
            for col in ['recent_team', 'team', 'team_abbr']:
                if col in te_tds.columns:
                    display_cols.append(col)
                    break
            for col in ['receiving_tds', 'total_tds']:
                if col in te_tds.columns:
                    display_cols.append(col)
            st.dataframe(te_tds[display_cols], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data source: nflverse via nflreadpy | Updated weekly during NFL season")
