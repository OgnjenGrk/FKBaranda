from __future__ import annotations

import io
from itertools import combinations
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="ФК Баранда статистика",
    layout="wide",
)


TERMINI_DATA_CANDIDATES = [
    Path(r"C:\Users\beoog\Desktop\Fudbal Bezanija\Sajt\Fudbal Bezanija Termini.xlsx"),
    Path("Fudbal Bezanija Termini.xlsx"),
    Path("Fudbal Bezanija Termini.csv"),
    Path("Fudbal Baranda Termini.xlsx"),
    Path("Fudbal Baranda Termini.csv"),
]

GOALS_DATA_CANDIDATES = [
    Path(r"C:\Users\beoog\Desktop\Fudbal Bezanija\Sajt\Fudbal Bezanija Golovi.xlsx"),
    Path("Fudbal Bezanija Golovi.xlsx"),
    Path("Fudbal Bezanija Golovi.csv"),
    Path("Fudbal Baranda Golovi.xlsx"),
    Path("Fudbal Baranda Golovi.csv"),
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
    "Goal Contributions per 60",
    "Big Chances Created per 60",
    "Shots on Goal per 60",
    "Successful passes per 60",
    "Successful dribbles per 60",
    "Tackles Won per 60",
    "Interceptions per 60",
]

LEADERBOARD_OPTIONS = {
    "Голови на 60 минута": "Goals per 60",
    "Асистенције на 60 минута": "Assists per 60",
    "Голови + асистенције на 60 минута": "Goal Contributions per 60",
    "Велике шансе на 60 минута": "Big Chances Created per 60",
    "Шутеви у оквир на 60 минута": "Shots on Goal per 60",
    "Додавања на 60 минута": "Total Passes per 60",
    "Успешна додавања на 60 минута": "Successful passes per 60",
    "Дриблинзи на 60 минута": "Total Dribbles per 60",
    "Успешни дриблинзи на 60 минута": "Successful dribbles per 60",
    "Освојени дуели на 60 минута": "Tackles Won per 60",
    "Пресечене лопте на 60 минута": "Interceptions per 60",
    "Блокаде на 60 минута": "Blocks per 60",
    "Одбране на 60 минута": "Saves per 60",
    "Прецизност паса": "Pass Accuracy",
    "Прецизност дриблинга": "Dribble Accuracy",
    "Бодови по термину": "Points per Game",
    "Укупно голова": "Goals",
    "Укупно асистенција": "Assists",
}

DISPLAY_LABELS = {
    "No.": "Бр.",
    GAME_COL: "Датум",
    "Game Label": "Термин",
    "Game Sort": "Сортирање термина",
    TEAM_COL: "Екипа",
    PLAYER_COL: "Играч",
    "Events": "Догађаји",
    "Left F. Goals": "Голови левом ногом",
    "Right F. Goals": "Голови десном ногом",
    "Header Goals": "Голови главом",
    "Body Goals": "Голови телом",
    "Goals": "Голови",
    "Assists": "Асистенције",
    "Goal Contributions": "Голови + асистенције",
    "Big Chances Created": "Велике шансе",
    "Shots on Goal": "Шутеви у оквир",
    "Hit Woodwork": "Погођен оквир гола",
    "Shots off Goal": "Шутеви ван оквира",
    "Blocked Shots": "Блокирани шутеви",
    "Total Shots": "Укупно шутева",
    "Blocks": "Блокаде",
    "Successful passes": "Успешна додавања",
    "Unsuccessful passes": "Неуспешна додавања",
    "Total Passes": "Укупно додавања",
    "Pass Accuracy": "Прецизност паса (%)",
    "Successful dribbles": "Успешни дриблинзи",
    "Unsuccessful dribbles": "Неуспешни дриблинзи",
    "Total Dribbles": "Укупно дриблинга",
    "Dribble Accuracy": "Прецизност дриблинга (%)",
    "Tackles Won": "Освојени дуели",
    "Interceptions": "Пресечене лопте",
    "Fouls Against": "Фаулови над играчем",
    "Fouls": "Направљени фаулови",
    "Saves": "Одбране",
    "Goals Conceded": "Примљени голови",
    "Corners Taken": "Изведени корнери",
    "Own Goals": "Аутоголови",
    "Penalties Taken": "Изведени пенали",
    "Penalties scored": "Постигнути пенали",
    POINTS_COL: "Бодови",
    MINUTES_COL: "Минути",
    "Games Played": "Термини",
    "Points per Game": "Бодови по термину",
    "Goals per 60": "Голови на 60 мин",
    "Assists per 60": "Асистенције на 60 мин",
    "Goal Contributions per 60": "Голови + асистенције на 60 мин",
    "Big Chances Created per 60": "Велике шансе на 60 мин",
    "Shots on Goal per 60": "Шутеви у оквир на 60 мин",
    "Total Shots per 60": "Шутеви на 60 мин",
    "Successful passes per 60": "Успешна додавања на 60 мин",
    "Total Passes per 60": "Додавања на 60 мин",
    "Successful dribbles per 60": "Успешни дриблинзи на 60 мин",
    "Total Dribbles per 60": "Дриблинзи на 60 мин",
    "Tackles Won per 60": "Освојени дуели на 60 мин",
    "Interceptions per 60": "Пресечене лопте на 60 мин",
    "Blocks per 60": "Блокаде на 60 мин",
    "Saves per 60": "Одбране на 60 мин",
    "Goals Conceded per 60": "Примљени голови на 60 мин",
    "Corners Taken per 60": "Изведени корнери на 60 мин",
    "Hit Woodwork per 60": "Погођен оквир гола на 60 мин",
    "Own Goals per 60": "Аутоголови на 60 мин",
    "Goalscorer": "Стрелац",
    "Goalkeeper": "Голман",
    "Assist": "Асистент",
    "Scored with": "Постигнуто",
    "Goal Method": "Начин гола",
    "Minute": "Минут",
    "Black/Colored": "Црни/обојени",
    "White/Bibs": "Бели/маркери",
    "Goal Count": "Број голова",
    "Goal Order": "Редослед гола",
    "Minute Interval": "Интервал",
    "Minute Bin": "Интервал",
    "Просечан_минут": "Просечан минут",
    "Најранији_гол": "Најранији гол",
    "Најкаснији_гол": "Најкаснији гол",
    "Голови_0_10": "Голови 0-10",
    "Голови_50_plus": "Голови 50+",
}

