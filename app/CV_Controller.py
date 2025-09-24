import cv2 # type: ignore
import numpy as np # type: ignore
import os
import math
import logging
import subprocess
import sys
from django.conf import settings


class CV_Controller:

    def __init__(self, img_path, out_path, overlay, fp_json):
        self.img_path = img_path
        self.out_path = out_path
        self.ovl_out = overlay
        # self.img_gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        # self.img_color = cv2.imread(img_path, cv2.IMREAD_COLOR)
        self.get_corners(fp_json)

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
            ["python3", "app/get_points.py", fp_json],  # changed from "python3" to "python"
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
        