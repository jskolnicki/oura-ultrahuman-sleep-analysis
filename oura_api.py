import os
import requests
from datetime import datetime, timedelta, date
import csv
from tabulate import tabulate

ACCESS_TOKEN = os.environ['OURA_ACCESS_TOKEN']

def get_oura_sleep_data(start_date, end_date=None, dates_to_exclude=[]):
    """
    Fetch Oura sleep data for a specified date range.

    Parameters:
    start_date (str): Start date in 'YYYY-MM-DD' format. This represents the day you woke up from that night's sleep.
    end_date (str, optional): End date in 'YYYY-MM-DD' format. 
                              If not provided, returns data for start_date only.
    dates_to_exclude (list): List of dates to exclude in 'YYYY-MM-DD' format.

    Returns:
    list: A list of dictionaries containing sleep data for each day in the range.
    """
    start_date = date.fromisoformat(start_date)
    
    if end_date is None:
        end_date = start_date
    else:
        end_date = date.fromisoformat(end_date)
    
    base_url = "https://api.ouraring.com/v2/usercollection/sleep"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": (end_date + timedelta(days=1)).isoformat()
    }

    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()['data']

        # Grouping and filtering by day to keep only the longest session
        sleep_data_by_day = {}
        for session in data:
            day = session['day']
            if day not in dates_to_exclude:
                total_sleep_duration = session['deep_sleep_duration'] + session['light_sleep_duration'] + session['rem_sleep_duration'] if 'rem_sleep_duration' in session else 0
                if day not in sleep_data_by_day or total_sleep_duration > sleep_data_by_day[day]['total_sleep_duration']:
                    sleep_data_by_day[day] = session
                    sleep_data_by_day[day]['total_sleep_duration'] = total_sleep_duration

        # Convert the dictionary back to a sorted list
        filtered_data = sorted(sleep_data_by_day.values(), key=lambda x: x['day'])
        return filtered_data
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def process_sleep_data(sleep_data_list, dates_to_exclude=[]):
    def time_to_minutes(time_str):
        time = datetime.fromisoformat(time_str)
        minutes = time.hour * 60 + time.minute
        if time.hour < 12:
            minutes += 24 * 60  # Add 24 hours if it's AM
        return minutes - 24 * 60  # Subtract 24 hours to get the correct range

    def parse_sleep_phases(sleep_phase_str):
        return [int(phase) for phase in sleep_phase_str]

    processed_data = []

    for sleep_data in sleep_data_list:
        if sleep_data['day'] not in dates_to_exclude:
            # Rest of the processing code remains the same
            bedtime_start = time_to_minutes(sleep_data['bedtime_start'])
            bedtime_end = time_to_minutes(sleep_data['bedtime_end'])

            # Process sleep phases
            sleep_phases = parse_sleep_phases(sleep_data['sleep_phase_5_min'])
            phase_duration = 5  # Each phase represents 5 minutes

            # Find sleeptime_start
            start_index = next((i for i, phase in enumerate(sleep_phases) if phase != 4), None)
            sleeptime_start = bedtime_start + (start_index * phase_duration if start_index is not None else 0)

            # Find sleeptime_end
            end_index = next((len(sleep_phases) - i - 1 for i, phase in enumerate(reversed(sleep_phases)) if phase != 4), None)
            sleeptime_end = bedtime_start + ((end_index + 1) * phase_duration if end_index is not None else len(sleep_phases) * phase_duration)

            # Calculate awake_time_filtered using both methods
            awake_time_filtered_phases = sum(1 for phase in sleep_phases[start_index:end_index+1] if phase == 4) * phase_duration
            
            total_awake_time = sleep_data['awake_time'] // 60  # Convert to minutes
            trimmed_time = (sleeptime_start - bedtime_start) + (bedtime_end - sleeptime_end)
            awake_time_filtered_subtraction = max(0, total_awake_time - trimmed_time)

            processed_entry = {
                'day': sleep_data['day'],
                'bedtime_start': bedtime_start,
                'bedtime_end': bedtime_end,
                'sleeptime_start': sleeptime_start,
                'sleeptime_end': sleeptime_end,
                'deep_sleep_duration': sleep_data['deep_sleep_duration'] // 60,
                'awake_time_filtered_phases': awake_time_filtered_phases,
                'awake_time_filtered_subtraction': awake_time_filtered_subtraction,
                'light_sleep_duration': sleep_data['light_sleep_duration'] // 60,
                'rem_sleep_duration': sleep_data['rem_sleep_duration'] // 60,
                'total_sleep_duration': sleep_data['total_sleep_duration'] // 60
            }
            processed_data.append(processed_entry)

    return processed_data

def print_formatted_sleep_data(processed_data):
    """
    Print the processed sleep data in a formatted table.
    """
    headers = ["Day", "Bedtime Start", "Bedtime End", "Sleep Start", "Sleep End", 
               "Deep Sleep", "Awake (Phases)", "Awake (Subtraction)", "Light Sleep", "REM Sleep", "Total Sleep"]
    
    table_data = []
    for entry in processed_data:
        row = [
            entry['day'],
            f"{entry['bedtime_start']} min",
            f"{entry['bedtime_end']} min",
            f"{entry['sleeptime_start']} min",
            f"{entry['sleeptime_end']} min",
            f"{entry['deep_sleep_duration']} min",
            f"{entry['awake_time_filtered_phases']} min",
            f"{entry['awake_time_filtered_subtraction']} min",
            f"{entry['light_sleep_duration']} min",
            f"{entry['rem_sleep_duration']} min",
            f"{entry['total_sleep_duration']} min"
        ]
        table_data.append(row)
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def save_sleep_data_to_csv(processed_data, filename="csv/oura_sleep_data.csv"):
    """
    Save the processed sleep data to a CSV file.
    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["Day", "Bedtime Start", "Bedtime End", "Sleep Start", "Sleep End", 
                      "Deep Sleep", "Awake (Phases)", "Awake (Subtraction)", "Light Sleep", "REM Sleep", "Total Sleep"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in processed_data:
            writer.writerow({
                "Day": entry['day'],
                "Bedtime Start": entry['bedtime_start'],
                "Bedtime End": entry['bedtime_end'],
                "Sleep Start": entry['sleeptime_start'],
                "Sleep End": entry['sleeptime_end'],
                "Deep Sleep": entry['deep_sleep_duration'],
                "Awake (Phases)": entry['awake_time_filtered_phases'],
                "Awake (Subtraction)": entry['awake_time_filtered_subtraction'],
                "Light Sleep": entry['light_sleep_duration'],
                "REM Sleep": entry['rem_sleep_duration'],
                "Total Sleep": entry['total_sleep_duration']
            })
    print(f"Sleep data saved to {filename}")


if __name__ == '__main__':
    raw_data = get_oura_sleep_data("2024-06-20", "2024-07-02")
    if raw_data:
        processed_data = process_sleep_data(raw_data)
        print_formatted_sleep_data(processed_data)
        save_sleep_data_to_csv(processed_data)