PLAYER_NAME_OVERRIDES = {
    "Drug Tegijev": "Друг Тегијев",
    "Drug Tegijev Marko": "Друг Тегијев Марко",
    "Dusan Bubanjin": "Душан Бубањин",
    "Filip Lazovic": "Филип Лазовић",
    "Ivan Apostolski": "Иван Апостолски",
    "Ivan Filipovic": "Иван Филиповић",
    "Lazar Petrovic": "Лазар Петровић",
    "Luka Ilic": "Лука Илић",
    "Luka Peric": "Лука Перић",
    "Marko Radulovic": "Марко Радуловић",
    "Marko Tegeltija": "Марко Тегелтија",
    "Mihajlo Jovanovic": "Михајло Јовановић",
    "Miljan Jovanovic": "Миљан Јовановић",
    "Nenad": "Ненад",
    "Nepoznat 1": "Непознат 1",
    "Nepoznat 2": "Непознат 2",
    "Nepoznat 3": "Непознат 3",
    "Nikola Nikolic": "Никола Николић",
    "Nikola Prtenjaca": "Никола Пртењача",
    "Ognjen Bubanja": "Огњен Бубања",
    "Ognjen Bubanja (golman)": "Огњен Бубања (голман)",
    "Ognjen Grkinic": "Огњен Гркинић",
    "Slobodan Sobat": "Слободан Шобат",
    "Stefan Lazovic": "Стефан Лазовић",
    "Stevan Lacmanovic": "Стеван Лаћмановић",
    "Strahinja Milovanovic": "Страхиња Миловановић",
    "Vanijev Burazer": "Ванијев Буразер",
    "Viktor Joldzic": "Виктор Џолџић",
    "~Viktor 2 (Bubanjin)": "~Виктор 2 (Бубањин)",
    "Right Foot": "Десна нога",
    "Left Foot": "Лева нога",
    "Header": "Глава",
    "Body": "Тело",
}

TEAM_LABELS = {
    "Black": "Црни",
    "Colored": "Обојени",
    "White": "Бели",
    "Bibs": "Маркери",
}

LATIN_DIGRAPHS = {
    "dž": "џ",
    "lj": "љ",
    "nj": "њ",
}

LATIN_TO_CYRILLIC = {
    "a": "а",
    "b": "б",
    "c": "ц",
    "č": "ч",
    "ć": "ћ",
    "d": "д",
    "đ": "ђ",
    "e": "е",
    "f": "ф",
    "g": "г",
    "h": "х",
    "i": "и",
    "j": "ј",
    "k": "к",
    "l": "л",
    "m": "м",
    "n": "н",
    "o": "о",
    "p": "п",
    "r": "р",
    "s": "с",
    "š": "ш",
    "t": "т",
    "u": "у",
    "v": "в",
    "z": "з",
    "ž": "ж",
}

CYRILLIC_CHARS = set("АБВГДЂЕЖЗИЈКЛЉМНЊОПРСТЋУФХЦЧЏШабвгдђежзијклљмнњопрстћуфхцчџш")


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
    existing = []
    seen = set()
    for column in columns:
        if column in df.columns and column not in seen:
            existing.append(column)
            seen.add(column)
    return existing


