# CubistHackathon

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Navigate to a map of New York City showing a simulation of cars:
3. Top-right corner has a dashboard link
   - **Data Dashboard**: View comprehensive entry analysis
   - **Spider Chart Analysis**: Compare entry points using radar visualization

### Data Dashboard Features
- Time-based filtering
- Detection group analysis
- Vehicle class categorization
- Statistical summaries
- Interactive data tables

### Spider Chart Features
- Select specific dates and times
- Save multiple chart states
- Overlay comparisons
- Interactive tooltips
- Clear visualization of entry point patterns

## Data Requirements

The application expects a CSV file (`congestiondata.csv`) with the following columns:
- Toll Date
- Toll Hour
- Detection Group
- Vehicle Class
- CRZ Entries
- Excluded Roadway Entries

## XG Boost
- Select features to include in a boosted decision tree
- Understand the importance of each feature in predicting CRZ_entries
- Find features that more useful in understanding the dataset


## Dependencies

- streamlit>=1.28.0
- pandas>=2.0.0
- plotly>=5.18.0
- numpy>=1.24.0
- python-dateutil>=2.8.2

## Spider Chart Functionality

### Saving Charts
1. Select a date and time
2. Click "Save Current Chart"
3. The chart will be saved for comparison

### Overlay Comparison
1. Enable "Show Saved Charts"
2. New charts will display alongside saved ones
3. Each saved state uses a distinct color

### Clearing Saved Charts
- Use "Clear All Saved Charts" to reset comparisons
- Individual charts maintain unique styling

## Customization

The spider chart visualization can be customized by modifying `spider_chart.py`:
- Color schemes
- Chart dimensions
- Grid styling
- Text formatting
- Hover information

## Performance

The dashboard is optimized for:
- Real-time data processing
- Smooth transitions between views
- Efficient memory usage
- Responsive visualization updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## Who Uses This

- Traffic analysts
- City planners
- Transportation researchers
- Urban development teams

## Acknowledgments

- Streamlit for the web framework
- Plotly for interactive visualizations
- Dataset: https://data.ny.gov/Transportation/MTA-Congestion-Relief-Zone-Vehicle-Entries-Beginni/t6yz-b64h/about_data
