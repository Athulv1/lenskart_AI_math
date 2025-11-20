import cv2 # type: ignore
import numpy as np # type: ignore
import os
import math
import logging
import subprocess
import sys
import json
from django.conf import settings
from typing import List, Tuple, Dict, Any
from ezdxf.math import Vec2

logger = logging.getLogger("app")
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

    # touched
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
        # Use the currently running Python interpreter to invoke the helper script
        # (avoids relying on "python3" being present on Windows)
        result = subprocess.run(
            [sys.executable, "app/layout.py", json.dumps(fp_json)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # to get output as string instead of bytes
        )
        # print("HERE")

        if result.returncode != 0:
            raise RuntimeError(f"Worker failed:\n{result.stderr}")
        
        # print(result.stdout.strip())

        self.plan_final = {}
        self.walls3d_final = {}
        self.windows = []
        self.doors = []
        self.corners = []
        end1 = False
        end2 = False
        end3 = False
        end4 = False
        output = result.stdout.strip()  # remove trailing newline
        output = output.split("\n")
        # print("HERE2")
        for row in output:
            rArr = row.split()
            # print(row)
            # print()
            if not end1:
                if len(row.strip()) > 0:
                    # print(1, row)
                    self.plan_final[rArr[0]] = [float(rArr[1]), float(rArr[2]), float(rArr[3]), float(rArr[4])]
                else:
                    end1 = True
            elif not end2:
                if len(row.strip()) > 0:
                    # print(2, row)
                    self.walls3d_final[rArr[0]] = [float(rArr[1]), float(rArr[2]), float(rArr[3]), float(rArr[4]), float(rArr[5])]
                else:
                    end2 = True
            elif not end3:
                if len(row.strip()) > 0:
                    # print(3, row.strip().replace("'", '"'))
                    temp = json.loads(row.strip().replace("'", '"'))
                    self.windows.append(temp)
                else:
                    end3 = True
            elif not end4:

                if len(row.strip()) > 0:
                    # print(4, row.strip().replace("'", '"'))
                    temp = json.loads(row.strip().replace("'", '"'))
                    self.doors.append(temp)
                else:
                    end4 = True
            else:
                if len(row.strip()) > 0:
                    # print(5, row)
                    self.corners.append([float(rArr[0]), float(rArr[1])])
        #     print()

        # print("HERE2")

            
        
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
    
    def get_internal_wall_partitions(self, min_length = 50.0 ,max_length=200.0, thickness= 200.0) -> List[Tuple[float, float, float, float]]:
        """
        Identifies small, internal wall segments that act as partitions or columns.
        It returns a list of their bounding boxes to be used as obstacles.

        Args:
            max_length: The maximum length for a segment to be considered a partition.
            thickness: The assumed thickness of the wall for creating the bounding box.

        Returns:
            A list of bounding box tuples [(min_x, min_y, max_x, max_y), ...].
        """
        print("  -> Identifying internal wall partitions to use as obstacles...")
        
        partitions = []
        if not self.plan_final:
            return []

        for key, value in self.plan_final.items():
            x1 = value[0]
            y1 = value[1]
            x2 = value[2]
            y2 = value[3]
            p1 = Vec2(x1, y1)
            p2 = Vec2(x2, y2)
            length = p1.distance(p2)

            # A segment is considered a partition if it's shorter than the max_length
            if min_length < length < max_length:
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
        print(f"  -> Identifying internal partitions larger than {min_length_mm}mm...")
        
        partitions = []
        if not self.plan_final:
            return []

        for key, value in self.plan_final.items():
            x1 = value[0]
            y1 = value[1]
            x2 = value[2]
            y2 = value[3]
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