#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

//perf stat -B -e cache-references,cache-misses,cycles,instructions,branches,faults,migrations ./t1 num_procs num_longs num_rounds
//aka perf stat -B -e cache-references,cache-misses,cycles,instructions,branches,faults,migrations ./t1 16 1000000 50
//standalone usage ./t1 num_procs num_longs num_rounds
void work(long num_longs, long num_rounds);//method stubby

int main(int argc, char *argv[])
{
	int num_procs = atoi(argv[1]);//number of processes to spawn to do work
	long num_longs = atol(argv[2]);//number of longs (increases number of different cache refs per loop)
	long num_rounds = atol(argv[3]);//number of rounds (increases repeats of cache refs)

	int wait_on[num_procs];//hold pids to wait on in main

	int making_procs = 1;//start out true for needing to make more
	int num_made;//keep track of how many procs have been made
	int fork_id;//ret of fork

	for(num_made = 0; num_made < num_procs; num_made++){
		fork_id = fork();//fork to make new proc
		wait_on[num_made] = fork_id;
		if(fork_id == 0){//if in a child process
			printf("Starting work in process %d.\n", num_made);
			work(num_longs, num_rounds);//do stuffs
			break;//don't want to loop if in child proc
		}
	}

	//in parent and need to wait for all the babies to die horrible deaths
	if(fork_id != 0){
		int i;
		for(i = 0; i < num_procs; i++){
			waitpid(wait_on[i], NULL, 0);
		}
	}
	return 0;
}

//with 1,000,000 longs and 50 rounds: 1 proc = 45% cache misses, 8 procs = 71% cache misses

//do work in an individual process 
//num_longs makes more distinct cache refs per round, num_rounds makes more rounds of those cache refs
void work(long num_longs, long num_rounds){
	long *p = malloc(num_longs*(sizeof(long)));
	long i;
	for(i = 0; i < num_longs; i++){//set up some values in memory
		p[i] = i; 
	}
					
	int j;
	for(j = 0; j < num_rounds; j++){//loop through memory num_rounds times
		for(i = 0; i < num_longs; i++){//loop through memory
			//printf("%ld",p[i]); 
			long x = p[i];
		}
	}
}



















