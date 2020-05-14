#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <sys/types.h>
#include <signal.h>

//cross compile: arm-linux-gnueabi-gcc io_tracking.c -o io_tracking -static


void sigint_handler(int sig)
{
	printf("\nEnding because of ctrl-c, flushing stdout\n");
	fflush(stdout);
	close(1);
	exit(0);
	return;
}

int main(int argc, char *argv[])
{

	if (argc < 3 || argc > 4) {
		printf("usage: ./io_tracking <pid> <rate_ms> <optional_output_file(not implemented yet)>\n");
		exit(1);
	}

	signal(SIGINT, sigint_handler);

	printf("tracking io counts and runtime of pid %s\n", argv[1]);

	char *pid = argv[1];

	int interval_ms = atoi(argv[2]);
	int interval_us = interval_ms*1000;//need this in microseconds for usleep call

	char io_filename[50];
	char runtime_filename[50];
	char *part1 = "/proc/";
	strcpy(io_filename, part1);
	strcpy(runtime_filename, part1);

	strcat(io_filename, pid);
	strcat(runtime_filename, pid);

	strcat(io_filename, "/power_veil_wait_count");
	strcat(runtime_filename, "/power_veil_runtime");

	FILE *io_file = fopen(io_filename, "r");
	if (!io_file) {
		printf("ERROR could not open io file: %s\n", io_filename);
	}
	FILE *runtime_file = fopen(runtime_filename, "r");
	if (!runtime_file) {
		printf("ERROR could not open runtime file: %s\n", runtime_filename);
	}

	//cool, everything is set up, so lets track forever and ever, maybe ctrl-c handler should close files?
	while (1) {
		char io_buf[22];
		char runtime_buf[22];
		struct timespec ts;

		io_buf[21] = '\0';
		runtime_buf[21] = '\0';

		clock_gettime(CLOCK_MONOTONIC, &ts);
		//long ns = ts.tv_nsec + ts.tv_sec*1000000000;
		long ns = ts.tv_nsec;
		time_t sec = ts.tv_sec;


		//TODO can we continuously read or do we need to open and then read each time?
		
		fread(&io_buf , 21*sizeof(char), 1,io_file);
		fread(&runtime_buf , 21*sizeof(char), 1,runtime_file);

		printf("s: %ld ns:%ld io:%s runtime:%s\n", sec, ns, io_buf, runtime_buf);

		fclose(io_file);
		fclose(runtime_file);

		usleep(interval_us);

		io_file = fopen(io_filename, "r");
		runtime_file = fopen(runtime_filename, "r");
	}


	return 0;
}
