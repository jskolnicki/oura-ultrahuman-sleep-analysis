import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from oura_api import get_oura_sleep_data, process_sleep_data
from ultrahuman_api import get_ultrahuman_sleep_data, process_ultrahuman_sleep_data
import seaborn as sns
import numpy as np


def fetch_and_process_data(start_date, end_date):
    # Fetch and process Oura data
    oura_raw_data = get_oura_sleep_data(start_date, end_date, DATES_TO_EXCLUDE)
    oura_processed_data = process_sleep_data(oura_raw_data, DATES_TO_EXCLUDE) if oura_raw_data else []

    # Fetch and process Ultrahuman data
    ultrahuman_raw_data = get_ultrahuman_sleep_data(start_date, end_date, DATES_TO_EXCLUDE)
    ultrahuman_processed_data = process_ultrahuman_sleep_data(ultrahuman_raw_data, DATES_TO_EXCLUDE) if ultrahuman_raw_data else []

    return oura_processed_data, ultrahuman_processed_data

def create_dataframes(oura_data, ultrahuman_data, anecdotal_data):
    oura_df = pd.DataFrame(oura_data)
    ultrahuman_df = pd.DataFrame(ultrahuman_data)

    # Convert 'day' column to datetime for easier manipulation
    oura_df['day'] = pd.to_datetime(oura_df['day'])
    ultrahuman_df['day'] = pd.to_datetime(ultrahuman_df['day'])

    # Merge dataframes
    merged_df = anecdotal_data.merge(oura_df, left_on='Date', right_on='day', how='left')
    merged_df = merged_df.merge(ultrahuman_df, on='day', how='left', suffixes=('_oura', '_ultrahuman'))

    # Handle missing data
    for col in merged_df.columns:
        if merged_df[col].dtype == 'float64' or merged_df[col].dtype == 'int64':
            merged_df[col] = merged_df[col].fillna(0)

    return merged_df

def calculate_errors(df):
    # Absolute error (for magnitude-based analyses)
    df['sleep_start_error_abs_oura'] = abs(df['jared_sleep_start'] - df['sleeptime_start_oura'])
    df['sleep_start_error_abs_ultrahuman'] = abs(df['jared_sleep_start'] - df['sleeptime_start_ultrahuman'])
    df['total_sleep_error_abs_oura'] = abs(df['jared_total_sleep'] - df['total_sleep_duration_oura'])
    df['total_sleep_error_abs_ultrahuman'] = abs(df['jared_total_sleep'] - df['total_sleep_duration_ultrahuman'])
    df['sleep_end_error_abs_oura'] = abs(df['jared_sleep_end'] - df['sleeptime_end_oura'])
    df['sleep_end_error_abs_ultrahuman'] = abs(df['jared_sleep_end'] - df['sleeptime_end_ultrahuman'])

    # Directional error (for direction-based analyses)
    df['sleep_start_error_oura'] = df['sleeptime_start_oura'] - df['jared_sleep_start']
    df['sleep_start_error_ultrahuman'] = df['sleeptime_start_ultrahuman'] - df['jared_sleep_start']
    df['total_sleep_error_oura'] = df['total_sleep_duration_oura'] - df['jared_total_sleep']
    df['total_sleep_error_ultrahuman'] = df['total_sleep_duration_ultrahuman'] - df['jared_total_sleep']
    df['sleep_end_error_oura'] = df['sleeptime_end_oura'] - df['jared_sleep_end']
    df['sleep_end_error_ultrahuman'] = df['sleeptime_end_ultrahuman'] - df['jared_sleep_end']
    
    return df

def plot_comparisons(df):
    metrics = [
        ('sleep_start', 'sleeptime_start_oura', 'sleeptime_start_ultrahuman'),
        ('total_sleep', 'total_sleep_duration_oura', 'total_sleep_duration_ultrahuman'),
        ('sleep_end', 'sleeptime_end_oura', 'sleeptime_end_ultrahuman')
    ]
    fig, axes = plt.subplots(3, 1, figsize=(12, 18))
    fig.suptitle('Sleep Metrics Comparison: Anecdotal vs Oura vs Ultrahuman')

    for i, (metric, oura_col, ultrahuman_col) in enumerate(metrics):
        ax = axes[i]
        ax.plot(df['Date'], df[f'jared_{metric}'], label='Anecdotal', marker='o')
        ax.plot(df['Date'], df[oura_col], label='Oura', marker='s')
        ax.plot(df['Date'], df[ultrahuman_col], label='Ultrahuman', marker='^')
        ax.set_title(f'{metric.replace("_", " ").title()}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Minutes')
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.savefig('output/graphs/sleep_metrics_comparison.png')
    plt.close()

