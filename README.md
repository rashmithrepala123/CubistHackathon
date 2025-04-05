# 🚦 CubistHackathon: NYC Congestion Zone Visualizer 🗽  
_A Streamlit-powered interactive dashboard for exploring New York City’s Congestion Relief Zone (CRZ) data_

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)  
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)  
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📚 Table of Contents
- [🚀 Getting Started](#-getting-started)
- [🗺️ App Features](#-app-features)
- [📊 Data Dashboard](#-data-dashboard)
- [🕸️ Spider Chart Analysis](#️-spider-chart-analysis)
- [🧠 XGBoost Feature Explorer](#-xgboost-feature-explorer)
- [📂 Data Requirements](#-data-requirements)
- [⚙️ Customization](#️-customization)
- [📈 Performance](#-performance)
- [🤝 Contributing](#-contributing)
- [👥 Who Uses This](#-who-uses-this)
- [🙏 Acknowledgments](#-acknowledgments)

---

## 🚀 Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. Navigate to the interactive NYC map to begin visualizing vehicle movement and congestion data.

---

## 🗺️ App Features

### 🔥 Real-Time CRZ Heatmap
- Visualize congestion levels across **12 major entry points**
- Track **live CRZ entries** at different times of day
- Color-coded intensity for quick interpretation

### 📍 Dashboard Access
Top-right corner includes:
- 🧭 **Data Dashboard** – Dive into data trends and summary statistics
- 🕸️ **Spider Chart Analysis** – Multi-dimensional entry point comparison

---

## 📊 Data Dashboard

💡 *Slice, dice, and dive into CRZ entry data with interactive visualizations.*

Features include:
- ⏱️ **Time-based filtering** (by date and hour)
- 🚙 **Vehicle class categorization**
- 📊 **Detection group analysis**
- 📋 **Interactive tables and statistical summaries**

---

## 🕸️ Spider Chart Analysis

🌐 *Reveal complex entry point dynamics across time with a radar chart interface.*

### Key Features:
- 🗓️ Selectable dates and times
- 📌 Save multiple chart states
- 🧪 Overlay comparisons with color-coded layers
- 🖱️ Interactive tooltips for precise value display
- 🔍 Pattern visualization across entry points

---

## 🧠 XGBoost Feature Explorer

Use machine learning to uncover insights:
- 📈 Build a boosted decision tree to predict `CRZ_Entries`
- 🎯 Visualize **feature importance**
- 🔍 Determine which variables most influence traffic behavior

---

## 📂 Data Requirements

The app expects a CSV named `congestiondata.csv` with the following columns:

| Column Name                | Description                                |
|----------------------------|--------------------------------------------|
| `Toll Date`                | Date of entry (MM/DD/YYYY format)          |
| `Toll Hour`                | Hour of day (0–23)                         |
| `Detection Group`          | Sensor group or camera region              |
| `Vehicle Class`            | Category of vehicle (e.g., car, truck)     |
| `CRZ Entries`              | Vehicles that entered the Congestion Zone  |
| `Excluded Roadway Entries` | Vehicles using excluded routes             |

---

## ⚙️ Customization

All styling and logic for the radar (spider) charts can be found in `spider_chart.py`. You can modify:
- 🎨 Color schemes
- 📐 Chart dimensions
- 🧩 Grid & axis styling
- 📝 Label text & formatting
- 🖱️ Tooltip behavior

---

## 📈 Performance

Optimized for:
- ⚡ Real-time data streaming
- 💾 Low memory overhead
- 🔄 Smooth state transitions
- 📱 Responsive visual rendering

---

## 🤝 Contributing

We welcome contributors!

1. 🍴 Fork the repo  
2. 🌿 Create a new branch (`git checkout -b feature-xyz`)  
3. 💬 Commit your changes (`git commit -am 'Add new feature'`)  
4. 📤 Push to the branch (`git push origin feature-xyz`)  
5. 🔁 Open a Pull Request

---

## 👥 Who Uses This

- 🧠 Transportation researchers  
- 🏙️ City planners  
- 📈 Traffic analysts  
- 🛣️ Urban development teams  

---

## 🙏 Acknowledgments

- 🎨 [Streamlit](https://streamlit.io/) – for the interactive dashboard framework  
- 📊 [Plotly](https://plotly.com/) – for stunning data visualizations  
- 📂 NYC Open Data – [Dataset Source](https://data.ny.gov/Transportation/MTA-Congestion-Relief-Zone-Vehicle-Entries-Beginni/t6yz-b64h/about_data)

---

🚀 *Built with ❤️ for Cubist Hackathon*
