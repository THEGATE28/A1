# ==============================================================================
# Project: Projectile Motion Simulator (Physics Interactive Animation)
# Mode: Processing (Python Mode)
# ==============================================================================

# --- ค่าคงที่และตัวแปรหลักทางฟิสิกส์ ---
g = 9.8  # ค่าความเร่งโน้มถ่วง (m/s^2)
initial_velocity = 45.0  # ความเร็วต้น v0 (m/s)
launch_angle = 45.0  # มุมยิง theta (องศา)
t = 0.0  # เวลาปัจจุบัน (s)
dt = 0.035  # delta t สำหรับการอัปเดตแต่ละเฟรม

current_x = 0.0
current_y = 0.0
is_animating = False
is_finished = False

# --- ผลลัพธ์การคำนวณ (Outputs) ---
max_height = 0.0
max_range = 0.0
total_time = 0.0

# --- อาเรย์เก็บพิกัดสำหรับวาด Trajectory Line ---
x_points = [0.0]
y_points = [0.0]

# --- สเกลและพิกัดการแสดงผลบน Canvas ---
origin_x = 90
origin_y = 530
scale_m = 1.7  # 1 เมตร = 1.7 พิกเซล


# --- คลาสจำลอง UI Controls (Slider & Button) ---
class Slider:

    def __init__(self, x, y, w, h, min_v, max_v, default_v, label, unit):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.min_v = min_v
        self.max_v = max_v
        self.val = default_v
        self.label = label
        self.unit = unit
        self.is_dragging = False

    def display(self):
        # แถบพื้นหลัง
        fill(45, 48, 65)
        stroke(70, 75, 100)
        strokeWeight(1.5)
        rect(self.x, self.y, self.w, self.h, 6)

        # แถบความคืบหน้า
        fill_w = map(self.val, self.min_v, self.max_v, 0, self.w)
        fill(66, 135, 245)
        rect(self.x, self.y, fill_w, self.h, 6)

        # ปุ่มเลื่อน (Knob)
        fill(255)
        stroke(40)
        ellipse(self.x + fill_w, self.y + self.h / 2, self.h + 8, self.h + 8)

        # ข้อความระบุค่า
        fill(220)
        textAlign(LEFT, CENTER)
        textSize(13)
        text(
            self.label + ": " + nf(float(self.val), 0, 1) + " " + self.unit,
            self.x,
            self.y - 12,
        )

    def is_hover(self):
        # ตรวจจับเฉพาะพื้นที่รอบตัว Slider อย่างแม่นยำ
        return (
            self.x - 10 <= mouseX <= self.x + self.w + 10
            and self.y - 10 <= mouseY <= self.y + self.h + 10
        )

    def update(self):
        if self.is_dragging:
            ratio = constrain((mouseX - self.x) / float(self.w), 0.0, 1.0)
            self.val = self.min_v + ratio * (self.max_v - self.min_v)
        return self.val


