from __future__ import annotations

import io
from itertools import combinations
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="ФК Баранда статистика",
    layout="wide",
)


DATA_CANDIDATES = [
    Path("Fudbal Bezanija Termini.xlsx"),
    Path("Fudbal Bezanija Termini.csv"),
    Path("Fudbal Baranda Termini.xlsx"),
    Path("Fudbal Baranda Termini.csv"),
]

PLAYER_COL = "Player Name"
GAME_COL = "Date"
TEAM_COL = "Team"
POINTS_COL = "Points"
MINUTES_COL = "Minutes Played"

CORE_STATS = [
    "Goals",
    "Assists",
    "Big Chances Created",
    "Shots on Goal",
    "Total Shots",
    "Successful passes",
    "Unsuccessful passes",
    "Successful dribbles",
    "Unsuccessful dribbles",
    "Tackles Won",
    "Interceptions",
    "Blocks",
    "Saves",
    "Goals Conceded",
    "Corners Taken",
    "Hit Woodwork",
    "Own Goals",
]

RADAR_STATS = [
    "Goals per 60",
    "Assists per 60",
    "Big Chances Created per 60",
    "Shots on Goal per 60",
    "Successful passes per 60",
    "Successful dribbles per 60",
    "Tackles Won per 60",
    "Interceptions per 60",
]

