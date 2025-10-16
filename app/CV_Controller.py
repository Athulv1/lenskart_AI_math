import cv2 # type: ignore
import numpy as np # type: ignore
import os
import math
import logging
import subprocess
import sys
from django.conf import settings
from typing import List, Tuple, Dict, Any
import json


Seg2D = Tuple[float, float, float, float]        # (x1, y1, x2, y2) mm
Wall3D = Tuple[float, float, float, float, float]  # (x1, y1, x2, y2, height_mm)
Pt = Tuple[float, float]

class CV_Controller:

    def __init__(self, img_path, out_path, overlay, fp_json):
        self.img_path = img_path
        self.out_path = out_path
        self.ovl_out = overlay
        # self.img_gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        # self.img_color = cv2.imread(img_path, cv2.IMREAD_COLOR)
        self.get_corners(fp_json)
        # self.get_corners_fortesting()

    def angle_between(p1, p2, p3):
        v1 = p1 - p2
        v2 = p3 - p2
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def get_botr_point(self):
        """
        Given a list of (x, y) tuples, return the point closest to the bottom-right:
        the point with the maximum x and minimum y.
        """
        if not self.corners:
            return None

        # Determine the theoretical bottom-right point
        max_x = max(p[0] for p in self.corners)
        min_y = min(p[1] for p in self.corners)
        target = (max_x, min_y)

        # Find the actual point closest to that target
        closest = min(self.corners, key=lambda p: ((p[0] - target[0])**2 + (p[1] - target[1])**2)**0.5)
        return closest


    def reorder_bot_left(self):
        # Find the point with lowest Y, then lowest X
        min_idx = min(
            range(len(self.corners)),
            key=lambda i: math.hypot(self.corners[i][0], self.corners[i][1])
        )

        self.corners = self.corners[min_idx:] + self.corners[:min_idx]
        return self.corners

    def reorder_bot_right(self):
        if not self.corners:
            return self.corners

        max_x = max(p[0] for p in self.corners)
        min_y = min(p[1] for p in self.corners)
        target = (max_x, min_y)

        def distance_to_target(p):
            return math.hypot(p[0] - target[0], p[1] - target[1])

        closest_idx = min(range(len(self.corners)), key=lambda i: distance_to_target(self.corners[i]))
        self.corners = self.corners[closest_idx:] + self.corners[:closest_idx]
        
        return self.corners
    
    def normalize_points(self):
        height = self.img_gray.shape[0]
        flipped_points = [(x, height - y) for (x, y) in self.corners]
        print(height)
        print(flipped_points)

        # Normalize points to start at (0, 0)
        min_x = min(x for (x, y) in flipped_points)
        min_y = min(y for (x, y) in flipped_points)
        normalized_points = [(x - min_x, y - min_y) for (x, y) in flipped_points]
        print(normalized_points)
        print(self.scale)

        # Apply scale to convert from pixels to mm
        self.corners = [(x * self.scale, y * self.scale) for (x, y) in normalized_points]

        return self.corners

    def get_metadata(self):
        # Extract all X and Y coordinates
        self.x_coords = [x for (x, y) in self.corners]
        self.y_coords = [y for (x, y) in self.corners]

        # Find leftmost (min X) and rightmost (max X) points
        self.min_x = min(self.x_coords)
        self.max_x = max(self.x_coords)

        # ADDED LINES
        self.min_y = min(self.y_coords)
        self.max_y = max(self.y_coords)

        self.leftmost_points = [(x, y) for (x, y) in self.corners if x == self.min_x]
        self.rightmost_points = [(x, y) for (x, y) in self.corners if x == self.max_x]

        # Among leftmost/rightmost points, find the one with smallest Y (bottom-most)
        self.leftmost_bottom_point = min(self.leftmost_points, key=lambda p: p[1]) if self.leftmost_points else (self.min_x, 0)
        self.rightmost_bottom_point = min(self.rightmost_points, key=lambda p: p[1]) if self.rightmost_points else (self.max_x, 0)

        # Find farthest point from Y=0 (vertically)
        self.max_y_point = max(self.corners, key=lambda p: p[1])  # (x, y) with max Y
        self.distance_from_bottom = self.max_y_point[1]  # Vertical distance from Y=0 (mm)

        # Find farthest point horizontally (from X=0)
        self.max_x_point = max(self.corners, key=lambda p: p[0])  # (x, y) with max X
        self.distance_from_left = self.max_x_point[0]  # Horizontal distance from X=0 (mm)

        # Determine if longer in length (X) or width (Y)
        if (max(self.x_coords) - min(self.x_coords)) > (max(self.y_coords) - min(self.y_coords)):
            self.orientation = "length-wise (longer on X-axis)"
        else:
            self.orientation = "width-wise (longer on Y-axis)"
       
        # **********************added
        # Determine if longer in length (X) or width (Y)
        total_width = max(self.x_coords) - min(self.x_coords)
        total_height = max(self.y_coords) - min(self.y_coords)

        #-----new logic for detecting landscape and portrait-----

        # --- NEW ORIENTATION LOGIC ---
        if total_height > total_width:
            self.orientation = "portrait"
        else:
            self.orientation = "landscape"
        
        print(f"✅ Orientation detected: {self.orientation.upper()}")

    def print_metadata(self):
        # Print results
        print("\n--- Floor Plan Dimensions Analysis ---")
        print(f"✅ Leftmost starting point (X=0): Y = {self.leftmost_bottom_point[1]} mm")
        print(f"✅ Leftmost starting point (y=0): x = {self.rightmost_bottom_point[1]} mm")
        print(f"✅ Farthest point from Y=0 (vertically): {self.max_y_point} | Distance: {self.distance_from_bottom} mm")
        print(f"✅ Farthest point from X=0 (horizontally): {self.max_x_point} | Distance: {self.distance_from_left} mm")
        print(f"✅ Orientation: {self.orientation}")
        print(f"✅ Total width (X-axis): {max(self.x_coords) - min(self.x_coords)} mm")
        print(f"✅ Total height (Y-axis): {max(self.y_coords) - min(self.y_coords)} mm")

    def get_wall_segments(self, min_length=200):
        """
        Splits the simplified wall into linear segments and returns valid ones
        (i.e., segments not part of inward jagged areas).
        """
        if not hasattr(self, "corners"):
            raise ValueError("No corners found. Run get_fp_points() first.")

        segments = []
        num_points = len(self.corners)
        for i in range(num_points):
            p1 = np.array(self.corners[i])
            p2 = np.array(self.corners[(i + 1) % num_points])  # loop around
            seg_vec = p2 - p1
            seg_len = np.linalg.norm(seg_vec)

            # Skip very small or tiny jagged edges
            if seg_len < min_length:
                continue

            # Optional: Angle-based bulge detection
            p0 = np.array(self.corners[i - 1])
            angle = CV_Controller.angle_between(p0, p1, p2)
            if angle < 85:  # Likely a bulge or corner inward
                continue

            segments.append((tuple(p1), tuple(p2)))
        return segments

    def flip_polygon_horizontally(self, points):

        if not points:
            return []

        # Find horizontal center (midpoint between min_x and max_x)
        xs = [p[0] for p in points]
        center_x = (min(xs) + max(xs)) / 2

        # Flip each point's x-coordinate about the center_x
        flipped_points = [[2 * center_x - x, y] for x, y in points]

        return flipped_points

    def get_corners(self, fp_json):
        # Call worker.py and capture stdout
        result = subprocess.run(
            ["python", "app/layout.py", json.dumps(fp_json)],  # changed from "python3" to "python"
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # to get output as string instead of bytes
        )

        if result.returncode != 0:
            raise RuntimeError(f"Worker failed:\n{result.stderr}")

        self.plan_final = []
        self.walls3d_final = []
        self.corners = []
        end1 = False
        end2 = False
        output = result.stdout.strip()  # remove trailing newline
        output = output.split("\n")
        for row in output:
            rArr = row.split()
            if not end1:
                if len(row.strip()) > 0:
                    self.plan_final.append([float(rArr[0]), float(rArr[1]), float(rArr[2]), float(rArr[3])])
                else:
                    end1 = True
            elif not end2:
                if len(row.strip()) > 0:
                    self.walls3d_final.append([float(rArr[0]), float(rArr[1]), float(rArr[2]), float(rArr[3]), float(rArr[4])])
                else:
                    end2 = True
            else:
                if len(row.strip()) > 0:
                    self.corners.append([float(rArr[0]), float(rArr[1])])
            
        
    def apply_rotation(self, plan_segments: List[Seg2D], walls3d: List[Wall3D], rot_deg: float) -> Tuple[List[Seg2D], List[Wall3D]]:

        def centroid_xy(plan_segments: List[Seg2D]) -> Tuple[float, float]:
            xs: List[float] = []
            ys: List[float] = []
            for x1, y1, x2, y2 in plan_segments:
                xs.extend([x1, x2])
                ys.extend([y1, y2])
            if not xs:
                return 0.0, 0.0
            return sum(xs) / len(xs), sum(ys) / len(ys)


        def rotate_xy(x: float, y: float, cx: float, cy: float, theta_deg: float) -> Tuple[float, float]:
            th = math.radians(theta_deg)
            ct, st = math.cos(th), math.sin(th)
            dx, dy = x - cx, y - cy
            rx = dx * ct - dy * st + cx
            ry = dx * st + dy * ct + cy
            return rx, ry


        if abs(rot_deg) < 1e-12:
            return list(plan_segments), list(walls3d)
        cx, cy = centroid_xy(plan_segments)

        plan_rot: List[Seg2D] = []
        for x1, y1, x2, y2 in plan_segments:
            rx1, ry1 = rotate_xy(x1, y1, cx, cy, rot_deg)
            rx2, ry2 = rotate_xy(x2, y2, cx, cy, rot_deg)
            plan_rot.append((rx1, ry1, rx2, ry2))

        walls_rot: List[Wall3D] = []
        for x1, y1, x2, y2, h in walls3d:
            rx1, ry1 = rotate_xy(x1, y1, cx, cy, rot_deg)
            rx2, ry2 = rotate_xy(x2, y2, cx, cy, rot_deg)
            walls_rot.append((rx1, ry1, rx2, ry2, h))

        return plan_rot, walls_rot
    
    

    def get_corners_fortesting(self):
        # Call worker.py and capture stdout
