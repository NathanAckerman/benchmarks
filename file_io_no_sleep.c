#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	pid_t pid = getpid();
	printf("io pid: %d\n", pid);
	

	char c;

	while (1) {
		FILE *fp = fopen("io_file.txt", "r");
		if (!fp) {
			printf("couldn't find/open io_file.txt\n");
			exit(1);
		}
		fread(&c, 1, 1, fp);	
		fclose(fp);
	}

	return 0;
}
