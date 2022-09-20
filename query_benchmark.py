import plotter
import influx
import opentsdb

# Initialize the parameters
workers_list = ['1']
queries_list = ['1000', '10000']
query_types = ["1-host-1-hr", "1-host-12-hr"]

for query_type in query_types:
    for w in workers_list:
        for q in queries_list:

            print(f"{query_type}_{q}_{w}")
            data_metrics_list = []

            # Create Influx data metrics
            influx_logs_folder = "influx_logs/big_dataset"
            logs_package = f"influx_{query_type}_{q}_{w}"
            data = influx.read_influx_logs(path_file=f"{influx_logs_folder}/{logs_package}/{logs_package}_logs_0.json")
            data_metrics = influx.collect_metrics(logs_data=data)
            data_metrics_list.append(data_metrics)

            # Parse the OpenTSDB queries and run them and collect the data metrics
            query_bodies = opentsdb.parse_bulk_queries(f'opentsdb_queries/opentsdb_{query_type}_{q}_{w}_logs_0.log')

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
                query_time = opentsdb.query_data(query_body=body)

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

            data_metrics = opentsdb.collect_metrics(
                query_response_data=query_times,
                wallClockTime=total_time/1000,
                totalQueries=len(query_bodies),
                workers=1
            )
            data_metrics_list.append(data_metrics)

            print(f"\t InfluxDB query rate:   {data_metrics_list[0]['queryRate']} ({data_metrics_list[0]['totalQueries']})")
            print(f"\t OpenTSDB query rate: {data_metrics_list[1]['queryRate']} ({data_metrics_list[1]['totalQueries']})")
            print('-----------------------------')

            plotter.plot_metrics(
                logs_metrics=data_metrics_list,
                database_name='InfluxDB vs OpenTSDB',
                num_queries=data_metrics_list[0]['totalQueries'],
                workers=data_metrics_list[0]['workers'],
                query_type=query_type,
                legends=["Influx", "OpenTSDB"],
                save=True
            )
