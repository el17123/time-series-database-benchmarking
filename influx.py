import json
import os
import plotter

def read_influx_logs(path_file: str) -> [dict]:

    # Opening JSON file
    f = open(path_file)

    # returns JSON object as a dictionary
    data = json.load(f)

    # Closing file
    f.close()

    return data

def collect_metrics(logs_data: [dict]) -> dict:

    # Initialize
    metrics = {
        'max': [],
        'mean': [],
        'min': [],
        'sum': [],
        'batchSize': logs_data[-1]['batchSize'],
        'queryRate': logs_data[-1]['queryRate'],
        'totalQueries': logs_data[-1]['totalQueries'],
        'wallClockTime': logs_data[-1]['wallClockTime'],
        'workers': logs_data[-1]['workers']
    }

    # Parse the data
    for x in logs_data[:-1]:
        metrics['max'].append(x['all queries']['max'])
        metrics['min'].append(x['all queries']['min'])
        metrics['mean'].append(x['all queries']['mean'])
        metrics['sum'].append(x['all queries']['sum'])

    return metrics

if __name__ == "__main__":

    # Collect data for all the log files
    logs_folder_path = "influx_logs/big_dataset"
    for logs_package in os.listdir(logs_folder_path):
        name = logs_package.split('_')[1]
        print(name)

        data_metrics_list = []
        for log_file in os.listdir(f"{logs_folder_path}/{logs_package}"):

            data = read_influx_logs(path_file=f"{logs_folder_path}/{logs_package}/{log_file}")
            data_metrics = collect_metrics(logs_data=data)
            data_metrics_list.append(data_metrics)

        # Plot the results
        plotter.plot_metrics(
            logs_metrics=data_metrics_list,
            database_name='InfluxDB',
            num_queries=data_metrics_list[0]['totalQueries'],
            workers=data_metrics_list[0]['workers'],
            query_type=name,
            save=True
        )
