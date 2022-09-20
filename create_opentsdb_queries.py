import os

GOPATH = '/home/airth/go/bin'
LOGSPATH = '/home/airth/PycharmProjects/pliroforiaka/opentsdb_queries'
workers = ['1']
queries = ['1000', '10000']
query_types = ["1-host-1-hr", "1-host-12-hr"]
timestamp_start = ""
timestamp_end = "2018-03-01T00:00:00Z"

for query_type in query_types:
    for w in workers:
        for q in queries:
            for i in range(1):

                print(f'Creating: opentsdb_{query_type}_{q}_{w}_logs_{i}.log')
                os.system(F"{GOPATH}/bulk_query_gen -query-type \"{query_type}\" -queries {q} -timestamp-end {timestamp_end} -format opentsdb | "
                          F"awk 'NR>7' > "
                          F"{LOGSPATH}/opentsdb_{query_type}_{q}_{w}_logs_{i}.log")

