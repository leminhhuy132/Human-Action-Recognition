import math

def add_feature(df_annot):
    print('Add angle feature...')
    # LWrist_x = annot.iloc[:, 17].tolist()
    # LWrist_y = annot.iloc[:, 18].tolist()
    # RWrist_x = annot.iloc[:, 20].tolist()
    # RWrist_x = annot.iloc[:, 21].tolist()
    # LShoulder_x = annot.iloc[:, 5].tolist()
    # LShoulder_y = annot.iloc[:, 6].tolist()
    # RShoulder_x = annot.iloc[:, 8].tolist()
    # RShoulder_y = annot.iloc[:, 9].tolist()
    #
    # LElbow_x = annot.iloc[:, 11].tolist()
    # LElbow_y = annot.iloc[:, 12].tolist()
    # RElbow_x = annot.iloc[:, 14].tolist()
    # RElbow_y = annot.iloc[:, 15].tolist()


    for i in range(len(df_annot)):
        #LWrist-LElbow_x vs LShoulder-RShoulder
        p1 = [df_annot.iloc[i, 17], df_annot.iloc[i, 18]]
        p2 = [df_annot.iloc[i, 11], df_annot.iloc[i, 12]]
        q1 = [df_annot.iloc[i, 5], df_annot.iloc[i, 6]]
        q2 = [df_annot.iloc[i, 8], df_annot.iloc[i, 9]]

        xc, yc = line_intersection((p1, p2), (q1, q2))
        c_ = [xc, yc]
        angleL = 180 - angle3pt(p1, c_, q1)
        print(angleL)

        # RWrist-RElbow_x vs LShoulder-RShoulder
        p1 = [df_annot.iloc[i, 20], df_annot.iloc[i, 21]]
        p2 = [df_annot.iloc[i, 14], df_annot.iloc[i, 15]]
        q1 = [df_annot.iloc[i, 5], df_annot.iloc[i, 6]]
        q2 = df_annot.iloc[i, 8], df_annot.iloc[i, 9]

        xc, yc = line_intersection((p1, p2), (q1, q2))
        c_ = [xc, yc]
        angleR = 180 - angle3pt(p1, c_, q1)
        print(angleR)
        df_annot.loc[i, 'RAnkle_x'] = angleL/180
        df_annot.loc[i, 'RAnkle_x'] = angleR/180
        df_annot.loc[i, 'RAnkle_s'] = (df_annot.loc[i, 'LElbow_s'] + df_annot.loc[i, 'RElbow_s'] + df_annot.loc[i, 'LWrist_s'] + df_annot.loc[i, 'RWrist_s'])/4


def angle3pt(a, b, c):
    """Counterclockwise angle in degrees by turning from a to c around b
        Returns a float between 0.0 and 360.0"""
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
    return ang + 360 if ang < 0 else ang


def line_intersection(line1, line2):
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


