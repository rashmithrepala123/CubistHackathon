import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from math import pi

# Define all entry points
ENTRY_POINTS = [
    "Lincoln Tunnel",
    "Holland Tunnel",
    "Queens-Midtown Tunnel",
    "Hugh L. Carey Tunnel",
    "George Washington Bridge",
    "Manhattan Bridge",
    "Brooklyn Bridge",
    "Williamsburg Bridge",
    "Queensboro Bridge",
    "Henry Hudson Bridge",
    "Robert F. Kennedy Bridge",
    "Cross Bay Bridge"
]

# Initialize session state for saved charts if not exists
if 'saved_charts' not in st.session_state:
    st.session_state.saved_charts = []

# Define a color palette for saved charts
COLORS = [
    ('rgba(255, 99, 71, 0.3)', 'rgba(255, 99, 71, 0.8)'),    # Tomato
    ('rgba(65, 105, 225, 0.3)', 'rgba(65, 105, 225, 0.8)'),  # Royal Blue
    ('rgba(50, 205, 50, 0.3)', 'rgba(50, 205, 50, 0.8)'),    # Lime Green
    ('rgba(255, 165, 0, 0.3)', 'rgba(255, 165, 0, 0.8)'),    # Orange
    ('rgba(186, 85, 211, 0.3)', 'rgba(186, 85, 211, 0.8)'),  # Medium Orchid
    ('rgba(30, 144, 255, 0.3)', 'rgba(30, 144, 255, 0.8)'),  # Dodger Blue
    ('rgba(255, 215, 0, 0.3)', 'rgba(255, 215, 0, 0.8)'),    # Gold
    ('rgba(220, 20, 60, 0.3)', 'rgba(220, 20, 60, 0.8)'),    # Crimson
    ('rgba(0, 255, 127, 0.3)', 'rgba(0, 255, 127, 0.8)'),    # Spring Green
    ('rgba(148, 0, 211, 0.3)', 'rgba(148, 0, 211, 0.8)')     # Dark Violet
]

@st.cache_data
def load_data():
    df = pd.read_csv('congestiondata.csv')
    df['Toll Date'] = pd.to_datetime(df['Toll Date'])
    df['Toll Hour'] = pd.to_datetime(df['Toll Hour'])
    return df

def create_spider_chart(categories, values, title, show_saved=False, color='white'):
    fig = go.Figure()
    
    # Add saved charts if showing overlay
    if show_saved and st.session_state.saved_charts:
        for idx, saved_chart in enumerate(st.session_state.saved_charts):
            # Get color from palette (cycling if more saved charts than colors)
            fill_color, line_color = COLORS[idx % len(COLORS)]
            
            fig.add_trace(go.Scatterpolar(
                r=np.concatenate((saved_chart['values'], [saved_chart['values'][0]])),
                theta=categories + [categories[0]],
                mode='lines+markers',
                name=saved_chart['name'],
                fill='toself',
                fillcolor=fill_color,
                line=dict(color=line_color, width=2),
                marker=dict(color=line_color, size=8),
                hovertemplate="<b>%{theta}</b><br>" +
                            f"Entries ({saved_chart['name']}): " + "%{r:,.0f}<br>" +
                            "<extra></extra>"
            ))
    
    # Add current chart (always in purple)
    fig.add_trace(go.Scatterpolar(
        r=np.concatenate((values, [values[0]])),
        theta=categories + [categories[0]],
        mode='lines+markers',
        name='Current',
        fill='toself',
        fillcolor='rgba(147, 112, 219, 0.3)',  # Purple
        line=dict(color='white', width=2),
        marker=dict(color='white', size=8),
        hovertemplate="<b>%{theta}</b><br>" +
                      "Entries (Current): %{r:,.0f}<br>" +
                      "<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            y=0.95,
            font=dict(color='white', size=16)
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        polar=dict(
            bgcolor='black',
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                tickformat=",d",
                color='white',
                tickfont=dict(color='white'),
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            angularaxis=dict(
                direction="clockwise",
                period=len(categories),
                color='white',
                tickfont=dict(color='white'),
                gridcolor='rgba(255, 255, 255, 0.2)'
            )
        ),
        showlegend=True,
        legend=dict(
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0.5)'
        ),
        height=700,
        width=700
    )
    
    return fig

