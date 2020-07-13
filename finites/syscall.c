#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>

int main()
{
	pid_t pid = getpid();
	printf("cpu pid: %d\n", pid);
	int agg = 0;
	int i;
	for (i=0; i < 5000000; i++) {
		agg += getpid();
	}
}
