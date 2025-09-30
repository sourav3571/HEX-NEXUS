import numpy as np
import math
from typing import List, Tuple, Union, Dict
import random 
import cv2 
import os

# ASSUMED IMPORTS: These classes must match the definitions used elsewhere (e.g., src.api.schemas)
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

class LinePath:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

class CurvePath:
    def __init__(self, p1: Point, ctrl: Point, p2: Point):
        self.p1 = p1
        self.ctrl = ctrl
        self.p2 = p2

# Assume render_kolam is imported from render.py
from .render import render_kolam 

DotTuple = Tuple[float, float]
PathType = Union[LinePath, CurvePath]

class KolamRecreator:
    """
    Generates authentic, symmetric Kolam paths by inferring grid relationships 
    between detected dots and generating looping Bezier curves.
    """
    def __init__(self, proximity_threshold: int = 200): # Increased to 200
        self.proximity_threshold = proximity_threshold 
        self.viewbox_size = 500 # Target size for all coordinate geometry
        self.center = Point(self.viewbox_size / 2, self.viewbox_size / 2) 
        self.tolerance = 30 # Increased to 30
        
    def _load_and_enhance_image(self, image_path: str) -> np.ndarray:
        """Loads, converts to grayscale, and enhances image contrast (CLAHE)."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")
            
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            raise IOError("Could not load image using OpenCV.")
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_gray = clahe.apply(gray)
        
        return enhanced_gray
    
    def _draw_minor_curve(self, image_data: np.ndarray, dots: List[Point]):
        """Placeholder for logic to draw small, local features."""
        pass
    
    def _scale_dot_coordinates(self, dots: List[DotTuple], original_width: int, original_height: int) -> List[DotTuple]:
        """Scales dot coordinates from original image size to the standard viewbox size (500x500)."""
        scale_x = self.viewbox_size / original_width
        scale_y = self.viewbox_size / original_height
        
        scaled_dots = []
        for x, y in dots:
            scaled_dots.append((x * scale_x, y * scale_y))
        return scaled_dots

    def _get_quadrant_dot_points(self, dots: List[DotTuple]) -> List[Point]:
        """
        Converts dot tuples to Point objects and filters for the top-right 
        quadrant (x >= center, y <= center) to define the base motif.
        """
        quadrant_points: List[Point] = []
        for x, y in dots:
            p = Point(x, y)
            if p.x >= self.center.x - self.tolerance and p.y <= self.center.y + self.tolerance:
                quadrant_points.append(p)
        return quadrant_points

    def _find_neighbors(self, base_dot: Point, all_dots: List[Point]) -> Dict[str, Point]:
        """
        Finds the closest horizontal and vertical neighbor for the base dot, 
        assuming a standard grid pattern.
        """
        neighbors = {}
        min_dist_x = float('inf')
        min_dist_y = float('inf')

        for dot in all_dots:
            if abs(dot.x - base_dot.x) < 1 and abs(dot.y - base_dot.y) < 1:
                continue

            dx = abs(dot.x - base_dot.x)
            dy = abs(dot.y - base_dot.y)

            if dy < self.tolerance and dx > self.tolerance and dx < self.proximity_threshold:
                if dx < min_dist_x:
                    neighbors['x_neighbor'] = dot
                    min_dist_x = dx
            
            elif dx < self.tolerance and dy > self.tolerance and dy < self.proximity_threshold:
                if dy < min_dist_y:
                    neighbors['y_neighbor'] = dot
                    min_dist_y = dy

        return neighbors

    def _create_loop(self, p1: Point, p2: Point) -> CurvePath:
        """
        Generates a Quadratic Bezier Curve that loops outward between two dots.
        
        The control point is set perpendicular to the line segment (p1, p2)
        and bulges inward toward the center of the canvas.
        """
        
        # Midpoint of the segment
        mid_x = (p1.x + p2.x) / 2
        mid_y = (p1.y + p2.y) / 2

        # Vector of the segment (p2 - p1)
        seg_x = p2.x - p1.x
        seg_y = p2.y - p1.y
        
        # Perpendicular vector (rotated 90 degrees: (-seg_y, seg_x) or (seg_y, -seg_x))
        # We need to choose the direction that pulls the curve AWAY from the canvas center.
        perp_x_a, perp_y_a = -seg_y, seg_x
        perp_x_b, perp_y_b = seg_y, -seg_x

        # Calculate control points for both directions
        # We test which control point direction points AWAY from the center (250, 250)
        
        # Direction A
        center_to_mid_x = self.center.x - mid_x
        center_to_mid_y = self.center.y - mid_y
        
        # Dot product test: (perp_vector) . (vector from control to center)
        # If the dot product is negative, the perp vector points away from the center
        dot_product_a = perp_x_a * center_to_mid_x + perp_y_a * center_to_mid_y
        
        # Choose the perpendicular vector that pulls the curve AWAY from the center
        if dot_product_a > 0:
            perp_x, perp_y = perp_x_a, perp_y_a
        else:
            perp_x, perp_y = perp_x_b, perp_y_b
            
        # Normalize the perpendicular vector
        perp_length = math.sqrt(perp_x**2 + perp_y**2)
        if perp_length > 0:
            unit_perp_x = perp_x / perp_length
            unit_perp_y = perp_y / perp_length
        else:
            # Fallback for zero-length segment (shouldn't happen)
            unit_perp_x, unit_perp_y = 0, 0
            
        # Determine bulge distance based on segment length (10% to 20% of segment length)
        segment_length = math.sqrt(seg_x**2 + seg_y**2)
        bulge_distance = segment_length * random.uniform(0.1, 0.2) 
        
        # Calculate final control point
        ctrl_x = mid_x + unit_perp_x * bulge_distance
        ctrl_y = mid_y + unit_perp_y * bulge_distance

        return CurvePath(p1, Point(ctrl_x, ctrl_y), p2)

    def _rotate_point(self, p: Point, angle_deg: int) -> Point:
        """Rotates a point around the center (250, 250) by a given angle."""
        angle_rad = math.radians(angle_deg)
        x = p.x - self.center.x
        y = p.y - self.center.y
        
        new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        
        return Point(new_x + self.center.x, new_y + self.center.y)

    def _create_symmetrical_paths(self, detected_paths: List[PathType]) -> List[PathType]:
        """
        Takes the base paths and generates 90, 180, and 270 degree rotations,
        enforcing C4 symmetry.
        """
        symmetrical_paths: List[PathType] = detected_paths.copy()
        
        for path in detected_paths:
            for angle in [90, 180, 270]:
                if isinstance(path, CurvePath):
                    new_p1 = self._rotate_point(path.p1, angle)
                    new_p2 = self._rotate_point(path.p2, angle)
                    new_ctrl = self._rotate_point(path.ctrl, angle)
                    symmetrical_paths.append(CurvePath(new_p1, new_ctrl, new_p2))
                                    
        return symmetrical_paths

    def recreate(self, detected_dots: List[DotTuple], image_path: str) -> str:
        """
        Main function to orchestrate recreation and rendering using grid inference.
        """
        # --- 0. Load and Pre-process Image ---
        try:
            enhanced_image = self._load_and_enhance_image(image_path)
            # Use original dimensions from the image to correctly scale the dot coordinates
            original_height, original_width = enhanced_image.shape[:2]
        except Exception as e:
            print(f"ERROR loading image for geometry: {e}. Proceeding with unscaled dots if available.")
            original_width, original_height = 0, 0 
            return render_kolam(detected_dots, []) if detected_dots else ""

        # --- 1. Scale Dots ---
        if original_width > 0 and original_height > 0:
            scaled_dots = self._scale_dot_coordinates(detected_dots, original_width, original_height)
        else:
            scaled_dots = detected_dots

        # --- 2. Identify Base Dots (Top-Right Quadrant) ---
        all_dot_points = [Point(x, y) for x, y in scaled_dots]
        base_dots = self._get_quadrant_dot_points(scaled_dots)
        
        if not base_dots:
            print("WARNING: No dots detected in the base quadrant for pattern creation.")
            return render_kolam(scaled_dots, []) 

        # --- 3. Generate Base Looping Paths ---
        detected_paths: List[PathType] = []
        processed_pairs = set()

        for dot1 in base_dots:
            neighbors = self._find_neighbors(dot1, all_dot_points)
            
            # Horizontal neighbor loop
            if 'x_neighbor' in neighbors:
                dot2 = neighbors['x_neighbor']
                pair = tuple(sorted(((dot1.x, dot1.y), (dot2.x, dot2.y))))
                if pair not in processed_pairs:
                    detected_paths.append(self._create_loop(dot1, dot2))
                    processed_pairs.add(pair)

            # Vertical neighbor loop
            if 'y_neighbor' in neighbors:
                dot2 = neighbors['y_neighbor']
                pair = tuple(sorted(((dot1.x, dot1.y), (dot2.x, dot2.y))))
                if pair not in processed_pairs:
                    detected_paths.append(self._create_loop(dot1, dot2))
                    processed_pairs.add(pair)
        
        if not detected_paths:
            print("WARNING: No meaningful looping paths could be inferred.")
            return render_kolam(scaled_dots, [])

        # --- 4. SYMMETRY ENFORCEMENT ---
        final_paths = self._create_symmetrical_paths(detected_paths)
        
        # --- 5. RENDERING ---
        return render_kolam(scaled_dots, final_paths)