class Button:

    def __init__(self, x, y, w, h, label, bg_color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.bg_color = bg_color

    def display(self):
        if self.is_hover():
            fill(
                red(self.bg_color) + 25,
                green(self.bg_color) + 25,
                blue(self.bg_color) + 25,
            )
        else:
            fill(self.bg_color)
        noStroke()
        rect(self.x, self.y, self.w, self.h, 8)

        fill(255)
        textAlign(CENTER, CENTER)
        textSize(14)
        text(self.label, self.x + self.w / 2, self.y + self.h / 2)

    def is_hover(self):
        return (
            self.x <= mouseX <= self.x + self.w
            and self.y <= mouseY <= self.y + self.h
        )


# สร้างอินสแตนซ์ของ UI (ใช้ Hex Colors เพื่อป้องกันข้อผิดพลาดก่อน setup)
slider_v = Slider(
    80, 50, 180, 12, 10.0, 65.0, initial_velocity, "Initial Velocity (v0)", "m/s"
)
slider_angle = Slider(
    300, 50, 180, 12, 0.0, 90.0, launch_angle, "Launch Angle (theta)", "deg"
)
btn_start = Button(520, 38, 95, 34, "LAUNCH", 0xFF22B473)
btn_reset = Button(630, 38, 90, 34, "RESET", 0xFFE14B4B)


# --- ฟังก์ชันคำนวณทางฟิสิกส์ ---
def calculate_position(v0, angle, time_val):
    rad = radians(angle)
    vx = v0 * cos(rad)
    vy = v0 * sin(rad)
    x = vx * time_val
    y = (vy * time_val) - (0.5 * g * (time_val**2))
    return x, y


def calculate_theoretical_stats():
    global max_height, max_range, total_time
    rad = radians(launch_angle)
    v_y = initial_velocity * sin(rad)

    total_time = (2.0 * v_y) / g
    max_height = (v_y**2) / (2.0 * g)
    max_range = (initial_velocity**2 * sin(2.0 * rad)) / g


def reset_simulation():
    global t, current_x, current_y, is_animating, is_finished, x_points, y_points
    t = 0.0
    current_x = 0.0
    current_y = 0.0
    is_animating = False
    is_finished = False
    x_points = [0.0]
    y_points = [0.0]


def update_animation():
    global t, current_x, current_y, is_animating, is_finished

    if launch_angle <= 0:
        current_x = 0.0
        current_y = 0.0
        is_animating = False
        is_finished = True
        return

    t += dt
    pos_x, pos_y = calculate_position(initial_velocity, launch_angle, t)

    if pos_y <= 0:
        current_y = 0.0
        current_x = initial_velocity * cos(radians(launch_angle)) * total_time
        is_animating = False
        is_finished = True
    else:
        current_x = pos_x
        current_y = pos_y

    x_points.append(current_x)
    y_points.append(current_y)


# --- ส่วนประมวลผลหลักของ Processing ---
def setup():
    size(1050, 620)
    frameRate(60)
    calculate_theoretical_stats()


def draw():
    background(24, 26, 36)

    draw_environment()

    if is_animating:
        update_animation()

    draw_trajectory()
    draw_cannon()
    draw_projectile()
    draw_ui()


# --- ฟังก์ชันการแสดงผลกราฟิก ---
def draw_environment():
    stroke(80, 200, 120)
    strokeWeight(3)
    line(origin_x - 30, origin_y, width - 40, origin_y)

    fill(140, 150, 175)
    textSize(11)
    textAlign(CENTER, TOP)
    for m in range(0, 550, 50):
        px = origin_x + m * scale_m
        if px < width - 40:
            stroke(90, 100, 130)
            strokeWeight(1)
            line(px, origin_y, px, origin_y + 8)
            text(str(m) + "m", px, origin_y + 12)


def draw_trajectory():
    if len(x_points) > 1:
        noFill()
        stroke(0, 230, 255, 180)
        strokeWeight(2.5)
        beginShape()
        for i in range(len(x_points)):
            px = origin_x + (x_points[i] * scale_m)
            py = origin_y - (y_points[i] * scale_m)
            vertex(px, py)
        endShape()


def draw_cannon():
    pushMatrix()
    translate(origin_x, origin_y)
    rotate(-radians(launch_angle))
    fill(90, 95, 120)
    stroke(140, 150, 180)
    strokeWeight(1.5)
    rect(-10, -8, 45, 16, 4)
    popMatrix()

    fill(60, 65, 85)
    noStroke()
    arc(origin_x, origin_y, 35, 35, PI, TWO_PI)


def draw_projectile():
    px = origin_x + (current_x * scale_m)
    py = origin_y - (current_y * scale_m)

    noStroke()
    fill(0, 0, 0, 70)
    ellipse(px, origin_y + 4, 16, 6)

    fill(255, 200, 40)
    stroke(255, 240, 150)
    strokeWeight(2)
    ellipse(px, py, 18, 18)

    if is_animating:
        rad = radians(launch_angle)
        vx = initial_velocity * cos(rad)
        vy = initial_velocity * sin(rad) - (g * t)

        stroke(40, 240, 120)
        strokeWeight(2)
        line(px, py, px + vx * 0.8, py)

        stroke(255, 75, 130)
        line(px, py, px, py - vy * 0.8)


def draw_ui():
    slider_v.display()
    slider_angle.display()
    btn_start.display()
    btn_reset.display()

    panel_x = width - 260
    panel_y = 35
    fill(35, 38, 52, 230)
    stroke(60, 65, 90)
    strokeWeight(1.5)
    rect(panel_x, panel_y, 230, 200, 10)

    fill(0, 230, 255)
    textAlign(LEFT, TOP)
    textSize(14)
    text("PHYSICS TELEMETRY", panel_x + 18, panel_y + 15)

    fill(200, 205, 225)
    textSize(12)
    line_h = 24
    y_off = panel_y + 42

    text("Flight Time (T): " + nf(total_time, 0, 2) + " s", panel_x + 18, y_off)
    text(
        "Max Height (H):  " + nf(max_height, 0, 2) + " m",
        panel_x + 18,
        y_off + line_h,
    )
    text(
        "Max Range (R):   " + nf(max_range, 0, 2) + " m",
        panel_x + 18,
        y_off + line_h * 2,
    )

    stroke(60, 65, 90)
    line(panel_x + 15, y_off + line_h * 3, panel_x + 215, y_off + line_h * 3)

    fill(255, 215, 0)
    text(
        "Realtime (t): " + nf(t, 0, 2) + " s",
        panel_x + 18,
        y_off + line_h * 3.5,
    )
    text(
        "Pos: ("
        + nf(current_x, 0, 1)
        + " m, "
        + nf(current_y, 0, 1)
        + " m)",
        panel_x + 18,
        y_off + line_h * 4.5,
    )

    if is_finished:
        fill(40, 240, 120)
        textAlign(CENTER)
        textSize(15)
        text("TARGET REACHED", panel_x + 115, y_off + line_h * 5.7)


# --- การจัดการ Event เมาส์ ---
def mousePressed():
    global is_animating

    if btn_start.is_hover() and not is_animating:
        reset_simulation()
        calculate_theoretical_stats()
        is_animating = True

    elif btn_reset.is_hover():
        reset_simulation()

    # ตรวจสอบการคลิกแยกสไลเดอร์แบบอิสระ
    if slider_v.is_hover():
        slider_v.is_dragging = True
        mouseDragged()
    elif slider_angle.is_hover():
        slider_angle.is_dragging = True
        mouseDragged()


def mouseDragged():
    global initial_velocity, launch_angle
    if slider_v.is_dragging and not is_animating:
        initial_velocity = slider_v.update()
        calculate_theoretical_stats()
    if slider_angle.is_dragging and not is_animating:
        launch_angle = slider_angle.update()
        calculate_theoretical_stats()


def mouseReleased():
    slider_v.is_dragging = False
    slider_angle.is_dragging = False
