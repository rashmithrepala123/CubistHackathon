import sys
import base64
from turtle import up
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
import itertools

#-------------------------------------------#
# OPTIONAL: set local image as background in streamlit
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file) 
    page_bg_img = f"""
    <style>
    .stApp {{
      background-image: url("data:image/png;base64,{bin_str}");
      background-size: cover;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return
#--------------------------------------------#

#----TITLE----#
st.markdown('<h1 style="text-align:center;">Interactive MTA Sankey Diagram</h1>', unsafe_allow_html=True)

#--------------------------------------------#
# (Optional) set_png_as_page_bg('your_background.png')
#--------------------------------------------#

st.markdown("""
This app lets you upload **one** CSV of MTA congestion data and interactively build a Sankey diagram. 
You'll pick up to three or more categorical columns (e.g. `time_period`, `vehicle_class`, `detection_group`) 
to form the Sankey flow, and one numeric column (e.g. `crz_entries`) to serve as the flow magnitude.
""")

# =========== SIDEBAR ============= #
with st.sidebar:
    st.header("2) Choose Sankey Columns")
    st.markdown("Select **categorical** columns (in order) to define your Sankey path:")
    categorical_columns = []
    
    # We'll let the user choose up to 3 (or more if you want).
    # They can reorder or add as many as they'd like, but 3 is typical.
    num_cols = st.number_input("How many categorical columns do you want in the flow?", 2, 5, 2)
    options = [
    "toll_date", "toll_10_min_block", "hour_of_day", "day_of_week_int",
    "toll_week", "time_period", "vehicle_class", "detection_group",
    "detection_region", "crz_entries", "excluded_roadway_entries"
    ]
    # We'll store user selections in a list
    for i in range(num_cols):
        cat_col = st.selectbox(f"Flow Level {i+1} column name:", options, index=5)
        categorical_columns.append(cat_col)
        
    st.header("3) Numeric Column to Sum")
    numeric_col = st.text_input("Which numeric column for link values?", "crz_entries")

    st.header("4) Sankey Appearance")
    orientation = st.radio("Orientation:", ('h', 'v'))
    valueformat = st.radio("Value format:", (".2f", ".1f",".0f"))
    valuesuffix = st.text_input("Value suffix (e.g. %, $, etc.):", "")
    
    title_diagram = st.text_input("Diagram title:", "MTA Congestion Flow")
    diagram_height = st.number_input("Diagram height (px):", 400, 2000, 600)
    diagram_width = st.number_input("Diagram width (px):", 400, 2000, 1000)
    diagram_bg_color = st.color_picker("Background color:", "#FFFFFF")
    font_color = st.color_picker("Font color:", "#000000")
    font_size = st.slider("Font size:", 10, 30, 12)

uploaded_file = pd.read_csv('cleaned_data.csv')

# =========== MAIN PAGE ============= #
if uploaded_file is not None:
    # Read the single CSV
    df = uploaded_file
    
    # Quick data check
    st.subheader("Preview of Uploaded Data")
    st.write(df.head())
    
    # Validate user columns exist
    valid_cats = [c for c in categorical_columns if c in df.columns]
    if len(valid_cats) < 2:
        st.error("Please make sure at least two valid categorical columns are provided.")
        st.stop()

    if numeric_col not in df.columns:
        st.error(f"The numeric column '{numeric_col}' does not exist in your data.")
        st.stop()
    
    # --- Build Sankey Nodes & Links automatically ---
    # 1) Gather unique values for each categorical column
    levels = []  # e.g. [[list_of_unique_time_periods], [list_of_unique_vehicle_class], ...]
    for col in valid_cats:
        levels.append(df[col].unique().tolist())
        
    # 2) Create a global dictionary {category_value: node_id}
    #    We'll offset node IDs by each level.
    node_labels = []
    node_dict = {}
    current_id = 0
    
    for i, unique_vals in enumerate(levels):
        for val in unique_vals:
            node_labels.append(val)
            node_dict[(i, val)] = current_id  # store the node ID for this level + value
            current_id += 1
    
    # 3) Build links between consecutive levels
    #    For each pair of consecutive columns, group by the two columns and sum numeric_col.
    link_source = []
    link_target = []
    link_value = []
    
    num_levels = len(valid_cats)
    
    for i in range(num_levels - 1):
        col_a = valid_cats[i]
        col_b = valid_cats[i+1]
        
        # group by col_a and col_b, summing numeric_col
        grouped = df.groupby([col_a, col_b])[numeric_col].sum().reset_index()
        
        for idx, row in grouped.iterrows():
            source_id = node_dict[(i, row[col_a])]
            target_id = node_dict[(i+1, row[col_b])]
            value_ = row[numeric_col]
            
            link_source.append(source_id)
            link_target.append(target_id)
            link_value.append(value_)
    
    # 4) Optional: assign node colors or link colors
    #    For simplicity, use a single color for all links or random palette for nodes.
    #    We'll just do a single link color here:
    link_colors = ["rgba(0,0,0,0.2)"] * len(link_value)
    # Node colors can be assigned if you want each level to have a different palette:
    # We'll keep it simple: every node gets same color or random
    node_colors = []
    for idx, label in enumerate(node_labels):
        node_colors.append("rgba(0,0,0,0.4)")  # same color for all nodes
    
    # --- Create Plotly Sankey object ---
    data_trace = dict(
        type='sankey',
        orientation=orientation,
        valueformat=valueformat,
        valuesuffix=valuesuffix,
        node = dict(
            pad = 15,
            thickness = 15,
            line = dict(color = "black", width = 0),
            label = node_labels,
            color = node_colors
        ),
        link = dict(
            source = link_source,
            target = link_target,
            value = link_value,
            color = link_colors
        )
    )

    layout = dict(
        title = title_diagram,
        height = diagram_height,
        width = diagram_width,
        hovermode = "x",
        plot_bgcolor= diagram_bg_color,
        paper_bgcolor=diagram_bg_color,
        font = dict(
            family="Helvetica", 
            size = font_size, 
            color= font_color
        )
    )

    fig = go.Figure(data=[data_trace], layout=layout)
    
    # Render the Sankey
    st.subheader("Sankey Diagram")
    st.plotly_chart(fig, use_container_width=False)
    
    st.markdown("Use the top-right toolbar to pan, zoom, or save the diagram as PNG.")
else:
    st.info("Please upload your CSV file in the sidebar to get started.")