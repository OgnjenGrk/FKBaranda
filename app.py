    default_players = list(filtered_players[PLAYER_COL].head(2))
    selected_players = st.multiselect(
        "Изабери 2 до 4 играча",
        sorted(filtered_players[PLAYER_COL].unique()),
        default=default_players,
        max_selections=4,
    )

    compare_metrics = st.multiselect(
        "Статистике за поређење",
        existing_columns(filtered_players, list(LEADERBOARD_OPTIONS.values())),
        default=existing_columns(
            filtered_players,
            ["Goals", "Assists", "Big Chances Created per 60", "Pass Accuracy", "Tackles Won"],
        ),
    )

    if len(selected_players) < 2 or not compare_metrics:
        st.info("Изабери бар два играча и бар једну статистику.")
    else:
        st.plotly_chart(
            comparison_chart(filtered_players, selected_players, compare_metrics),
            use_container_width=True,
        )
        table_cols = [PLAYER_COL, "Games Played"] + existing_columns(filtered_players, [MINUTES_COL]) + compare_metrics
        st.dataframe(
            filtered_players[filtered_players[PLAYER_COL].isin(selected_players)][table_cols],
            use_container_width=True,
            hide_index=True,
        )


elif page == "Листе":
    st.title("Листе и рангирања")

    available_options = {
        label: metric
        for label, metric in LEADERBOARD_OPTIONS.items()
        if metric in filtered_players.columns
    }
    selected_label = st.selectbox("Статистика", list(available_options.keys()))
    selected_metric = available_options[selected_label]
    top_n = st.slider("Број играча", 5, min(30, len(filtered_players)), min(10, len(filtered_players)))

    st.plotly_chart(
        make_top_bar(filtered_players, selected_metric, selected_label, top_n=top_n),
        use_container_width=True,
    )

    ranking_cols = existing_columns(
        filtered_players,
        [PLAYER_COL, "Games Played", MINUTES_COL, selected_metric, "Goals", "Assists", "Points per Game"],
    )
    st.dataframe(
        filtered_players[ranking_cols].sort_values(selected_metric, ascending=False),
        use_container_width=True,
        hide_index=True,
    )


elif page == "X-Y анализа":
    st.title("X-Y анализа")

    numeric_analysis_cols = [
        column
        for column in filtered_players.select_dtypes(include="number").columns
        if column not in ["No."]
    ]

    default_x = "Pass Accuracy" if "Pass Accuracy" in numeric_analysis_cols else numeric_analysis_cols[0]
    default_y = (
        "Big Chances Created per 60"
        if "Big Chances Created per 60" in numeric_analysis_cols
        else numeric_analysis_cols[min(1, len(numeric_analysis_cols) - 1)]
    )
    default_size = MINUTES_COL if MINUTES_COL in numeric_analysis_cols else "Games Played"

    c1, c2, c3 = st.columns(3)
    x_metric = c1.selectbox("X оса", numeric_analysis_cols, index=numeric_analysis_cols.index(default_x))
    y_metric = c2.selectbox("Y оса", numeric_analysis_cols, index=numeric_analysis_cols.index(default_y))
    size_metric = c3.selectbox("Величина тачке", numeric_analysis_cols, index=numeric_analysis_cols.index(default_size))

    st.plotly_chart(
        quadrant_chart(
            filtered_players,
            x_metric,
            y_metric,
            size_metric,
            f"{x_metric} vs {y_metric}",
        ),
        use_container_width=True,
    )


elif page == "Синергија":
    st.title("Синергија и дуели")

    required = {GAME_COL, TEAM_COL, PLAYER_COL, POINTS_COL}
    missing = sorted(required.difference(df.columns))
    if missing:
        st.info("За ову анализу недостају колоне: " + ", ".join(missing))
    else:
        min_pair_games = st.slider("Минимум заједничких термина", 1, 10, 3)
        tab_same, tab_opp = st.tabs(["Иста екипа", "Играч против играча"])

        with tab_same:
            same_heatmap = build_same_team_heatmap(df, min_pair_games)
            if same_heatmap.empty:
                st.info("Нема парова који пролазе задати минимум.")
            else:
                st.plotly_chart(
                    heatmap_figure(
                        same_heatmap,
                        "Проценат победа када играчи играју заједно",
                        "RdYlGn",
                    ),
                    use_container_width=True,
                )

        with tab_opp:
            opp_heatmap = build_opponent_heatmap(df, min_pair_games)
            if opp_heatmap.empty:
                st.info("Нема дуела који пролазе задати минимум.")
            else:
                st.plotly_chart(
                    heatmap_figure(
                        opp_heatmap,
                        "Проценат победа играча против конкретног противника",
                        "RdBu",
                    ),
                    use_container_width=True,
                )


elif page == "Рекорди":
    st.title("Рекорди на једном термину")

    record_stats = st.multiselect(
        "Статистике",
        existing_columns(df, CORE_STATS + [POINTS_COL]),
        default=existing_columns(
            df,
            [
                "Goals",
                "Assists",
                "Big Chances Created",
                "Total Shots",
                "Saves",
                "Blocks",
                "Successful passes",
                "Successful dribbles",
                "Tackles Won",
                "Interceptions",
            ],
        ),
    )

    records = single_game_records(df, record_stats)
    if records.empty:
        st.info("Нема доступних рекорда за изабране статистике.")
    else:
        st.dataframe(records, use_container_width=True, hide_index=True)


elif page == "Подаци":
    st.title("Подаци")
    tab_raw, tab_players = st.tabs(["Сви редови", "Агрегирано по играчу"])

    with tab_raw:
        st.dataframe(df, use_container_width=True, hide_index=True)
        download_table_button(df, "Преузми све редове као CSV", "fk_baranda_svi_redovi.csv")

    with tab_players:
        st.dataframe(player_stats, use_container_width=True, hide_index=True)
        download_table_button(player_stats, "Преузми табелу играча као CSV", "fk_baranda_igraci.csv")