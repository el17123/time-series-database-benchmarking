import json
import requests
import time
from statistics import mean, median
import plotter

def parse_bulk_queries(path_file: str) -> [dict]:

    """
    This function get a file of the queries after the query_generation.
    Parses them and creates json objects for each query in order to use it for the api request.

    :param path_file:
    :return:
    """

    with open(path_file, errors='replace') as f:
        lines = f.readlines()
        index_pos_list = [i for i in range(len(lines)) if lines[i] == '{\n']

        request_bodies = []
        for i in index_pos_list:
            array_string = lines[i:i+35]
            json_str = "".join(x for x in array_string if x != '\n')
            try:
                json_obj = json.loads(json_str)
            except json.decoder.JSONDecodeError:
                print(json_str)

            request_bodies.append(json_obj)

    return request_bodies

def query_data(query_body: dict) -> float:
    """
    This function calls the query API and returns the execution time in milliseconds.

    :param query_body:
    :return:
    """

    url = "http://localhost:4242/api/query/exp?jsonp=callback"

    payload = json.dumps(query_body)
    headers = {
        'Content-Type': 'application/json'
    }

    start_time = time.time()
    response = requests.request("POST", url, headers=headers, data=payload)
    end_time = time.time()

    # print(response)

    return (end_time - start_time)*1000

def collect_metrics(query_response_data: [dict], wallClockTime: float, batchSize: int = 1, totalQueries: int = 1000, workers: int = 1) -> dict:

    # Initialize
    metrics = {
        'max': [],
        'mean': [],
        'min': [],
        'sum': [],
        'batchSize': batchSize,
        'queryRate': totalQueries/wallClockTime,
        'totalQueries': totalQueries,
        'wallClockTime': wallClockTime,
        'workers': workers
    }

    # Parse the data
    for x in query_response_data.values():
        metrics['max'].append(x['max'])
        metrics['min'].append(x['min'])
        metrics['mean'].append(x['mean'])
        metrics['sum'].append(x['sum'])

    return metrics

if __name__ == "__main__":

    query_bodies = parse_bulk_queries('opentsdb_queries/opentsdb_1-host-1-hr_1000_1_logs_0.log')

    # Run the queries and get the times
    query_times = {}
    min_time = 100.0
    max_time = 0.0
    total_time = 0.0
    for q_i, body in enumerate(query_bodies):

        # Initialize the list for the times
        index = int(q_i / 100)
        if index not in query_times.keys():
            query_times[index] = {
                'times_ms': [],
                'min': min_time,
                'max': max_time,
                'mean': 0.0
            }

        # Run the query
        query_time = query_data(query_body=body)

        # Keep the stats
        max_time = max(max_time, query_time)
        min_time = min(min_time, query_time)
        total_time += query_time

        # Save them for each 100
        query_times[index]['min'] = min_time
        query_times[index]['max'] = max_time
        query_times[index]['mean'] = total_time/(q_i+1)
        query_times[index]['sum'] = total_time

        # Also keep the actual times
        query_times[index]['times_ms'].append(query_time)

    data_metrics = collect_metrics(
        query_response_data=query_times,
        wallClockTime=total_time/1000,
        totalQueries=len(query_bodies),
        workers=1
    )

    # Plot the results
    data_metrics_list = [data_metrics]
    plotter.plot_metrics(
        logs_metrics=data_metrics_list,
        database_name='InfluxDB',
        num_queries=data_metrics_list[0]['totalQueries'],
        workers=data_metrics_list[0]['workers'],
        query_type='1-host-12-hr'
    )

print()
