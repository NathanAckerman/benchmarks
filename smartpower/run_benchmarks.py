import os
import sys
from subprocess import Popen, PIPE
import random
import time
import shutil

#this must be run as sudo, you also must have the userspace governor active
#and have minicom set up to connect to the odroid smartpower 2


#/sys/devices/system/cpu/cpufreq/policy0
#/sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors
#/sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies

little_cpus = [0,1,2,3]
big_cpus = [4,5,6,7]
bmc_runs_hm = {}


def main():
    if len(sys.argv) != 4:
        print_usage()
        exit(0)

    benchmarks_file = sys.argv[1]
    all_frequencies = sys.argv[2] == "true"
    num_runs = int(sys.argv[3])

    try:
        shutil.rmtree('generated_data/')
    except:
        print("problem deleting old folder")
        #exit(1)

    try:
        os.mkdir("generated_data")
    except:
        print("failed to make data directory, may be that it already existed")

    
    benchmark_commands = get_benchmarks_from_file(benchmarks_file)
    generate_folders_for_benchmarks(benchmark_commands)
    benchmark_commands_all = generate_runs(benchmark_commands, num_runs)

    for bmc in benchmark_commands_all:
        run_bmc(bmc, all_frequencies) #slight typo, should be run_dmc ;)
    




def generate_runs(bmcs, num_runs):
    cmds = []
    for i in range(num_runs):
        cmds.extend(bmcs)
    random.shuffle(cmds)
    return cmds

def generate_folders_for_benchmarks(benchmarks):
    for bm in benchmarks:
        bm = "_".join(bm.split())
        try:
            os.mkdir("generated_data/"+bm)
        except:
            print("failed to make folder for benchmark")
            exit(1)

def run_bmc(bmc, all_frequencies):
    available_freqs_little = get_available_frequencies_little()
    random.shuffle(available_freqs_little)
    available_freqs_big = get_available_frequencies_big()
    random.shuffle(available_freqs_big)

    #yes, it could in theory just run on one big and one little core, but this
    #adds some randomization and repeat of runs
    for cpu_num in little_cpus:
        if all_frequencies:
            for freq in available_freqs_little:
                run_bmc_at_freq_on_core(bmc, freq, cpu_num)
        else:
            run_bmc_on_core(bmc, cpu_num)

    for cpu_num in big_cpus:
        if all_frequencies:
            for freq in available_freqs_big:
                run_bmc_at_freq_on_core(bmc, freq, cpu_num)
        else:
            run_bmc_on_core(bmc, cpu_num)

   

def run_bmc_at_freq_on_core(bmc, freq, core):
    print("running benchmark: "+bmc+" on core" +str(core)+" at freq "+str(freq))
    run_num = get_run_num(bmc, core, freq)
    #affinity_mask = {core}
    #pid = os.getpid()
    #os.sched_setaffinity(pid, affinity_mask)
    set_freq(freq, core)
    spawn_power_thread(bmc, freq, core, run_num)
    run_bmc_command(bmc, run_num, freq, core)
    kill_power_thread()
    print("finished running benchmark: "+bmc+" on core" +str(core)+" at freq "+str(freq))
    return

def run_bmc_on_core(bmc, core):
    print("running benchmark: "+bmc)
    run_num = get_run_num(bmc, core, "stdfreq")
    #affinity_mask = {core}
    #pid = os.getpid()
    #os.sched_setaffinity(pid, affinity_mask)
    spawn_power_thread(bmc, freq, core, run_num)
    run_bmc_command(bmc, run_num, "", core)
    kill_power_thread()
    print("finished running benchmark: "+bmc)

def run_bmc_command(bmc, run_num, freq, core):
    print("actually running the command... ")
    #shell_file_name = create_shell_file(bmc)
    #mod_name = shell_file_name.split("/")[1]
    #shell_file_run = "sudo /home/odroid/benchmarks/smartpower_tests/"+mod_name
    #process = Popen(shell_file_run.split(), stdout=PIPE, stderr=PIPE)
    #stdout, stderr = process.communicate()
    cmd = "sudo python3 run_single.py "+str(core)+" "+bmc
    process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    bmc = "_".join(bmc.split())
    file_out = "generated_data/"+bmc+"/"+str(freq)+"_"+str(core)+"_stdout_"+str(run_num)
    f = open(file_out, "w+")
    stderr = stderr.decode('utf-8')
    stdout = stdout.decode('utf-8')
    output = stdout+"\n\n"+stderr
    f.write(output)
    f.close()
    #os.remove(shell_file_name)
    print("done running the actual command")


def get_run_num(bmc, core, freq):
    key = bmc+"_"+str(freq)+"_"+str(core)
    if key not in bmc_runs_hm:
        bmc_runs_hm[key] = 0
        return 0
    else:
        num = bmc_runs_hm[key]
        bmc_runs_hm[key] = num+1
        return num


def spawn_power_thread(bmc, freq, core, run_num):#should we spawn with nohup?
    file_out = "generated_data/"+bmc+"/"+str(freq)+"_"+str(core)+"_power_"+str(run_num)
    sudo_pass = "odroid" #oh no, now they know!
    os.popen("sudo -S minicom -C "+file_out, 'w').write(sudo_pass)
    #process = Popen(['minicom', '-C', file_out, "&"], stdout=PIPE, stderr=PIPE)
    #stdout, stderr = process.communicate()

def kill_power_thread():
    sudo_pass = "odroid" #oh no, now they know!
    os.popen("sudo -S killall -9 minicom", 'w').write(sudo_pass)
    time.sleep(1)

def set_freq(freq, core):
    if core <= 3:
        core = 0
    else:
        core = 4
    min_file = "/sys/devices/system/cpu/cpufreq/policy"+str(core)+"/scaling_min_freq"
    max_file = "/sys/devices/system/cpu/cpufreq/policy"+str(core)+"/scaling_max_freq"
    echo_as_sudo(freq, min_file)
    echo_as_sudo(freq, max_file)
    echo_as_sudo(freq, min_file)#do this again because if going up in freq, the first one fails
    echo_as_sudo(freq, max_file)
    time.sleep(1)

def echo_as_sudo(freq, the_file):
    sudo_pass = "odroid" #oh no, now they know!
    os.popen("echo "+str(freq)+" | sudo -S tee -a %s"%(the_file), 'w').write(sudo_pass)

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

def print_usage():
    print("USAGE: python3 run_benchmarks.py <file_of_bench_commands> <true or false> <num_runs>")

def get_benchmarks_from_file(benchmarks_file):
    f = open(benchmarks_file)
    cmds = f.read().splitlines()
    f.close()
    return cmds

if __name__ == "__main__":
    main()