def safe_div(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.where(denominator != 0)
    return numerator.div(denominator)


def format_number(value: float | int | None, decimals: int = 0) -> str:
    if pd.isna(value):
        return "-"
    if decimals == 0:
        return f"{value:,.0f}".replace(",", ".")
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_game_dates(values: pd.Series) -> pd.Series:
    raw_values = values.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    ymd_dates = pd.to_datetime(raw_values, format="%Y%m%d", errors="coerce")
    generic_dates = pd.to_datetime(raw_values.where(ymd_dates.isna()), errors="coerce", dayfirst=True)
    return ymd_dates.fillna(generic_dates)


def format_timestamp(value: pd.Timestamp) -> str:
    return f"{value.day}. {value.month}. {value.year}."


def format_date_value(value: object) -> str:
    parsed = parse_game_dates(pd.Series([value])).iloc[0]
    if pd.isna(parsed):
        return str(value).strip()
    return format_timestamp(parsed)


def format_game_labels(values: pd.Series, fallback_prefix: str) -> pd.Series:
    parsed_dates = parse_game_dates(values)
    raw_labels = values.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    labels = [
        format_timestamp(parsed) if pd.notna(parsed) else raw_label
        for raw_label, parsed in zip(raw_labels, parsed_dates)
    ]
    fallback = fallback_prefix + " " + pd.Series(range(1, len(values) + 1), index=values.index).astype(str)
    has_label = raw_labels.ne("") & raw_labels.str.lower().ne("nan")
    return pd.Series(labels, index=values.index).where(has_label, fallback)


def match_cyrillic_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement.upper()
    return replacement


def serbian_latin_to_cyrillic(text: str) -> str:
    result = []
    index = 0
    while index < len(text):
        two_chars = text[index : index + 2]
        digraph = LATIN_DIGRAPHS.get(two_chars.lower())
        if digraph:
            result.append(match_cyrillic_case(two_chars, digraph))
            index += 2
            continue

        char = text[index]
        replacement = LATIN_TO_CYRILLIC.get(char.lower())
        result.append(match_cyrillic_case(char, replacement) if replacement else char)
        index += 1
    return "".join(result)


def transliterate_person_name(value: object) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()
    if not text:
        return ""

    if text in PLAYER_NAME_OVERRIDES:
        return PLAYER_NAME_OVERRIDES[text]

    if text.startswith("OG - "):
        return "Аутогол - " + transliterate_person_name(text[5:])

    if any(char in CYRILLIC_CHARS for char in text):
        return text

    return serbian_latin_to_cyrillic(text)


def display_label(column: str) -> str:
    if column in DISPLAY_LABELS:
        return DISPLAY_LABELS[column]
    if column.endswith(" per 60"):
        base = column.removesuffix(" per 60")
        return f"{display_label(base)} на 60 мин"
    return column.replace("_", " ")


def display_labels(columns: list[str]) -> dict[str, str]:
    return {column: display_label(column) for column in columns}


def localize_people_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for column in existing_columns(df, columns):
        df[column] = df[column].apply(transliterate_person_name)
    return df


def localize_team_values(df: pd.DataFrame) -> pd.DataFrame:
    if TEAM_COL not in df.columns:
        return df

    df = df.copy()
    df[TEAM_COL] = df[TEAM_COL].apply(lambda value: TEAM_LABELS.get(str(value).strip(), str(value).strip()))
    return df


def prepare_display_table(data: pd.DataFrame, show_index: bool = False) -> pd.DataFrame:
    display_df = data.copy()

    for column in existing_columns(display_df, [PLAYER_COL, "Goalscorer", "Goalkeeper", "Assist"]):
        display_df[column] = display_df[column].apply(transliterate_person_name)

    if TEAM_COL in display_df.columns:
        display_df[TEAM_COL] = display_df[TEAM_COL].apply(
            lambda value: TEAM_LABELS.get(str(value).strip(), str(value).strip())
        )

    for column in existing_columns(display_df, [GAME_COL]):
        display_df[column] = display_df[column].apply(format_date_value)

    if "Scored with" in display_df.columns:
        display_df["Scored with"] = display_df["Scored with"].apply(normalize_goal_method)

    display_df = display_df.rename(columns=display_labels(list(display_df.columns)))
    if show_index:
        display_df.index = [display_label(str(index_value)) for index_value in display_df.index]
    return display_df


def normalize_goal_method(value: object) -> str:
    if pd.isna(value):
        return "Непознато"

    text = str(value).strip()
    if not text:
        return "Непознато"

    lowered = text.lower()
    if "right" in lowered:
        return "Десна нога"
    if "left" in lowered:
        return "Лева нога"
    if "header" in lowered or "head" in lowered:
        return "Глава"
    if "body" in lowered:
        return "Тело"
    if "own" in lowered:
        return "Аутогол"

    try:
        float(text)
    except ValueError:
        return text
    return "Непознато"


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
        raise ValueError("Недостаје колона са именом играча.")

    numeric_candidates = existing_columns(df, CORE_STATS + [POINTS_COL, MINUTES_COL, "No."])
    for column in numeric_candidates:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    if GAME_COL in df.columns:
        parsed_dates = parse_game_dates(df[GAME_COL])
        df["Game Label"] = format_game_labels(df[GAME_COL], "Термин")
        df["Game Sort"] = parsed_dates.fillna(pd.Timestamp("1900-01-01"))
    else:
        df["Game Label"] = "Термин " + (df.index + 1).astype(str)
        df["Game Sort"] = df.index

    df[PLAYER_COL] = df[PLAYER_COL].astype(str).str.strip()
    df = df[df[PLAYER_COL].ne("")]
    df = localize_people_columns(df, [PLAYER_COL])
    df = localize_team_values(df)
    return df


@st.cache_data(show_spinner=False)
def read_goal_data(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    suffix = Path(file_name).suffix.lower()
    buffer = io.BytesIO(file_bytes)

    if suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(buffer)
    elif suffix == ".csv":
        df = pd.read_csv(buffer)
    else:
        raise ValueError("Подржани су Excel и CSV фајлови.")

    df.columns = [str(column).strip() for column in df.columns]
    if "Goalscorer" not in df.columns:
        raise ValueError("Недостаје колона са стрелцем у фајлу са головима.")

    text_columns = ["Team", "Goalscorer", "Goalkeeper", "Assist", "Scored with"]
    for column in existing_columns(df, text_columns):
        df[column] = df[column].fillna("").astype(str).str.strip()

    numeric_columns = existing_columns(
        df,
        ["No.", "Minute", "Black/Colored", "White/Bibs", "Goal Count"],
    )
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if "Scored with" in df.columns:
        df["Goal Method"] = df["Scored with"].apply(normalize_goal_method)

    if GAME_COL in df.columns:
        parsed_dates = parse_game_dates(df[GAME_COL])
        df["Game Label"] = format_game_labels(df[GAME_COL], "Термин")
        df["Game Sort"] = parsed_dates.fillna(pd.Timestamp("1900-01-01"))
    else:
        df["Game Label"] = "Гол " + (df.index + 1).astype(str)
        df["Game Sort"] = df.index

    df = df[df["Goalscorer"].ne("")]
    df = localize_people_columns(df, ["Goalscorer", "Goalkeeper", "Assist"])
    df = localize_team_values(df)
    return df


def load_default_file(candidates: list[Path]) -> tuple[str, bytes] | None:
    for candidate in candidates:
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
        if column not in ["No.", GAME_COL, "Game Sort"]
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
        if "Goal Contributions" in player_stats.columns:
            player_stats["Goal Contributions per 60"] = (
                safe_div(player_stats["Goal Contributions"], minutes) * 60
            ).round(2)
        if "Total Passes" in player_stats.columns:
            player_stats["Total Passes per 60"] = (
                safe_div(player_stats["Total Passes"], minutes) * 60
            ).round(2)
        if "Total Dribbles" in player_stats.columns:
            player_stats["Total Dribbles per 60"] = (
                safe_div(player_stats["Total Dribbles"], minutes) * 60
            ).round(2)

        per_60_candidates = existing_columns(player_stats, CORE_STATS)
        for column in per_60_candidates:
            if column not in ["Unsuccessful passes", "Unsuccessful dribbles"]:
                player_stats[f"{column} per 60"] = (
                    safe_div(player_stats[column], minutes) * 60
                ).round(2)

    sort_col = (
        "Goal Contributions per 60"
        if "Goal Contributions per 60" in player_stats.columns
        else "Goal Contributions"
        if "Goal Contributions" in player_stats.columns
        else "Games Played"
    )
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
        labels=display_labels([PLAYER_COL, metric]),
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
    labels = [display_label(column) for column in radar_cols]

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
    long_df["Статистика"] = long_df["Статистика"].map(display_label)
    fig = px.bar(
        long_df,
        x="Статистика",
        y="Вредност",
        color=PLAYER_COL,
        barmode="group",
        text_auto=".2s",
        labels={PLAYER_COL: "Играч"},
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
        labels=dict(color="Победе %"),
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
        labels=display_labels([PLAYER_COL, x_metric, y_metric, size_metric, "Games Played"]),
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
        xaxis_title=display_label(x_metric),
        yaxis_title=display_label(y_metric),
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
                    "Статистика": display_label(stat),
                    "Играч": row[PLAYER_COL],
                    "Вредност": max_value,
                    "Термин": row.get("Game Label", ""),
                    "Екипа": row.get(TEAM_COL, ""),
                }
            )
    return pd.DataFrame(rows)


def download_table_button(df: pd.DataFrame, label: str, file_name: str) -> None:
    csv = prepare_display_table(df).to_csv(index=False).encode("utf-8-sig")
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

    display_df = prepare_display_table(display_df, show_index=show_index)
    if show_index and display_df.index.name is None:
        display_df.index.name = "Статистика"

    html = display_df.to_html(
        index=show_index,
        escape=True,
        border=0,
        classes="fk-table",
        na_rep="-",
    )
    table_height = min(590, max(150, 42 * (len(display_df) + 1)))
    components.html(
        f"""
        <style>
        body {{
            margin: 0;
            font-family: "Source Sans Pro", sans-serif;
        }}
        .fk-table-wrap {{
            max-height: 560px;
            overflow: auto;
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 8px;
        }}
        .fk-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        .fk-table thead th {{
            position: sticky;
            top: 0;
            z-index: 1;
            background: #f7f7f8;
            color: #1f2937;
            text-align: left;
            border-bottom: 1px solid rgba(49, 51, 63, 0.2);
            padding: 0.55rem 0.65rem;
            white-space: nowrap;
        }}
        .fk-table thead th.sortable {{
            cursor: pointer;
            user-select: none;
        }}
        .fk-table thead th.sortable:hover {{
            background: #eceff3;
        }}
        .fk-table td,
        .fk-table tbody th {{
            border-bottom: 1px solid rgba(49, 51, 63, 0.1);
            padding: 0.45rem 0.65rem;
            white-space: nowrap;
        }}
        .fk-table tbody th {{
            color: #1f2937;
            font-weight: 600;
            text-align: left;
        }}
        .fk-table tbody tr:nth-child(even) td,
        .fk-table tbody tr:nth-child(even) th {{
            background: #fafafa;
        }}
        .sort-arrows {{
            margin-left: 0.35rem;
            color: #6b7280;
            font-size: 0.72rem;
            letter-spacing: 0;
        }}
        .fk-table th.sorted-desc .sort-arrows,
        .fk-table th.sorted-asc .sort-arrows {{
            color: #111827;
        }}
        </style>
        <div class="fk-table-wrap">{html}</div>
        <script>
        const table = document.querySelector(".fk-table");

        function normalizeValue(text) {{
            const value = text.trim();
            if (!value || value === "-") {{
                return {{ kind: "empty", value: "" }};
            }}

            const dateMatch = value.match(/^(\\d{{1,2}})\\.\\s*(\\d{{1,2}})\\.\\s*(\\d{{4}})\\.$/);
            if (dateMatch) {{
                const day = Number(dateMatch[1]);
                const month = Number(dateMatch[2]) - 1;
                const year = Number(dateMatch[3]);
                return {{ kind: "number", value: new Date(year, month, day).getTime() }};
            }}

            const numberCandidate = value.replace(/\\./g, "").replace(",", ".");
            if (/^-?\\d+(\\.\\d+)?$/.test(numberCandidate)) {{
                return {{ kind: "number", value: Number(numberCandidate) }};
            }}

            return {{ kind: "text", value: value.toLocaleLowerCase("sr") }};
        }}

        function compareCells(a, b, direction) {{
            const aValue = normalizeValue(a.textContent);
            const bValue = normalizeValue(b.textContent);

            if (aValue.kind === "empty" && bValue.kind !== "empty") return 1;
            if (bValue.kind === "empty" && aValue.kind !== "empty") return -1;

            let result = 0;
            if (aValue.kind === "number" && bValue.kind === "number") {{
                result = aValue.value - bValue.value;
            }} else {{
                result = String(aValue.value).localeCompare(String(bValue.value), "sr");
            }}
            return direction === "desc" ? -result : result;
        }}

        if (table) {{
            const headers = Array.from(table.querySelectorAll("thead th"));
            const body = table.querySelector("tbody");

            headers.forEach((header, columnIndex) => {{
                const label = header.textContent.trim() || "Статистика";
                header.classList.add("sortable");
                header.innerHTML = `<span>${{label}}</span><span class="sort-arrows">▲▼</span>`;
                header.dataset.sortDirection = "";

                header.addEventListener("click", () => {{
                    const nextDirection = header.dataset.sortDirection === "desc" ? "asc" : "desc";
                    headers.forEach((otherHeader) => {{
                        otherHeader.dataset.sortDirection = "";
                        otherHeader.classList.remove("sorted-desc", "sorted-asc");
                    }});
                    header.dataset.sortDirection = nextDirection;
                    header.classList.add(nextDirection === "desc" ? "sorted-desc" : "sorted-asc");

                    const rows = Array.from(body.querySelectorAll("tr"));
                    rows.sort((rowA, rowB) => {{
                        const cellA = rowA.children[columnIndex];
                        const cellB = rowB.children[columnIndex];
                        return compareCells(cellA, cellB, nextDirection);
                    }});
                    rows.forEach((row) => body.appendChild(row));
                }});
            }});
        }}
        </script>
        """,
        height=table_height,
        scrolling=False,
    )


def count_by_column(df: pd.DataFrame, column: str, value_name: str) -> pd.DataFrame:
    if column not in df.columns:
        return pd.DataFrame(columns=[column, value_name])

    filtered = df[df[column].fillna("").astype(str).str.strip().ne("")]
    if filtered.empty:
        return pd.DataFrame(columns=[column, value_name])

    return (
        filtered.groupby(column)
        .size()
        .rename(value_name)
        .reset_index()
        .sort_values(value_name, ascending=False)
    )


def goal_count_bar(
    data: pd.DataFrame,
    name_col: str,
    value_col: str,
    title: str,
    color: str,
    top_n: int = 12,
) -> go.Figure:
    top = data.head(top_n).sort_values(value_col)
    fig = px.bar(
        top,
        x=value_col,
        y=name_col,
        orientation="h",
        text=value_col,
        title=title,
        labels=display_labels([name_col, value_col]),
        color_discrete_sequence=[color],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=max(360, 34 * len(top) + 120),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=24, t=56, b=24),
    )
    return fig