def plot_errors(df):
    metrics = ['sleep_start', 'total_sleep', 'sleep_end']
    fig, axes = plt.subplots(3, 1, figsize=(15, 22))
    fig.suptitle('Error Comparison: Oura vs Ultrahuman', fontsize=24, y=0.95)

    for i, metric in enumerate(metrics):
        ax = axes[i]
        ax.bar(df['Date'], df[f'{metric}_error_abs_oura'], width=0.4, align='edge', label='Oura Error')
        ax.bar(df['Date'], df[f'{metric}_error_abs_ultrahuman'], width=-0.4, align='edge', label='Ultrahuman Error')
        ax.set_title(f'{metric.replace("_", " ").title()} Error', fontsize=20)
        ax.set_xlabel('Date', fontsize=16)
        ax.set_ylabel('Minutes', fontsize=16)
        
        ax.legend(fontsize=15, loc='upper right')
        
        ax.grid(True)
        
        # Set major ticks for every other day (with labels)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        
        # Set minor ticks for every day (without labels)
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        
        # Customize tick parameters
        ax.tick_params(axis='x', which='major', labelsize=14, length=9, width=1)
        ax.tick_params(axis='x', which='minor', length=6, width=1, labelsize=0)
        ax.tick_params(axis='y', which='major', labelsize=14, length=6, width=1)
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        ax.set_xlim(df['Date'].min() - pd.Timedelta(days=0.5), 
                    df['Date'].max() + pd.Timedelta(days=0.5))

    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.3, bottom=0.1)
    plt.savefig('output/graphs/error_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_error_distributions(df):
    metrics = ['sleep_start', 'total_sleep', 'sleep_end']
    bin_sizes = {'sleep_start': 5, 'total_sleep': 10, 'sleep_end': 5}
    fig, axes = plt.subplots(3, 2, figsize=(20, 24))
    
    # Set the main title with even larger font size
    fig.suptitle('Error Distributions: Oura vs Ultrahuman', fontsize=34, y=0.95)

    oura_color = '#0052CC'
    ultra_color = '#FF7F00'

    for i, metric in enumerate(metrics):
        oura_data = df[f'{metric}_error_abs_oura']
        ultra_data = df[f'{metric}_error_abs_ultrahuman']
        
        x_min = min(min(oura_data.min(), ultra_data.min()), 0)
        x_max = max(oura_data.max(), ultra_data.max())
        x_max += (x_max - x_min) * 0.1
        
        bin_size = bin_sizes[metric]
        bins = np.arange(x_min, x_max + bin_size, bin_size)

        # Plot Oura
        sns.histplot(data=oura_data, ax=axes[i, 0], kde=True, color=oura_color, bins=bins)
        axes[i, 0].set_title(f'Oura {metric.replace("_", " ").title()} Error', fontsize=26)
        axes[i, 0].set_xlabel('Error (minutes)', fontsize=20)
        axes[i, 0].set_ylabel('Count', fontsize=20)
        axes[i, 0].set_xlim(x_min, x_max)
        axes[i, 0].tick_params(axis='both', which='major', labelsize=20)

        # Plot Ultrahuman
        sns.histplot(data=ultra_data, ax=axes[i, 1], kde=True, color=ultra_color, bins=bins)
        axes[i, 1].set_title(f'Ultrahuman {metric.replace("_", " ").title()} Error', fontsize=26)
        axes[i, 1].set_xlabel('Error (minutes)', fontsize=20)
        axes[i, 1].set_ylabel('Count', fontsize=20)
        axes[i, 1].set_xlim(x_min, x_max)
        axes[i, 1].tick_params(axis='both', which='major', labelsize=20)

        y_max = max(axes[i, 0].get_ylim()[1], axes[i, 1].get_ylim()[1])
        y_max = np.ceil(y_max)
        axes[i, 0].set_ylim(0, y_max)
        axes[i, 1].set_ylim(0, y_max)

        axes[i, 0].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        axes[i, 1].yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    plt.tight_layout()
    # Adjust the layout to accommodate the larger main title
    plt.subplots_adjust(top=0.90, hspace=0.24)
    plt.savefig('output/graphs/error_distributions.png', dpi=300)
    plt.close()

def plot_error_direction(df):
    # Prepare the data
    metrics = ['sleep_start', 'total_sleep', 'sleep_end']
    plot_data = []

    for metric in metrics:
        oura_errors = df[f'{metric}_error_oura']
        ultra_errors = df[f'{metric}_error_ultrahuman']
        
        plot_data.extend([
            {'Metric': metric.replace('_', ' ').title(), 'Device': 'Oura', 'Error': error}
            for error in oura_errors
        ])
        plot_data.extend([
            {'Metric': metric.replace('_', ' ').title(), 'Device': 'Ultrahuman', 'Error': error}
            for error in ultra_errors
        ])

    plot_df = pd.DataFrame(plot_data)

    # Create the plot
    plt.figure(figsize=(15, 10))
    sns.set_style("whitegrid")
    
    ax = sns.violinplot(x='Metric', y='Error', hue='Device', data=plot_df, 
                        split=True, inner="quartile", cut=0)

    # Customize the plot
    plt.title('Error Direction and Magnitude: Oura vs Ultrahuman', fontsize=20)
    plt.xlabel('Metric', fontsize=16)
    plt.ylabel('Error (minutes)', fontsize=16)
    plt.axhline(y=0, color='r', linestyle='--')  # Add a line at y=0 for reference

    # Adjust legend and labels
    plt.legend(title='Device', fontsize=12, title_fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=12)

    # Add annotations
    plt.text(0.02, 0.98, 'Above 0: Overestimation', transform=ax.transAxes, fontsize=12, va='top')
    plt.text(0.02, 0.02, 'Below 0: Underestimation', transform=ax.transAxes, fontsize=12, va='bottom')

    plt.tight_layout()
    plt.savefig('output/graphs/error_direction.png', dpi=300)
    plt.close()


if __name__ == '__main__':
    start_date = "2024-06-20"
    end_date = "2024-07-22"

    DATES_TO_EXCLUDE = ['2024-06-21', '2024-06-24', '2024-06-26', '2024-07-16']

    # Anecdotal data
    anecdotal_data_df = pd.read_csv("anecdotal_sleep_data.csv")
    anecdotal_data_df['Date'] = pd.to_datetime(anecdotal_data_df['Date'], format='%m/%d/%Y')
    anecdotal_data_df = anecdotal_data_df[~anecdotal_data_df['Date'].dt.strftime('%Y-%m-%d').isin(DATES_TO_EXCLUDE)]

    oura_data, ultrahuman_data = fetch_and_process_data(start_date, end_date, DATES_TO_EXCLUDE)
    merged_df = create_dataframes(oura_data, ultrahuman_data, anecdotal_data_df)
    merged_df = calculate_errors(merged_df)

    plot_comparisons(merged_df)
    plot_errors(merged_df)
    plot_error_distributions(merged_df)
    plot_error_direction(merged_df)

    # Calculate average errors
    avg_errors = {
        'Oura': {
            'sleep_start': merged_df['sleep_start_error_oura'].mean(),
            'total_sleep': merged_df['total_sleep_error_oura'].mean(),
            'sleep_end': merged_df['sleep_end_error_oura'].mean()
        },
        'Ultrahuman': {
            'sleep_start': merged_df['sleep_start_error_ultrahuman'].mean(),
            'total_sleep': merged_df['total_sleep_error_ultrahuman'].mean(),
            'sleep_end': merged_df['sleep_end_error_ultrahuman'].mean()
        }
    }

    print("Average Errors:")
    print(pd.DataFrame(avg_errors))

    # Save the merged dataframe to CSV for further analysis
    merged_df.to_csv('output/csv/sleep_data_comparison.csv', index=False)