# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import cv2
import numpy as np
import tempfile
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import pdist, squareform
import math

from render import render_kolam
from schemas import KolamRequest, Dot, LinePath, CurvePath

app = FastAPI(title="Kolam AI server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/img", StaticFiles(directory="img"), name="img")

@app.post("/api/create_kolam")
def create_kolam(data: KolamRequest):
    filename = render_kolam(
        [(dot.x, dot.y) for dot in data.dots],
        data.paths
    )
    return {"message": "Kolam created", "file": filename}


def detect_dots_in_image(img):
    """Detect dots in the kolam image using advanced computer vision techniques"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Multiple detection strategies
    detected_points = []
    
    # Strategy 1: HoughCircles for circular dots
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
        param1=50, param2=30, minRadius=2, maxRadius=15
    )
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            detected_points.append((x, y))
    
    # Strategy 2: Corner detection for dot intersections
    corners = cv2.goodFeaturesToTrack(
        gray, maxCorners=100, qualityLevel=0.01, minDistance=15
    )
    
    if corners is not None:
        for corner in corners:
            x, y = corner.ravel()
            detected_points.append((int(x), int(y)))
    
    # Strategy 3: Blob detection
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 10
    params.maxArea = 200
    params.filterByCircularity = True
    params.minCircularity = 0.3
    
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(gray)
    
    for kp in keypoints:
        detected_points.append((int(kp.pt[0]), int(kp.pt[1])))
    
    if not detected_points:
        # Fallback: Create regular grid based on image dimensions
        h, w = gray.shape
        # Determine grid size based on image analysis
        grid_size = determine_grid_size(gray)
        return create_regular_grid(w, h, grid_size)
    
    # Cluster similar points to remove duplicates
    if len(detected_points) > 1:
        clustering = DBSCAN(eps=15, min_samples=1).fit(detected_points)
        unique_points = []
        for cluster_id in set(clustering.labels_):
            cluster_points = [detected_points[i] for i in range(len(detected_points)) 
                            if clustering.labels_[i] == cluster_id]
            # Take centroid of cluster
            center_x = int(np.mean([p[0] for p in cluster_points]))
            center_y = int(np.mean([p[1] for p in cluster_points]))
            unique_points.append((center_x, center_y))
        detected_points = unique_points
    
    return detected_points


def determine_grid_size(gray):
    """Determine the grid size of the kolam based on image analysis"""
    # Analyze the image to determine likely grid dimensions
    h, w = gray.shape
    
    # Use edge detection to find structure
    edges = cv2.Canny(gray, 50, 150)
    
    # Find horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w//10, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h//10))
    
    horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
    
    # Count intersections to estimate grid size
    combined = cv2.add(horizontal_lines, vertical_lines)
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Estimate grid size based on content density
    content_area = cv2.countNonZero(cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1])
    total_area = h * w
    density = content_area / total_area
    
    if density > 0.3:
        return 5  # Complex kolam
    elif density > 0.15:
        return 4  # Medium kolam
    else:
        return 3  # Simple kolam


def create_regular_grid(width, height, grid_size):
    """Create a regular grid of dots"""
    margin = min(width, height) * 0.1
    x_positions = np.linspace(margin, width - margin, grid_size)
    y_positions = np.linspace(margin, height - margin, grid_size)
    
    dots = []
    for y in y_positions:
        for x in x_positions:
            dots.append((int(x), int(y)))
    
    return dots


def detect_lines_and_curves(img, dots):
    """Detect lines and curves in the kolam image - FIXED VERSION"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Preprocess image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    lines = []
    curves = []
    
    # Convert dots to Dot objects for easier handling
    dot_objects = [Dot(x=float(x), y=float(y)) for x, y in dots]
    
    # Strategy 1: Detect straight lines using HoughLinesP
    edges = cv2.Canny(thresh, 50, 150)
    detected_lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, minLineLength=30, maxLineGap=15)
    
    if detected_lines is not None:
        for line in detected_lines:
            x1, y1, x2, y2 = line[0]
            # Find closest dots to line endpoints
            start_dot = find_closest_dot(dot_objects, (x1, y1))
            end_dot = find_closest_dot(dot_objects, (x2, y2))
            
            if start_dot != end_dot:  # Avoid self-loops
                lines.append(LinePath(p1=start_dot, p2=end_dot))
    
    # Strategy 2: Color-based detection for red elements (curves in kolams)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Detect red elements (often curves in kolams)
    red_mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
    red_mask2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
    red_mask = red_mask1 + red_mask2
    
    # ONLY create curves if there are actually red elements detected
    if cv2.countNonZero(red_mask) > 100:
        # Strategy 2a: Detect curves using contour analysis (ONLY if red elements exist)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area threshold
                # Check if contour is curved
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if 0.1 < circularity < 0.8:  # Curved shape
                        # Approximate contour to get key points
                        epsilon = 0.02 * perimeter
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) >= 3:
                            # Create curves from approximated points
                            for i in range(len(approx) - 2):
                                p1 = approx[i][0]
                                ctrl = approx[i + 1][0]
                                p2 = approx[i + 2][0]
                                
                                start_dot = find_closest_dot(dot_objects, (p1[0], p1[1]))
                                control_dot = Dot(x=float(ctrl[0]), y=float(ctrl[1]))
                                end_dot = find_closest_dot(dot_objects, (p2[0], p2[1]))
                                
                                curves.append(CurvePath(p1=start_dot, ctrl=control_dot, p2=end_dot))
        
        # Strategy 2b: Find red contours and create curves from them
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in red_contours:
            if cv2.contourArea(contour) > 50:
                # Create curve from contour
                moments = cv2.moments(contour)
                if moments["m00"] != 0:
                    cx = int(moments["m10"] / moments["m00"])
                    cy = int(moments["m01"] / moments["m00"])
                    
                    # Find nearest dots to create meaningful curves
                    center_dot = Dot(x=float(cx), y=float(cy))
                    closest_dots = sorted(dot_objects, key=lambda d: distance(d, center_dot))[:3]
                    
                    if len(closest_dots) >= 3:
                        curves.append(CurvePath(
                            p1=closest_dots[0],
                            ctrl=center_dot,
                            p2=closest_dots[1]
                        ))
    
    # Strategy 3: Pattern-based detection for common kolam structures
    lines.extend(detect_common_patterns(dot_objects, w, h))
    
    # Remove duplicate lines and curves
    lines = remove_duplicate_lines(lines)
    curves = remove_duplicate_curves(curves)
    
    return lines, curves


