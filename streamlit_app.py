"""Εφαρμογή συσταδοποίησης με KMeans — web έκδοση (Streamlit + Matplotlib).

Τοπικά:   streamlit run streamlit_app.py
Online:   Streamlit Community Cloud (share.streamlit.io) → αυτό το repo → streamlit_app.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # χωρίς παράθυρο: το Streamlit δείχνει την εικόνα
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

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
point_size = st.sidebar.slider("Μέγεθος σημείων", 2, 40, 10)

st.sidebar.subheader("Γωνία θέασης")
elev = st.sidebar.slider("Ύψος (elevation)", -90, 90, 25)
azim = st.sidebar.slider("Περιστροφή (azimuth)", -180, 180, -60)
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

# ___________________ 3D γράφημα (Matplotlib, όπως η desktop εφαρμογή) ___________________
cmap = plt.get_cmap(palette)
# ποιοτικά colormaps (tab10, Set1…): ένα χρώμα ανά συστάδα · συνεχή (viridis…): ισαπέχοντα χρώματα
colors = [cmap(i % cmap.N) if cmap.N <= 20 else cmap(i / max(k - 1, 1)) for i in range(k)]

fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(projection="3d")
for i in range(k):
    pts = result[result["cluster"] == i]
    ax.scatter(pts[f1], pts[f2], pts[f3], color=colors[i], s=point_size, alpha=0.7,
               depthshade=False, label=f"Συστάδα {i + 1} ({sizes[i]})")
ax.scatter(centers[:, 0], centers[:, 1], centers[:, 2], c="black", marker="*", s=200,
           edgecolors="white", linewidths=0.8, depthshade=False, label="Κέντρα")
ax.set_xlabel(f1)
ax.set_ylabel(f2)
ax.set_zlabel(f3)
ax.set_title(f"Αριθμός συστάδων: {k}")
ax.view_init(elev=elev, azim=azim)
ax.legend(loc="upper left", fontsize=8, markerscale=1.5)
fig.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)
st.caption("Αλλάξτε τη γωνία θέασης από τα sliders στην πλευρική στήλη.")

# ___________________ πίνακας δεδομένων ___________________
with st.expander("Δεδομένα με τη στήλη cluster", expanded=False):
    st.dataframe(result, use_container_width=True, height=350)
    st.download_button("⬇️ Λήψη CSV", result.to_csv(index=False).encode("utf-8"),
                       file_name=f"clusters_{Path(dataset).stem}_k{k}.csv", mime="text/csv")