#         corners_str =  """7296.005238, 264.375568
# 802.140633, 264.375568
# 802.140633, 568.766409
# 290.405057, 568.776409
# 290.405057, 6859.707120
# 802.130633, 6859.707120
# 802.140633, 7164.107961
# 7296.005238, 7164.107961
# 7296.005238, 6859.717120
# 8006.283866, 6859.707120
# 8006.293866, 7164.107961
# 11811.284377, 7164.107961
# 11811.284377, 6859.717120
# 12521.563006, 6859.707120
# 12521.573006, 7164.107961
# 15565.561414, 7164.107961
# 15565.561414, 6555.316279
# 16453.397200, 6555.306279
# 16453.397200, 847.810513
# 16250.473306, 847.810513
# 16250.463306, 264.375568
# 12521.573006, 264.375568
# 12521.573006, 568.766409
# 11811.294377, 568.776409
# 11811.284377, 264.375568
# 8006.293866, 264.375568
# 8006.293866, 568.766409
# 7296.015238, 568.776409
# """   

#         corners_str =  """-9947.441270834726, 904.8552451991931
# -9903.533456636998, -6698.440921312511
# -9142.151824306997, -6694.043793607298
# -9110.432805682796, -12186.58952051225
# -1471.7030548420462, -12201.801141225098
# -1490.473885296976, -8951.415476387
# -2983.7350611024945, -8960.038789567838
# -2992.211484478189, -7492.198304828206
# -3189.790124093337, -7493.339465113909
# -3226.660677646923, -1108.898329831973
# -1851.255522851363, -1100.956153570252
# -1856.148496033759, -253.6356323036389
# -5137.00437182057, -272.5836092965819
# -5141.995232396771, 591.4121242280839
# -6712.899570009638, 582.3416333200084
# -6714.870315545983, 923.5231239181277
# -7484.536736440774, 919.0782975638841
# -7484.536740221379, 919.0789522156928
# -9947.441270834726, 904.8552451991931
# """

