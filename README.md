# Oura vs Ultrahuman Ring Analysis

## Overview
This project compares sleep tracking data from the Oura Ring and the Ultrahuman Ring against manually recorded sleep data. The analysis aims to evaluate the accuracy and reliability of these wearable devices in tracking sleep metrics.

## Features
- Fetches sleep data from Oura and Ultrahuman APIs
- Processes and compares the data with manually recorded sleep information
- Generates various visualizations to illustrate the comparison:
  - Sleep metrics comparison
  - Error comparison
  - Error distributions
  - Error direction and magnitude

## Requirements
- Python 3.7+
- pandas
- matplotlib
- seaborn
- numpy
- scipy

## Setup
1. Clone this repository
2. (Optional but recommended) Create a virtual environment:
3. Install the required packages: pip install -r requirements.txt
4. Set up your environment variables (see Configuration section)

## Configuration
Set the following environment variables:
- `ULTRAHUMAN_AUTHORIZATION_TOKEN`: Your Ultrahuman API authorization token
- `ULTRAHUMAN_EMAIL`: Your Ultrahuman account email
- `OURA_ACCESS_TOKEN`: Your Oura API access token

You can set these environment variables in your shell or use a `.env` file with a package like `python-dotenv`.

## Usage
1. Ensure your environment variables are set (see Configuration section)
2. Run the main analysis script: python main_analysis.py

## Data
- `anecdotal_sleep_data.csv`: Manually recorded sleep data
- `sleep_history.csv`: Manually recorded sleep data
- Oura and Ultrahuman data are fetched via their respective APIs

## Output
- Graphs are saved in the `output/graphs/` directory
- CSV output is saved in the `output/csv/` directory

## Analysis Components
1. **Data Fetching and Processing**: 
- Retrieves data from Oura and Ultrahuman APIs
- Processes and aligns the data with manual records
2. **Error Calculation**: 
- Computes the difference between device-recorded and manually-recorded sleep metrics
3. **Visualizations**:
- Sleep Metrics Comparison: Plots sleep start, total sleep, and sleep end times for all three data sources
- Error Comparison: Bar charts showing the error magnitude for each metric and device
- Error Distributions: Histograms with KDE showing the distribution of errors for each metric and device
- Error Direction: Violin plots illustrating the tendency of each device to over- or underestimate sleep metrics

## Contributing
Contributions to improve the analysis or extend the project are welcome. Please feel free to submit issues or pull requests.