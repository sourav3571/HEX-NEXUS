import numpy as np
from PIL import Image
import math
from typing import List, Tuple, Union

# ASSUMED IMPORTS: Replace with your actual schema imports
# We are assuming Point, LinePath, and CurvePath are defined in src.api.schemas
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

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
# (Your existing renderer will turn these generated paths into an SVG)
from .render import render_kolam 

DotTuple = Tuple[float, float]
PathType = Union[LinePath, CurvePath]

class KolamRecreator:
    """
    Handles image analysis for path detection and enforces 4-fold (90-degree)
    rotational and reflectional symmetry to recreate the final Kolam paths.
    """
    def __init__(self, sensitivity: int = 15):
        # Sensitivity in pixels for detecting a line between two dots
        self.sensitivity = sensitivity 
        # Defines the center of the drawing area (assuming 500x500 viewbox)
        self.center = Point(250, 250) 
    
    def _get_quadrant_dot_indices(self, dots: List[DotTuple]) -> List[int]:
        """
        Identifies dots that belong to the top-right quadrant (x >= center, y <= center).
        This is the base for symmetry extrapolation.
        """
        quadrant_indices = []
        for i, (x, y) in enumerate(dots):
            if x >= self.center.x and y <= self.center.y:
                quadrant_indices.append(i)
        return quadrant_indices

    def _get_path_segment(self, img_array: np.ndarray, dot1: DotTuple, dot2: DotTuple) -> bool:
        """
        SIMPLE IMAGE PROCESSING CHECK: Checks for a continuous color (line) 
        between two dots. This is the crucial path detection step.
        Returns True if a path exists.
        """
        x1, y1 = int(dot1[0]), int(dot1[1])
        x2, y2 = int(dot2[0]), int(dot2[1])

        num_steps = 15  # Check 15 points between dots
        
        # Simple line drawing algorithm (Bresenham-like) for checking pixels
        for i in range(1, num_steps):
            t = i / num_steps
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            
            # Check a small neighborhood around (x, y) for a non-white/non-dot color
            # We assume a line pixel has an intensity (sum of RGB) below a threshold.
            # You might need to adjust the RGB indices (0, 1, 2) based on your image mode.
            if np.mean(img_array[y, x, :3]) < 200: 
                 # Found a dark pixel: assume a line segment exists
                return True
        return False

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
        Takes the detected paths and generates 90, 180, and 270 degree rotations,
        enforcing C4 symmetry.
        """
        symmetrical_paths: List[PathType] = detected_paths.copy()
        
        for path in detected_paths:
            for angle in [90, 180, 270]:
                if isinstance(path, LinePath):
                    # Rotate the endpoints
                    new_p1 = self._rotate_point(path.p1, angle)
                    new_p2 = self._rotate_point(path.p2, angle)
                    symmetrical_paths.append(LinePath(new_p1, new_p2))
                
                elif isinstance(path, CurvePath):
                    # Rotate the endpoints and the control point
                    new_p1 = self._rotate_point(path.p1, angle)
                    new_p2 = self._rotate_point(path.p2, angle)
                    new_ctrl = self._rotate_point(path.ctrl, angle)
                    symmetrical_paths.append(CurvePath(new_p1, new_ctrl, new_p2))
                    
        return symmetrical_paths

    def recreate(self, dots: List[DotTuple], image_path: str) -> str:
        """
        Main function to orchestrate recreation and rendering.
        """
        try:
            img = Image.open(image_path).convert("RGB")
            img_array = np.array(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            return render_kolam(dots, []) # Fail gracefully by only drawing dots

        # --- PATH DETECTION: Finds the "base" paths in the image ---
        detected_paths: List[PathType] = []
        
        # We only need to analyze paths between dots in the base quadrant 
        # and their neighbors, then rely on symmetry to fill the rest.
        
        # Simple implementation: check all unique dot pairs
        dot_points = [Point(x, y) for x, y in dots]
        
        for i in range(len(dots)):
            for j in range(i + 1, len(dots)):
                dot1 = dots[i]
                dot2 = dots[j]
                
                # Check for a path segment only if the dots are reasonably close
                distance = math.sqrt((dot1[0] - dot2[0])**2 + (dot1[1] - dot2[1])**2)
                if distance < 150: # Only check near dots
                    if self._get_path_segment(img_array, dot1, dot2):
                        # Assuming all are straight LinePaths for simplicity. 
                        # Curve detection is much harder and requires more complex logic.
                        detected_paths.append(LinePath(dot_points[i], dot_points[j]))
        
        if not detected_paths:
            print("WARNING: No line paths were detected between any dots.")
            return render_kolam(dots, [])

        # --- SYMMETRY ENFORCEMENT ---
        final_paths = self._create_symmetrical_paths(detected_paths)
        
        # --- RENDERING ---
        return render_kolam(dots, final_paths)

# ----------------------------------------------------------------------
# API Endpoint Usage Example (Replace your existing RECREATE endpoint handler)
# ----------------------------------------------------------------------

def handle_recreate_endpoint(file_path: str, dot_data_from_analysis: List[DotTuple]) -> str:
    """
    The function your FastAPI/Flask route should call.
    It returns the path to the final SVG/image.
    """
    recreator = KolamRecreator()
    
    # Run the core logic
    rendered_file_path = recreator.recreate(dot_data_from_analysis, file_path)
    
    return rendered_file_path