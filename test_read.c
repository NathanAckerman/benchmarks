
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

int main(int argc, char *argv[])
{

	char *io_filename = "/proc/236/sessionid";
	FILE *io_file = fopen(io_filename, "r");
	if (!io_file) {
		printf("ERROR could not open io file: %s", io_filename);
	}

	while (1) {
		char io_buf[11];
		struct timespec ts;

		io_buf[10] = '\0';

		clock_gettime(CLOCK_MONOTONIC, &ts);
		long ns = ts.tv_nsec + ts.tv_sec*1000000000;
		
		//TODO can we continuously read or do we need to open and then read each time?
		
		fread(&io_buf , 10*sizeof(char), 1,io_file);

		printf("%ld %s\n", ns, io_buf);

		sleep(1);
	}


	return 0;
}
