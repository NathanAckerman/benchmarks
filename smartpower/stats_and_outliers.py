import os
import statistics
import csv
import numpy as np
from sklearn.ensemble import IsolationForest

all_edp_mappings = []
all_ed2p_mappings = []
hm_for_outliers = {}
hm_for_stats = {}

def main():
    benchmarks = os.listdir()
    benchmarks = [b for b in benchmarks if "." not in b]
    for bmc in benchmarks:
        generate_analysis(bmc)


def write_file_as_csv(filename, data):
    with open(filename, 'w+', newline='\n') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_NONE)
        for line in data:
            wr.writerow(line)

def generate_analysis(bmc):
    all_freqs = get_available_frequencies_big()
    data_files = os.listdir(bmc)
    all_run_data = []
    for freq in all_freqs:
        freq_files = [f for f in data_files if f.split("_")[0] == str(freq)] 
        for f in freq_files:
            run_data = process_file(f, bmc)
            if run_data is not None:#meaning it was a power file
                all_run_data.append(run_data)

    group_entries_in_hm(all_run_data)
    get_stats()

def get_stats():
    total_groups = 0
    groups_with_outliers = 0
    for k,v in hm_for_outliers.items():
        #print(v)
        total_groups += 1
        runtimes = [float(rd[8]) for rd in v]
        min_runtime = min(runtimes)
        max_runtime = max(runtimes)
        mean_runtime = statistics.mean(runtimes)
        stddev_runtime = statistics.stdev(runtimes)
        print(f"bmc: {k}\nmin:    {min_runtime}\nmax:    {max_runtime}\nmean:   {mean_runtime}\nstddev: {stddev_runtime}")
        print("\n\n")
        hm_for_stats[k] = [min_runtime, max_runtime, mean_runtime, stddev_runtime]
        outliers = get_outliers(runtimes)
        if outliers is not None and len(outliers) > 0:
            groups_with_outliers += 1
            print("values:")
            print(v)
            print("outliers")
            print(outliers)
    
    print(f"total groups with outliers: {groups_with_outliers}")

#using z-score outlier detection
def get_outliers(runtimes):
    outs = []
    threshold = 3
    mean_1 = statistics.mean(runtimes)
    std_1 = statistics.stdev(runtimes)
    for y in runtimes:
        z_score= (y - mean_1)/std_1 
        if np.abs(z_score) > threshold:
            outs.append(y)
    return outs




def group_entries_in_hm(all_runs):
    for m in all_runs:
        key = str(m[0])+"_"+str(m[1])+"_"+str(get_core_cluster(m[2]))
        if key not in hm_for_outliers:
            hm_for_outliers[key] = [m]
        else:
            entries = hm_for_outliers[key]
            entries.append(m)
            hm_for_outliers[key] = entries




def generate_mappings(all_run_data):
    rd_best_edp = None
    rd_best_edp_rd = None
    rd_best_ed2p = None
    rd_best_ed2p_rd = None
    for rd in all_run_data:
        edp = rd[-2]
        ed2p = rd[-1]
        if rd_best_edp is None:
            rd_best_edp = edp
            rd_best_edp_rd = rd
            rd_best_ed2p = ed2p
            rd_best_ed2p_rd = rd
            continue
        if edp < rd_best_edp:
            rd_best_edp = edp
            rd_best_edp_rd = rd
        if ed2p < rd_best_ed2p:
            rd_best_ed2p = ed2p
            rd_best_ed2p_rd = rd

    edp_map = get_mapping(rd_best_edp_rd)
    ed2p_map = get_mapping(rd_best_ed2p_rd)
    #rd is:
    #(0:bmc, 1:freq, 2:core, 3:run_num, 4:ipc, 5:instructions, 6:cycles, 7:cache_misses, 8:wall_time, 9:user_time, 10:sys_time, 11:avg_power, 12:edp, 13:ed2p) 
    #edp_mappings = [(r[1], r[2], get_core_cluster(r[2]), r[4], r[5], r[6], r[7], r[8], r[9], r[10], edp_map) for r in all_run_data]
    edp_mappings = [(r[1], get_core_cluster(r[2]), r[4], cache_misses_per_cycle(r), cache_misses_per_wall(r), cache_misses_per_cpu(r), edp_map) for r in all_run_data]
    ed2p_mappings = [(r[1], get_core_cluster(r[2]), r[4], cache_misses_per_cycle(r), cache_misses_per_wall(r), cache_misses_per_cpu(r), ed2p_map) for r in all_run_data]
    #ed2p_mappings = [(r[1], r[2], get_core_cluster(r[2]), r[4], r[5], r[6], r[7], r[8], r[9], r[10], ed2p_map) for r in all_run_data]

    return edp_mappings, ed2p_mappings