def goal_timeline_figure(goal_rows: pd.DataFrame) -> go.Figure:
    plot_df = goal_rows.copy()
    symbol_col = "Goal Method" if "Goal Method" in plot_df.columns else "Scored with" if "Scored with" in plot_df.columns else None
    hover_cols = existing_columns(
        plot_df,
        ["Goalscorer", "Assist", "Goalkeeper", "Goal Method", "Black/Colored", "White/Bibs"],
    )

    if "Minute" not in plot_df.columns or plot_df["Minute"].isna().all():
        plot_df["Goal Order"] = range(1, len(plot_df) + 1)
        x_col = "Goal Order"
    else:
        x_col = "Minute"

    plot_df["Goal Marker Size"] = 12
    fig = px.scatter(
        plot_df.sort_values(x_col),
        x=x_col,
        y="Goalscorer",
        color="Team" if "Team" in plot_df.columns else None,
        symbol=symbol_col,
        size="Goal Marker Size",
        hover_data=hover_cols,
        title="Ток голова на термину",
        labels=display_labels(
            ["Goalscorer", "Assist", "Goalkeeper", "Goal Method", "Team", x_col, "Goal Marker Size"]
        ),
    )
    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1)))
    fig.update_layout(
        height=max(420, 28 * plot_df["Goalscorer"].nunique() + 160),
        xaxis_title="Минут" if x_col == "Minute" else "Редослед гола",
        yaxis_title="Стрелац",
        margin=dict(l=8, r=8, t=56, b=24),
    )
    return fig


