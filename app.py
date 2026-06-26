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

# Тамна тема преко CSS инјекције
st.markdown("""
<style>
/* Основна позадина и боје */
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: #e8eaed;
}
[data-testid="stSidebar"] {
    background-color: #111318;
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: rgba(47,125,89,0.25) !important;
    border-radius: 6px;
    color: #4ade80 !important;
}
/* Метрике */
[data-testid="stMetric"] {
    background: #1a1d24;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 0.8rem 1rem;
}
[data-testid="stMetricLabel"] {
    color: #9ca3af !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stMetricValue"] {
    color: #f9fafb !important;
    font-weight: 700;
}
/* Заглавља */
h1, h2, h3, h4 {
    color: #f9fafb !important;
}
/* Дивидер */
hr {
    border-color: rgba(255,255,255,0.08) !important;
}
/* Табови */
[data-testid="stTabs"] [role="tab"] {
    color: #9ca3af;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #4ade80 !important;
    border-bottom-color: #2f7d59 !important;
}
/* Selectbox и слајдери */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #1a1d24 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e8eaed !important;
}
/* Слајдер */
[data-testid="stSlider"] .stSlider > div > div {
    background: #2f7d59 !important;
}
/* Info/warning поруке */
[data-testid="stInfo"] {
    background: rgba(47,125,89,0.1);
    border: 1px solid rgba(47,125,89,0.3);
    color: #c9d1d9 !important;
}
/* Caption текст */
[data-testid="stCaptionContainer"] {
    color: #6b7280 !important;
}
/* Дугмад за преузимање */
[data-testid="stDownloadButton"] button {
    background: #1a1d24 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e8eaed !important;
}
</style>
""", unsafe_allow_html=True)

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
    "Створене шансе на 60 минута": "Big Chances Created per 60",
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
    "Big Chances Created": "Створене шансе",
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
    "Big Chances Created per 60": "Створене шансе на 60 мин",
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
    "Stevan Lacmanovic": "Стеван Лацмановић",
    "Strahinja Milovanovic": "Страхиња Миловановић",
    "Vanijev Burazer": "Ванијев Буразер",
    "Viktor Joldzic": "Виктор Јолџић",
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
def build_same_team_heatmap(df: pd.DataFrame, min_games: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {GAME_COL, TEAM_COL, PLAYER_COL, POINTS_COL}
    if not required.issubset(df.columns):
        return pd.DataFrame(), pd.DataFrame()

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
    games_matrix = pd.DataFrame(index=players, columns=players, dtype=float)
    for (p1, p2), stats in pair_stats.items():
        if stats["games"] >= min_games:
            win_pct = stats["wins"] / stats["games"] * 100
            heatmap.loc[p1, p2] = win_pct
            heatmap.loc[p2, p1] = win_pct
            games_matrix.loc[p1, p2] = int(stats["games"])
            games_matrix.loc[p2, p1] = int(stats["games"])

    valid = heatmap.notna().any(axis=1)
    return heatmap.loc[valid, valid], games_matrix.loc[valid, valid]


@st.cache_data(show_spinner=False)
def build_opponent_heatmap(df: pd.DataFrame, min_games: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {GAME_COL, TEAM_COL, PLAYER_COL, POINTS_COL}
    if not required.issubset(df.columns):
        return pd.DataFrame(), pd.DataFrame()

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
    games_matrix = pd.DataFrame(index=players, columns=players, dtype=float)
    for (player, opponent), stats in pair_stats.items():
        if stats["games"] >= min_games:
            heatmap.loc[player, opponent] = stats["wins"] / stats["games"] * 100
            games_matrix.loc[player, opponent] = int(stats["games"])

    valid_rows = heatmap.notna().any(axis=1)
    valid_cols = heatmap.notna().any(axis=0)
    return heatmap.loc[valid_rows, valid_cols], games_matrix.loc[valid_rows, valid_cols]


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
    freeze_first_col: bool = False,
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
    freeze_js = "true" if freeze_first_col else "false"
    components.html(
        f"""
        <style>
        body {{
            margin: 0;
            font-family: "Source Sans Pro", sans-serif;
            background: transparent;
        }}
        .fk-table-wrap {{
            max-height: 560px;
            overflow: auto;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            background: #0e1117;
        }}
        .fk-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            color: #e8eaed;
        }}
        .fk-table thead th {{
            position: sticky;
            top: 0;
            z-index: 2;
            background: #1a1d24;
            color: #9ca3af;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 0.55rem 0.75rem;
            white-space: nowrap;
            font-weight: 600;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .fk-table thead th.sortable {{
            cursor: pointer;
            user-select: none;
        }}
        .fk-table thead th.sortable:hover {{
            background: #22262f;
            color: #e8eaed;
        }}
        .fk-table td,
        .fk-table tbody th {{
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding: 0.45rem 0.75rem;
            white-space: nowrap;
            color: #e8eaed;
        }}
        .fk-table tbody th {{
            color: #f9fafb;
            font-weight: 600;
            text-align: left;
        }}
        .fk-table tbody tr:nth-child(even) td,
        .fk-table tbody tr:nth-child(even) th {{
            background: rgba(255,255,255,0.03);
        }}
        .fk-table tbody tr:hover td,
        .fk-table tbody tr:hover th {{
            background: rgba(47,125,89,0.15);
        }}
        .sort-arrows {{
            margin-left: 0.35rem;
            color: #4b5563;
            font-size: 0.72rem;
        }}
        .fk-table th.sorted-desc .sort-arrows,
        .fk-table th.sorted-asc .sort-arrows {{
            color: #2f7d59;
        }}
        .fk-table.freeze td:first-child,
        .fk-table.freeze tbody th:first-child {{
            position: sticky;
            left: 0;
            z-index: 1;
            background: #0e1117;
            border-right: 1px solid rgba(255,255,255,0.1);
            font-weight: 600;
        }}
        .fk-table.freeze tbody tr:nth-child(even) td:first-child,
        .fk-table.freeze tbody tr:nth-child(even) th:first-child {{
            background: #111318;
        }}
        .fk-table.freeze tbody tr:hover td:first-child,
        .fk-table.freeze tbody tr:hover th:first-child {{
            background: #0d1a12;
        }}
        .fk-table.freeze thead th:first-child {{
            position: sticky;
            left: 0;
            z-index: 3;
            background: #1a1d24;
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        </style>
        <div class="fk-table-wrap">{html}</div>
        <script>
        const freezeFirstCol = {freeze_js};
        const table = document.querySelector(".fk-table");
        if (table && freezeFirstCol) {{
            table.classList.add("freeze");
        }}

        function normalizeValue(text) {{
            const value = text.trim();
            if (!value || value === "-") {{
                return {{ kind: "empty", value: "" }};
            }}

            const dateMatch = value.match(/^(\d{{1,2}})\.\s*(\d{{1,2}})\.\s*(\d{{4}})\.$/);
            if (dateMatch) {{
                const day = Number(dateMatch[1]);
                const month = Number(dateMatch[2]) - 1;
                const year = Number(dateMatch[3]);
                return {{ kind: "number", value: new Date(year, month, day).getTime() }};
            }}

            const numberCandidate = value.replace(/\./g, "").replace(",", ".");
            if (/^-?\d+(\.\d+)?$/.test(numberCandidate)) {{
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



# ── DATA LOADING ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("ФК Баранда")
    st.caption("5-на-5 аналитика")

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
            "🏆 Почетна",
            "👤 Играчи",
            "🤝 Хемија",
            "📈 Трендови",
            "🥇 Награде",
            "📊 Историја термина",
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

    st.divider()
    season_label = df["Game Sort"].max()
    if hasattr(season_label, "year"):
        st.caption(f"Сезона {season_label.year - 1}/{str(season_label.year)[2:]}")
    latest_game_label = df.sort_values("Game Sort")["Game Label"].iloc[-1]
    st.caption(f"Последњи термин: {latest_game_label}")


filtered_players = apply_player_filters(player_stats, min_games, min_minutes)
if filtered_players.empty:
    st.warning("Нема играча који пролазе тренутне филтере.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# 🏆 ПОЧЕТНА
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏆 Почетна":
    st.title("Добродошли у ФК Баранда")
    st.caption("Преглед сезоне и најважније статистике нашег термина.")

    # ── Метрике ──────────────────────────────────────────────────────────────
    metric_card_grid(player_stats, df)

    st.divider()

    # ── Последња утакмица ────────────────────────────────────────────────────
    st.subheader("Последњи термин")
    games_sorted = df.sort_values("Game Sort")
    last_game_label = games_sorted["Game Label"].iloc[-1]
    last_game_df = df[df["Game Label"] == last_game_label]

    col_last, col_form = st.columns([1, 1])
    with col_last:
        if TEAM_COL in last_game_df.columns and POINTS_COL in last_game_df.columns:
            teams = last_game_df[[TEAM_COL, POINTS_COL]].drop_duplicates(TEAM_COL)
            if "Goals" in last_game_df.columns:
                team_goals = last_game_df.groupby(TEAM_COL)["Goals"].sum().reset_index()
                teams = teams.merge(team_goals, on=TEAM_COL, how="left")
            if len(teams) == 2:
                t1, t2 = teams.iloc[0], teams.iloc[1]
                score1 = int(t1.get("Goals", 0)) if "Goals" in t1.index else "?"
                score2 = int(t2.get("Goals", 0)) if "Goals" in t2.index else "?"
                sc1, sc_sep, sc2 = st.columns([2, 1, 2])
                sc1.metric(str(t1[TEAM_COL]), score1)
                sc_sep.markdown("<h2 style='text-align:center;margin-top:1rem'>:</h2>", unsafe_allow_html=True)
                sc2.metric(str(t2[TEAM_COL]), score2)

        # MVP последње утакмице
        if "Goal Contributions per 60" in last_game_df.columns:
            mvp_col = "Goal Contributions per 60"
        elif "Goals" in last_game_df.columns:
            mvp_col = "Goals"
        else:
            mvp_col = None

        if mvp_col and POINTS_COL in last_game_df.columns:
            last_ps = build_player_stats(last_game_df)
            if not last_ps.empty and mvp_col in last_ps.columns:
                mvp_row = last_ps.sort_values(mvp_col, ascending=False).iloc[0]
                mvp_name = mvp_row[PLAYER_COL]
                mvp_val = mvp_row[mvp_col]
                st.markdown(f"**МВП:** {mvp_name} — {format_number(mvp_val, 2)} {display_label(mvp_col)}")

        # Стрелци и асистенти
        if "Goals" in last_game_df.columns:
            scorers = (
                last_game_df[last_game_df["Goals"] > 0][[PLAYER_COL, "Goals"]]
                .sort_values("Goals", ascending=False)
            )
            if not scorers.empty:
                st.markdown("**Стрелци:**")
                for _, r in scorers.iterrows():
                    st.markdown(f"- {r[PLAYER_COL]}: {int(r['Goals'])}")

    with col_form:
        # Форма екипе (последних 5 термина)
        game_labels_sorted = (
            df[["Game Label", "Game Sort"]]
            .drop_duplicates()
            .sort_values("Game Sort")["Game Label"]
            .tolist()
        )
        last_5 = game_labels_sorted[-5:]
        form_data = []
        for gl in last_5:
            g_df = df[df["Game Label"] == gl]
            if POINTS_COL not in g_df.columns:
                continue
            # Просечан учинак играча у термину - форма индекс
            avg_pts = g_df[POINTS_COL].mean()
            goals_scored = g_df["Goals"].sum() if "Goals" in g_df.columns else 0
            # Форма индекс 0-100 на основу бодова и голова
            form_index = round(min(100, avg_pts * 30 + goals_scored * 2), 0)
            form_data.append({"Термин": gl, "Форма": form_index})

        if len(form_data) >= 2:
            form_df = pd.DataFrame(form_data)
            fig_form = px.line(
                form_df,
                x="Термин",
                y="Форма",
                markers=True,
                title="Форма екипе (последњих 5 термина)",
                text="Форма",
            )
            fig_form.update_traces(
                line_color="#2f7d59",
                textposition="top center",
                marker=dict(size=8),
            )
            fig_form.update_layout(
                yaxis_range=[0, 100],
                height=300,
                margin=dict(l=8, r=8, t=48, b=24),
                xaxis_title="",
                yaxis_title="Индекс форме (0-100)",
            )
            st.plotly_chart(fig_form, use_container_width=True)

    st.divider()

    # ── Топ листе ─────────────────────────────────────────────────────────────
    st.subheader("Ко је носио игру")
    c1, c2 = st.columns(2)
    if "Goal Contributions per 60" in filtered_players.columns:
        c1.plotly_chart(
            make_top_bar(filtered_players, "Goal Contributions per 60", "Голови + асистенције на 60 минута"),
            use_container_width=True,
        )
    if "Interceptions per 60" in filtered_players.columns:
        c2.plotly_chart(
            make_top_bar(filtered_players, "Interceptions per 60", "Пресечене лопте на 60 минута", color="#536dfe"),
            use_container_width=True,
        )

    st.divider()

    # ── Табела играча ─────────────────────────────────────────────────────────
    st.subheader("Табела играча")
    table_cols = existing_columns(
        filtered_players,
        [
            PLAYER_COL,
            "Games Played",
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
            "Goals",
            "Assists",
        ],
    )
    show_table(
        filtered_players[table_cols].sort_values(
            "Goal Contributions per 60" if "Goal Contributions per 60" in table_cols else "Games Played",
            ascending=False,
        ),
        freeze_first_col=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 👤 ИГРАЧИ
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Играчи":
    st.title("Профили играча")

    player = st.selectbox("Изабери играча", sorted(filtered_players[PLAYER_COL].unique()))
    row = player_stats[player_stats[PLAYER_COL] == player].iloc[0]

    # ── Картица играча ────────────────────────────────────────────────────────
    with st.container():
        c1, c2, c3, c4, c5 = st.columns(5)
        if "Goals per 60" in row.index:
            c1.metric("Голови/60", format_number(row["Goals per 60"], 2))
        if "Assists per 60" in row.index:
            c2.metric("Асист./60", format_number(row["Assists per 60"], 2))
        if "Goal Contributions per 60" in row.index:
            c3.metric("Г + А/60", format_number(row["Goal Contributions per 60"], 2))
        if "Interceptions per 60" in row.index:
            c4.metric("Прес./60", format_number(row["Interceptions per 60"], 2))
        c5.metric("Термини", format_number(row["Games Played"]))

    st.divider()

    # ── Радар и статистике ────────────────────────────────────────────────────
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

    st.divider()

    # ── График напретка по терминима ──────────────────────────────────────────
    st.subheader("График напретка по терминима")
    player_games = df[df[PLAYER_COL] == player].sort_values("Game Sort").copy()

    progress_metric = st.selectbox(
        "Статистика за праћење",
        existing_columns(player_games, ["Goals", "Assists", "Interceptions", "Successful passes", "Points"]),
        format_func=display_label,
        key="progress_metric",
    )
    if progress_metric and progress_metric in player_games.columns:
        player_games["Кумулативно"] = player_games[progress_metric].cumsum()
        fig_progress = go.Figure()
        fig_progress.add_bar(
            x=player_games["Game Label"],
            y=player_games[progress_metric],
            name="По термину",
            marker_color="#2f7d59",
        )
        fig_progress.add_scatter(
            x=player_games["Game Label"],
            y=player_games["Кумулативно"],
            name="Кумулативно",
            mode="lines+markers",
            line=dict(color="#fbbf24", width=2),
            yaxis="y2",
        )
        fig_progress.update_layout(
            height=380,
            yaxis=dict(title=display_label(progress_metric)),
            yaxis2=dict(title="Кумулативно", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1),
            margin=dict(l=8, r=8, t=48, b=24),
            xaxis_title="",
        )
        st.plotly_chart(fig_progress, use_container_width=True)

    st.divider()

    # ── Учинак по термину ─────────────────────────────────────────────────────
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
            "Dribble Accuracy",
            "Tackles Won",
            "Interceptions",
            "Saves",
            "Goals Conceded",
        ],
    )
    show_table(player_games[match_cols])

    st.divider()

    # ── Поређење играча ───────────────────────────────────────────────────────
    st.subheader("Поређење играча")
    default_compare = list(filtered_players[PLAYER_COL].head(2))
    selected_players = st.multiselect(
        "Изабери 2 до 4 играча за поређење",
        sorted(filtered_players[PLAYER_COL].unique()),
        default=default_compare,
        max_selections=4,
        key="compare_multi",
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
                "Interceptions per 60",
                "Total Passes per 60",
                "Successful passes per 60",
            ],
        ),
        format_func=display_label,
        key="compare_metrics",
    )
    if len(selected_players) >= 2 and compare_metrics:
        st.plotly_chart(
            comparison_chart(filtered_players, selected_players, compare_metrics),
            use_container_width=True,
        )
        table_cols = [PLAYER_COL, "Games Played"] + existing_columns(filtered_players, [MINUTES_COL]) + compare_metrics
        show_table(
            filtered_players[filtered_players[PLAYER_COL].isin(selected_players)][table_cols],
        )
    else:
        st.info("Изабери бар два играча и бар једну статистику.")


# ═══════════════════════════════════════════════════════════════════════════════
# 🤝 ХЕМИЈА
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤝 Хемија":
    st.title("Хемија и синергија")

    required = {GAME_COL, TEAM_COL, PLAYER_COL, POINTS_COL}
    missing = sorted(required.difference(df.columns))
    if missing:
        st.info("За ову анализу недостају колоне: " + ", ".join(display_label(c) for c in missing))
    else:
        min_pair_games = st.slider("Минимум заједничких термина", 1, 10, 3)

        # Хемија анализа - исти тим
        same_heatmap, same_games_matrix = build_same_team_heatmap(df, min_pair_games)

        # Рачунај парове за топ/флоп
        st.subheader("Најбољи и најгори парови")
        if not same_heatmap.empty:
            pair_rows = []
            for p1 in same_heatmap.index:
                for p2 in same_heatmap.columns:
                    val = same_heatmap.loc[p1, p2]
                    if pd.notna(val) and p1 < p2:
                        ng = same_games_matrix.loc[p1, p2] if (p1 in same_games_matrix.index and p2 in same_games_matrix.columns) else None
                        ng_val = int(ng) if pd.notna(ng) else "-"
                        pair_rows.append({"Пар": f"{p1} + {p2}", "Победе %": round(val, 1), "Заједно термина": ng_val})
            pairs_df = pd.DataFrame(pair_rows).sort_values("Победе %", ascending=False)

            if not pairs_df.empty:
                col_best, col_worst = st.columns(2)
                with col_best:
                    st.markdown("**🟢 Најбољи парови**")
                    show_table(pairs_df.head(5).reset_index(drop=True))
                with col_worst:
                    st.markdown("**🔴 Најгори парови**")
                    show_table(pairs_df.tail(5).sort_values("Победе %").reset_index(drop=True))

        st.divider()

        tab_same, tab_opp = st.tabs(["Мрежа хемије (исти тим)", "Играч против играча"])

        with tab_same:
            if same_heatmap.empty:
                st.info("Нема парова који пролазе задати минимум.")
            else:
                # Припреми customdata матрицу са бројем термина
                import numpy as np
                games_vals = same_games_matrix.reindex(index=same_heatmap.index, columns=same_heatmap.columns).values
                fig_h = px.imshow(
                    same_heatmap,
                    text_auto=".0f",
                    color_continuous_scale="RdYlGn",
                    zmin=0,
                    zmax=100,
                    aspect="auto",
                    labels=dict(color="Победе %"),
                    title="Проценат победа када играчи играју заједно",
                )
                fig_h.update_traces(
                    customdata=games_vals,
                    hovertemplate="<b>%{y}</b> + <b>%{x}</b><br>Победе: %{z:.0f}%<br>Заједничких термина: %{customdata:.0f}<extra></extra>",
                )
                fig_h.update_layout(
                    height=max(520, 28 * len(same_heatmap.index) + 160),
                    xaxis_title="", yaxis_title="",
                    margin=dict(l=8, r=8, t=56, b=24),
                )
                st.plotly_chart(fig_h, use_container_width=True)

        with tab_opp:
            opp_heatmap, opp_games_matrix = build_opponent_heatmap(df, min_pair_games)
            if opp_heatmap.empty:
                st.info("Нема дуела који пролазе задати минимум.")
            else:
                import numpy as np
                opp_games_vals = opp_games_matrix.reindex(index=opp_heatmap.index, columns=opp_heatmap.columns).values
                fig_opp = px.imshow(
                    opp_heatmap,
                    text_auto=".0f",
                    color_continuous_scale="RdBu",
                    zmin=0,
                    zmax=100,
                    aspect="auto",
                    labels=dict(color="Победе %"),
                    title="Проценат победа играча против конкретног противника",
                )
                fig_opp.update_traces(
                    customdata=opp_games_vals,
                    hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Победе: %{z:.0f}%<br>Дуела одиграно: %{customdata:.0f}<extra></extra>",
                )
                fig_opp.update_layout(
                    height=max(520, 28 * len(opp_heatmap.index) + 160),
                    xaxis_title="", yaxis_title="",
                    margin=dict(l=8, r=8, t=56, b=24),
                )
                st.plotly_chart(fig_opp, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 📈 ТРЕНДОВИ
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Трендови":
    st.title("Трендови сезоне")

    # ── Форма последњих 5 термина ────────────────────────────────────────────
    st.subheader("Форма екипе по терминима")
    game_labels_sorted = (
        df[["Game Label", "Game Sort"]]
        .drop_duplicates()
        .sort_values("Game Sort")["Game Label"]
        .tolist()
    )
    n_games = st.slider("Број термина за приказ", 3, len(game_labels_sorted), min(10, len(game_labels_sorted)))
    last_n = game_labels_sorted[-n_games:]

    trend_metric = st.selectbox(
        "Метрика форме",
        existing_columns(player_stats, ["Goal Contributions per 60", "Goals per 60", "Interceptions per 60", "Pass Accuracy", "Points per Game"]),
        format_func=display_label,
        key="trend_metric",
    )

    form_rows = []
    for gl in last_n:
        g_df = df[df["Game Label"] == gl]
        g_stats = build_player_stats(g_df)
        if trend_metric and trend_metric in g_stats.columns:
            val = g_stats[trend_metric].mean()
            form_rows.append({"Термин": gl, "Вредност": round(val, 2)})
        else:
            form_rows.append({"Термин": gl, "Вредност": None})

    if form_rows:
        form_trend_df = pd.DataFrame(form_rows).dropna()
        if not form_trend_df.empty:
            fig_trend = px.line(
                form_trend_df,
                x="Термин",
                y="Вредност",
                markers=True,
                title=f"Просек: {display_label(trend_metric) if trend_metric else ''}",
                text="Вредност",
            )
            fig_trend.update_traces(line_color="#2f7d59", textposition="top center", marker=dict(size=8))
            fig_trend.update_layout(
                height=380, xaxis_title="", margin=dict(l=8, r=8, t=48, b=24),
                yaxis_title=display_label(trend_metric) if trend_metric else "",
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    # ── Голови по месецима ────────────────────────────────────────────────────
    if not goals_df.empty and "Game Sort" in goals_df.columns:
        st.subheader("Голови по месецима")
        goals_monthly = goals_df.copy()
        goals_monthly["Месец"] = goals_monthly["Game Sort"].dt.to_period("M").astype(str)
        monthly_counts = goals_monthly.groupby("Месец").size().reset_index(name="Голови")
        fig_monthly = px.bar(
            monthly_counts,
            x="Месец",
            y="Голови",
            color_discrete_sequence=["#2f7d59"],
            title="Голови по месецима",
            text="Голови",
        )
        fig_monthly.update_layout(height=350, xaxis_title="", margin=dict(l=8, r=8, t=48, b=24))
        st.plotly_chart(fig_monthly, use_container_width=True)

        st.divider()

    # ── Анализа две осе ───────────────────────────────────────────────────────
    st.subheader("Анализа две осе")
    numeric_analysis_cols = [
        c for c in filtered_players.select_dtypes(include="number").columns
        if c not in ["No."]
    ]
    if len(numeric_analysis_cols) >= 2:
        default_x = next((m for m in ["Successful passes per 60", "Pass Accuracy"] if m in numeric_analysis_cols), numeric_analysis_cols[0])
        default_y = next((m for m in ["Big Chances Created per 60", "Goals per 60"] if m in numeric_analysis_cols), numeric_analysis_cols[1])
        default_size = MINUTES_COL if MINUTES_COL in numeric_analysis_cols else "Games Played"

        ca1, ca2, ca3 = st.columns(3)
        x_metric = ca1.selectbox("Водоравна оса", numeric_analysis_cols, index=numeric_analysis_cols.index(default_x), format_func=display_label)
        y_metric = ca2.selectbox("Усправна оса", numeric_analysis_cols, index=numeric_analysis_cols.index(default_y), format_func=display_label)
        size_metric = ca3.selectbox("Величина тачке", numeric_analysis_cols, index=numeric_analysis_cols.index(default_size), format_func=display_label)

        st.plotly_chart(
            quadrant_chart(filtered_players, x_metric, y_metric, size_metric, f"{display_label(x_metric)} и {display_label(y_metric)}"),
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 🥇 НАГРАДЕ
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🥇 Награде":
    st.title("Награде сезоне")
    st.caption("Признања за истакнуте играче сезоне.")

    def award_card(emoji: str, title: str, player_name: str, value: str, desc: str) -> None:
        st.markdown(
            f"""
            <div style='background:rgba(47,125,89,0.12);border:1px solid rgba(47,125,89,0.3);
                        border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:0.8rem;'>
                <div style='font-size:2rem;margin-bottom:0.3rem'>{emoji}</div>
                <div style='font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280;margin-bottom:0.2rem'>{title}</div>
                <div style='font-size:1.5rem;font-weight:700;margin-bottom:0.1rem'>{player_name}</div>
                <div style='font-size:1.1rem;color:#2f7d59;font-weight:600;margin-bottom:0.2rem'>{value}</div>
                <div style='font-size:0.8rem;color:#9ca3af'>{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)

    with col1:
        # Golden Boot - највише голова на 60 мин
        if "Goals per 60" in filtered_players.columns:
            gb_row = filtered_players.sort_values("Goals per 60", ascending=False).iloc[0]
            award_card(
                "⚽", "Golden Boot — Топ стрелац",
                gb_row[PLAYER_COL],
                f"{format_number(gb_row['Goals per 60'], 2)} гол./60 мин",
                f"Укупно голова: {format_number(gb_row.get('Goals', 0))}",
            )

        # Iron Man - највише минута
        if MINUTES_COL in filtered_players.columns:
            im_row = player_stats.sort_values(MINUTES_COL, ascending=False).iloc[0]
            award_card(
                "💪", "Iron Man — Највише минута",
                im_row[PLAYER_COL],
                f"{format_number(im_row[MINUTES_COL])} мин",
                f"У {format_number(im_row['Games Played'])} термина",
            )

        # Clutch Player - највише бодова по термину
        if "Points per Game" in filtered_players.columns:
            cp_row = filtered_players.sort_values("Points per Game", ascending=False).iloc[0]
            award_card(
                "🔥", "Clutch Player — Кључни играч",
                cp_row[PLAYER_COL],
                f"{format_number(cp_row['Points per Game'], 2)} бода/термин",
                "Највиши просечан учинак",
            )

    with col2:
        # Playmaker - највише асистенција
        if "Assists per 60" in filtered_players.columns:
            pm_row = filtered_players.sort_values("Assists per 60", ascending=False).iloc[0]
            award_card(
                "🎯", "Playmaker — Пласирач игре",
                pm_row[PLAYER_COL],
                f"{format_number(pm_row['Assists per 60'], 2)} асист./60 мин",
                f"Укупно асистенција: {format_number(pm_row.get('Assists', 0))}",
            )

        # Clean Sheet / Дефанзивац - највише пресечених лопти
        if "Interceptions per 60" in filtered_players.columns:
            cs_row = filtered_players.sort_values("Interceptions per 60", ascending=False).iloc[0]
            award_card(
                "🛡️", "Clean Sheet — Најбољи дефанзивац",
                cs_row[PLAYER_COL],
                f"{format_number(cs_row['Interceptions per 60'], 2)} прес./60 мин",
                "Највише пресечених лопти на 60 мин",
            )

        # Пасер - највише успешних додавања
        if "Successful passes per 60" in filtered_players.columns:
            pa_row = filtered_players.sort_values("Successful passes per 60", ascending=False).iloc[0]
            award_card(
                "🔗", "Пасер — Мајстор додавања",
                pa_row[PLAYER_COL],
                f"{format_number(pa_row['Successful passes per 60'], 2)} додав./60 мин",
                f"Прецизност паса: {format_number(pa_row.get('Pass Accuracy', 0), 1)}%",
            )

    st.divider()
    st.subheader("🏆 Рекорди на једном термину")
    record_stats = st.multiselect(
        "Статистике",
        existing_columns(df, CORE_STATS + [POINTS_COL]),
        default=existing_columns(df, ["Goals", "Assists", "Big Chances Created", "Saves", "Blocks", "Successful passes", "Interceptions"]),
        format_func=display_label,
    )
    records = single_game_records(df, record_stats)
    if records.empty:
        st.info("Нема доступних рекорда за изабране статистике.")
    else:
        show_table(records)


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 ИСТОРИЈА ТЕРМИНА
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Историја термина":
    st.title("Историја термина")

    game_labels_all = (
        df[["Game Label", "Game Sort"]]
        .drop_duplicates()
        .sort_values("Game Sort", ascending=False)["Game Label"]
        .tolist()
    )

    selected_game = st.selectbox("Изабери термин", game_labels_all)
    game_df = df[df["Game Label"] == selected_game].copy()

    # ── Резултат ─────────────────────────────────────────────────────────────
    if TEAM_COL in game_df.columns and POINTS_COL in game_df.columns:
        teams_info = game_df[[TEAM_COL, POINTS_COL]].drop_duplicates(TEAM_COL)
        if "Goals" in game_df.columns:
            tg = game_df.groupby(TEAM_COL)["Goals"].sum().reset_index()
            teams_info = teams_info.merge(tg, on=TEAM_COL, how="left")
        if len(teams_info) == 2:
            t1, t2 = teams_info.iloc[0], teams_info.iloc[1]
            s1 = int(t1.get("Goals", 0)) if "Goals" in t1.index else "?"
            s2 = int(t2.get("Goals", 0)) if "Goals" in t2.index else "?"
            ca, cb, cc = st.columns([2, 1, 2])
            ca.metric(str(t1[TEAM_COL]), s1)
            cb.markdown("<h2 style='text-align:center;margin-top:1rem'>:</h2>", unsafe_allow_html=True)
            cc.metric(str(t2[TEAM_COL]), s2)

    st.divider()

    # ── Статистика термина ────────────────────────────────────────────────────
    st.subheader("Статистика термина")
    match_cols = existing_columns(
        game_df,
        [
            PLAYER_COL,
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
            "Dribble Accuracy",
            "Tackles Won",
            "Interceptions",
            "Saves",
            "Goals Conceded",
        ],
    )
    show_table(game_df[match_cols].sort_values(TEAM_COL if TEAM_COL in match_cols else PLAYER_COL))

    # ── Голови у термину ─────────────────────────────────────────────────────
    if not goals_df.empty:
        game_goals = goals_df[goals_df["Game Label"] == selected_game].sort_values(
            "Minute" if "Minute" in goals_df.columns else "Game Sort"
        )
        if not game_goals.empty:
            st.divider()
            st.subheader("Голови у термину")
            st.plotly_chart(goal_timeline_figure(game_goals), use_container_width=True)
            goal_table_cols = existing_columns(
                game_goals,
                ["Minute", "Team", "Goalscorer", "Assist", "Goalkeeper", "Goal Method", "Black/Colored", "White/Bibs", "Goal Count"],
            )
            show_table(game_goals[goal_table_cols])

    st.divider()

    # ── Целокупна историја ────────────────────────────────────────────────────
    st.subheader("Сви термини — преглед")
    all_games_summary = []
    for gl in reversed(game_labels_all):
        g_df = df[df["Game Label"] == gl]
        row_d = {"Термин": gl}
        if TEAM_COL in g_df.columns and "Goals" in g_df.columns:
            tg = g_df.groupby(TEAM_COL)["Goals"].sum()
            teams_in_game = list(tg.index)
            if len(teams_in_game) == 2:
                row_d["Екипа 1"] = teams_in_game[0]
                row_d["Голови 1"] = int(tg.iloc[0])
                row_d["Екипа 2"] = teams_in_game[1]
                row_d["Голови 2"] = int(tg.iloc[1])
        row_d["Играча"] = g_df[PLAYER_COL].nunique()
        if "Goals" in g_df.columns:
            row_d["Укупно голова"] = int(g_df["Goals"].sum())
        all_games_summary.append(row_d)

    if all_games_summary:
        summary_df = pd.DataFrame(all_games_summary)
        show_table(summary_df)