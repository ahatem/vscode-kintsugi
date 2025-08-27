#include <math.h>
#include <stdio.h>

typedef struct
{
    double x;
    double y;
} Point;

double calculateDistance(const Point *p1, const Point *p2)
{
    if (p1 == NULL || p2 == NULL)
    {
        return -1.0;
    }

    double dx = p2->x - p1->x;
    double dy = p2->y - p1->y;

    return sqrt(pow(dx, 2) + pow(dy, 2));
}

int main()
{
    Point origin = {0.0, 0.0};
    Point target = {3.0, 4.0};
    printf("Distance: %.2f\n", calculateDistance(&origin, &target));
    return 0;
}