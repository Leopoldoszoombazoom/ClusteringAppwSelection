


![Uploading ezgif-5aaa8fdb7fbd4e82-3.gif…]()
# K-Means Clustering App · Εφαρμογή συσταδοποίησης με KMeans

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://k-meansapp.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Interactive k-means clustering on 10 real datasets, with a rotatable 3D plot of the clusters and their centroids.

**▶ Try it online, nothing to install: https://k-meansapp.streamlit.app**

<img width="800" height="943" alt="ezgif-5aaa8fdb7fbd4e82" src="https://github.com/user-attachments/assets/2fdeac0f-c9a3-4027-a210-96b455e5823e" />
<img width="800" height="894" alt="ezgif-2069627019f19a75" src="https://github.com/user-attachments/assets/5d899996-d1c9-45e9-aa35-8e762499bd00" />
<img width="800" height="894" alt="ezgif-2664a32026c55119" src="https://github.com/user-attachments/assets/de48096f-2b61-4bc2-a35d-14b3a61159c5" />
<img width="800" height="894" alt="ezgif-25a439268c981386" src="https://github.com/user-attachments/assets/f2789fe8-667e-4537-8aa3-135716ed7e5e" />
<img width="800" height="894" alt="ezgif-23af432fa3168403" src="https://github.com/user-attachments/assets/fe491964-1f5a-4183-95e0-b3df5a749b24" />
<img width="800" height="894" alt="ezgif-2bd672ec0ed4e5cd" src="https://github.com/user-attachments/assets/994f2811-7b03-429e-8688-391ab990df23" />
<img width="800" height="894" alt="ezgif-2ab0968876b17a25" src="https://github.com/user-attachments/assets/cabcf167-94ec-42a5-acca-44ba88618b73" />

## Features

- Pick one of **10 datasets** (see below)
- Choose the number of clusters **k** (1–10) and any **3 numeric features** as the x / y / z axes
- **Interactive 3D chart** (Plotly, styled like the Matplotlib desktop app): drag to rotate, scroll to zoom, hover a point to see its values, click the legend to hide a cluster
- Cluster **centroids**, cluster sizes and inertia (SSE)
- Data table with the assigned `cluster` column and **CSV download**
- Colour palettes, point size, and a random seed for reproducible results

## Datasets

All from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/):

| File | Dataset |
|---|---|
| `winequality-red.csv`, `winequality-white.csv` | Wine Quality |
| `HTRU_2.csv` | HTRU2 (pulsar candidates) |
| `ecoli.data` | Ecoli |
| `yeast.data` | Yeast |
| `abalone.data` | Abalone |
| `iris.data` | Iris |
| `Data_Cortex_Nuclear.xls` | Mice Protein Expression |
| `BreastTissue.xls` | Breast Tissue |
| `CTG 2.xls` | Cardiotocography |

## Run it yourself

The app comes in two versions that share the same datasets:

| Version | File | Interface |
|---|---|---|
| **Web** | `streamlit_app.py` | Streamlit + Plotly (Matplotlib look), runs in the browser |
| **Desktop** | `ClusterigAppwSelection/LoadMyProjectwith3Selections.py` | Tkinter + Matplotlib window |

```bash
git clone https://github.com/Leopoldoszoombazoom/ClusteringAppwSelection.git
cd ClusteringAppwSelection
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

streamlit run streamlit_app.py                                   # web version
python ClusterigAppwSelection/LoadMyProjectwith3Selections.py    # desktop version
```

### Windows .exe (desktop version)

`build.ps1` packages the desktop app with PyInstaller into `dist\ClusteringApp\ClusteringApp.exe` (plus a zip), so it runs on PCs without Python:

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

The .exe is not code-signed, so Windows SmartScreen or Smart App Control may warn about it or block it. The online version avoids this.

## License

[MIT](LICENSE) © Leopoldos
