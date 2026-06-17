import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ФК Баранд Статистика",
    layout="wide"
)

# =========================
# UCITAVANJE PODATAKA
# =========================

@st.cache_data
def load_data():

    df = pd.read_excel("Fudbal Bezanija Termini.xlsx")

    if (
        "Successful passes" in df.columns
        and "Unsuccessful passes" in df.columns
    ):
        df["Pass Accuracy"] = (
            df["Successful passes"]
            / (
                df["Successful passes"]
                + df["Unsuccessful passes"]
            )
            * 100
        )

    if (
        "Successful dribbles" in df.columns
        and "Unsuccessful dribbles" in df.columns
    ):
        df["Dribble Accuracy"] = (
            df["Successful dribbles"]
            / (
                df["Successful dribbles"]
                + df["Unsuccessful dribbles"]
            )
            * 100
        )

    return df


df = load_data()

# =========================
# AGREGACIJA PO IGRACU
# =========================

player_stats = (
    df.groupby("Player Name")
    .agg({
        "Goals": "sum",
        "Assists": "sum",
        "Big Chances Created": "sum",
        "Shots on Goal": "sum",
        "Successful passes": "sum",
        "Successful dribbles": "sum",
        "Tackles Won": "sum",
        "Interceptions": "sum",
        "Points": "sum",
        "Minutes Played": "sum",
        "Saves": "sum",
        "Goals Conceded": "sum"
    })
    .reset_index()
)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("⚽ ФК Баранд")

page = st.sidebar.radio(
    "Навигација",
    [
        "Профил играча",
        "Поређење играча",
        "Листа стрелаца",
        "Асистенције"
    ]
)

# =========================
# PROFIL IGRACA
# =========================

if page == "Профил играча":

    st.title("Профил играча")

    player = st.selectbox(
        "Изабери играча",
        sorted(player_stats["Player Name"].unique())
    )

    row = player_stats[
        player_stats["Player Name"] == player
    ].iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Голови", int(row["Goals"]))
    c2.metric("Асистенције", int(row["Assists"]))
    c3.metric("Бодови", int(row["Points"]))
    c4.metric("Минути", int(row["Minutes Played"]))

    radar_cols = [
        "Goals",
        "Assists",
        "Big Chances Created",
        "Shots on Goal",
        "Successful passes",
        "Successful dribbles",
        "Tackles Won",
        "Interceptions"
    ]

    values = [row[c] for c in radar_cols]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=radar_cols,
            fill="toself",
            name=player
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# POREDJENJE IGRACA
# =========================

elif page == "Поређење играча":

    st.title("Поређење играча")

    col1, col2 = st.columns(2)

    p1 = col1.selectbox(
        "Играч 1",
        sorted(player_stats["Player Name"].unique())
    )

    p2 = col2.selectbox(
        "Играч 2",
        sorted(player_stats["Player Name"].unique()),
        index=1
    )

    s1 = player_stats[
        player_stats["Player Name"] == p1
    ].iloc[0]

    s2 = player_stats[
        player_stats["Player Name"] == p2
    ].iloc[0]

    compare_cols = [
        "Goals",
        "Assists",
        "Big Chances Created",
        "Shots on Goal",
        "Successful passes",
        "Successful dribbles",
        "Tackles Won",
        "Interceptions"
    ]

    comp_df = pd.DataFrame({
        "Category": compare_cols,
        p1: [s1[c] for c in compare_cols],
        p2: [s2[c] for c in compare_cols]
    })

    st.dataframe(comp_df)

# =========================
# STRELCI
# =========================

elif page == "Листа стрелаца":

    st.title("Листа стрелаца")

    top = player_stats.sort_values(
        "Goals",
        ascending=False
    )

    fig = px.bar(
        top,
        x="Player Name",
        y="Goals"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================
# ASISTENCIJE
# =========================

elif page == "Асистенције":

    st.title("Асистенције")

    top = player_stats.sort_values(
        "Assists",
        ascending=False
    )

    fig = px.bar(
        top,
        x="Player Name",
        y="Assists"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )