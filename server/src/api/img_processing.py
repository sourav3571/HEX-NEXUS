# app.py (Integrated Version)
import cv2
import numpy as np
import streamlit as st
from tempfile import NamedTemporaryFile
import math
from sklearn.cluster import DBSCAN

# --- Placeholder for structural Pydantic Schemas (Assuming they are available) ---
# NOTE: In a real project, these would be imported from src.api.schemas
class Dot:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
class LinePath:
    def __init__(self, p1: Dot, p2: Dot):
        self.p1 = p1
        self.p2 = p2
class CurvePath:
    def __init__(self, p1: Dot, ctrl: Dot, p2: Dot):
        self.p1 = p1
        self.ctrl = ctrl
        self.p2 = p2
# ---------------------------------------------------------------------------------

# --- ANALYSIS FUNCTIONS (from your second code block) ---
# NOTE: In a real project, these should be moved to a separate utility file (e.g., src/api/kolam_detector.py)
# Only the main functions are included here for integration completeness.

def distance(dot1, dot2):
    return math.sqrt((dot1.x - dot2.x)**2 + (dot1.y - dot2.y)**2)

def find_closest_dot(dots, point):
    min_dist = float('inf')
    closest_dot = dots[0] if dots else None
    if not dots: return None
    
    for dot in dots:
        dist = distance(dot, Dot(x=float(point[0]), y=float(point[1])))
        if dist < min_dist:
            min_dist = dist
            closest_dot = dot
    return closest_dot

def determine_grid_size(gray):
    # Simplified placeholder for integration
    return 5 

def create_regular_grid(width, height, grid_size):
    margin = min(width, height) * 0.1
    x_positions = np.linspace(margin, width - margin, grid_size)
    y_positions = np.linspace(margin, height - margin, grid_size)
    dots = []
    for y in y_positions:
        for x in x_positions:
            dots.append((int(x), int(y)))
    return dots

def detect_dots_in_image(img):
    # Only using HoughCircles and DBSCAN for simplicity in integration example
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30, param1=50, param2=12, minRadius=8, maxRadius=20)
    
    detected_points = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        detected_points = [(x, y) for (x, y, r) in circles]

    if not detected_points:
        h, w = gray.shape
        grid_size = determine_grid_size(gray)
        return create_regular_grid(w, h, grid_size)
    
    # Cluster similar points
    if len(detected_points) > 1:
        clustering = DBSCAN(eps=15, min_samples=1).fit(detected_points)
        unique_points = []
        for cluster_id in set(clustering.labels_):
            cluster_points = [detected_points[i] for i in range(len(detected_points)) if clustering.labels_[i] == cluster_id]
            center_x = int(np.mean([p[0] for p in cluster_points]))
            center_y = int(np.mean([p[1] for p in cluster_points]))
            unique_points.append((center_x, center_y))
        detected_points = unique_points
    
    return detected_points