def goals_with_minutes(goals: pd.DataFrame) -> pd.DataFrame:
    if "Minute" not in goals.columns:
        return pd.DataFrame(columns=list(goals.columns) + ["Minute"])

    minute_df = goals.copy()
    minute_df["Minute"] = pd.to_numeric(minute_df["Minute"], errors="coerce")
    return minute_df.dropna(subset=["Minute"])


def minute_bins(max_minute: float, bin_size: int) -> list[int]:
    safe_max = int(max(70, max_minute if pd.notna(max_minute) else 70))
    upper = ((safe_max // bin_size) + 1) * bin_size
    return list(range(0, upper + bin_size, bin_size))


def add_minute_intervals(
    goals: pd.DataFrame,
    bin_size: int,
    column_name: str = "Minute Interval",
) -> pd.DataFrame:
    minute_df = goals_with_minutes(goals)
    if minute_df.empty:
        minute_df[column_name] = pd.Series(dtype="category")
        return minute_df

    bins = minute_bins(minute_df["Minute"].max(), bin_size)
    labels = [f"{start}-{end}" for start, end in zip(bins[:-1], bins[1:])]
    minute_df[column_name] = pd.cut(
        minute_df["Minute"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True,
    )
    return minute_df


def minute_histogram_figure(goals: pd.DataFrame, bin_size: int) -> go.Figure:
    minute_df = goals_with_minutes(goals)
    bins = minute_bins(minute_df["Minute"].max(), bin_size)

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=minute_df["Minute"],
            xbins=dict(start=bins[0], end=bins[-1], size=bin_size),
            marker_color="#4f46e5",
            marker_line=dict(color="#111827", width=1),
            opacity=0.82,
        )
    )
    fig.update_layout(
        title="Расподела постигнутих голова по минутима",
        height=470,
        bargap=0.04,
        xaxis_title="Минут",
        yaxis_title="Број голова",
        margin=dict(l=8, r=8, t=56, b=24),
    )
    fig.update_xaxes(range=[0, bins[-1]], dtick=max(5, bin_size))
    return fig


def interval_donut_figure(goals: pd.DataFrame, bin_size: int = 10) -> tuple[go.Figure, pd.DataFrame]:
    interval_df = add_minute_intervals(goals, bin_size)
    counts = (
        interval_df["Minute Interval"]
        .value_counts(dropna=False)
        .sort_index()
        .rename("Голови")
        .reset_index()
        .rename(columns={"Minute Interval": "Интервал"})
    )
    counts = counts[counts["Голови"] > 0]

    fig = px.pie(
        counts,
        names="Интервал",
        values="Голови",
        title="Расподела голова по интервалима",
        hole=0.42,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=470, margin=dict(l=8, r=8, t=56, b=24))
    return fig, counts


def player_minute_heatmap_figure(
    goals: pd.DataFrame,
    min_goals: int,
    bin_size: int,
) -> tuple[go.Figure, pd.DataFrame]:
    interval_df = add_minute_intervals(goals, bin_size, "Minute Bin")
    scorer_counts = interval_df["Goalscorer"].value_counts()
    selected_scorers = scorer_counts[scorer_counts >= min_goals].index
    interval_df = interval_df[interval_df["Goalscorer"].isin(selected_scorers)]

    if interval_df.empty:
        return go.Figure(), pd.DataFrame()

    heatmap = pd.crosstab(interval_df["Goalscorer"], interval_df["Minute Bin"])
    heatmap = heatmap.loc[heatmap.sum(axis=1).sort_values(ascending=False).index]
    fig = px.imshow(
        heatmap,
        text_auto=True,
        color_continuous_scale="Inferno",
        aspect="auto",
        labels=dict(color="Голови"),
        title="Кад који играч постиже голове",
    )
    fig.update_layout(
        height=max(480, 32 * len(heatmap.index) + 150),
        xaxis_title="Минут",
        yaxis_title="Играч",
        margin=dict(l=8, r=8, t=56, b=24),
    )
    return fig, heatmap.reset_index()


def goalkeeper_minute_heatmap_figure(
    goals: pd.DataFrame,
    min_conceded: int,
    bin_size: int,
) -> tuple[go.Figure, pd.DataFrame]:
    if "Goalkeeper" not in goals.columns:
        return go.Figure(), pd.DataFrame()

    interval_df = add_minute_intervals(goals, bin_size, "Minute Bin")
    interval_df = interval_df[interval_df["Goalkeeper"].fillna("").astype(str).str.strip().ne("")]
    goalkeeper_counts = interval_df["Goalkeeper"].value_counts()
    selected_goalkeepers = goalkeeper_counts[goalkeeper_counts >= min_conceded].index
    interval_df = interval_df[interval_df["Goalkeeper"].isin(selected_goalkeepers)]

    if interval_df.empty:
        return go.Figure(), pd.DataFrame()

    heatmap = pd.crosstab(interval_df["Goalkeeper"], interval_df["Minute Bin"])
    heatmap = heatmap.loc[heatmap.sum(axis=1).sort_values(ascending=False).index]
    fig = px.imshow(
        heatmap,
        text_auto=True,
        color_continuous_scale="Reds",
        aspect="auto",
        labels=dict(color="Примљени голови"),
        title="Кад голмани примају голове",
    )
    fig.update_layout(
        height=max(420, 32 * len(heatmap.index) + 150),
        xaxis_title="Минут",
        yaxis_title="Голман",
        margin=dict(l=8, r=8, t=56, b=24),
    )
    return fig, heatmap.reset_index()


def player_timing_summary(goals: pd.DataFrame) -> pd.DataFrame:
    minute_df = goals_with_minutes(goals)
    if minute_df.empty:
        return pd.DataFrame()

    grouped = minute_df.groupby("Goalscorer")["Minute"]
    summary = grouped.agg(
        Голови="count",
        Просечан_минут="mean",
        Медијана="median",
        Најранији_гол="min",
        Најкаснији_гол="max",
    ).reset_index()

    early = (
        minute_df[minute_df["Minute"] < 10]
        .groupby("Goalscorer")
        .size()
        .rename("Голови_0_10")
        .reset_index()
    )
    late = (
        minute_df[minute_df["Minute"] >= 50]
        .groupby("Goalscorer")
        .size()
        .rename("Голови_50_plus")
        .reset_index()
    )

    summary = summary.merge(early, on="Goalscorer", how="left").merge(late, on="Goalscorer", how="left")
    summary[["Голови_0_10", "Голови_50_plus"]] = summary[["Голови_0_10", "Голови_50_plus"]].fillna(0)
    for column in ["Просечан_минут", "Медијана"]:
        summary[column] = summary[column].round(1)

    return summary.sort_values(["Голови", "Просечан_минут"], ascending=[False, True])


def assist_scorer_pairs(goals: pd.DataFrame) -> pd.DataFrame:
    if not {"Assist", "Goalscorer"}.issubset(goals.columns):
        return pd.DataFrame()

    pairs = goals.copy()
    pairs["Assist"] = pairs["Assist"].fillna("").astype(str).str.strip()
    pairs = pairs[pairs["Assist"].ne("")]
    if pairs.empty:
        return pd.DataFrame()

    pair_counts = (
        pairs.groupby(["Assist", "Goalscorer"])
        .size()
        .rename("Голови")
        .reset_index()
        .sort_values("Голови", ascending=False)
    )
    pair_counts["Комбинација"] = pair_counts["Assist"] + " → " + pair_counts["Goalscorer"]
    return pair_counts


def assist_scorer_bar_figure(pairs: pd.DataFrame, top_n: int) -> go.Figure:
    top = pairs.head(top_n).sort_values("Голови")
    fig = px.bar(
        top,
        x="Голови",
        y="Комбинација",
        orientation="h",
        text="Голови",
        title="Најчешће комбинације асистент-стрелац",
        color_discrete_sequence=["#0f766e"],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=max(360, 34 * len(top) + 120),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=24, t=56, b=24),
    )
    return fig


