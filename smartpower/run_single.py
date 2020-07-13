from subprocess import Popen, PIPE
import os
import sys

def main():
    core = sys.argv[1]
    bmc = " ".join(sys.argv[2:])
    #bmc = "./loop"
    shell_file_name = create_shell_file(bmc, core)
    mod_name = shell_file_name.split("/")[1]
    shell_file_run = "sudo /home/odroid/benchmarks/smartpower_tests/"+mod_name
    process = Popen(shell_file_run.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()



    #bmc = "sudo /home/odroid/benchmarks/smartpower_tests/bench_tests/shell_command.sh"
    #process = Popen(bmc.split(), stdout=PIPE, stderr=PIPE)
    #stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    output = stdout+"\n\n"+stderr
    #print("done running the actual command")
    #print(stdout)
    #print("error out:")
    print(output)
    os.remove(shell_file_name)


def create_shell_file(bmc, core):
    bmc_file = "_".join(bmc.split())
    bmc_file += ".sh"
    core_mask = get_mask(core)
    f = open(bmc_file, "w+")
    file_text = "#!/bin/bash\ntime sudo /usr/bin/perf stat -B -e cycles,instructions,cache-misses taskset "+core_mask+" "+bmc
    f.write(file_text)
    f.close()
    os.chmod(bmc_file, 0o777)
    return bmc_file

def get_mask(core):
    masks = ["0x1", "0x2", "0x4", "0x8",
            "0x10", "0x20", "0x40", "0x80"]
    #return "0x1"
    return masks[int(core)]


if __name__ == "__main__":
    main()
