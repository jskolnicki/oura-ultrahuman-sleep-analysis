import requests
import os
from datetime import datetime, timedelta
import csv
from tabulate import tabulate

def get_ultrahuman_sleep_data(start_date, end_date=None, dates_to_exclude=[]):
    AUTH_TOKEN = os.environ["ULTRAHUMAN_AUTHORIZATION_TOKEN"]
    USER_EMAIL = os.environ["ULTRAHUMAN_EMAIL"]
    url = "https://partner.ultrahuman.com/api/v1/metrics"
    headers = {"Authorization": AUTH_TOKEN}

    if end_date is None:
        end_date = start_date

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    
    sleep_data_list = []

    current_date = start_date
    while current_date <= end_date:
        if current_date.date().isoformat() not in dates_to_exclude:
            params = {
                "email": USER_EMAIL,
                "date": current_date.isoformat()
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                sleep_data = response.json()['data']['metric_data'][6]
                sleep_data_list.append(sleep_data)
            else:
                print(f"Error retrieving Ultrahuman data for {current_date.isoformat()}: {response.status_code}")
                print(response.text)

        current_date += timedelta(days=1)

    return sleep_data_list

def process_ultrahuman_sleep_data(sleep_data_list, dates_to_exclude=[]):
    processed_data = []
    daily_sleep_data = {}

    print(f"Total sleep data entries: {len(sleep_data_list)}")

    def time_to_minutes(dt, reference_date):
        delta = dt - reference_date
        return delta.days * 24 * 60 + delta.seconds // 60

    for sleep_data in sleep_data_list:
        bedtime_start = datetime.fromtimestamp(sleep_data['object']['bedtime_start'])
        bedtime_end = datetime.fromtimestamp(sleep_data['object']['bedtime_end'])
        day = bedtime_end.date().isoformat()  # Use the end date as the key
        
        if day not in dates_to_exclude:
            reference_date = bedtime_end.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # If we haven't seen this day before, or if this sleep session is longer than the previous one
            if day not in daily_sleep_data or (bedtime_end - bedtime_start) > daily_sleep_data[day]['duration']:
                daily_sleep_data[day] = {
                    'data': sleep_data,
                    'duration': bedtime_end - bedtime_start,
                    'reference_date': reference_date
                }

    for day, day_sleep_data in daily_sleep_data.items():
        # Rest of the processing code remains the same
        sleep_data = day_sleep_data['data']
        reference_date = day_sleep_data['reference_date']
        bedtime_start = datetime.fromtimestamp(sleep_data['object']['bedtime_start'])
        bedtime_end = datetime.fromtimestamp(sleep_data['object']['bedtime_end'])

        bedtime_start_minutes = time_to_minutes(bedtime_start, reference_date)
        bedtime_end_minutes = time_to_minutes(bedtime_end, reference_date)

        sleep_stages = sleep_data['object']['sleep_stages']
        deep_sleep = next((stage for stage in sleep_stages if stage['type'] == 'deep_sleep'), {'stage_time': 0})
        light_sleep = next((stage for stage in sleep_stages if stage['type'] == 'light_sleep'), {'stage_time': 0})
        rem_sleep = next((stage for stage in sleep_stages if stage['type'] == 'rem_sleep'), {'stage_time': 0})
        awake = next((stage for stage in sleep_stages if stage['type'] == 'awake'), {'stage_time': 0})

        sleep_graph = sleep_data['object']['sleep_graph']['data']
        non_awake_segments = [segment for segment in sleep_graph if segment['type'] != 'awake']
        
        if non_awake_segments:
            sleeptime_start = datetime.fromtimestamp(min(segment['start'] for segment in non_awake_segments))
            sleeptime_end = datetime.fromtimestamp(max(segment['end'] for segment in non_awake_segments))
            
            sleeptime_start_minutes = time_to_minutes(sleeptime_start, reference_date)
            sleeptime_end_minutes = time_to_minutes(sleeptime_end, reference_date)

            awake_time_filtered = sum(
                segment['end'] - segment['start'] 
                for segment in sleep_graph 
                if segment['type'] == 'awake' and sleeptime_start.timestamp() <= segment['start'] < sleeptime_end.timestamp()
            ) // 60  # Convert to minutes
        else:
            sleeptime_start_minutes = bedtime_start_minutes
            sleeptime_end_minutes = bedtime_end_minutes
            awake_time_filtered = 0

        processed_entry = {
            'day': day,
            'bedtime_start': bedtime_start_minutes,
            'bedtime_end': bedtime_end_minutes,
            'sleeptime_start': sleeptime_start_minutes,
            'sleeptime_end': sleeptime_end_minutes,
            'deep_sleep_duration': deep_sleep['stage_time'] // 60,
            'awake_time_filtered': awake_time_filtered,
            'light_sleep_duration': light_sleep['stage_time'] // 60,
            'rem_sleep_duration': rem_sleep['stage_time'] // 60,
            'total_sleep_duration': sum(stage['stage_time'] for stage in sleep_stages if stage['type'] != 'awake') // 60
        }
        processed_data.append(processed_entry)

    return sorted(processed_data, key=lambda x: x['day'])
    

def print_formatted_sleep_data(processed_data):
    """
    Print the processed sleep data in a formatted table.
    """
    headers = ["Day", "Bedtime Start", "Bedtime End", "Sleep Start", "Sleep End", 
               "Deep Sleep", "Awake (Filtered)", "Light Sleep", "REM Sleep", "Total Sleep"]
    
    table_data = []
    for entry in processed_data:
        row = [
            entry['day'],
            f"{entry['bedtime_start']} min",
            f"{entry['bedtime_end']} min",
            f"{entry['sleeptime_start']} min",
            f"{entry['sleeptime_end']} min",
            f"{entry['deep_sleep_duration']} min",
            f"{entry['awake_time_filtered']} min",
            f"{entry['light_sleep_duration']} min",
            f"{entry['rem_sleep_duration']} min",
            f"{entry['total_sleep_duration']} min"
        ]
        table_data.append(row)
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def save_sleep_data_to_csv(processed_data, filename="ultrahuman_sleep_data.csv"):
    """
    Save the processed sleep data to a CSV file.
    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["Day", "Bedtime Start", "Bedtime End", "Sleep Start", "Sleep End", 
                      "Deep Sleep", "Awake (Filtered)", "Light Sleep", "REM Sleep", "Total Sleep"]
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
                "Awake (Filtered)": entry['awake_time_filtered'],
                "Light Sleep": entry['light_sleep_duration'],
                "REM Sleep": entry['rem_sleep_duration'],
                "Total Sleep": entry['total_sleep_duration']
            })
    print(f"Sleep data saved to {filename}")


if __name__ == '__main__':
    start_date = '2024-06-20'
    end_date = '2024-07-02'

    ultrahuman_raw_data = get_ultrahuman_sleep_data(start_date, end_date)
    if ultrahuman_raw_data:
        print("\nRaw data for 2024-07-01:")
        for entry in ultrahuman_raw_data:
            if datetime.fromtimestamp(entry['object']['bedtime_start']).date().isoformat() == '2024-07-01':
                print(entry)
        
        ultrahuman_processed_data = process_ultrahuman_sleep_data(ultrahuman_raw_data)
        print("\nUltrahuman Sleep Data:")
        print_formatted_sleep_data(ultrahuman_processed_data)
        save_sleep_data_to_csv(ultrahuman_processed_data, "ultrahuman_sleep_data.csv")