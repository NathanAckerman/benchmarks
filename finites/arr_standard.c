//sudo perf stat -B -e cache-references,LLC-load-misses,cycles,instructions ls
#include <stdlib.h>
#include <stdio.h>

long ops = 0;

void fill_arr(long *arr)
{
	int i;
	for (i = 0; i < 100000; i++) {//list size of 100,000
		arr[i] = i;
	}
}

void iterate_once(long *arr)
{
	long agg = 0;
	int i;
	for (i = 0; i < 100000; i++) {
		agg += arr[i];
		ops++;
	}
}

void iterate_arr_a_bunch(long *arr)
{
	int i;
	for (i = 0; i < 1000; i++) {
		iterate_once(arr);
	}
}

int main(int argc, char *argv[])
{
	printf("starting\n");
	fflush(stdout);
	long arr[100000];//arr of length 100,000
	fill_arr(arr);
	iterate_arr_a_bunch(arr);
	printf("done\n");
	printf("%ld\n", ops);
	return 0;
}







