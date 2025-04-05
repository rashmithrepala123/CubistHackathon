import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as path_effects

# Set page config
st.set_page_config(
    page_title="CRZ Entries Analysis",
    page_icon="🚗",
    layout="wide"
)

# Initialize session state for saved statistics and radar data stamps
if 'saved_stats' not in st.session_state:
    st.session_state.saved_stats = []
if 'radar_stamps' not in st.session_state:
    st.session_state.radar_stamps = []

# Title and description
st.title("CRZ Entries Analysis Dashboard")
st.markdown("""
This dashboard visualizes the number of Congestion Reduction Zone (CRZ) entries and Excluded Roadway Entries (ERE) over time.
Use the sidebar to filter and analyze the data.
""")

# Create tabs for different visualizations
tab1, tab2 = st.tabs(["Time Series Analysis", "Detection Group Radar Chart"])

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('congestiondata.csv')
    df['Toll Date'] = pd.to_datetime(df['Toll Date'])
    df['Toll Hour'] = pd.to_datetime(df['Toll Hour'])
    return df

# Load the data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Entry type selection
st.sidebar.subheader("Entry Type")
show_crz = st.sidebar.checkbox("Show CRZ Entries", value=True)
show_ere = st.sidebar.checkbox("Show Excluded Roadway Entries", value=False)

# Date and time filters
st.sidebar.subheader("Time Range")
col1, col2 = st.sidebar.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=df['Toll Date'].min(),
        min_value=df['Toll Date'].min(),
        max_value=df['Toll Date'].max()
    )
    start_time = st.time_input(
        "Start Time",
        value=datetime.strptime("00:00", "%H:%M").time()
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=df['Toll Date'].max(),
        min_value=df['Toll Date'].min(),
        max_value=df['Toll Date'].max()
    )
    end_time = st.time_input(
        "End Time",
        value=datetime.strptime("23:59", "%H:%M").time()
    )

# Detection group filter
st.sidebar.subheader("Detection Groups")
show_by_group = st.sidebar.checkbox("Show entries by detection group", value=False)

# Get unique detection groups
detection_groups = sorted(df['Detection Group'].unique())
selected_groups = st.sidebar.multiselect(
    "Select detection groups to display",
    options=detection_groups,
    default=detection_groups[:3] if len(detection_groups) > 3 else detection_groups,
    disabled=not show_by_group
)

# Vehicle Class filter
st.sidebar.subheader("Vehicle Classes")
show_by_vehicle = st.sidebar.checkbox("Show entries by vehicle class", value=False)

# Get unique vehicle classes
vehicle_classes = sorted(df['Vehicle Class'].unique())
selected_vehicles = st.sidebar.multiselect(
    "Select vehicle classes to display",
    options=vehicle_classes,
    default=vehicle_classes[:3] if len(vehicle_classes) > 3 else vehicle_classes,
    disabled=not show_by_vehicle
)

# Combine date and time
start_datetime = datetime.combine(start_date, start_time)
end_datetime = datetime.combine(end_date, end_time)

# Filter data based on datetime range
mask = (df['Toll Hour'] >= start_datetime) & (df['Toll Hour'] <= end_datetime)
filtered_df = df[mask]