def assist_scorer_sankey_figure(pairs: pd.DataFrame, top_n: int) -> go.Figure:
    top = pairs.head(top_n)
    assistants = [f"А: {name}" for name in top["Assist"]]
    scorers = [f"С: {name}" for name in top["Goalscorer"]]
    labels = list(dict.fromkeys(assistants + scorers))
    label_index = {label: index for index, label in enumerate(labels)}

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=18,
                    thickness=16,
                    line=dict(color="rgba(17, 24, 39, 0.35)", width=0.5),
                    label=labels,
                    color="#dbeafe",
                ),
                link=dict(
                    source=[label_index[f"А: {name}"] for name in top["Assist"]],
                    target=[label_index[f"С: {name}"] for name in top["Goalscorer"]],
                    value=top["Голови"].tolist(),
                    color="rgba(15, 118, 110, 0.35)",
                ),
            )
        ]
    )
    fig.update_layout(
        title="Мрежа асистенција",
        height=520,
        margin=dict(l=8, r=8, t=56, b=24),
        font_size=12,
    )
    return fig


with st.sidebar:
    st.title("ФК Баранда")

    default_file = load_default_file(TERMINI_DATA_CANDIDATES)
    if default_file is not None:
        source_name, source_bytes = default_file
    else:
        source_name = ""
        source_bytes = b""

    default_goals_file = load_default_file(GOALS_DATA_CANDIDATES)
    if default_goals_file is not None:
        goals_source_name, goals_source_bytes = default_goals_file
    else:
        goals_source_name = ""
        goals_source_bytes = b""


