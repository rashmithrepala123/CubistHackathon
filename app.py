import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from spider_chart import show_spider_analysis  # Import the spider chart

# Set page config with light theme
st.set_page_config(
    page_title="CRZ Entries Analysis",
    page_icon="🚗",
    layout="wide"
)

# Add navigation with just dashboard and spider chart
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select View",
    ["Data Dashboard", "Spider Chart Analysis"]
)

if page == "Data Dashboard":
    # Initialize session state for saved statistics
    if 'saved_stats' not in st.session_state:
        st.session_state.saved_stats = []

    # Title and description
    st.title("🚗 CRZ Entries Analysis Dashboard")
    st.markdown("""
    This dashboard visualizes the number of Congestion Reduction Zone (CRZ) entries and Excluded Roadway Entries (ERE) over time.
    Use the sidebar to filter and analyze the data.
    """)

    # Sidebar filters
    st.sidebar.header("Filters")

    # Entry type selection
    st.sidebar.subheader("Entry Type")
    show_crz = st.sidebar.checkbox("Show CRZ Entries", value=True)
    show_ere = st.sidebar.checkbox("Show Excluded Roadway Entries", value=False)

    # Load data
    @st.cache_data
    def load_data():
        df = pd.read_csv('congestiondata.csv')
        df['Toll Date'] = pd.to_datetime(df['Toll Date'])
        df['Toll Hour'] = pd.to_datetime(df['Toll Hour'])
        return df

    # Load the data
    df = load_data()

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
        
        # Calculate overall statistics for saving
        overall_stats = {}
        
        if not show_by_group and not show_by_vehicle:
            # Calculate overall statistics
            if show_crz:
                crz_total = time_series['CRZ Entries'].sum()
                crz_avg = time_series['CRZ Entries'].mean()
                crz_max = time_series['CRZ Entries'].max()
                crz_min = time_series['CRZ Entries'].min()
                crz_std = time_series['CRZ Entries'].std()
                crz_median = time_series['CRZ Entries'].median()
                
                overall_stats['CRZ'] = {
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
                
                overall_stats['ERE'] = {
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
            # Display statistics for groups or vehicle classes
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
                        
                        st.markdown("Excluded Roadway Entries:")
                        st.metric("Total", f"{ere_total:,.0f}")
                        st.metric("Average per Hour", f"{ere_avg:,.2f}")
                        st.metric("Maximum", f"{ere_max:,.0f}")
                        st.metric("Minimum", f"{ere_min:,.0f}")
                    
                    st.markdown("---")

    # Save statistics section
    st.markdown("---")
    st.subheader("Save Statistics")

    # Only show save options if we have overall statistics (not grouped)
    if overall_stats:
        # Create a name for this timeframe
        timeframe_name = st.text_input("Name this timeframe", value=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Save button
        if st.button("Save Statistics"):
            # Create a dictionary with the statistics
            stats_to_save = {
                'name': timeframe_name,
                'start_date': start_date,
                'end_date': end_date,
                'stats': overall_stats
            }
            
            # Add to session state
            st.session_state.saved_stats.append(stats_to_save)
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
                    'End Date': saved_stat['end_date']
                }
                
                # Add CRZ stats if available
                if 'CRZ' in saved_stat['stats']:
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
    else:
        st.info("Statistics can only be saved when viewing overall data (not grouped by detection group or vehicle class).")

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

elif page == "Spider Chart Analysis":
    show_spider_analysis() 