# plan_1
        corners_str = """0.010000, 350.008934
0.010000, 4884.990000
89.999998, 4884.990000
90.009998, 5245.000000
0.010000, 5245.010000
0.010000, 9639.988934
2849.990915, 9639.988937
2849.990915, 9549.998937
3150.000915, 9549.988937
3150.010911, 9639.988937
7089.990039, 9639.988934
7089.990039, 8209.998934
8150.000039, 8209.988934
8150.010039, 8429.998934
7395.010039, 8430.008934
7395.010039, 9629.988934
8844.990039, 9629.988934
8844.991302, 0.010734
6135.035531, 0.010023
6135.011302, 350.000023
5875.001302, 350.010023
5874.991302, 0.010023
3150.011302, 0.010000
3150.011302, 350.000000
2890.005398, 350.010000
2889.995398, 0.010021
90.010000, 0.010023
90.009998, 349.998934"""


# #plan_2
#         corners_str = """0.010000, 262.727321
# 0.010000, 4672.707321
# 250.000000, 4672.707321
# 250.010000, 4972.717321
# 0.010000, 4972.727321
# 0.010000, 8332.707321
# 250.000000, 8332.707321
# 250.010000, 8612.717321
# 0.010000, 8612.727321
# 0.010000, 12032.707321
# 110.000000, 12032.707321
# 110.010000, 12403.537596
# 2809.990000, 12403.537596
# 2809.990000, 12128.547596
# 2929.990000, 12128.537596
# 2929.990000, 11678.547596
# 3054.990000, 11678.537596
# 3054.990000, 10378.547596
# 3180.000000, 10378.537596
# 3180.010000, 11678.547596
# 3180.010000, 12128.537596
# 3585.000000, 12128.537596
# 3585.010000, 12399.367872
# 4694.990000, 12399.367872
# 4694.990000, 10843.557596
# 3930.000000, 10843.557596
# 3929.990000, 10728.547596
# 6179.990000, 10728.537596
# 6179.990000, 8648.557596
# 5615.000000, 8648.557596
# 5614.990000, 8248.547596
# 5779.990000, 8248.537596
# 5779.990000, 4938.557596
# 5615.000000, 4938.557596
# 5614.990000, 4538.547596
# 5779.990000, 4538.537596
# 5779.990000, 1433.557596
# 5490.000000, 1433.557596
# 5489.990000, 1087.300876
# 3480.010000, 669.422968
# 3480.010000, 934.969701
# 2755.000000, 934.979701
# 2754.990000, 518.697462
# 260.010000, 0.012293
# 260.010000, 262.717321"""