if not source_bytes:
    st.title("ФК Баранда статистика")
    st.info(
        "Није пронађен фајл са статистиком термина. Постави "
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
goals_df = pd.DataFrame()
if goals_source_bytes:
    try:
        goals_df = read_goal_data(goals_source_name, goals_source_bytes)
    except Exception as exc:
        st.sidebar.warning(f"Фајл са головима није учитан: {exc}")

with st.sidebar:
    st.divider()
    page = st.radio(
        "Навигација",
        [
            "Преглед",
            "Профил играча",
            "Поређење играча",
            "Листе",
            "Голови",
            "Анализа две осе",
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
    if "Goal Contributions per 60" in filtered_players.columns:
        c1.plotly_chart(
            make_top_bar(filtered_players, "Goal Contributions per 60", "Голови + асистенције на 60 минута"),
            use_container_width=True,
        )
    elif "Goals per 60" in filtered_players.columns:
        c1.plotly_chart(
            make_top_bar(filtered_players, "Goals per 60", "Голови на 60 минута"),
            use_container_width=True,
        )

    overview_second_metric = next(
        (
            metric
            for metric in ["Interceptions per 60", "Total Passes per 60", "Successful passes per 60", "Tackles Won per 60", "Points per Game"]
            if metric in filtered_players.columns
        ),
        None,
    )
    if overview_second_metric:
        c2.plotly_chart(
            make_top_bar(
                filtered_players,
                overview_second_metric,
                display_label(overview_second_metric),
                color="#536dfe",
            ),
            use_container_width=True,
        )

    table_cols = existing_columns(
        filtered_players,
        [
            PLAYER_COL,
            "Одиграно утакмица",
            MINUTES_COL,
            "Goal Contributions per 60",
            "Goals per 60",
            "Assists per 60",
            "Total Passes per 60",
            "Successful passes per 60",
            "Interceptions per 60",
            "Tackles Won per 60",
            "Points per Game",
            "Pass Accuracy",
            "Dribble Accuracy",
            "Goals",
            "Assists",
        ],
    )
    st.subheader("Табела играча")
    show_table(
        filtered_players[table_cols].sort_values(
            "Goal Contributions per 60" if "Goal Contributions per 60" in table_cols else "Games Played",
            ascending=False,
        )
    )


elif page == "Профил играча":
    st.title("Профил играча")
    player = st.selectbox("Изабери играча", sorted(filtered_players[PLAYER_COL].unique()))
    row = player_stats[player_stats[PLAYER_COL] == player].iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    if "Goals per 60" in row.index:
        c1.metric("Голови/60", format_number(row["Goals per 60"], 2))
    elif "Goals" in row.index:
        c1.metric("Голови", format_number(row["Goals"]))
    if "Assists per 60" in row.index:
        c2.metric("Асист./60", format_number(row["Assists per 60"], 2))
    elif "Assists" in row.index:
        c2.metric("Асистенције", format_number(row["Assists"]))
    if "Goal Contributions per 60" in row.index:
        c3.metric("Г + А/60", format_number(row["Goal Contributions per 60"], 2))
    elif "Goal Contributions" in row.index:
        c3.metric("Г + А", format_number(row["Goal Contributions"]))
    if "Points per Game" in row.index:
        c4.metric("Бодови/термин", format_number(row["Points per Game"], 2))
    c5.metric("Термини", format_number(row["Games Played"]))

    c1, c2 = st.columns([1.05, 0.95])
    with c1:
        st.subheader("Профил по перцентилима")
        fig = percentile_radar(player_stats, player, min_games, min_minutes)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нема довољно колона за радарски приказ.")

    with c2:
        st.subheader("Кључне статистике")
        profile_cols = existing_columns(
            player_stats,
            [
                PLAYER_COL,
                "Games Played",
                MINUTES_COL,
                "Goal Contributions per 60",
                "Goals per 60",
                "Assists per 60",
                "Big Chances Created per 60",
                "Shots on Goal per 60",
                "Total Passes per 60",
                "Successful passes per 60",
                "Interceptions per 60",
                "Tackles Won per 60",
                "Big Chances Created",
                "Shots on Goal",
                "Pass Accuracy",
                "Dribble Accuracy",
                "Goals",
                "Assists",
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

    compare_metric_options = existing_columns(filtered_players, list(LEADERBOARD_OPTIONS.values()))
    compare_metrics = st.multiselect(
        "Статистике за поређење",
        compare_metric_options,
        default=existing_columns(
            filtered_players,
            [
                "Goal Contributions per 60",
                "Goals per 60",
                "Assists per 60",
                "Big Chances Created per 60",
                "Total Passes per 60",
                "Successful passes per 60",
                "Interceptions per 60",
            ],
        ),
        format_func=display_label,
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
    top_limit = min(30, len(filtered_players))
    top_min = min(5, top_limit)
    top_n = st.slider("Број играча", top_min, top_limit, min(10, top_limit))

    st.plotly_chart(
        make_top_bar(filtered_players, selected_metric, selected_label, top_n=top_n),
        use_container_width=True,
    )

    ranking_cols = existing_columns(
        filtered_players,
        [
            PLAYER_COL,
            "Games Played",
            MINUTES_COL,
            selected_metric,
            "Goal Contributions per 60",
            "Goals per 60",
            "Assists per 60",
            "Total Passes per 60",
            "Successful passes per 60",
            "Interceptions per 60",
            "Points per Game",
            "Goals",
            "Assists",
        ],
    )
    show_table(
        filtered_players[ranking_cols].sort_values(selected_metric, ascending=False),
    )


elif page == "Голови":
    st.title("Голови")

    if goals_df.empty:
        st.info(
            "Фајл са головима није пронађен. Локално се тражи "
            "`C:\\Users\\beoog\\Desktop\\Fudbal Bezanija\\Sajt\\Fudbal Bezanija Golovi.xlsx`, "
            "или `Fudbal Bezanija Golovi.xlsx` у истом фолдеру као апликација."
        )
    else:
        assisted_goals = 0
        if "Assist" in goals_df.columns:
            assisted_goals = goals_df["Assist"].fillna("").astype(str).str.strip().ne("").sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Голова", format_number(len(goals_df)))
        c2.metric("Термина", format_number(goals_df["Game Label"].nunique()))
        c3.metric("Стрелаца", format_number(goals_df["Goalscorer"].nunique()))
        c4.metric("Голова са асистенцијом", format_number(assisted_goals))

        tab_scorers, tab_minutes, tab_player_minutes, tab_assists, tab_goalkeepers, tab_games = st.tabs(
            ["Стрелци", "Минути", "Играч/минути", "Асистенције", "Голмани", "По термину"]
        )

        with tab_scorers:
            scorer_counts = count_by_column(goals_df, "Goalscorer", "Голови")
            if scorer_counts.empty:
                st.info("Нема података о стрелцима.")
            else:
                st.plotly_chart(
                    goal_count_bar(
                        scorer_counts,
                        "Goalscorer",
                        "Голови",
                        "Листа стрелаца из фајла голова",
                        "#2f7d59",
                    ),
                    use_container_width=True,
                )
                show_table(scorer_counts)

            if "Goal Method" in goals_df.columns:
                scored_with = count_by_column(goals_df, "Goal Method", "Голови")
                if not scored_with.empty:
                    fig = px.pie(
                        scored_with,
                        names="Goal Method",
                        values="Голови",
                        title="Како су постизани голови",
                        hole=0.35,
                        labels=display_labels(["Goal Method", "Голови"]),
                        color_discrete_sequence=px.colors.qualitative.Set2,
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with tab_minutes:
            minute_goals = goals_with_minutes(goals_df)
            if minute_goals.empty:
                st.info("Нема употребљивих минута у фајлу са головима.")
            else:
                bin_size = st.select_slider(
                    "Ширина интервала за хистограм",
                    options=[1, 2, 5, 10],
                    value=1,
                    key="goal_hist_bin_size",
                )
                c1, c2 = st.columns([1.25, 0.75])
                with c1:
                    st.plotly_chart(
                        minute_histogram_figure(minute_goals, bin_size),
                        use_container_width=True,
                    )
                with c2:
                    donut_fig, interval_counts = interval_donut_figure(minute_goals, 10)
                    st.plotly_chart(donut_fig, use_container_width=True)
                    show_table(interval_counts)

        with tab_player_minutes:
            minute_goals = goals_with_minutes(goals_df)
            if minute_goals.empty:
                st.info("Нема употребљивих минута у фајлу са головима.")
            else:
                c1, c2 = st.columns(2)
                min_goal_options = list(range(1, max(2, int(minute_goals["Goalscorer"].value_counts().max())) + 1))
                min_player_goals = c1.select_slider(
                    "Минимум голова за топлотну мапу",
                    options=min_goal_options,
                    value=4 if 4 in min_goal_options else min_goal_options[0],
                    key="player_minute_min_goals",
                )
                player_bin_size = c2.select_slider(
                    "Интервал минута",
                    options=[5, 10, 15],
                    value=5,
                    key="player_minute_bin_size",
                )
                fig, heatmap_table = player_minute_heatmap_figure(
                    minute_goals,
                    min_player_goals,
                    player_bin_size,
                )
                if fig.data:
                    st.plotly_chart(fig, use_container_width=True)
                    with st.expander("Табела података за топлотну мапу"):
                        show_table(heatmap_table)
                else:
                    st.info("Нема играча који пролазе задати минимум голова.")

                st.subheader("Профил стрелаца по минутима")
                timing_summary = player_timing_summary(minute_goals)
                if timing_summary.empty:
                    st.info("Нема довољно података за профил по минутима.")
                else:
                    show_table(timing_summary)

        with tab_assists:
            assist_counts = count_by_column(goals_df, "Assist", "Асистенције")
            if assist_counts.empty:
                st.info("Нема уписаних асистенција у фајлу са головима.")
            else:
                st.plotly_chart(
                    goal_count_bar(
                        assist_counts,
                        "Assist",
                        "Асистенције",
                        "Асистенти из фајла голова",
                        "#536dfe",
                    ),
                    use_container_width=True,
                )
                show_table(assist_counts)

                pairs = assist_scorer_pairs(goals_df)
                if not pairs.empty:
                    if len(pairs) <= 5:
                        top_pairs = len(pairs)
                    else:
                        top_pairs = st.slider(
                            "Број комбинација асистент-стрелац",
                            5,
                            min(30, len(pairs)),
                            min(12, len(pairs)),
                            key="assist_pair_top_n",
                        )
                    st.plotly_chart(
                        assist_scorer_bar_figure(pairs, top_pairs),
                        use_container_width=True,
                    )
                    st.plotly_chart(
                        assist_scorer_sankey_figure(pairs, top_pairs),
                        use_container_width=True,
                    )
                    show_table(pairs.head(top_pairs))

        with tab_goalkeepers:
            goalkeeper_counts = count_by_column(goals_df, "Goalkeeper", "Примљени голови")
            if goalkeeper_counts.empty:
                st.info("Нема података о голманима.")
            else:
                st.plotly_chart(
                    goal_count_bar(
                        goalkeeper_counts,
                        "Goalkeeper",
                        "Примљени голови",
                        "Примљени голови по голману",
                        "#d95f02",
                    ),
                    use_container_width=True,
                )
                show_table(goalkeeper_counts)

                minute_goals = goals_with_minutes(goals_df)
                if not minute_goals.empty:
                    c1, c2 = st.columns(2)
                    max_conceded = int(goalkeeper_counts["Примљени голови"].max())
                    min_conceded = c1.slider(
                        "Минимум примљених голова за топлотну мапу",
                        1,
                        max(1, max_conceded),
                        min(8, max(1, max_conceded)),
                        key="goalkeeper_min_conceded",
                    )
                    gk_bin_size = c2.select_slider(
                        "Интервал минута",
                        options=[5, 10, 15],
                        value=10,
                        key="goalkeeper_bin_size",
                    )
                    fig, gk_heatmap = goalkeeper_minute_heatmap_figure(
                        minute_goals,
                        min_conceded,
                        gk_bin_size,
                    )
                    if fig.data:
                        st.plotly_chart(fig, use_container_width=True)
                        with st.expander("Табела голманске топлотне мапе"):
                            show_table(gk_heatmap)

        with tab_games:
            game_options = (
                goals_df[["Game Label", "Game Sort"]]
                .drop_duplicates()
                .sort_values("Game Sort")["Game Label"]
                .tolist()
            )
            selected_game = st.selectbox("Изабери термин", game_options)
            game_goals = goals_df[goals_df["Game Label"] == selected_game].sort_values(
                "Minute" if "Minute" in goals_df.columns else "Game Sort"
            )

            if game_goals.empty:
                st.info("Нема голова за изабрани термин.")
            else:
                st.plotly_chart(goal_timeline_figure(game_goals), use_container_width=True)
                table_cols = existing_columns(
                    game_goals,
                    [
                        "Minute",
                        "Team",
                        "Goalscorer",
                        "Assist",
                        "Goalkeeper",
                        "Goal Method",
                        "Black/Colored",
                        "White/Bibs",
                        "Goal Count",
                    ],
                )
                show_table(game_goals[table_cols])


elif page == "Анализа две осе":
    st.title("Анализа две осе")

    numeric_analysis_cols = [
        column
        for column in filtered_players.select_dtypes(include="number").columns
        if column not in ["No."]
    ]

    default_x = (
        "Successful passes per 60"
        if "Successful passes per 60" in numeric_analysis_cols
        else "Pass Accuracy"
        if "Pass Accuracy" in numeric_analysis_cols
        else numeric_analysis_cols[0]
    )
    default_y = (
        "Big Chances Created per 60"
        if "Big Chances Created per 60" in numeric_analysis_cols
        else numeric_analysis_cols[min(1, len(numeric_analysis_cols) - 1)]
    )
    default_size = MINUTES_COL if MINUTES_COL in numeric_analysis_cols else "Games Played"

    c1, c2, c3 = st.columns(3)
    x_metric = c1.selectbox(
        "Водоравна оса",
        numeric_analysis_cols,
        index=numeric_analysis_cols.index(default_x),
        format_func=display_label,
    )
    y_metric = c2.selectbox(
        "Усправна оса",
        numeric_analysis_cols,
        index=numeric_analysis_cols.index(default_y),
        format_func=display_label,
    )
    size_metric = c3.selectbox(
        "Величина тачке",
        numeric_analysis_cols,
        index=numeric_analysis_cols.index(default_size),
        format_func=display_label,
    )

    st.plotly_chart(
        quadrant_chart(
            filtered_players,
            x_metric,
            y_metric,
            size_metric,
            f"{display_label(x_metric)} и {display_label(y_metric)}",
        ),
        use_container_width=True,
    )


elif page == "Синергија":
    st.title("Синергија и дуели")

    required = {GAME_COL, TEAM_COL, PLAYER_COL, POINTS_COL}
    missing = sorted(required.difference(df.columns))
    if missing:
        st.info("За ову анализу недостају колоне: " + ", ".join(display_label(column) for column in missing))
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
        format_func=display_label,
    )

    records = single_game_records(df, record_stats)
    if records.empty:
        st.info("Нема доступних рекорда за изабране статистике.")
    else:
        show_table(records)


elif page == "Подаци":
    st.title("Подаци")
    tab_raw, tab_players, tab_goals = st.tabs(["Сви редови", "Агрегирано по играчу", "Голови"])

    with tab_raw:
        show_table(df, max_rows=500)
        download_table_button(df, "Преузми све редове као CSV", "fk_baranda_svi_redovi.csv")

    with tab_players:
        show_table(player_stats, max_rows=500)
        download_table_button(player_stats, "Преузми табелу играча као CSV", "fk_baranda_igraci.csv")

    with tab_goals:
        if goals_df.empty:
            st.info("Фајл са головима није учитан.")
        else:
            show_table(goals_df, max_rows=500)
            download_table_button(goals_df, "Преузми голове као CSV", "fk_baranda_golovi.csv")
