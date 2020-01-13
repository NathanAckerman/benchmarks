#define _GNU_SOURCE
#include <stdio.h>
#include <sched.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	//set affinity
	cpu_set_t mask;
	CPU_ZERO(&mask);
	CPU_SET(atoi(argv[1]), &mask);
	int res = sched_setaffinity( 0, sizeof(mask), &mask);
	if (res != 0) {
		printf("failed to set affinity\n");
	}
	printf("running\n");

	int agg = 1;
	int i;
	for(i = 0; i < 2000000000; i++) {
		agg = i;
	}

	return 0;
}