LEADERBOARD_OPTIONS = {
    "Голови": "Goals",
    "Асистенције": "Assists",
    "Голови + асистенције": "Goal Contributions",
    "Бодови по термину": "Points per Game",
    "Шансе на 60 минута": "Big Chances Created per 60",
    "Голови на 60 минута": "Goals per 60",
    "Асистенције на 60 минута": "Assists per 60",
    "Прецизност паса": "Pass Accuracy",
    "Прецизност дриблинга": "Dribble Accuracy",
    "Освојени дуели": "Tackles Won",
    "Интерцепције": "Interceptions",
    "Одбране": "Saves",
}


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.9rem;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(49, 51, 63, 0.16);
        border-radius: 8px;
    }
    .fk-table-wrap {
        max-height: 560px;
        overflow: auto;
        border: 1px solid rgba(49, 51, 63, 0.16);
        border-radius: 8px;
    }
    .fk-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }
    .fk-table th {
        position: sticky;
        top: 0;
        z-index: 1;
        background: #f7f7f8;
        color: #1f2937;
        text-align: left;
        border-bottom: 1px solid rgba(49, 51, 63, 0.2);
        padding: 0.55rem 0.65rem;
        white-space: nowrap;
    }
    .fk-table td {
        border-bottom: 1px solid rgba(49, 51, 63, 0.1);
        padding: 0.45rem 0.65rem;
        white-space: nowrap;
    }
    .fk-table tr:nth-child(even) td {
        background: #fafafa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def existing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def safe_div(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.where(denominator != 0)
    return numerator.div(denominator)


def format_number(value: float | int | None, decimals: int = 0) -> str:
    if pd.isna(value):
        return "-"
    if decimals == 0:
        return f"{value:,.0f}".replace(",", ".")
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data(show_spinner=False)
def read_data(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    suffix = Path(file_name).suffix.lower()
    buffer = io.BytesIO(file_bytes)

    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(buffer)
    elif suffix == ".csv":
        df = pd.read_csv(buffer)
    else:
        raise ValueError("Подржани су Excel и CSV фајлови.")

    df.columns = [str(column).strip() for column in df.columns]
    if PLAYER_COL not in df.columns:
        raise ValueError(f"Недостаје колона '{PLAYER_COL}'.")

    numeric_candidates = existing_columns(df, CORE_STATS + [POINTS_COL, MINUTES_COL, "No."])
    for column in numeric_candidates:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    if GAME_COL in df.columns:
        parsed_dates = pd.to_datetime(df[GAME_COL], errors="coerce", dayfirst=True)
        df["Game Label"] = df[GAME_COL].astype(str)
        df["Game Sort"] = parsed_dates.fillna(pd.Timestamp("1900-01-01"))
    else:
        df["Game Label"] = "Термин " + (df.index + 1).astype(str)
        df["Game Sort"] = df.index

    df[PLAYER_COL] = df[PLAYER_COL].astype(str).str.strip()
    df = df[df[PLAYER_COL].ne("")]
    return df


def load_default_file() -> tuple[str, bytes] | None:
    for candidate in DATA_CANDIDATES:
        if candidate.exists():
            return candidate.name, candidate.read_bytes()
    return None


def add_accuracy_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if {"Successful passes", "Unsuccessful passes"}.issubset(df.columns):
        total_passes = df["Successful passes"] + df["Unsuccessful passes"]
        df["Total Passes"] = total_passes
        df["Pass Accuracy"] = safe_div(df["Successful passes"], total_passes) * 100

    if {"Successful dribbles", "Unsuccessful dribbles"}.issubset(df.columns):
        total_dribbles = df["Successful dribbles"] + df["Unsuccessful dribbles"]
        df["Total Dribbles"] = total_dribbles
        df["Dribble Accuracy"] = safe_div(df["Successful dribbles"], total_dribbles) * 100

    return df


def build_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        column
        for column in df.select_dtypes(include="number").columns
        if column not in ["No.", "Game Sort"]
    ]

    player_stats = df.groupby(PLAYER_COL, as_index=False)[numeric_cols].sum()
    games_played = df.groupby(PLAYER_COL).size().rename("Games Played").reset_index()
    player_stats = player_stats.merge(games_played, on=PLAYER_COL, how="left")

    if POINTS_COL in player_stats.columns:
        player_stats["Points per Game"] = (
            safe_div(player_stats[POINTS_COL], player_stats["Games Played"]).round(2)
        )

    if {"Goals", "Assists"}.issubset(player_stats.columns):
        player_stats["Goal Contributions"] = player_stats["Goals"] + player_stats["Assists"]

    if {"Successful passes", "Unsuccessful passes"}.issubset(player_stats.columns):
        total_passes = player_stats["Successful passes"] + player_stats["Unsuccessful passes"]
        player_stats["Total Passes"] = total_passes
        player_stats["Pass Accuracy"] = (
            safe_div(player_stats["Successful passes"], total_passes) * 100
        ).round(2)

    if {"Successful dribbles", "Unsuccessful dribbles"}.issubset(player_stats.columns):
        total_dribbles = (
            player_stats["Successful dribbles"] + player_stats["Unsuccessful dribbles"]
        )
        player_stats["Total Dribbles"] = total_dribbles
        player_stats["Dribble Accuracy"] = (
            safe_div(player_stats["Successful dribbles"], total_dribbles) * 100
        ).round(2)

    if MINUTES_COL in player_stats.columns:
        minutes = player_stats[MINUTES_COL]
        per_60_candidates = existing_columns(player_stats, CORE_STATS)
        for column in per_60_candidates:
            if column not in ["Unsuccessful passes", "Unsuccessful dribbles"]:
                player_stats[f"{column} per 60"] = (
                    safe_div(player_stats[column], minutes) * 60
                ).round(2)

    sort_col = "Goal Contributions" if "Goal Contributions" in player_stats.columns else "Games Played"
    return player_stats.sort_values(sort_col, ascending=False).reset_index(drop=True)


def apply_player_filters(
    player_stats: pd.DataFrame,
    min_games: int,
    min_minutes: int,
) -> pd.DataFrame:
    filtered = player_stats[player_stats["Games Played"] >= min_games]
    if MINUTES_COL in filtered.columns:
        filtered = filtered[filtered[MINUTES_COL] >= min_minutes]
    return filtered.copy()


def metric_card_grid(player_stats: pd.DataFrame, raw_df: pd.DataFrame) -> None:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Играчи", format_number(player_stats[PLAYER_COL].nunique()))
    c2.metric("Термини", format_number(raw_df["Game Label"].nunique()))
    if "Goals" in player_stats.columns:
        c3.metric("Голови", format_number(player_stats["Goals"].sum()))
    if "Assists" in player_stats.columns:
        c4.metric("Асистенције", format_number(player_stats["Assists"].sum()))
    if MINUTES_COL in player_stats.columns:
        c5.metric("Минути", format_number(player_stats[MINUTES_COL].sum()))


def make_top_bar(
    data: pd.DataFrame,
    metric: str,
    title: str,
    top_n: int = 10,
    color: str = "#2f7d59",
) -> go.Figure:
    top = (
        data[[PLAYER_COL, metric]]
        .dropna()
        .sort_values(metric, ascending=False)
        .head(top_n)
        .sort_values(metric)
    )
    fig = px.bar(
        top,
        x=metric,
        y=PLAYER_COL,
        orientation="h",
        text=metric,
        title=title,
        color_discrete_sequence=[color],
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=max(360, 34 * len(top) + 120),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=24, t=56, b=24),
    )
    return fig


