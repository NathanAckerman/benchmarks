//sudo perf stat -B -e cache-references,LLC-load-misses,cycles,instructions ls
#include <stdlib.h>
#include <stdio.h>

long ops = 0;

struct node {
	long val;
	struct node *next;
};


struct node* create_list()
{
	struct node *head = malloc(sizeof(struct node));
	struct node *cur;
	cur = head;
	int i;
	for (i = 0; i < 100000; i++) {//list size of 100,000
		cur->val = i;
		cur->next = malloc(sizeof(struct node));
		cur = cur->next;
	}
	cur->next = NULL;
	return head;
}

void iterate_once(struct node *head)
{
	long agg = 0;
	struct node *cur = head;
	while (cur != NULL) {
		ops++;
		agg += cur->val;
		cur = cur->next;
	}
}

void iterate_list_a_bunch(struct node *head)
{
	int i;
	for (i = 0; i < 1200; i++) {
		iterate_once(head);
	}
}

int main(int argc, char *argv[])
{
	printf("starting\n");
	fflush(stdout);
	struct node *list_head = create_list();
	iterate_list_a_bunch(list_head);
	printf("done\n");
	printf("%ld\n", ops);
	return 0;
}