#plan_3

#         corners_str = """0.011494, 3734.537973
# 130.215570, 3732.975651
# 130.225690, 4134.544986
# 0.270790, 4134.554986
# 100.324405, 7616.420799
# 220.215403, 7612.975655
# 220.225690, 8009.985651
# 80.225690, 8009.995651
# 80.225690, 11445.102015
# 240.215370, 11439.975656
# 240.225690, 11843.985651
# 80.545521, 11849.111777
# 290.420403, 15213.106307
# 430.215466, 15209.975653
# 430.225690, 15609.985651
# 300.225690, 15609.995651
# 300.225690, 17538.979205
# 1180.225994, 17538.979205
# 1180.235994, 17654.989205
# 300.225690, 17654.999205
# 300.225690, 18576.975651
# 430.215690, 18576.975651
# 430.225690, 18973.985651
# 300.225690, 18973.995651
# 300.225690, 19204.979205
# 1930.205690, 19204.979205
# 1930.215994, 17538.989205
# 2045.225994, 17538.979205
# 2045.225690, 19204.979205
# 2121.215200, 19204.979205
# 4470.205690, 18973.976586
# 4470.205690, 18819.985651
# 4820.205690, 18819.963544
# 4820.205690, 15848.995651
# 4476.225994, 15848.995650
# 4476.205690, 15553.985651
# 4820.205690, 15553.963636
# 4820.205690, 12151.995651
# 4455.226059, 12151.995650
# 4455.205690, 11843.985651
# 4820.324529, 11843.963359
# 4820.205690, 8313.995651
# 4473.226131, 8313.995650
# 4473.205690, 8012.985651
# 4820.328306, 8012.963610
# 4820.205690, 4477.995651
# 4484.226784, 4477.995650
# 4484.205690, 4163.985651
# 4820.206703, 4163.975651
# 5169.204563, 901.999205
# 4837.215690, 901.999205
# 4837.205690, 607.012225
# 589.225690, 0.011531
# 589.225690, 408.029801
# 459.218310, 408.039801"""