def percentile_radar(player_stats: pd.DataFrame, player: str, min_games: int, min_minutes: int) -> go.Figure:
    radar_cols = existing_columns(player_stats, RADAR_STATS)
    filtered = apply_player_filters(player_stats, min_games, min_minutes)

    if not radar_cols or player not in filtered[PLAYER_COL].values:
        return go.Figure()

    percentiles = filtered[radar_cols].rank(pct=True).mul(100).round(1)
    percentiles[PLAYER_COL] = filtered[PLAYER_COL].values
    row = percentiles[percentiles[PLAYER_COL] == player].iloc[0]

    values = [row[column] for column in radar_cols]
    labels = [column.replace(" per 60", "") for column in radar_cols]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=player,
            line_color="#2f7d59",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], visible=True)),
        showlegend=False,
        height=520,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def comparison_chart(data: pd.DataFrame, players: list[str], metrics: list[str]) -> go.Figure:
    rows = data[data[PLAYER_COL].isin(players)][[PLAYER_COL] + metrics]
    long_df = rows.melt(id_vars=PLAYER_COL, var_name="Статистика", value_name="Вредност")
    fig = px.bar(
        long_df,
        x="Статистика",
        y="Вредност",
        color=PLAYER_COL,
        barmode="group",
        text_auto=".2s",
    )
    fig.update_layout(
        height=520,
        xaxis_title="",
        yaxis_title="",
        legend_title="Играч",
        margin=dict(l=8, r=8, t=24, b=24),
    )
    return fig


def points_to_win_value(points: float) -> float:
    if points == 3:
        return 1.0
    if points == 1:
        return 0.5
    return 0.0


@st.cache_data(show_spinner=False)
def build_same_team_heatmap(df: pd.DataFrame, min_games: int) -> pd.DataFrame:
    required = {GAME_COL, TEAM_COL, PLAYER_COL, POINTS_COL}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    pair_stats: dict[tuple[str, str], dict[str, float]] = {}
    players_per_game = df.groupby([GAME_COL, TEAM_COL])[PLAYER_COL].apply(list)
    points_per_game = df.groupby([GAME_COL, TEAM_COL])[POINTS_COL].first()
    players = sorted(df[PLAYER_COL].dropna().astype(str).unique())

    for key, player_list in players_per_game.items():
        win_value = points_to_win_value(points_per_game.loc[key])
        clean_players = sorted(set(str(player) for player in player_list))
        for p1, p2 in combinations(clean_players, 2):
            pair = tuple(sorted((p1, p2)))
            pair_stats.setdefault(pair, {"wins": 0.0, "games": 0.0})
            pair_stats[pair]["games"] += 1
            pair_stats[pair]["wins"] += win_value

    heatmap = pd.DataFrame(index=players, columns=players, dtype=float)
    for (p1, p2), stats in pair_stats.items():
        if stats["games"] >= min_games:
            win_pct = stats["wins"] / stats["games"] * 100
            heatmap.loc[p1, p2] = win_pct
            heatmap.loc[p2, p1] = win_pct

    valid = heatmap.notna().any(axis=1)
    return heatmap.loc[valid, valid]


