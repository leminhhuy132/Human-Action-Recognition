import math

def angle3pt(a, b, c):
    """Counterclockwise angle in degrees by turning from a to c around b
        Returns a float between 0.0 and 360.0"""
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
    return ang + 360 if ang < 0 else ang

def line_intersection(line1, line2):
    # xdiff = (p1.x - p2.x, q1.x - q2.x)
    # ydiff = (p1.y - p2.y, q1.y - q2.y)

    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        print('lines do not intersect')
        return 0, 0

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y




# p1_ = [10, 10]
# p2_ = [20, 20]
# 
# q1_ = [0, 5]
# q2_ = [5, 0]
# 
# xc, yc = line_intersection((p1_, p2_), (q1_, q2_))
# print(xc, yc)
# 
# c_ = [xc, yc]
# angle = 180 - angle3pt(p1_, c_, q1_)
# 
# print(angle)