#plan_4

#         corners_str = """0.010000, 340.010000
# 0.010000, 3559.990000
# 110.000000, 3559.990000
# 110.010000, 3790.000000
# 0.010000, 3790.010000
# 0.010000, 6279.990000
# 110.000000, 6279.990000
# 110.010000, 6740.000000
# 0.010000, 6740.010000
# 0.010000, 10979.990337
# 6141.007559, 11190.672591
# 6145.807442, 11050.764902
# 6405.664902, 11059.669956
# 6400.874671, 11199.587989
# 7869.990000, 11249.989651
# 7869.990000, 5960.010000
# 7570.000000, 5960.010000
# 7569.990000, 4640.000000
# 7869.990000, 4639.990000
# 7869.990000, 340.010000
# 7384.000000, 340.010000
# 7383.985904, 0.010000
# 3424.014096, 0.010000
# 3424.010000, 390.000000
# 2864.000000, 390.010000
# 2863.990000, 0.010000
# 140.010000, 0.010000
# 140.010000, 340.000000"""

#plan_5

#         corners_str = """0.010000, 1800.010000
# 0.010000, 5719.990000
# 110.000000, 5719.990000
# 110.010000, 5970.000000
# 0.010000, 5970.010000
# 0.010000, 9799.990000
# 100.000000, 9799.990000
# 100.010000, 10050.000000
# 0.010000, 10050.010000
# 0.010000, 13849.990000
# 110.000000, 13849.990000
# 110.010000, 14100.000000
# 0.010000, 14100.010000
# 0.010000, 18329.990220
# 4489.990000, 18429.989775
# 4489.990000, 14100.010000
# 4360.000000, 14100.010000
# 4359.990000, 13850.000000
# 4489.990000, 13849.990000
# 4489.990000, 10050.010000
# 4355.000000, 10050.010000
# 4354.990000, 9800.000000
# 4489.990000, 9799.990000
# 4489.990000, 5970.010000
# 4340.000000, 5970.010000
# 4339.990000, 5720.000000
# 4489.990000, 5719.990000
# 4489.990000, 1800.010000
# 4360.000000, 1800.010000
# 4359.990000, 1550.000000
# 4489.990000, 1549.990000
# 4489.990000, 250.010000
# 4230.000000, 250.010000
# 4229.990000, 0.010000
# 250.010000, 0.010000
# 250.010000, 250.000000
# 0.010000, 250.010000
# 0.010000, 1549.990000
# 100.000000, 1549.990000
# 100.010000, 1800.000000"""


#plan_6

#         corners_str = """0.010000, 602.010000
# 0.010000, 3773.990000
# 164.999992, 3773.990000
# 165.009992, 4264.000000
# 0.010000, 4264.010000
# 0.010000, 6683.990000
# 175.000000, 6683.990000
# 175.010000, 7159.000000
# 20.010000, 7159.010000
# 20.010000, 9655.990000
# 179.999992, 9655.990000
# 180.009992, 9969.989994
# 4409.989992, 9967.490006
# 4409.989992, 9815.000000
# 4899.999992, 9814.990000
# 4900.009992, 9967.490193
# 5027.989992, 9969.989803
# 5027.989992, 9220.000000
# 5177.999992, 9219.990000
# 5178.009992, 9969.990000
# 6677.989992, 9969.990000
# 6677.989992, 8470.010032
# 5028.000024, 8475.218333
# 5027.989992, 8320.000000
# 6677.989992, 8319.990000
# 6677.989992, 6583.000000
# 6827.989992, 6582.990000
# 6827.989992, 4177.010000
# 6677.999992, 4177.010000
# 6677.989992, 3692.000000
# 6862.989992, 3691.990000
# 6862.989992, 522.010000
# 6646.999992, 522.010000
# 6646.989992, 0.010000
# 355.009992, 0.010000
# 355.009992, 602.000000"""


# #plan_7