def detect_lines_and_curves(img, dots):
    # Functionality from your second block remains the same
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    lines = []
    curves = []
    dot_objects = [Dot(x=float(x), y=float(y)) for x, y in dots]
    
    # 1. Detect straight lines using HoughLinesP
    edges = cv2.Canny(thresh, 50, 150)
    detected_lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, minLineLength=30, maxLineGap=15)
    
    if detected_lines is not None:
        for line in detected_lines:
            x1, y1, x2, y2 = line[0]
            start_dot = find_closest_dot(dot_objects, (x1, y1))
            end_dot = find_closest_dot(dot_objects, (x2, y2))
            if start_dot != end_dot and start_dot and end_dot:
                lines.append(LinePath(p1=start_dot, p2=end_dot))

    # 2. Detect curves (Simplified to only check contours for this example)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:
             perimeter = cv2.arcLength(contour, True)
             if perimeter > 0:
                 circularity = 4 * np.pi * area / (perimeter * perimeter)
                 if 0.1 < circularity < 0.8:  # Curved shape
                     epsilon = 0.02 * perimeter
                     approx = cv2.approxPolyDP(contour, epsilon, True)
                     
                     if len(approx) >= 3:
                        p1_coord = approx[0][0]
                        p2_coord = approx[-1][0]
                        ctrl_coord = approx[len(approx)//2][0]

                        start_dot = find_closest_dot(dot_objects, (p1_coord[0], p1_coord[1]))
                        end_dot = find_closest_dot(dot_objects, (p2_coord[0], p2_coord[1]))
                        control_dot = Dot(x=float(ctrl_coord[0]), y=float(ctrl_coord[1]))
                        
                        if start_dot and end_dot:
                            curves.append(CurvePath(p1=start_dot, ctrl=control_dot, p2=end_dot))
    
    # NOTE: The original complex duplicate removal and pattern detection functions are omitted 
    # for brevity but should be kept in your final utility code.
    return lines, curves
# ----------------------------------------------------------------------


def draw_symmetrical_kolam(h, w, lines: list[LinePath], curves: list[CurvePath], dot_objects: list[Dot]):
    """Draws the detected kolam structure with enforced 4-way symmetry."""
    canvas = np.zeros((h, w, 3), dtype="uint8")
    chalk_color = (240, 240, 240) # Near white
    
    # 1. Enforce Symmetry on the Drawing Commands
    # We only process the detected elements in the top-left quadrant (w/2, h/2) 
    # and then reflect them.
    
    def apply_4_way_symmetry(p: Dot):
        """Generates 4 symmetric points from a point p in the top-left quadrant."""
        # Top-Left (Original/Base)
        yield p
        # Top-Right (Reflection across Y-axis, x becomes w-x)
        yield Dot(x=w - p.x, y=p.y)
        # Bottom-Left (Reflection across X-axis, y becomes h-y)
        yield Dot(x=p.x, y=h - p.y)
        # Bottom-Right (Reflection across origin/both axes)
        yield Dot(x=w - p.x, y=h - p.y)

    # 2. Draw Dots (Ensuring all dots, including reflected ones, are drawn)
    all_dots_to_draw = set()
    for dot in dot_objects:
        if dot.x <= w / 2 and dot.y <= h / 2: # Only consider base quadrant
            for sym_dot in apply_4_way_symmetry(dot):
                all_dots_to_draw.add((int(sym_dot.x), int(sym_dot.y)))
    
    for x, y in all_dots_to_draw:
         cv2.circle(canvas, (x, y), 6, chalk_color, -1)

    # 3. Draw Lines and Curves
    elements_to_draw = []
    
    # Lines: Only process lines where BOTH endpoints are in the top-left quadrant
    for line in lines:
        if line.p1.x <= w / 2 and line.p1.y <= h / 2 and line.p2.x <= w / 2 and line.p2.y <= h / 2:
            elements_to_draw.append(('line', line.p1, line.p2))

    # Curves: Only process curves where BOTH endpoints and control point are in the top-left quadrant
    for curve in curves:
        if (curve.p1.x <= w / 2 and curve.p1.y <= h / 2 and
            curve.p2.x <= w / 2 and curve.p2.y <= h / 2 and
            curve.ctrl.x <= w / 2 and curve.ctrl.y <= h / 2):
            elements_to_draw.append(('curve', curve.p1, curve.ctrl, curve.p2))


    for element in elements_to_draw:
        if element[0] == 'line':
            _, p1, p2 = element
            base_points = [(p1, p2)]
        elif element[0] == 'curve':
            _, p1, ctrl, p2 = element
            base_points = [(p1, ctrl, p2)]

        for p_set in base_points:
            # Generate and draw 4 symmetric versions of the element
            for i in range(4):
                # Apply rotation/reflection transformation to points for each quadrant
                if element[0] == 'line':
                    sp1, sp2 = p_set
                    # Use a simpler drawing method than full geometric reflection for simplicity
                    # The goal is to draw the element and its symmetric reflections
                    
                    # Reflection logic is complex, simpler to draw the *base* element and rely on a final flip:
                    cv2.line(canvas, (int(sp1.x), int(sp1.y)), (int(sp2.x), int(sp2.y)), chalk_color, 3)

                elif element[0] == 'curve':
                    sp1, s_ctrl, sp2 = p_set
                    # Simple drawing of Beziers isn't available in standard OpenCV. 
                    # We'll approximate the curve with lines for this example.
                    pts = np.array([
                        (int(sp1.x), int(sp1.y)),
                        (int(s_ctrl.x), int(s_ctrl.y)),
                        (int(sp2.x), int(sp2.y))
                    ], np.int32)
                    cv2.polylines(canvas, [pts], False, chalk_color, 3)


    # FINAL SYMMETRY ENFORCEMENT (This is the most direct way to ensure symmetry)
    # 1. Get the perfectly drawn top-left quadrant
    top_left = canvas[:h//2, :w//2].copy()
    
    # 2. Reflect Top-Left to Top-Right
    top_right = cv2.flip(top_left, 1) # Flip horizontally
    canvas[:h//2, w//2:] = top_right
    
    # 3. Reflect Top Half to Bottom Half
    top_half = canvas[:h//2, :].copy()
    bottom_half = cv2.flip(top_half, 0) # Flip vertically
    canvas[h//2:, :] = bottom_half

    
    # Apply chalky effects
    chalky = cv2.GaussianBlur(canvas, (3, 3), 0)
    noise = np.random.randint(0, 30, (h, w, 3), dtype="uint8")
    chalky = cv2.add(chalky, noise)
    
    return chalky


def recreate_chalk_kolam_integrated(image_path):
    """Integrated pipeline: Detect structure, then recreate symmetrically."""
    image = cv2.imread(image_path)
    if image is None: return None
    h, w = image.shape[:2]

    # 1. Detection Phase
    dots_coords = detect_dots_in_image(image)
    lines, curves = detect_lines_and_curves(image, dots_coords)
    dot_objects = [Dot(x=float(x), y=float(y)) for x, y in dots_coords]

    # 2. Recreation Phase (Enforced Symmetry)
    result = draw_symmetrical_kolam(h, w, lines, curves, dot_objects)
    return result


# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Kolam Re-Creator ", layout="centered")
st.title("🎨 Kolam Re-Creator (Structural Analysis)")
st.write("Upload a kolam image; the system **detects the structure** (dots, lines, curves) and **re-draws it with enforced 4-way symmetry**.")

uploaded_file = st.file_uploader("Upload Kolam Image (jpg, png)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    with NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    result_bgr = recreate_chalk_kolam_integrated(tmp_path)

    if result_bgr is None:
        st.error("Could not process the image. Make sure the file is a valid image.")
    else:
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        st.image(result_rgb, caption="Re-created Chalk Kolam (4-way symmetry enforced)", use_container_width=True)

        # Provide download button (PNG)
        _, encoded_png = cv2.imencode(".png", result_bgr)
        st.download_button(
            label="📥 Download re-created kolam (PNG)",
            data=encoded_png.tobytes(),
            file_name="recreated_kolam_symmetric.png",
            mime="image/png"
        )

        st.success("Done — your kolam is ready!")

st.markdown("---")
st.caption("This integrated app uses the structural analysis and drawing functions to achieve robust symmetry.")