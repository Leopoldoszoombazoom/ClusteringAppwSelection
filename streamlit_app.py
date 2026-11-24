"""Εφαρμογή συσταδοποίησης με KMeans — web έκδοση (Streamlit + Plotly με εμφάνιση Matplotlib).

Τοπικά:   streamlit run streamlit_app.py
Online:   Streamlit Community Cloud (share.streamlit.io) → αυτό το repo → streamlit_app.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # μόνο για τα colormaps (tab10, Set1…)
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from matplotlib.colors import to_hex

DATA_DIR = Path(__file__).parent / "ClusterigAppwSelection"
sys.path.insert(0, str(DATA_DIR))
from kmeans_np import KMeans  # noqa: E402  (NumPy μόνο, χωρίς sklearn/SciPy)

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

palette = st.sidebar.selectbox("Χρώματα (colormap)",
                               ["tab10", "Set1", "Dark2", "Set2", "Paired", "viridis", "plasma"])
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

# ___________________ 3D γράφημα: Plotly (γυρίζει με το ποντίκι) με εμφάνιση Matplotlib ___________________
cmap = plt.get_cmap(palette)
# ποιοτικά colormaps (tab10, Set1…): ένα χρώμα ανά συστάδα · συνεχή (viridis…): ισαπέχοντα χρώματα
colors = [to_hex(cmap(i % cmap.N) if cmap.N <= 20 else cmap(i / max(k - 1, 1))) for i in range(k)]
hover_extra = [c for c in data.columns if c not in features][:4]   # π.χ. η πραγματική κλάση

fig = go.Figure()
for i in range(k):
    pts = result[result["cluster"] == i]
    extra = "".join(f"<br>{c}=%{{customdata[{j}]}}" for j, c in enumerate(hover_extra))
    fig.add_trace(go.Scatter3d(
        x=pts[f1], y=pts[f2], z=pts[f3], mode="markers",
        name=f"Συστάδα {i + 1} ({sizes[i]})",
        marker=dict(size=point_size, color=colors[i], opacity=0.75, line=dict(width=0)),
        customdata=pts[hover_extra].to_numpy() if hover_extra else None,
        hovertemplate=f"Συστάδα {i + 1}<br>{f1}=%{{x}}<br>{f2}=%{{y}}<br>{f3}=%{{z}}{extra}<extra></extra>",
    ))
# κέντρα: μαύρα αστέρια όπως στην desktop εφαρμογή (το Scatter3d δεν έχει σύμβολο αστεριού → κείμενο ★)
fig.add_trace(go.Scatter3d(
    x=centers[:, 0], y=centers[:, 1], z=centers[:, 2], mode="text", text=["★"] * k,
    textfont=dict(size=26, color="black"), legendgroup="κέντρα", showlegend=False,
    hovertemplate=f"κέντρο<br>{f1}=%{{x:.3f}}<br>{f2}=%{{y:.3f}}<br>{f3}=%{{z:.3f}}<extra></extra>",
))
# καταχώρηση υπομνήματος για τα κέντρα (αλλιώς το Plotly δείχνει «Aa» για ίχνος κειμένου)
fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode="markers", name="★ Κέντρα",
                           legendgroup="κέντρα", marker=dict(size=1, opacity=0)))

MPL_FONT = "DejaVu Sans, Verdana, sans-serif"
axis = dict(backgroundcolor="#f2f2f2", showbackground=True, gridcolor="#d0d0d0",
            zeroline=False, showspikes=False, linecolor="black", ticks="outside",
            tickfont=dict(size=11, color="black"))
fig.update_layout(
    height=600, paper_bgcolor="white", font=dict(family=MPL_FONT, color="black"),
    title=dict(text=f"Αριθμός συστάδων: {k}", x=0.5, xanchor="center", font=dict(size=16)),
    margin=dict(l=0, r=0, t=45, b=0),
    legend=dict(x=0.01, y=0.98, bgcolor="rgba(255,255,255,0.85)", bordercolor="#cccccc",
                borderwidth=1, itemsizing="constant", font=dict(size=12)),
    scene=dict(
        xaxis=dict(title=f1, **axis), yaxis=dict(title=f2, **axis), zaxis=dict(title=f3, **axis),
        aspectmode="cube",
        camera=dict(eye=dict(x=1.05, y=-1.8, z=0.95)),  # περίπου η προεπιλεγμένη γωνία του Matplotlib
    ),
)
# τα 2/3 του πλάτους σε υπολογιστή (όχι τεράστιο)· σε κινητό οι στήλες στοιβάζονται → όλο το πλάτος
chart_col, _ = st.columns([2, 1])
chart_col.plotly_chart(fig, theme=None, config={"displayModeBar": False, "displaylogo": False})
chart_col.caption("🖱️ Σύρετε για περιστροφή · ροδέλα για zoom · κλικ στο υπόμνημα για απόκρυψη συστάδας")

# ___________________ πίνακας δεδομένων ___________________
with st.expander("Δεδομένα με τη στήλη cluster", expanded=False):
    st.dataframe(result, use_container_width=True, height=350)
    st.download_button("⬇️ Λήψη CSV", result.to_csv(index=False).encode("utf-8"),
                       file_name=f"clusters_{Path(dataset).stem}_k{k}.csv", mime="text/csv")