# Create time series based on selected filters
if show_by_group and selected_groups:
    # Filter by selected groups
    group_mask = filtered_df['Detection Group'].isin(selected_groups)
    filtered_df = filtered_df[group_mask]
    
    if show_by_vehicle and selected_vehicles:
        # Filter by selected vehicle classes
        vehicle_mask = filtered_df['Vehicle Class'].isin(selected_vehicles)
        filtered_df = filtered_df[vehicle_mask]
        
        # Create time series by group and vehicle class
        time_series = filtered_df.groupby(['Toll Hour', 'Detection Group', 'Vehicle Class']).agg({
            'CRZ Entries': 'sum',
            'Excluded Roadway Entries': 'sum'
        }).reset_index()
        
        # Create a combined label for the chart
        time_series['Label'] = time_series['Detection Group'] + ' - ' + time_series['Vehicle Class']
        
        # Create separate dataframes for each entry type
        crz_data = time_series.pivot(index='Toll Hour', columns='Label', values='CRZ Entries')
        ere_data = time_series.pivot(index='Toll Hour', columns='Label', values='Excluded Roadway Entries')
        
        # Combine the dataframes based on selection
        pivot_data = pd.DataFrame()
        if show_crz:
            for col in crz_data.columns:
                pivot_data[f"{col} (CRZ)"] = crz_data[col]
        if show_ere:
            for col in ere_data.columns:
                pivot_data[f"{col} (ERE)"] = ere_data[col]
    else:
        # Create time series by group only
        time_series = filtered_df.groupby(['Toll Hour', 'Detection Group']).agg({
            'CRZ Entries': 'sum',
            'Excluded Roadway Entries': 'sum'
        }).reset_index()
        
        # Create separate dataframes for each entry type
        crz_data = time_series.pivot(index='Toll Hour', columns='Detection Group', values='CRZ Entries')
        ere_data = time_series.pivot(index='Toll Hour', columns='Detection Group', values='Excluded Roadway Entries')
        
        # Combine the dataframes based on selection
        pivot_data = pd.DataFrame()
        if show_crz:
            for col in crz_data.columns:
                pivot_data[f"{col} (CRZ)"] = crz_data[col]
        if show_ere:
            for col in ere_data.columns:
                pivot_data[f"{col} (ERE)"] = ere_data[col]
elif show_by_vehicle and selected_vehicles:
    # Filter by selected vehicle classes
    vehicle_mask = filtered_df['Vehicle Class'].isin(selected_vehicles)
    filtered_df = filtered_df[vehicle_mask]
    
    # Create time series by vehicle class
    time_series = filtered_df.groupby(['Toll Hour', 'Vehicle Class']).agg({
        'CRZ Entries': 'sum',
        'Excluded Roadway Entries': 'sum'
    }).reset_index()
    
    # Create separate dataframes for each entry type
    crz_data = time_series.pivot(index='Toll Hour', columns='Vehicle Class', values='CRZ Entries')
    ere_data = time_series.pivot(index='Toll Hour', columns='Vehicle Class', values='Excluded Roadway Entries')
    
    # Combine the dataframes based on selection
    pivot_data = pd.DataFrame()
    if show_crz:
        for col in crz_data.columns:
            pivot_data[f"{col} (CRZ)"] = crz_data[col]
    if show_ere:
        for col in ere_data.columns:
            pivot_data[f"{col} (ERE)"] = ere_data[col]
else:
    # Create overall time series
    time_series = filtered_df.groupby('Toll Hour').agg({
        'CRZ Entries': 'sum',
        'Excluded Roadway Entries': 'sum'
    }).reset_index()
    
    # Create separate dataframes for each entry type
    crz_data = time_series.set_index('Toll Hour')[['CRZ Entries']]
    ere_data = time_series.set_index('Toll Hour')[['Excluded Roadway Entries']]
    
    # Combine the dataframes based on selection
    pivot_data = pd.DataFrame()
    if show_crz:
        pivot_data['CRZ Entries'] = crz_data['CRZ Entries']
    if show_ere:
        pivot_data['Excluded Roadway Entries'] = ere_data['Excluded Roadway Entries']