def show_spider_analysis():
    st.title("Entry Points Spider Chart Analysis")

    try:
        # Load data
        df = load_data()

        # Sidebar filters
        st.sidebar.header("Filters")

        # Entry type selection
        st.sidebar.subheader("Entry Type")
        show_crz = st.sidebar.checkbox("Show CRZ Entries", value=True)
        show_ere = st.sidebar.checkbox("Show Excluded Roadway Entries", value=False)

        # Date and Time Selection
        st.sidebar.subheader("Date and Time Selection")
        selected_date = st.sidebar.date_input(
            "Select Date",
            value=df['Toll Date'].min(),
            min_value=df['Toll Date'].min(),
            max_value=df['Toll Date'].max()
        )
        selected_hour = st.sidebar.slider(
            "Select Hour",
            min_value=0,
            max_value=23,
            value=12,
            format="%d:00"
        )

        # Save and overlay controls
        st.sidebar.subheader("Save and Overlay Controls")
        show_saved = st.sidebar.checkbox("Show Saved Charts", value=True)
        
        # Create datetime for filtering
        selected_datetime = datetime.combine(
            selected_date, 
            datetime.strptime(f"{selected_hour}:00", "%H:%M").time()
        )

        # Filter and process data
        mask = (
            (df['Toll Date'].dt.date == selected_date) & 
            (df['Toll Hour'].dt.hour == selected_hour)
        )
        filtered_df = df[mask].copy()
        detection_groups = sorted(df['Detection Group'].unique())
        time_series = filtered_df.groupby('Detection Group').agg({
            'CRZ Entries': 'sum',
            'Excluded Roadway Entries': 'sum'
        }).reset_index()

        # Ensure all detection groups are present
        all_groups_df = pd.DataFrame({'Detection Group': detection_groups})
        time_series = pd.merge(
            all_groups_df, 
            time_series, 
            on='Detection Group', 
            how='left'
        ).fillna(0)

        # Create columns for charts
        if show_crz and show_ere:
            chart_cols = st.columns(2)
        else:
            chart_cols = [st]

        # Display CRZ Spider Chart
        if show_crz:
            crz_values = time_series['CRZ Entries'].values
            crz_title = f"CRZ Entries by Entry Point<br>{selected_datetime.strftime('%Y-%m-%d %H:00')}"
            
            # Save chart controls
            save_crz = chart_cols[0].button("Save Current CRZ Chart")
            if save_crz:
                save_name = f"CRZ {selected_datetime.strftime('%Y-%m-%d %H:00')}"
                st.session_state.saved_charts.append({
                    'name': save_name,
                    'values': crz_values
                })
                st.success(f"Saved chart: {save_name}")
            
            fig_crz = create_spider_chart(detection_groups, crz_values, crz_title, show_saved)
            chart_cols[0].plotly_chart(fig_crz, use_container_width=True)

        # Display ERE Spider Chart
        if show_ere:
            col_idx = 1 if show_crz else 0
            ere_values = time_series['Excluded Roadway Entries'].values
            ere_title = f"Excluded Roadway Entries by Entry Point<br>{selected_datetime.strftime('%Y-%m-%d %H:00')}"
            
            # Save chart controls
            save_ere = chart_cols[col_idx].button("Save Current ERE Chart")
            if save_ere:
                save_name = f"ERE {selected_datetime.strftime('%Y-%m-%d %H:00')}"
                st.session_state.saved_charts.append({
                    'name': save_name,
                    'values': ere_values
                })
                st.success(f"Saved chart: {save_name}")
            
            fig_ere = create_spider_chart(detection_groups, ere_values, ere_title, show_saved)
            chart_cols[col_idx].plotly_chart(fig_ere, use_container_width=True)

        # Clear saved charts button
        if st.session_state.saved_charts:
            if st.sidebar.button("Clear All Saved Charts"):
                st.session_state.saved_charts = []
                st.sidebar.success("Cleared all saved charts")

        # Display saved charts list with colors
        if st.session_state.saved_charts:
            st.sidebar.subheader("Saved Charts")
            for idx, saved_chart in enumerate(st.session_state.saved_charts):
                _, line_color = COLORS[idx % len(COLORS)]
                st.sidebar.markdown(
                    f"<span style='color: {line_color}'>{idx + 1}. {saved_chart['name']}</span>",
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Please ensure congestiondata.csv is present and contains the required columns.")

if __name__ == "__main__":
    show_spider_analysis() 