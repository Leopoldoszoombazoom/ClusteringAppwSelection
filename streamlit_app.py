"""Εφαρμογή συσταδοποίησης με KMeans — web έκδοση (Streamlit + Plotly).

Τοπικά:   streamlit run streamlit_app.py
Online:   Streamlit Community Cloud (share.streamlit.io) → αυτό το repo → streamlit_app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans

DATA_DIR = Path(__file__).parent / "ClusterigAppwSelection"

st.set_page_config(page_title="Συσταδοποίηση KMeans", page_icon="🔵", layout="wide")


# ___________________ φόρτωση δεδομένων (ίδια λογική με την desktop εφαρμογή) ___________________
def _wine(f):
    return pd.read_csv(f, sep=";")


def _htru(f):
    return pd.read_csv(f, names=["Mean", "Std", "kurtosis", "skewness", "mean curve",
                                 "Std dm", "exess kurtosis", "Skewness DM-SNR", "dm"])


def _ecoli(f):
    return pd.read_fwf(f, names=["Sequence Name", "mcg", "gvh", "lip", "chg",
                                 "aac", "alm1", "alm2", "Class"])


def _yeast(f):
    return pd.read_fwf(f, names=["Sequence Name", "mcg", "gvh", "alm", "mit", "erl",
                                 "pox", "vac", "nuc", "Class Distribution"])


def _abalone(f):
    return pd.read_csv(f, names=["Sex", "Length", "Diameter", "Height", "Whole weight",
                                 "Shucked weight", "Viscera weight", "Shell weight", "Rings"])


def _iris(f):
    return pd.read_csv(f, names=["sepal length", "sepal width", "petal length",
                                 "petal width", "class"]).dropna()


def _cortex(f):
    df = pd.read_excel(f, engine="xlrd")
    return df.select_dtypes(include=np.number).dropna(axis=1)


def _breast(f):
    return pd.read_excel(f, sheet_name="Data", engine="xlrd")


def _ctg(f):
    df = pd.read_excel(f, sheet_name="Data", skiprows=1, engine="xlrd")
    df = df.iloc[:, list(range(0, 21)) + [22]]
    return df.drop("Unnamed: 9", axis=1).dropna()


DATASETS = {
    "winequality-red.csv": _wine,
    "winequality-white.csv": _wine,
    "HTRU_2.csv": _htru,
    "ecoli.data": _ecoli,
    "yeast.data": _yeast,
    "abalone.data": _abalone,
    "iris.data": _iris,
    "Data_Cortex_Nuclear.xls": _cortex,
    "BreastTissue.xls": _breast,
    "CTG 2.xls": _ctg,
}


@st.cache_data(show_spinner="Φόρτωση δεδομένων…")
def load_data(name: str) -> pd.DataFrame:
    return DATASETS[name](DATA_DIR / name)


@st.cache_data(show_spinner="Συσταδοποίηση…")
def run_kmeans(name: str, features: tuple, k: int, seed: int):
    X = load_data(name)[list(features)].to_numpy()
    model = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
    return model.labels_, model.cluster_centers_, model.inertia_


# ___________________ πλευρική στήλη: επιλογές ___________________
st.sidebar.header("Ρυθμίσεις")
dataset = st.sidebar.selectbox("Σύνολο δεδομένων", list(DATASETS))
data = load_data(dataset)

numeric_cols = data.select_dtypes(include=np.number).columns.tolist()
if len(numeric_cols) < 3:
    st.error("Το σύνολο δεδομένων χρειάζεται τουλάχιστον 3 αριθμητικά χαρακτηριστικά.")
    st.stop()

k = st.sidebar.slider("Αριθμός συστάδων (k)", min_value=1, max_value=10, value=3)

st.sidebar.subheader("Χαρακτηριστικά (άξονες)")
f1 = st.sidebar.selectbox("Χαρακτηριστικό 1 (x)", numeric_cols, index=0, key=f"{dataset}-f1")
f2 = st.sidebar.selectbox("Χαρακτηριστικό 2 (y)", [c for c in numeric_cols if c != f1],
                          index=0, key=f"{dataset}-f2")
f3 = st.sidebar.selectbox("Χαρακτηριστικό 3 (z)", [c for c in numeric_cols if c not in (f1, f2)],
                          index=0, key=f"{dataset}-f3")
features = (f1, f2, f3)

palettes = {name: getattr(px.colors.qualitative, name)
            for name in ["Plotly", "D3", "T10", "Set1", "Dark24", "Bold", "Vivid", "Pastel", "Safe"]}
palette = st.sidebar.selectbox("Χρώματα", list(palettes))
point_size = st.sidebar.slider("Μέγεθος σημείων", 2, 10, 4)
seed = st.sidebar.number_input("Random seed", value=0, step=1,
                               help="Ίδιο seed → ίδιο αποτέλεσμα σε κάθε εκτέλεση")

# ___________________ συσταδοποίηση ___________________
labels, centers, inertia = run_kmeans(dataset, features, k, int(seed))
result = data.copy()
result["cluster"] = labels

st.title("Εφαρμογή συσταδοποίησης με KMeans")
st.caption(f"**{dataset}** · {len(data):,} γραμμές · {len(numeric_cols)} αριθμητικά χαρακτηριστικά")

sizes = np.bincount(labels, minlength=k)
c1, c2, c3 = st.columns(3)
c1.metric("Συστάδες", k)
c2.metric("Inertia (SSE)", f"{inertia:,.2f}")
c3.metric("Μέγεθος συστάδων", " / ".join(str(s) for s in sizes))

# ___________________ 3D γράφημα (Plotly: περιστροφή/zoom με το ποντίκι) ___________________
plot_df = result.copy()
plot_df["συστάδα"] = (plot_df["cluster"] + 1).astype(str)
hover_extra = [c for c in data.columns if c not in features][:4]   # π.χ. η πραγματική κλάση

fig = px.scatter_3d(
    plot_df, x=f1, y=f2, z=f3, color="συστάδα",
    color_discrete_sequence=palettes[palette],
    category_orders={"συστάδα": [str(i + 1) for i in range(k)]},
    hover_data=hover_extra, opacity=0.8,
)
fig.update_traces(marker=dict(size=point_size))
fig.add_trace(go.Scatter3d(
    x=centers[:, 0], y=centers[:, 1], z=centers[:, 2],
    mode="markers", name="κέντρα",
    marker=dict(symbol="diamond", size=11, color="white", line=dict(color="#222222", width=3)),
    hovertemplate="κέντρο<br>" + f"{f1}=%{{x:.3f}}<br>{f2}=%{{y:.3f}}<br>{f3}=%{{z:.3f}}<extra></extra>",
))
fig.update_layout(height=650, margin=dict(l=0, r=0, t=30, b=0),
                  legend=dict(title="Συστάδα", itemsizing="constant"))
st.plotly_chart(fig, use_container_width=True)
st.caption("🖱️ Σύρετε για περιστροφή · ροδέλα για zoom · κλικ στο υπόμνημα για απόκρυψη συστάδας")

# ___________________ πίνακας δεδομένων ___________________
with st.expander("Δεδομένα με τη στήλη cluster", expanded=False):
    st.dataframe(result, use_container_width=True, height=350)
    st.download_button("⬇️ Λήψη CSV", result.to_csv(index=False).encode("utf-8"),
                       file_name=f"clusters_{Path(dataset).stem}_k{k}.csv", mime="text/csv")