# Tab 1: Time Series Analysis
with tab1:
    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Entries Over Time")
        
        # Create the time series plot using Streamlit's native line chart
        st.line_chart(
            pivot_data,
            use_container_width=True
        )

    with col2:
        st.subheader("Statistics")
        
        # Calculate statistics for saving
        stats_to_save = {}
        
        if not show_by_group and not show_by_vehicle:
            # Calculate overall statistics
            if show_crz:
                crz_total = time_series['CRZ Entries'].sum()
                crz_avg = time_series['CRZ Entries'].mean()
                crz_max = time_series['CRZ Entries'].max()
                crz_min = time_series['CRZ Entries'].min()
                crz_std = time_series['CRZ Entries'].std()
                crz_median = time_series['CRZ Entries'].median()
                
                stats_to_save['CRZ'] = {
                    'Total': crz_total,
                    'Average': crz_avg,
                    'Maximum': crz_max,
                    'Minimum': crz_min,
                    'Std Dev': crz_std,
                    'Median': crz_median
                }
                
                st.markdown("**CRZ Entries:**")
                st.metric("Total", f"{crz_total:,.0f}")
                st.metric("Average per Hour", f"{crz_avg:,.2f}")
                st.metric("Maximum in an Hour", f"{crz_max:,.0f}")
                st.metric("Minimum in an Hour", f"{crz_min:,.0f}")
                st.metric("Standard Deviation", f"{crz_std:,.2f}")
                st.metric("Median", f"{crz_median:,.2f}")
            
            if show_ere:
                ere_total = time_series['Excluded Roadway Entries'].sum()
                ere_avg = time_series['Excluded Roadway Entries'].mean()
                ere_max = time_series['Excluded Roadway Entries'].max()
                ere_min = time_series['Excluded Roadway Entries'].min()
                ere_std = time_series['Excluded Roadway Entries'].std()
                ere_median = time_series['Excluded Roadway Entries'].median()
                
                stats_to_save['ERE'] = {
                    'Total': ere_total,
                    'Average': ere_avg,
                    'Maximum': ere_max,
                    'Minimum': ere_min,
                    'Std Dev': ere_std,
                    'Median': ere_median
                }
                
                st.markdown("**Excluded Roadway Entries:**")
                st.metric("Total", f"{ere_total:,.0f}")
                st.metric("Average per Hour", f"{ere_avg:,.2f}")
                st.metric("Maximum in an Hour", f"{ere_max:,.0f}")
                st.metric("Minimum in an Hour", f"{ere_min:,.0f}")
                st.metric("Standard Deviation", f"{ere_std:,.2f}")
                st.metric("Median", f"{ere_median:,.2f}")
        else:
            # Calculate statistics for groups or vehicle classes
            if show_by_group and selected_groups:
                if show_by_vehicle and selected_vehicles:
                    # Calculate statistics for each group and vehicle class combination
                    for group in selected_groups:
                        for vehicle in selected_vehicles:
                            group_data = time_series[(time_series['Detection Group'] == group) & 
                                                    (time_series['Vehicle Class'] == vehicle)]
                            
                            if not group_data.empty:
                                st.markdown(f"**{group} - {vehicle}**")
                                
                                if show_crz:
                                    crz_total = group_data['CRZ Entries'].sum()
                                    crz_avg = group_data['CRZ Entries'].mean()
                                    crz_max = group_data['CRZ Entries'].max()
                                    crz_min = group_data['CRZ Entries'].min()
                                    
                                    # Store in stats_to_save
                                    if 'CRZ' not in stats_to_save:
                                        stats_to_save['CRZ'] = {}
                                    stats_to_save['CRZ'][f"{group} - {vehicle}"] = {
                                        'Total': crz_total,
                                        'Average': crz_avg,
                                        'Maximum': crz_max,
                                        'Minimum': crz_min
                                    }
                                    
                                    st.markdown("CRZ Entries:")
                                    st.metric("Total", f"{crz_total:,.0f}")
                                    st.metric("Average per Hour", f"{crz_avg:,.2f}")
                                    st.metric("Maximum", f"{crz_max:,.0f}")
                                    st.metric("Minimum", f"{crz_min:,.0f}")
                                
                                if show_ere:
                                    ere_total = group_data['Excluded Roadway Entries'].sum()
                                    ere_avg = group_data['Excluded Roadway Entries'].mean()
                                    ere_max = group_data['Excluded Roadway Entries'].max()
                                    ere_min = group_data['Excluded Roadway Entries'].min()
                                    
                                    # Store in stats_to_save
                                    if 'ERE' not in stats_to_save:
                                        stats_to_save['ERE'] = {}
                                    stats_to_save['ERE'][f"{group} - {vehicle}"] = {
                                        'Total': ere_total,
                                        'Average': ere_avg,
                                        'Maximum': ere_max,
                                        'Minimum': ere_min
                                    }
                                    
                                    st.markdown("Excluded Roadway Entries:")
                                    st.metric("Total", f"{ere_total:,.0f}")
                                    st.metric("Average per Hour", f"{ere_avg:,.2f}")
                                    st.metric("Maximum", f"{ere_max:,.0f}")
                                    st.metric("Minimum", f"{ere_min:,.0f}")
                                
                                st.markdown("---")
                else:
                    # Calculate statistics for each group
                    for group in selected_groups:
                        group_data = time_series[time_series['Detection Group'] == group]
                        
                        st.markdown(f"**{group}**")
                        
                        if show_crz:
                            crz_total = group_data['CRZ Entries'].sum()
                            crz_avg = group_data['CRZ Entries'].mean()
                            crz_max = group_data['CRZ Entries'].max()
                            crz_min = group_data['CRZ Entries'].min()
                            
                            # Store in stats_to_save
                            if 'CRZ' not in stats_to_save:
                                stats_to_save['CRZ'] = {}
                            stats_to_save['CRZ'][group] = {
                                'Total': crz_total,
                                'Average': crz_avg,
                                'Maximum': crz_max,
                                'Minimum': crz_min
                            }
                            
                            st.markdown("CRZ Entries:")
                            st.metric("Total", f"{crz_total:,.0f}")
                            st.metric("Average per Hour", f"{crz_avg:,.2f}")
                            st.metric("Maximum", f"{crz_max:,.0f}")
                            st.metric("Minimum", f"{crz_min:,.0f}")
                        
                        if show_ere:
                            ere_total = group_data['Excluded Roadway Entries'].sum()
                            ere_avg = group_data['Excluded Roadway Entries'].mean()
                            ere_max = group_data['Excluded Roadway Entries'].max()
                            ere_min = group_data['Excluded Roadway Entries'].min()
                            
                            # Store in stats_to_save
                            if 'ERE' not in stats_to_save:
                                stats_to_save['ERE'] = {}
                            stats_to_save['ERE'][group] = {
                                'Total': ere_total,
                                'Average': ere_avg,
                                'Maximum': ere_max,
                                'Minimum': ere_min
                            }
                            
                            st.markdown("Excluded Roadway Entries:")
                            st.metric("Total", f"{ere_total:,.0f}")
                            st.metric("Average per Hour", f"{ere_avg:,.2f}")
                            st.metric("Maximum", f"{ere_max:,.0f}")
                            st.metric("Minimum", f"{ere_min:,.0f}")
                        
                        st.markdown("---")
            elif show_by_vehicle and selected_vehicles:
                # Calculate statistics for each vehicle class
                for vehicle in selected_vehicles:
                    vehicle_data = time_series[time_series['Vehicle Class'] == vehicle]
                    
                    st.markdown(f"**{vehicle}**")
                    
                    if show_crz:
                        crz_total = vehicle_data['CRZ Entries'].sum()
                        crz_avg = vehicle_data['CRZ Entries'].mean()
                        crz_max = vehicle_data['CRZ Entries'].max()
                        crz_min = vehicle_data['CRZ Entries'].min()
                        
                        # Store in stats_to_save
                        if 'CRZ' not in stats_to_save:
                            stats_to_save['CRZ'] = {}
                        stats_to_save['CRZ'][vehicle] = {
                            'Total': crz_total,
                            'Average': crz_avg,
                            'Maximum': crz_max,
                            'Minimum': crz_min
                        }
                        
                        st.markdown("CRZ Entries:")
                        st.metric("Total", f"{crz_total:,.0f}")
                        st.metric("Average per Hour", f"{crz_avg:,.2f}")
                        st.metric("Maximum", f"{crz_max:,.0f}")
                        st.metric("Minimum", f"{crz_min:,.0f}")
                    
                    if show_ere:
                        ere_total = vehicle_data['Excluded Roadway Entries'].sum()
                        ere_avg = vehicle_data['Excluded Roadway Entries'].mean()
                        ere_max = vehicle_data['Excluded Roadway Entries'].max()
                        ere_min = vehicle_data['Excluded Roadway Entries'].min()
                        
                        # Store in stats_to_save
                        if 'ERE' not in stats_to_save:
                            stats_to_save['ERE'] = {}
                        stats_to_save['ERE'][vehicle] = {
                            'Total': ere_total,
                            'Average': ere_avg,
                            'Maximum': ere_max,
                            'Minimum': ere_min
                        }
                        
                        st.markdown("Excluded Roadway Entries:")
                        st.metric("Total", f"{ere_total:,.0f}")
                        st.metric("Average per Hour", f"{ere_avg:,.2f}")
                        st.metric("Maximum", f"{ere_max:,.0f}")
                        st.metric("Minimum", f"{ere_min:,.0f}")
                    
                    st.markdown("---")

    # Save statistics section
    st.markdown("---")
    st.subheader("Save Statistics")

    # Create a name for this timeframe
    timeframe_name = st.text_input("Name this timeframe", value=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Add group/vehicle class info to the name if applicable
    if show_by_group and selected_groups:
        if show_by_vehicle and selected_vehicles:
            timeframe_name += f" - Groups: {', '.join(selected_groups)} - Vehicles: {', '.join(selected_vehicles)}"
        else:
            timeframe_name += f" - Groups: {', '.join(selected_groups)}"
    elif show_by_vehicle and selected_vehicles:
        timeframe_name += f" - Vehicles: {', '.join(selected_vehicles)}"

    # Save button
    if st.button("Save Statistics"):
        # Create a dictionary with the statistics
        stats_to_save_dict = {
            'name': timeframe_name,
            'start_date': start_date,
            'end_date': end_date,
            'stats': stats_to_save,
            'pivot_data': pivot_data.copy(),  # Save the pivot data for later use
            'is_grouped': show_by_group or show_by_vehicle,
            'groups': selected_groups if show_by_group else [],
            'vehicles': selected_vehicles if show_by_vehicle else []
        }
        
        # Add to session state
        st.session_state.saved_stats.append(stats_to_save_dict)
        st.success(f"Statistics for '{timeframe_name}' saved successfully!")

    # Display saved statistics
    if st.session_state.saved_stats:
        st.subheader("Saved Statistics")
        
        # Create a dataframe for comparison
        comparison_data = []
        
        for saved_stat in st.session_state.saved_stats:
            row_data = {
                'Timeframe': saved_stat['name'],
                'Start Date': saved_stat['start_date'],
                'End Date': saved_stat['end_date'],
                'Grouped': 'Yes' if saved_stat['is_grouped'] else 'No'
            }
            
            # Add CRZ stats if available
            if 'CRZ' in saved_stat['stats']:
                if saved_stat['is_grouped']:
                    # For grouped data, we need to handle differently
                    crz_stats = saved_stat['stats']['CRZ']
                    if isinstance(crz_stats, dict) and any(isinstance(v, dict) for v in crz_stats.values()):
                        # This is nested grouped data
                        for group, stats in crz_stats.items():
                            row_data[f"CRZ {group} Total"] = stats['Total']
                            row_data[f"CRZ {group} Average"] = stats['Average']
                    else:
                        # This is regular grouped data
                        for group, stats in crz_stats.items():
                            row_data[f"CRZ {group} Total"] = stats['Total']
                            row_data[f"CRZ {group} Average"] = stats['Average']
                else:
                    # For non-grouped data
                    crz_stats = saved_stat['stats']['CRZ']
                    row_data.update({
                        'CRZ Total': crz_stats['Total'],
                        'CRZ Average': crz_stats['Average'],
                        'CRZ Maximum': crz_stats['Maximum'],
                        'CRZ Minimum': crz_stats['Minimum'],
                        'CRZ Std Dev': crz_stats['Std Dev'],
                        'CRZ Median': crz_stats['Median']
                    })
            
            # Add ERE stats if available
            if 'ERE' in saved_stat['stats']:
                if saved_stat['is_grouped']:
                    # For grouped data, we need to handle differently
                    ere_stats = saved_stat['stats']['ERE']
                    if isinstance(ere_stats, dict) and any(isinstance(v, dict) for v in ere_stats.values()):
                        # This is nested grouped data
                        for group, stats in ere_stats.items():
                            row_data[f"ERE {group} Total"] = stats['Total']
                            row_data[f"ERE {group} Average"] = stats['Average']
                    else:
                        # This is regular grouped data
                        for group, stats in ere_stats.items():
                            row_data[f"ERE {group} Total"] = stats['Total']
                            row_data[f"ERE {group} Average"] = stats['Average']
                else:
                    # For non-grouped data
                    ere_stats = saved_stat['stats']['ERE']
                    row_data.update({
                        'ERE Total': ere_stats['Total'],
                        'ERE Average': ere_stats['Average'],
                        'ERE Maximum': ere_stats['Maximum'],
                        'ERE Minimum': ere_stats['Minimum'],
                        'ERE Std Dev': ere_stats['Std Dev'],
                        'ERE Median': ere_stats['Median']
                    })
            
            comparison_data.append(row_data)
        
        # Create dataframe
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display the dataframe
        st.dataframe(comparison_df)
        
        # Option to clear saved statistics
        if st.button("Clear All Saved Statistics"):
            st.session_state.saved_stats = []
            st.experimental_rerun()
        
        # Compare saved timeframes
        st.subheader("Compare Saved Timeframes")
        
        # Create a multiselect for selecting timeframes to compare
        timeframe_options = [f"{stat['name']} ({stat['start_date'].strftime('%Y-%m-%d')} to {stat['end_date'].strftime('%Y-%m-%d')})" 
                            for stat in st.session_state.saved_stats]
        
        selected_timeframes = st.multiselect(
            "Select timeframes to compare",
            options=timeframe_options,
            default=timeframe_options[:min(2, len(timeframe_options))] if timeframe_options else []
        )
        
        # Display overlaid graphs for selected timeframes
        if selected_timeframes:
            st.subheader("Comparison Graph")
            
            # Create a combined dataframe for all selected timeframes
            combined_data = pd.DataFrame()
            
            # Add each selected timeframe's data to the combined dataframe
            for timeframe in selected_timeframes:
                # Find the index of the selected timeframe
                idx = timeframe_options.index(timeframe)
                saved_stat = st.session_state.saved_stats[idx]
                
                # Get the pivot data for this timeframe
                timeframe_data = saved_stat['pivot_data']
                
                # Rename columns to include the timeframe name
                renamed_cols = {}
                for col in timeframe_data.columns:
                    renamed_cols[col] = f"{col} ({saved_stat['name']})"
                
                # Add the renamed data to the combined dataframe
                combined_data = pd.concat([combined_data, timeframe_data.rename(columns=renamed_cols)], axis=1)
            
            # Display the combined graph
            st.line_chart(
                combined_data,
                use_container_width=True
            )
            
            # Add a legend explanation
            st.markdown("**Legend:** Each line represents a different timeframe. The timeframe name is included in the legend.")

# Tab 2: Detection Group Radar Chart
with tab2:
    st.subheader("Detection Group Radar Chart")
    
    # Create a date and time selector for the radar chart
    radar_col1, radar_col2 = st.columns(2)
    
    with radar_col1:
        radar_date = st.date_input(
            "Select Date",
            value=df['Toll Date'].min(),
            min_value=df['Toll Date'].min(),
            max_value=df['Toll Date'].max()
        )
    
    with radar_col2:
        radar_time = st.time_input(
            "Select Time",
            value=datetime.strptime("12:00", "%H:%M").time()
        )
    
    # Combine date and time
    radar_datetime = datetime.combine(radar_date, radar_time)
    
    # Filter data for the selected date and time
    radar_mask = (df['Toll Hour'].dt.date == radar_date) & (df['Toll Hour'].dt.hour == radar_time.hour)
    radar_df = df[radar_mask]
    
    # Check if we have data for the selected date and time
    if radar_df.empty:
        st.warning(f"No data available for {radar_date.strftime('%Y-%m-%d')} at {radar_time.strftime('%H:%M')}. Please select a different date or time.")
    else:
        # Group by detection group and calculate CRZ entries
        radar_data = radar_df.groupby('Detection Group')['CRZ Entries'].sum().reset_index()
        
        # Create a Matplotlib radar chart
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
        
        # Set dark theme
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # Number of variables
        num_vars = len(radar_data)
        
        # Compute angle for each axis
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]  # Complete the circle
        
        # Draw one axis per variable + add labels
        plt.xticks(angles[:-1], radar_data['Detection Group'], size=10, color='white')
        
        # Draw y-axis labels
        plt.yticks([0, radar_data['CRZ Entries'].max()/4, radar_data['CRZ Entries'].max()/2, 
                    3*radar_data['CRZ Entries'].max()/4, radar_data['CRZ Entries'].max()], 
                   [0, f"{int(radar_data['CRZ Entries'].max()/4):,}", 
                    f"{int(radar_data['CRZ Entries'].max()/2):,}", 
                    f"{int(3*radar_data['CRZ Entries'].max()/4):,}", 
                    f"{int(radar_data['CRZ Entries'].max()):,}"], 
                   size=8, color='white')
        
        # Plot data
        values = radar_data['CRZ Entries'].values.flatten().tolist()
        values += values[:1]  # Complete the circle
        
        # Plot the data
        ax.plot(angles, values, linewidth=2, linestyle='solid', color='purple')
        ax.fill(angles, values, alpha=0.25, color='purple')
        
        # Add value labels at each point
        for i, (angle, value) in enumerate(zip(angles[:-1], values[:-1])):
            # Calculate position for the label
            x = 1.1 * np.cos(angle - np.pi/2)
            y = 1.1 * np.sin(angle - np.pi/2)
            
            # Add the label with a black outline for better visibility
            text = ax.text(x, y, f"{int(value):,}", 
                          ha='center', va='center', color='white', fontsize=8)
            text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        
        # Add a title
        plt.title(f"CRZ Entries by Detection Group on {radar_date.strftime('%Y-%m-%d')} at {radar_time.strftime('%H:%M')}", 
                  y=1.05, size=12, color='white')
        
        # Adjust layout to prevent clipping
        plt.tight_layout()
        
        # Display the chart
        st.pyplot(fig)
        
        # Save data stamp section
        st.markdown("---")
        st.subheader("Save Data Stamp")
        
        # Create a name for this data stamp
        stamp_name = st.text_input("Name this data stamp", value=f"{radar_date.strftime('%Y-%m-%d')} {radar_time.strftime('%H:%M')}")
        
        # Save button
        if st.button("Save Data Stamp"):
            # Create a dictionary with the data stamp
            stamp_to_save = {
                'name': stamp_name,
                'date': radar_date,
                'time': radar_time,
                'data': radar_data.copy()
            }
            
            # Add to session state
            st.session_state.radar_stamps.append(stamp_to_save)
            st.success(f"Data stamp '{stamp_name}' saved successfully!")
        
        # Display saved data stamps
        if st.session_state.radar_stamps:
            st.subheader("Saved Data Stamps")
            
            # Create a multiselect for selecting data stamps to compare
            stamp_options = [f"{stamp['name']} ({stamp['date'].strftime('%Y-%m-%d')} {stamp['time'].strftime('%H:%M')})" 
                            for stamp in st.session_state.radar_stamps]
            
            selected_stamps = st.multiselect(
                "Select data stamps to compare",
                options=stamp_options,
                default=stamp_options[:min(3, len(stamp_options))] if stamp_options else []
            )
            
            # Option to clear saved data stamps
            if st.button("Clear All Saved Data Stamps"):
                st.session_state.radar_stamps = []
                st.experimental_rerun()
            
            # Display comparison chart if stamps are selected
            if selected_stamps:
                st.subheader("Comparison Chart")
                
                # Create a Matplotlib radar chart for comparison
                fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
                
                # Set dark theme
                fig.patch.set_facecolor('black')
                ax.set_facecolor('black')
                
                # Define colors for different stamps
                colors = ['purple', 'blue', 'green', 'red', 'orange', 'brown', 'pink', 'gray', 'cyan', 'magenta']
                
                # Plot each selected stamp
                for i, stamp_name in enumerate(selected_stamps):
                    # Find the index of the selected stamp
                    idx = stamp_options.index(stamp_name)
                    stamp = st.session_state.radar_stamps[idx]
                    
                    # Get the data for this stamp
                    stamp_data = stamp['data']
                    
                    # Number of variables
                    num_vars = len(stamp_data)
                    
                    # Compute angle for each axis
                    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
                    angles += angles[:1]  # Complete the circle
                    
                    # Draw one axis per variable + add labels (only for the first stamp)
                    if i == 0:
                        plt.xticks(angles[:-1], stamp_data['Detection Group'], size=10, color='white')
                        
                        # Draw y-axis labels
                        max_value = max([max(st['data']['CRZ Entries']) for st in st.session_state.radar_stamps])
                        plt.yticks([0, max_value/4, max_value/2, 3*max_value/4, max_value], 
                                   [0, f"{int(max_value/4):,}", f"{int(max_value/2):,}", 
                                    f"{int(3*max_value/4):,}", f"{int(max_value):,}"], 
                                   size=8, color='white')
                    
                    # Plot data
                    values = stamp_data['CRZ Entries'].values.flatten().tolist()
                    values += values[:1]  # Complete the circle
                    
                    # Plot the data
                    color = colors[i % len(colors)]
                    ax.plot(angles, values, linewidth=2, linestyle='solid', color=color, label=stamp['name'])
                    ax.fill(angles, values, alpha=0.1, color=color)
                    
                    # Add value labels at each point (only for the first stamp to avoid clutter)
                    if i == 0:
                        for j, (angle, value) in enumerate(zip(angles[:-1], values[:-1])):
                            # Calculate position for the label
                            x = 1.1 * np.cos(angle - np.pi/2)
                            y = 1.1 * np.sin(angle - np.pi/2)
                            
                            # Add the label with a black outline for better visibility
                            text = ax.text(x, y, f"{int(value):,}", 
                                          ha='center', va='center', color='white', fontsize=8)
                            text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
                
                # Add a title
                plt.title("CRZ Entries by Detection Group - Comparison", y=1.05, size=12, color='white')
                
                # Add a legend
                plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), facecolor='black', edgecolor='white', labelcolor='white')
                
                # Adjust layout to prevent clipping
                plt.tight_layout()
                
                # Display the chart
                st.pyplot(fig)
        
        # Display the data in a table
        st.subheader("Data Table")
        st.dataframe(radar_data.sort_values('CRZ Entries', ascending=False))

# Additional analysis section
st.markdown("---")
st.subheader("Data Overview")

# Show raw data
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)

# Show time series data
if st.checkbox("Show Time Series Data"):
    st.dataframe(time_series)

# Footer
st.markdown("---")
st.markdown("Data source: NYC Congestion Reduction Zone Data")