def find_closest_dot(dots, point):
    """Find the closest dot to a given point"""
    min_dist = float('inf')
    closest_dot = dots[0] if dots else None
    
    if not dots:
        return None
    
    for dot in dots:
        dist = distance(dot, Dot(x=float(point[0]), y=float(point[1])))
        if dist < min_dist:
            min_dist = dist
            closest_dot = dot
    
    return closest_dot


def distance(dot1, dot2):
    """Calculate Euclidean distance between two dots"""
    return math.sqrt((dot1.x - dot2.x)**2 + (dot1.y - dot2.y)**2)


def detect_common_patterns(dots, width, height):
    """Detect common kolam patterns like perimeters, diagonals, etc."""
    lines = []
    
    if len(dots) < 4:
        return lines
    
    # Sort dots by position to identify patterns
    sorted_by_x = sorted(dots, key=lambda d: d.x)
    sorted_by_y = sorted(dots, key=lambda d: d.y)
    
    # Detect perimeter (border) lines
    # Top and bottom edges
    top_dots = [d for d in dots if abs(d.y - sorted_by_y[0].y) < height * 0.1]
    bottom_dots = [d for d in dots if abs(d.y - sorted_by_y[-1].y) < height * 0.1]
    
    if len(top_dots) >= 2:
        top_sorted = sorted(top_dots, key=lambda d: d.x)
        for i in range(len(top_sorted) - 1):
            lines.append(LinePath(p1=top_sorted[i], p2=top_sorted[i + 1]))
    
    if len(bottom_dots) >= 2:
        bottom_sorted = sorted(bottom_dots, key=lambda d: d.x)
        for i in range(len(bottom_sorted) - 1):
            lines.append(LinePath(p1=bottom_sorted[i], p2=bottom_sorted[i + 1]))
    
    # Left and right edges
    left_dots = [d for d in dots if abs(d.x - sorted_by_x[0].x) < width * 0.1]
    right_dots = [d for d in dots if abs(d.x - sorted_by_x[-1].x) < width * 0.1]
    
    if len(left_dots) >= 2:
        left_sorted = sorted(left_dots, key=lambda d: d.y)
        for i in range(len(left_sorted) - 1):
            lines.append(LinePath(p1=left_sorted[i], p2=left_sorted[i + 1]))
    
    if len(right_dots) >= 2:
        right_sorted = sorted(right_dots, key=lambda d: d.y)
        for i in range(len(right_sorted) - 1):
            lines.append(LinePath(p1=right_sorted[i], p2=right_sorted[i + 1]))
    
    return lines