def cache_misses_per_wall(r):
    return float(r[7])/float(r[8])

def cache_misses_per_cpu(r):
    total_time_on_cpu = float(r[9])+float(r[10])
    cache_misses_per_total_time_on_cpu = float(r[7])/total_time_on_cpu
    return cache_misses_per_total_time_on_cpu

def cache_misses_per_cycle(r):
    return float(r[7])/float(r[6])

def get_mapping(rd):
    core = None
    if int(rd[2]) <= 3:
        core = "L"
    else:
        core = "B"
    freq = rd[1]
    return str(core)+"_"+str(freq)

def get_core_cluster(core_num):
    if int(core_num) <= 3:
        return 0
    else:
        return 1


def process_file(f, bmc):#only process power files and grab matching stdout files when we do
    if "power" not in f:
        return
    pf = open(bmc+"/"+f, "r")
    power_readings = []
    for line in pf.readlines()[1:-1]:
        split_lines = line.split(",")
        try:
            w = float(split_lines[0])*float(split_lines[1])
        except:
            continue
        power_readings.append(w)
    avg_power = statistics.mean(power_readings)
    stdout_file_name = get_stdout_file_name(f)
    stdout_file = open(bmc+"/"+stdout_file_name, "r")
    stdout = stdout_file.readlines()

    instructions, cycles, cache_misses, wall_time, user_time, sys_time = process_stdout(stdout)

    if instructions == "<not":#perf fucked up
        return
    ipc = float(instructions)/float(cycles)
    edp = avg_power*float(wall_time)
    ed2p = edp*float(wall_time)
    
    split_file = f.split("_")
    freq = split_file[0]
    core = split_file[1]
    run_num = split_file[3]

    stdout_file.close()
    pf.close()
    return (bmc, freq, core, run_num, ipc, instructions, cycles, cache_misses, wall_time, user_time, sys_time, avg_power, edp, ed2p) 


def process_stdout(stdout):
    cycles = ""
    instructions = ""
    cache_misses = ""
    wall_time = ""
    user_time = ""
    sys_time = ""
    for line in stdout:
        if "cycles" in line:
            cycles = line.split()[0]
        elif "instructions" in line:
            instructions = line.split()[0]
        elif "cache-misses" in line:
            cache_misses = line.split()[0]
        elif "real" in line:
            wall_time = get_time(line)
        elif "user" in line:
            user_time = get_time(line)
        elif "sys" in line:
            sys_time = get_time(line)
    return (instructions, cycles, cache_misses, wall_time, user_time, sys_time)

def get_time(line):
    return line.split()[1][2:-1]

        
def get_stdout_file_name(f):
    split_file = f.split("_")
    return split_file[0]+"_"+split_file[1]+"_stdout_"+split_file[3]

    



def get_available_frequencies_little():
    return [200000, 300000, 400000, 500000,
            600000, 700000, 800000, 900000, 
            1000000, 1100000, 1200000, 1300000, 
            1400000, 1500000]
def get_available_frequencies_big():
    return [200000, 300000, 400000, 500000,
            600000, 700000, 800000, 900000, 
            1000000, 1100000, 1200000, 1300000, 
            1400000, 1500000, 1600000, 1700000,
            1800000, 1900000, 2000000]





if __name__ == "__main__":
    main()
