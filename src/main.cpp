
#include "autoconfig.h"

#include <iostream>

#include <bsp.h>

int main(int argc, char *argv[])
{
	bsp_init(&argc, &argv);

	bsp_end();
	return 0;
}