#         corners_str = """0.010000, 325.010000
# 0.010000, 3754.990000
# 226.000000, 3754.990000
# 226.010000, 4079.000000
# 0.010000, 4079.010000
# 0.010000, 7548.990000
# 226.000000, 7548.990000
# 226.010000, 7869.000000
# 0.010000, 7869.010000
# 0.010000, 11328.990000
# 226.000000, 11328.990000
# 226.010000, 11651.000000
# 0.010000, 11651.010000
# 0.010000, 15122.990000
# 226.000000, 15122.990000
# 226.010000, 15449.000000
# 0.010000, 15449.010000
# 0.010000, 18563.990000
# 226.000000, 18563.990000
# 226.010000, 18653.989846
# 2997.990000, 18611.489300
# 2997.990000, 16885.434412
# 3148.000000, 16885.424412
# 3148.010000, 18609.189164
# 4697.990000, 18585.424564
# 4697.990000, 17035.444412
# 3898.000000, 17035.444412
# 3897.990000, 16885.434412
# 4697.990000, 16885.424412
# 4697.990000, 332.010000
# 4458.000000, 332.010000
# 4457.990000, 0.010000
# 226.010000, 0.010000
# 226.010000, 325.000000"""


#plan_8

#         corners_str = """0.010000, 609.592734
# 0.010000, 5029.047554
# 62.228237, 5029.047554
# 62.238237, 5664.039568
# 0.010000, 5664.049568
# 0.010000, 8814.493597
# 750.000000, 8814.493597
# 750.010000, 8964.503597
# 0.010000, 8964.513597
# 0.010000, 10086.044317
# 62.228237, 10086.044317
# 62.238237, 10338.767158
# 316.221043, 10338.767158
# 316.231043, 10464.493597
# 1499.990000, 10464.493597
# 1499.990000, 8814.503597
# 1650.000000, 8814.493597
# 1650.010000, 10464.493597
# 6998.761763, 10464.493597
# 6998.761763, 10086.054317
# 7060.990000, 10086.044317
# 7060.990000, 5664.049568
# 6998.771763, 5664.049568
# 6998.761763, 5029.057554
# 7060.990000, 5029.047554
# 7060.990000, 609.592734
# 6998.771763, 609.592734
# 6998.761763, 228.603525
# 6426.017986, 228.603525
# 6426.007986, 0.010358
# 634.992014, 0.010000
# 634.992014, 228.593525
# 62.238237, 228.603525
# 62.238237, 609.582734"""

# #plan_9

#         corners_str = """0.010000, 295.010000
# 0.010000, 14514.990000
# 200.000000, 14514.990000
# 200.010000, 15214.990000
# 4139.990000, 15214.990000
# 4139.990000, 14915.000000
# 4729.990000, 14914.990000
# 4729.990000, 14165.010000
# 4465.000000, 14165.010000
# 4464.990000, 13165.000000
# 4729.990000, 13164.990000
# 4729.990000, 1445.010000
# 4465.000000, 1445.010000
# 4464.990000, 255.010000
# 4165.000000, 255.010000
# 4164.990000, 0.010358
# 265.010000, 0.010000
# 265.010000, 295.000000"""

# #plan_10