@st.cache_data(show_spinner=False)
def build_opponent_heatmap(df: pd.DataFrame, min_games: int) -> pd.DataFrame:
    required = {GAME_COL, TEAM_COL, PLAYER_COL, POINTS_COL}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    pair_stats: dict[tuple[str, str], dict[str, float]] = {}
    players = sorted(df[PLAYER_COL].dropna().astype(str).unique())

    for game in df[GAME_COL].dropna().unique():
        game_df = df[df[GAME_COL] == game]
        teams = list(game_df[TEAM_COL].dropna().unique())

        if len(teams) != 2:
            continue

        team_1, team_2 = teams
        team_1_players = game_df[game_df[TEAM_COL] == team_1][PLAYER_COL].dropna().astype(str)
        team_2_players = game_df[game_df[TEAM_COL] == team_2][PLAYER_COL].dropna().astype(str)
        team_1_points = game_df[game_df[TEAM_COL] == team_1][POINTS_COL].iloc[0]
        team_2_points = game_df[game_df[TEAM_COL] == team_2][POINTS_COL].iloc[0]

        for player in team_1_players:
            for opponent in team_2_players:
                pair_stats.setdefault((player, opponent), {"wins": 0.0, "games": 0.0})
                pair_stats[(player, opponent)]["games"] += 1
                pair_stats[(player, opponent)]["wins"] += points_to_win_value(team_1_points)

        for player in team_2_players:
            for opponent in team_1_players:
                pair_stats.setdefault((player, opponent), {"wins": 0.0, "games": 0.0})
                pair_stats[(player, opponent)]["games"] += 1
                pair_stats[(player, opponent)]["wins"] += points_to_win_value(team_2_points)

    heatmap = pd.DataFrame(index=players, columns=players, dtype=float)
    for (player, opponent), stats in pair_stats.items():
        if stats["games"] >= min_games:
            heatmap.loc[player, opponent] = stats["wins"] / stats["games"] * 100

    valid_rows = heatmap.notna().any(axis=1)
    valid_cols = heatmap.notna().any(axis=0)
    return heatmap.loc[valid_rows, valid_cols]


def heatmap_figure(heatmap: pd.DataFrame, title: str, colorscale: str) -> go.Figure:
    fig = px.imshow(
        heatmap,
        text_auto=".0f",
        color_continuous_scale=colorscale,
        zmin=0,
        zmax=100,
        aspect="auto",
        labels=dict(color="Win %"),
        title=title,
    )
    fig.update_layout(
        height=max(520, 28 * len(heatmap.index) + 160),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=8, t=56, b=24),
    )
    return fig


def quadrant_chart(
    data: pd.DataFrame,
    x_metric: str,
    y_metric: str,
    size_metric: str,
    title: str,
) -> go.Figure:
    plot_df = data[[PLAYER_COL, x_metric, y_metric, size_metric, "Games Played"]].dropna()
    x_mean = plot_df[x_metric].mean()
    y_mean = plot_df[y_metric].mean()

    fig = px.scatter(
        plot_df,
        x=x_metric,
        y=y_metric,
        size=size_metric,
        hover_name=PLAYER_COL,
        text=PLAYER_COL,
        color="Games Played",
        color_continuous_scale="Viridis",
        title=title,
    )
    fig.update_traces(textposition="top center", marker=dict(opacity=0.78, line=dict(width=1)))
    fig.add_vline(x=x_mean, line_dash="dash", line_color="gray")
    fig.add_hline(y=y_mean, line_dash="dash", line_color="gray")
    fig.add_annotation(
        x=plot_df[x_metric].max(),
        y=plot_df[y_metric].max(),
        text="изнад просека у оба правца",
        showarrow=False,
        xanchor="right",
        yanchor="top",
    )
    fig.update_layout(
        height=640,
        margin=dict(l=8, r=8, t=56, b=24),
        xaxis_title=x_metric,
        yaxis_title=y_metric,
        coloraxis_colorbar_title="Термини",
    )
    return fig


