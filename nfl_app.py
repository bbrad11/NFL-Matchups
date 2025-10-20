# ----------------- TAB 6: BETTING -----------------
from betting_analyzer import render_betting_tab

# Detect the proper player column before passing to betting tab
if 'player_display_name' not in stats_df.columns:
    possible_player_cols = [c for c in ['player_name', 'name', 'display_name'] if c in stats_df.columns]
    if possible_player_cols:
        stats_df = stats_df.rename(columns={possible_player_cols[0]: 'player_display_name'})
    else:
        st.warning("⚠️ No player column found in stats_df. Betting tab may not work correctly.")

# Betting Tab
with tab6:
    st.header("💰 Betting Insights")
    st.markdown(
        """
        Explore potential betting edges based on matchups, player trends, and defensive weaknesses.
        This is meant for analysis purposes — always gamble responsibly.
        """
    )

    # Select game
    current_games = schedule_df[schedule_df['week'] == current_week].copy()
    if current_games.empty:
        st.warning(f"No games available for Week {current_week}")
    else:
        game_options = [f"{row['away_team']} @ {row['home_team']}" for _, row in current_games.iterrows()]
        selected_game = st.selectbox("Select Game", game_options)

        # Extract teams
        selected_row = current_games.iloc[game_options.index(selected_game)]
        away_team = selected_row['away_team']
        home_team = selected_row['home_team']

        st.markdown(f"### Analyzing {away_team} @ {home_team}")

        # Example: Weak defense check (reuse previous logic)
        def get_weak_defense_for_game(team, pos_list):
            pos_stats = stats_df[stats_df['position'].isin(pos_list)].copy()
            if pos_stats.empty:
                return pd.DataFrame()
            agg_dict = {}
            for col in ['passing_tds', 'rushing_tds', 'receiving_tds', 'passing_yards', 'rushing_yards', 'receiving_yards', 'fantasy_points_ppr']:
                if col in pos_stats.columns:
                    agg_dict[col] = 'sum'
            if not agg_dict:
                return pd.DataFrame()
            defense_stats = pos_stats.groupby('opponent_team').agg(agg_dict).reset_index()
            defense_stats.columns = ['Defense'] + [col.replace('_', ' ').title() for col in defense_stats.columns[1:]]
            if team in defense_stats['Defense'].values:
                return defense_stats[defense_stats['Defense'] == team]
            return pd.DataFrame()

        # Tabs within betting for offense/defense analysis
        betting_subtab = st.radio("View", ["Offensive Edges", "Player Props"], horizontal=True)

        if betting_subtab == "Offensive Edges":
            st.subheader("Offensive Matchup Edges")

            for pos_name, pos_codes in positions.items():
                weak_def = get_weak_defense_for_game(home_team, pos_codes)
                if not weak_def.empty:
                    st.markdown(f"**{away_team} {pos_name} vs {home_team}**")
                    st.dataframe(weak_def, use_container_width=True, hide_index=True)

                weak_def = get_weak_defense_for_game(away_team, pos_codes)
                if not weak_def.empty:
                    st.markdown(f"**{home_team} {pos_name} vs {away_team}**")
                    st.dataframe(weak_def, use_container_width=True, hide_index=True)

        elif betting_subtab == "Player Props":
            st.subheader("Player Prop Suggestions")

            # Example: top 5 players by fantasy points in matchup
            matchup_players = stats_df[
                (stats_df['team'].isin([home_team, away_team])) &
                (stats_df['week'] == current_week)
            ].copy()

            if matchup_players.empty:
                st.info("No player data available for this matchup")
            else:
                top_players = matchup_players.nlargest(5, 'fantasy_points_ppr') \
                                             [['player_display_name', 'team', 'position', 'fantasy_points_ppr']]
                st.dataframe(top_players, use_container_width=True, hide_index=True)

    # Render additional betting analysis (optional external function)
    try:
        render_betting_tab(sport="NFL", stats_df=stats_df, schedule_df=schedule_df)
    except Exception as e:
        st.error(f"Betting tab could not load fully: {e}")
