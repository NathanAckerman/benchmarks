#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>


int main()
{
	pid_t pid = getpid();
	printf("io pid: %d\n", pid);
	int agg = 0;
	while (1) {
		char c;
		read(0, &c, 1);
		agg += c;
	}
}