def remove_duplicate_lines(lines):
    """Remove duplicate line paths"""
    unique_lines = []
    for line in lines:
        is_duplicate = False
        for existing in unique_lines:
            if ((line.p1.x == existing.p1.x and line.p1.y == existing.p1.y and
                 line.p2.x == existing.p2.x and line.p2.y == existing.p2.y) or
                (line.p1.x == existing.p2.x and line.p1.y == existing.p2.y and
                 line.p2.x == existing.p1.x and line.p2.y == existing.p1.y)):
                is_duplicate = True
                break
        if not is_duplicate:
            unique_lines.append(line)
    return unique_lines


def remove_duplicate_curves(curves):
    """Remove duplicate curve paths"""
    unique_curves = []
    for curve in curves:
        is_duplicate = False
        for existing in unique_curves:
            if (abs(curve.p1.x - existing.p1.x) < 5 and abs(curve.p1.y - existing.p1.y) < 5 and
                abs(curve.p2.x - existing.p2.x) < 5 and abs(curve.p2.y - existing.p2.y) < 5 and
                abs(curve.ctrl.x - existing.ctrl.x) < 5 and abs(curve.ctrl.y - existing.ctrl.y) < 5):
                is_duplicate = True
                break
        if not is_duplicate:
            unique_curves.append(curve)
    return unique_curves


@app.post("/api/know-your-kolam")
async def know_your_kolam(file: UploadFile = File(...)):
    """Enhanced kolam detection that works with different kolam designs"""
    # Save uploaded file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(await file.read())
    tmp.close()
    
    try:
        # Load and process image
        img = cv2.imread(tmp.name, cv2.IMREAD_COLOR)
        if img is None:
            return {"error": "Could not load image"}
        
        h, w = img.shape[:2]
        
        # Step 1: Detect dots in the image
        detected_dots = detect_dots_in_image(img)
        
        # Convert to Dot objects
        dots = [Dot(x=float(x), y=float(y)) for x, y in detected_dots]
        
        # Step 2: Detect lines and curves
        lines, curves = detect_lines_and_curves(img, detected_dots)
        
        # Combine all paths
        all_paths = []
        for line in lines:
            all_paths.append(line)
        for curve in curves:
            all_paths.append(curve)
        
        # Step 3: Return formatted response that matches KolamRequest schema
        result = {
            "dots": [{"x": dot.x, "y": dot.y} for dot in dots],
            "paths": []
        }
        
        # Format paths according to schema
        for path in all_paths:
            if isinstance(path, LinePath):
                result["paths"].append({
                    "type": "line",
                    "p1": {"x": path.p1.x, "y": path.p1.y},
                    "p2": {"x": path.p2.x, "y": path.p2.y}
                })
            elif isinstance(path, CurvePath):
                result["paths"].append({
                    "type": "curve",
                    "p1": {"x": path.p1.x, "y": path.p1.y},
                    "ctrl": {"x": path.ctrl.x, "y": path.ctrl.y},
                    "p2": {"x": path.p2.x, "y": path.p2.y}
                })
        
        return result
        
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)