#         corners_str = """0.011598, 9833.696462
# 125.796330, 9856.441231
# 73.629434, 10144.994503
# 1723.607492, 10167.109881
# 1723.607492, 8517.120016
# 1873.617492, 8517.110016
# 1873.627492, 10169.120665
# 4962.762033, 10210.525688
# 4962.762033, 9915.886698
# 5190.010366, 9915.876698
# 5190.020366, 10210.516698
# 8315.525455, 10210.516698
# 8338.892811, 9930.108421
# 8476.684073, 9930.683844
# 8883.415822, 5613.136698
# 8756.876635, 5613.136698
# 8756.866635, 5216.886698
# 8920.745240, 5216.876698
# 9390.890334, 226.182915
# 9263.057024, 229.179026
# 9284.645657, 0.010275
# 5190.020440, 101.336447
# 5195.251073, 324.508802
# 4834.410600, 332.976054
# 4834.866638, 101.336703
# 1866.401233, 101.336732
# 1825.428663, 329.928462
# 1696.419835, 329.936698
# 819.779981, 5241.121631
# 945.564713, 5263.866399
# 875.066875, 5653.794748
# 750.148521, 5631.216803
# 234.981471, 8517.328633
# 973.617489, 8517.110016
# 973.627492, 8667.120016
# 208.242127, 8667.130016"""







        self.corners = []
        self.plan_final = []
        self.walls3d_final = []
        
        for c in corners_str.split("\n"):
            if len(c.strip()) > 0:
                temp = c.split(", ")
                self.corners.append((float(temp[0]), float(temp[1])))
        
        n = len(self.corners)
        for i in range(n):
            self.plan_final.append((self.corners[i][0], self.corners[i][1], self.corners[(i+1)%n][0], self.corners[(i+1)%n][1]))
            self.walls3d_final.append((self.corners[i][0], self.corners[i][1], self.corners[(i+1)%n][0], self.corners[(i+1)%n][1], 2613))

        self.plan_final, self.walls3d_final = self.apply_rotation(self.plan_final, self.walls3d_final, 0)
        self.corners = []
        for seg in self.plan_final:
            self.corners.append((seg[0], seg[1]))
        # for i in plan_final:
        #     print(i[0], i[1], i[2], i[3])
        # print()
        # for i in walls3d_final:
        #     print(i[0], i[1], i[2], i[3], i[4])
        # print()
        # print(corners)



    def get_internal_wall_partitions(self, max_length=200.0, thickness= 200.0) -> List[Tuple[float, float, float, float]]:
        """
        Identifies small, internal wall segments that act as partitions or columns.
        It returns a list of their bounding boxes to be used as obstacles.

        Args:
            max_length: The maximum length for a segment to be considered a partition.
            thickness: The assumed thickness of the wall for creating the bounding box.

        Returns:
            A list of bounding box tuples [(min_x, min_y, max_x, max_y), ...].
        """
        from ezdxf.math import Vec2
        print("  -> Identifying internal wall partitions to use as obstacles...")
        
        partitions = []
        if not self.plan_final:
            return []

        for (x1, y1, x2, y2) in self.plan_final:
            p1 = Vec2(x1, y1)
            p2 = Vec2(x2, y2)
            length = p1.distance(p2)

            # A segment is considered a partition if it's shorter than the max_length
            if 50.0 < length < max_length:
                # Create a bounding box for the wall segment
                min_x = min(p1.x, p2.x) - (thickness / 2)
                max_x = max(p1.x, p2.x) + (thickness / 2)
                min_y = min(p1.y, p2.y) - (thickness / 2)
                max_y = max(p1.y, p2.y) + (thickness / 2)
                partitions.append((min_x, min_y, max_x, max_y))
                
        print(f"    -> Found {len(partitions)} internal wall partitions.")
        return partitions
    
    def get_internal_wall_partitions_boh(self, min_length_mm=800.0, thickness=200.0, msp_debug=None) -> List[Dict[str, Any]]:
        """
        [MODIFIED] Identifies internal wall segments LARGER than a minimum size.
        Now returns a list of dictionaries, each with endpoints and a bbox.
        """
        from ezdxf.math import Vec2
        print(f"  -> Identifying internal partitions larger than {min_length_mm}mm...")
        
        partitions = []
        if not self.plan_final:
            return []

        for (x1, y1, x2, y2) in self.plan_final:
            p1 = Vec2(x1, y1)
            p2 = Vec2(x2, y2)
            length = p1.distance(p2)

            if length >= min_length_mm:
                if msp_debug:
                    msp_debug.add_line(
                        (x1, y1), (x2, y2), 
                        dxfattribs={"layer": "DEBUG_STOPPER_PARTITIONS", "lineweight": 50}
                    )
                
                min_x = min(p1.x, p2.x) - (thickness / 2)
                max_x = max(p1.x, p2.x) + (thickness / 2)
                min_y = min(p1.y, p2.y) - (thickness / 2)
                max_y = max(p1.y, p2.y) + (thickness / 2)

                # --- MODIFIED: Append a dictionary instead of a tuple ---
                partitions.append({
                    'endpoints': (x1, y1, x2, y2),
                    'bbox': (min_x, min_y, max_x, max_y)
                })
                
        print(f"    -> Found {len(partitions)} stopper partitions.")
        return partitions