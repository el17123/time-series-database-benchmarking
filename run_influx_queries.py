import os

def refactor_log_files(folder_path: str):

    for file_name in os.listdir(folder_path):

        fin = open(f"{folder_path}/{file_name}", "rt")
        fout = open(f"{folder_path}/{file_name[:-4]}.json", "wt")

        print(f'\t {file_name}')

        # Add commas
        fout.write('[')
        for line in fin:
            fout.write(line.replace('}{"InfluxDB (InfluxQL)', '},{"InfluxDB (InfluxQL)'))
        fout.write(']')

        fin.close()
        fout.close()

        os.remove(f"{folder_path}/{file_name}")

GOPATH = '/home/airth/go/bin'
LOGSPATH = '/home/airth/PycharmProjects/pliroforiaka/influx_logs/big_dataset'
workers = ['1', '5']
queries = ['1000', '10000']
query_types = ["1-host-1-hr", "1-host-12-hr"]
timestamp_start = ""
timestamp_end = "2018-03-01T00:00:00Z"

for query_type in query_types:
    for w in workers:
        for q in queries:
            for i in range(1):

                print(f'Creating: influx_{query_type}_{q}_{w}_logs_{i}.log')

                if not os.path.exists(f'{LOGSPATH}/influx_{query_type}_{q}_{w}'):
                    os.makedirs(f'{LOGSPATH}/influx_{query_type}_{q}_{w}')

                os.system(F'{GOPATH}/bulk_query_gen -query-type \"{query_type}\" -queries {q} -timestamp-end {timestamp_end} | '
                          F'{GOPATH}/query_benchmarker_influxdb -workers {w} > '
                          F'{LOGSPATH}/influx_{query_type}_{q}_{w}/influx_{query_type}_{q}_{w}_logs_{i}.log')

            print(f'Refactoring...')
            refactor_log_files(
                folder_path=f'{LOGSPATH}/influx_{query_type}_{q}_{w}'
            )