def single_game_records(df: pd.DataFrame, stats: list[str]) -> pd.DataFrame:
    rows = []
    for stat in stats:
        if stat not in df.columns:
            continue

        max_value = df[stat].max()
        if pd.isna(max_value):
            continue

        record_rows = df[df[stat] == max_value]
        for _, row in record_rows.iterrows():
            rows.append(
                {
                    "Статистика": stat,
                    "Играч": row[PLAYER_COL],
                    "Вредност": max_value,
                    "Термин": row.get("Game Label", ""),
                    "Екипа": row.get(TEAM_COL, ""),
                }
            )
    return pd.DataFrame(rows)


def download_table_button(df: pd.DataFrame, label: str, file_name: str) -> None:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=label,
        data=csv,
        file_name=file_name,
        mime="text/csv",
        use_container_width=True,
    )


def show_table(
    data: pd.DataFrame,
    max_rows: int = 250,
    show_index: bool = False,
) -> None:
    display_df = data.copy()

    if len(display_df) > max_rows:
        st.caption(f"Приказано је првих {max_rows} редова од укупно {len(display_df)}.")
        display_df = display_df.head(max_rows)

    html = display_df.to_html(
        index=show_index,
        escape=True,
        border=0,
        classes="fk-table",
        na_rep="-",
    )
    st.markdown(f'<div class="fk-table-wrap">{html}</div>', unsafe_allow_html=True)


with st.sidebar:
    st.title("ФК Баранда")
    uploaded_file = st.file_uploader("Excel или CSV са статистиком", type=["xlsx", "xls", "csv"])

    default_file = load_default_file()
    if uploaded_file is not None:
        source_name = uploaded_file.name
        source_bytes = uploaded_file.getvalue()
    elif default_file is not None:
        source_name, source_bytes = default_file
        st.caption(f"Учитан фајл: {source_name}")
    else:
        source_name = ""
        source_bytes = b""


if not source_bytes:
    st.title("ФК Баранда статистика")
    st.info(
        "Додај Excel или CSV фајл кроз sidebar, или постави "
        "`Fudbal Bezanija Termini.xlsx` у исти фолдер као апликацију."
    )
    st.stop()


try:
    df = read_data(source_name, source_bytes)
except Exception as exc:
    st.error(f"Подаци нису могли да се учитају: {exc}")
    st.stop()


df = add_accuracy_columns(df)
player_stats = build_player_stats(df)

with st.sidebar:
    st.divider()
    page = st.radio(
        "Навигација",
        [
            "Преглед",
            "Профил играча",
            "Поређење играча",
            "Листе",
            "X-Y анализа",
            "Синергија",
            "Рекорди",
            "Подаци",
        ],
    )

    st.divider()
    st.caption("Филтери за анализе")
    default_min_minutes = 220 if MINUTES_COL in player_stats.columns else 0
    min_games = st.slider("Минимум термина", 1, int(player_stats["Games Played"].max()), 1)
    min_minutes = 0
    if MINUTES_COL in player_stats.columns:
        max_minutes = int(player_stats[MINUTES_COL].max())
        min_minutes = st.slider("Минимум минута", 0, max_minutes, min(default_min_minutes, max_minutes), step=10)


filtered_players = apply_player_filters(player_stats, min_games, min_minutes)
if filtered_players.empty:
    st.warning("Нема играча који пролазе тренутне филтере.")
    st.stop()


if page == "Преглед":
    st.title("Преглед сезоне")
    metric_card_grid(player_stats, df)

    st.subheader("Ко је носио игру")
    c1, c2 = st.columns(2)
    if "Goal Contributions" in filtered_players.columns:
        c1.plotly_chart(
            make_top_bar(filtered_players, "Goal Contributions", "Голови + асистенције"),
            use_container_width=True,
        )
    if "Points per Game" in filtered_players.columns:
        c2.plotly_chart(
            make_top_bar(filtered_players, "Points per Game", "Бодови по термину", color="#536dfe"),
            use_container_width=True,
        )

    table_cols = existing_columns(
        filtered_players,
        [
            PLAYER_COL,
            "Games Played",
            MINUTES_COL,
            "Goals",
            "Assists",
            "Goal Contributions",
            "Points per Game",
            "Pass Accuracy",
            "Dribble Accuracy",
        ],
    )
    st.subheader("Табела играча")
    show_table(
        filtered_players[table_cols].sort_values(
            "Goal Contributions" if "Goal Contributions" in table_cols else "Games Played",
            ascending=False,
        )
    )


elif page == "Профил играча":
    st.title("Профил играча")
    player = st.selectbox("Изабери играча", sorted(filtered_players[PLAYER_COL].unique()))
    row = player_stats[player_stats[PLAYER_COL] == player].iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    if "Goals" in row.index:
        c1.metric("Голови", format_number(row["Goals"]))
    if "Assists" in row.index:
        c2.metric("Асистенције", format_number(row["Assists"]))
    if "Goal Contributions" in row.index:
        c3.metric("Г + А", format_number(row["Goal Contributions"]))
    if "Points per Game" in row.index:
        c4.metric("Бодови/термин", format_number(row["Points per Game"], 2))
    c5.metric("Термини", format_number(row["Games Played"]))

    c1, c2 = st.columns([1.05, 0.95])
    with c1:
        st.subheader("Профил по percentile-у")
        fig = percentile_radar(player_stats, player, min_games, min_minutes)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нема довољно колона за radar приказ.")

    with c2:
        st.subheader("Кључне статистике")
        profile_cols = existing_columns(
            player_stats,
            [
                PLAYER_COL,
                "Games Played",
                MINUTES_COL,
                "Goals",
                "Assists",
                "Big Chances Created",
                "Shots on Goal",
                "Pass Accuracy",
                "Dribble Accuracy",
                "Tackles Won",
                "Interceptions",
                "Saves",
                "Goals Conceded",
            ],
        )
        show_table(
            player_stats[player_stats[PLAYER_COL] == player][profile_cols].T.rename(columns={row.name: "Вредност"}),
            show_index=True,
        )

    st.subheader("Учинак по термину")
    match_cols = existing_columns(
        df,
        [
            "Game Label",
            TEAM_COL,
            POINTS_COL,
            MINUTES_COL,
            "Goals",
            "Assists",
            "Big Chances Created",
            "Shots on Goal",
            "Successful passes",
            "Unsuccessful passes",
            "Pass Accuracy",
            "Successful dribbles",
            "Unsuccessful dribbles",
            "Dribble Accuracy",
            "Tackles Won",
            "Interceptions",
            "Saves",
            "Goals Conceded",
        ],
    )
    player_matches = df[df[PLAYER_COL] == player].sort_values("Game Sort")
    show_table(player_matches[match_cols])


elif page == "Поређење играча":
    st.title("Поређење играча")

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
        show_table(
            filtered_players[filtered_players[PLAYER_COL].isin(selected_players)][table_cols],
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
    show_table(
        filtered_players[ranking_cols].sort_values(selected_metric, ascending=False),
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
        show_table(records)


elif page == "Подаци":
    st.title("Подаци")
    tab_raw, tab_players = st.tabs(["Сви редови", "Агрегирано по играчу"])

    with tab_raw:
        show_table(df, max_rows=500)
        download_table_button(df, "Преузми све редове као CSV", "fk_baranda_svi_redovi.csv")

    with tab_players:
        show_table(player_stats, max_rows=500)
        download_table_button(player_stats, "Преузми табелу играча као CSV", "fk_baranda_igraci.csv")
