"""Diagrams for Modules 1-3."""
from __future__ import annotations

import math

from svglib import ARROW, MUTED, PAL, TEXT, Diagram, text_width

REGISTRY = {}

HL_FILL = "#9DC2EC"   # highlighted region (joins, windows)
HL_STROKE = "#1F5FA8"
ACCENT = "#B5520C"


def diagram(fn):
    REGISTRY[fn.__name__] = fn
    return fn


def grid(d: Diagram, x, y, widths, header, rows, row_h=19, size=9.4, hl_rows=(), hl_cols=(), hl_fill="#DCEBFB",
         head_fill="#E9EEF5"):
    """Small data grid drawn inside a diagram."""
    total_w = sum(widths)
    d.rect(x, y, total_w, row_h, head_fill, "#C8D1DD", 0.8, 0)
    cx = x
    for wcol, h in zip(widths, header):
        d.text(cx + wcol / 2, y + row_h * 0.68, h, size, 600, "#13294B", mono=True)
        cx += wcol
    for r, row in enumerate(rows):
        ry = y + row_h * (r + 1)
        fill = hl_fill if r in hl_rows else "#FFFFFF"
        d.rect(x, ry, total_w, row_h, fill, "#D9DFE7", 0.8, 0)
        cx = x
        for c, (wcol, v) in enumerate(zip(widths, row)):
            if c in hl_cols:
                d.rect(cx, ry, wcol, row_h, "#FFF1D6", "#D9DFE7", 0.8, 0)
            d.text(cx + wcol / 2, ry + row_h * 0.68, str(v), size, 400, TEXT, mono=True)
            cx += wcol
    return y + row_h * (len(rows) + 1)


# =============================================================== MODULE 1
@diagram
def app_architecture():
    d = Diagram(720, 500)
    X, W, H = 120, 230, 52
    cx = X + W / 2
    d.box(X, 14, W, H, "User", "user", "customer on a phone or laptop")
    d.box(X, 104, W, H, "Frontend", "client", "web page / mobile app (the UI)")
    d.box(X, 194, W, H, "Backend / API", "service", "business rules + REST endpoints")
    d.db(X, 280, W, 66, "Database", "db", "PostgreSQL / MySQL / MongoDB")
    d.box(X, 420, W, H, "Analytics", "analytics", "data warehouse + dashboards")
    # request / response pairs
    pairs = [(66, 104, "taps 'Place order'", "sees confirmation"),
             (156, 194, "HTTP request (JSON)", "JSON response"),
             (246, 280, "SQL query", "rows / result")]
    for y1, y2, down, up in pairs:
        d.arrow(cx - 14, y1 + 2, cx - 14, y2 - 2)
        d.arrow(cx + 14, y2 - 2, cx + 14, y1 + 2, dash="4 3", color="#667085")
        d.text(cx - 24, (y1 + y2) / 2 + 4, down, 10, 500, "#344054", "end")
        d.text(cx + 24, (y1 + y2) / 2 + 4, up, 10, 400, MUTED, "start", italic=True)
    d.arrow(cx, 348, cx, 418)
    d.text(cx + 12, 380, "data copied by a pipeline", 10, 500, "#344054", "start")
    d.text(cx + 12, 394, "(nightly ETL or streaming)", 10, 400, MUTED, "start")
    # other services
    d.box(480, 180, 225, 80, "Other services", "external",
          "payment gateway · SMS / email\nmaps · inventory · auth")
    d.arrow(X + W + 2, 213, 478, 213, both=True)
    d.text(415, 205, "API calls", 10, 500, "#344054")
    d.text(415, 232, "(HTTPS + JSON)", 9.5, 400, MUTED)
    ex = ["Example: food-delivery order", "1. user taps 'Order'", "2. app sends the order as JSON",
          "3. API validates it and saves it (SQL)", "4. API calls the payment gateway",
          "5. order is copied to the warehouse", "    for 'orders per city' dashboards"]
    for i, ln in enumerate(ex):
        d.text(482, 300 + i * 16, ln, 10.5 if i == 0 else 9.6, 600 if i == 0 else 400,
               "#13294B" if i == 0 else MUTED, "start")
    return d


@diagram
def data_system_components():
    d = Diagram(720, 215)
    steps = [("Sources", "apps, devices,\nfiles, SaaS tools", "user"),
             ("Ingestion", "APIs, ETL,\nqueues, CDC", "queue"),
             ("Storage", "databases, lake,\nwarehouse", "db"),
             ("Processing", "batch and\nstreaming jobs", "service"),
             ("Serving", "APIs, BI models,\nfeature stores", "analytics"),
             ("Consumers", "users, analysts,\nML models", "user")]
    x, w, gap = 8, 102, 18
    for i, (t, s, k) in enumerate(steps):
        bx = x + i * (w + gap)
        d.box(bx, 20, w, 86, t, k, s, size=12.5, sub_size=9.6)
        if i < len(steps) - 1:
            d.arrow(bx + w + 2, 63, bx + w + gap - 2, 63, head=6.5)
    d.rect(8, 132, 704, 34, "#F2F4F7", "#98A2B3", 1, 6)
    d.text(360, 154, "Cross-cutting: governance · security & access control · data quality · metadata · monitoring",
           10.5, 500, "#344054")
    for i in range(6):
        bx = x + i * (w + gap) + w / 2
        d.line(bx, 108, bx, 130, "#B8C0CC", 1, "3 3")
    d.text(360, 196, "Data flows left to right; every stage must also be secured, monitored and documented.",
           10, 400, MUTED, italic=True)
    return d


@diagram
def polyglot_food_delivery():
    d = Diagram(720, 350)
    cxb, cyb = 265, 148
    d.box(cxb, cyb, 190, 64, "Food-delivery app", "navy", "backend services")
    stores = [
        (20, 18, "PostgreSQL", "orders, payments\n(needs ACID)", "db"),
        (265, 18, "Redis", "cache, sessions,\nlive rider location", "queue"),
        (510, 18, "MongoDB", "restaurant menus\n(flexible documents)", "db"),
        (20, 148, "Elasticsearch", "search 'biryani\nnear me'", "service"),
        (510, 148, "Object storage (S3)", "food photos,\ninvoices (files)", "external"),
        (140, 270, "Kafka", "events: OrderPlaced,\nRiderAssigned", "queue"),
        (390, 270, "Data warehouse", "daily sales,\ncity-wise reports", "analytics"),
    ]
    W, H = 190, 64
    for x, y, t, s, k in stores:
        d.box(x, y, W, H, t, k, s, size=12, sub_size=9.6)
    c = (cxb + 95, cyb + 32)
    targets = [(115, 82), (360, 82), (605, 82), (210, 180), (510, 180), (235, 270), (485, 270)]
    for tx, ty in targets:
        sx = c[0] + (tx - c[0]) * 0.32
        sy = c[1] + (ty - c[1]) * 0.42
        if (tx, ty) == (210, 180):
            sx, sy = cxb, 180
        if (tx, ty) == (510, 180):
            sx, sy = cxb + 190, 180
        if ty == 82:
            sy = cyb
            sx = {115: cxb + 30, 360: cxb + 95, 605: cxb + 160}[tx]
        if ty == 270:
            sy = cyb + 64
            sx = {235: cxb + 50, 485: cxb + 140}[tx]
        d.arrow(sx, sy, tx, ty, head=6.5, color="#667085")
    return d


@diagram
def batch_vs_stream():
    d = Diagram(720, 260)
    # batch row
    d.box(8, 34, 78, 40, "BATCH", "navy", size=11.5)
    for i in range(3):
        for j in range(3):
            d.rect(98 + j * 13, 36 + i * 13, 10, 10, "#C8D1DD", "#98A2B3", 0.8, 2)
    d.arrow(142, 54, 168, 54, head=6)
    d.box(170, 24, 160, 60, "Collect all day", "neutral", "files / staging tables")
    d.arrow(332, 54, 362, 54, head=6)
    d.box(364, 24, 160, 60, "Scheduled job", "service", "e.g. every night 2:00 AM")
    d.arrow(526, 54, 556, 54, head=6)
    d.box(558, 24, 154, 60, "Report ready", "analytics", "next morning")
    d.text(360, 106, "Large volumes processed together · simple and cheap · results are hours old",
           10, 400, MUTED, italic=True)
    # streaming row
    d.box(8, 154, 78, 40, "STREAM", "navy", size=11.5)
    for j in range(5):
        d.circle(100 + j * 13, 174, 4.2, "#F2B37A", ACCENT, 0.8)
    d.arrow(162, 174, 168, 174, head=6)
    d.box(170, 144, 160, 60, "Event stream", "queue", "Kafka / Kinesis / Event Hubs")
    d.arrow(332, 174, 362, 174, head=6)
    d.box(364, 144, 160, 60, "Stream processor", "service", "handles each event as it arrives")
    d.arrow(526, 174, 556, 174, head=6)
    d.box(558, 144, 154, 60, "Alert / live view", "good", "within seconds")
    d.text(360, 228, "Continuous small events · low latency · harder to build, test and operate",
           10, 400, MUTED, italic=True)
    return d


@diagram
def oltp_to_olap():
    d = Diagram(720, 262)
    srcs = [("Orders DB", 10), ("Payments DB", 76), ("CRM (Salesforce)", 142)]
    for t, y in srcs:
        d.db(14, y, 150, 56, t, "db", size=11.5)
    d.text(89, 226, "OLTP — many small, fast reads/writes", 9.6, 600, "#0B4F4A")
    d.box(222, 96, 128, 62, "ETL / ELT", "queue", "copy, clean, reshape")
    for _, y in srcs:
        d.arrow(166, y + 31, 220, 127, head=6.5, color="#667085")
    d.db(400, 76, 150, 102, "Data warehouse", "analytics", "history, star schemas")
    d.arrow(352, 127, 398, 127)
    d.text(475, 206, "OLAP — few large analytical queries", 9.6, 600, "#3E1F8C")
    d.box(594, 96, 118, 62, "Dashboards", "user", "reports, ad-hoc SQL")
    d.arrow(552, 127, 592, 127)
    d.text(475, 226, "\"Revenue by city by month for 3 years\"", 9.6, 400, MUTED, italic=True)
    d.text(89, 244, "\"Insert order #9001\" · \"Update stock\"", 9.4, 400, MUTED, italic=True)
    return d


@diagram
def monolith_vs_microservices():
    d = Diagram(720, 270)
    d.frame(8, 18, 300, 240, "Monolith", "#667085")
    d.box(30, 44, 256, 120, "", "service")
    d.text(158, 64, "One application (one deployment)", 11, 600, "#13294B")
    for i, t in enumerate(["Users", "Orders", "Payments"]):
        d.box(44 + i * 82, 82, 72, 62, t, "plain", "module", size=11, sub_size=9)
    d.db(98, 186, 120, 58, "One database", "db", size=11)
    d.arrow(158, 166, 158, 184)
    d.frame(328, 18, 384, 240, "Microservices", "#1F5FA8")
    d.box(430, 40, 180, 38, "API gateway", "navy", size=11.5)
    svcs = [(346, "User service", "PostgreSQL"), (470, "Order service", "MongoDB"), (594, "Payment service", "PostgreSQL")]
    for x, t, store in svcs:
        d.box(x, 110, 104, 50, t, "service", size=10.5)
        d.db(x + 7, 186, 90, 56, store, "db", size=10)
        d.arrow(x + 52, 162, x + 52, 184, head=6)
        d.arrow(520, 80, x + 52, 108, head=6, color="#667085")
    return d


# =============================================================== MODULE 2
@diagram
def relationships():
    d = Diagram(720, 360)
    rows = [
        (18, "One-to-one", "1 : 1", "each user has exactly\none profile"),
        (138, "One-to-many", "1 : N", "one customer places\nmany orders"),
        (258, "Many-to-many", "M : N", "students take many courses;\ncourses have many students"),
    ]
    for y, t, card, s in rows:
        d.text(14, y + 22, t, 12.5, 700, "#13294B", "start")
        d.text(14, y + 40, card, 11, 600, ACCENT, "start")
        d.mtext(14, y + 64, s, 9.4, 400, MUTED, "start")
    # 1:1
    a = d.table(220, 18, 150, "users", [("user_id", "PK"), ("name", "")])
    b = d.table(480, 18, 180, "user_profiles", [("user_id", "PK FK"), ("bio", ""), ("photo_url", "")])
    d.line(370, a["user_id"], 480, b["user_id"], ARROW, 1.4)
    d.text(380, a["user_id"] - 5, "1", 11, 700, ACCENT)
    d.text(470, b["user_id"] - 5, "1", 11, 700, ACCENT)
    # 1:N
    a = d.table(220, 138, 150, "customers", [("customer_id", "PK"), ("name", "")])
    b = d.table(480, 138, 180, "orders", [("order_id", "PK"), ("customer_id", "FK"), ("amount", "")])
    d.parrow([(370, a["customer_id"]), (425, a["customer_id"]), (425, b["customer_id"]), (480, b["customer_id"])],
             head=6.5)
    d.text(380, a["customer_id"] - 5, "1", 11, 700, ACCENT)
    d.text(466, b["customer_id"] - 5, "N", 11, 700, ACCENT)
    # M:N
    s = d.table(220, 258, 130, "students", [("student_id", "PK"), ("name", "")])
    e = d.table(395, 258, 170, "enrollments", [("student_id", "PK FK"), ("course_id", "PK FK"), ("enrolled_on", "")],
                kind="queue")
    c = d.table(600, 258, 112, "courses", [("course_id", "PK"), ("title", "")])
    d.line(350, s["student_id"], 395, e["student_id"], ARROW, 1.4)
    d.text(358, s["student_id"] - 5, "1", 11, 700, ACCENT)
    d.text(386, e["student_id"] - 5, "N", 11, 700, ACCENT)
    d.parrow([(600, c["course_id"]), (583, c["course_id"]), (583, e["course_id"]), (565, e["course_id"])], head=6)
    d.text(593, c["course_id"] - 5, "1", 11, 700, ACCENT)
    d.text(574, e["course_id"] + 13, "N", 11, 700, ACCENT)
    d.text(480, 352, "junction (bridge) table", 9.4, 500, "#7A3608", italic=True)
    return d


@diagram
def er_ecommerce():
    d = Diagram(720, 205)
    cu = d.table(8, 22, 152, "customers", [("customer_id", "PK"), ("customer_name", ""), ("email", ""), ("city", "")])
    od = d.table(196, 22, 152, "orders", [("order_id", "PK"), ("customer_id", "FK"), ("order_date", ""),
                                          ("status", ""), ("total_amount", "")])
    oi = d.table(384, 22, 152, "order_items", [("order_id", "PK FK"), ("product_id", "PK FK"), ("quantity", ""),
                                               ("unit_price", "")], kind="queue")
    pr = d.table(566, 22, 146, "products", [("product_id", "PK"), ("product_name", ""), ("category", ""), ("price", "")])
    d.parrow([(160, cu["customer_id"]), (178, cu["customer_id"]), (178, od["customer_id"]), (196, od["customer_id"])], head=6)
    d.text(168, cu["customer_id"] - 4, "1", 10.5, 700, ACCENT)
    d.text(188, od["customer_id"] + 14, "N", 10.5, 700, ACCENT)
    d.parrow([(348, od["order_id"]), (366, od["order_id"]), (366, oi["order_id"]), (384, oi["order_id"])], head=6)
    d.text(356, od["order_id"] - 4, "1", 10.5, 700, ACCENT)
    d.text(376, oi["order_id"] + 14, "N", 10.5, 700, ACCENT)
    d.parrow([(566, pr["product_id"]), (551, pr["product_id"]), (551, oi["product_id"]), (536, oi["product_id"])], head=6)
    d.text(558, pr["product_id"] - 4, "1", 10.5, 700, ACCENT)
    d.text(544, oi["product_id"] + 14, "N", 10.5, 700, ACCENT)
    d.text(360, 190, "customers 1—N orders 1—N order_items N—1 products   (orders ↔ products is many-to-many)",
           9.8, 500, MUTED)
    return d


@diagram
def sample_db_map():
    d = Diagram(720, 450)
    d.frame(6, 14, 336, 220, "HR", "#1F5FA8")
    dp = d.table(20, 36, 128, "departments", [("dept_id", "PK"), ("dept_name", ""), ("location", "")])
    em = d.table(176, 36, 150, "employees", [("emp_id", "PK"), ("emp_name", ""), ("email", ""), ("dept_id", "FK"),
                                             ("manager_id", "FK"), ("salary", ""), ("hire_date", ""), ("city", "")])
    d.parrow([(148, dp["dept_id"]), (162, dp["dept_id"]), (162, em["dept_id"]), (176, em["dept_id"])], head=6)
    d.parrow([(326, em["manager_id"]), (336, em["manager_id"]), (336, em["emp_id"]), (326, em["emp_id"])],
             head=6, color=ACCENT)
    d.text(251, 226, "manager_id → emp_id (self reference)", 9, 500, ACCENT)
    d.frame(356, 14, 358, 420, "E-commerce", "#0F766E")
    cu = d.table(368, 36, 158, "customers", [("customer_id", "PK"), ("customer_name", ""), ("email", ""), ("city", ""),
                                             ("signup_date", "")], kind="db")
    od = d.table(546, 36, 158, "orders", [("order_id", "PK"), ("customer_id", "FK"), ("order_date", ""), ("status", ""),
                                          ("total_amount", "")], kind="db")
    pr = d.table(368, 250, 158, "products", [("product_id", "PK"), ("product_name", ""), ("category", ""), ("price", "")],
                 kind="db")
    oi = d.table(546, 250, 158, "order_items", [("order_id", "PK FK"), ("product_id", "PK FK"), ("quantity", ""),
                                                ("unit_price", "")], kind="queue")
    d.parrow([(526, cu["customer_id"]), (536, cu["customer_id"]), (536, od["customer_id"]), (546, od["customer_id"])], head=6)
    d.parrow([(625, 36 + od["_h"]), (625, 250)], head=6)
    d.parrow([(526, pr["product_id"]), (536, pr["product_id"]), (536, oi["product_id"]), (546, oi["product_id"])], head=6)
    d.text(447, 196, "orders ↔ products is", 9, 500, MUTED)
    d.text(447, 209, "many-to-many via order_items", 9, 500, MUTED)
    d.frame(6, 250, 336, 184, "Other tables", "#6941C6")
    d.table(18, 270, 150, "accounts", [("account_id", "PK"), ("holder_name", ""), ("balance", "")], kind="analytics",
            row_h=16, head_h=20, size=9.2)
    d.table(180, 270, 150, "daily_sales", [("sale_date", "PK"), ("region", "PK"), ("amount", "")], kind="analytics",
            row_h=16, head_h=20, size=9.2)
    d.table(18, 346, 150, "leads", [("lead_id", "PK"), ("full_name", ""), ("email", ""), ("created_at", "")],
            kind="analytics", row_h=16, head_h=20, size=9.2)
    d.table(180, 346, 150, "user_logins", [("login_id", "PK"), ("user_id", "FK"), ("login_time", ""), ("device", "")],
            kind="analytics", row_h=16, head_h=20, size=9.2)
    return d


@diagram
def normalization_stairs():
    d = Diagram(720, 260)
    steps = [
        ("1NF", "one value per cell\nno repeating groups\nrows identified by a key", 150, "service"),
        ("2NF", "1NF +\nno partial dependency\n(every non-key column needs\nthe WHOLE composite key)", 112, "service"),
        ("3NF", "2NF +\nno transitive dependency\n(non-key columns depend only\non the key, not on each other)", 74, "service"),
        ("BCNF", "3NF made stricter:\nevery determinant\nis a candidate key", 36, "navy"),
    ]
    for i, (t, s, y, k) in enumerate(steps):
        x = 14 + i * 176
        h = 240 - y
        fill, stroke, tcol = PAL[k]
        d.rect(x, y, 168, h, fill, stroke, 1.3, 7)
        d.text(x + 84, y + 26, t, 17, 700, tcol)
        lines = s.split("\n")
        for j, ln in enumerate(lines):
            d.text(x + 84, y + 50 + j * 14, ln, 9.6, 400, "#C9D5E8" if k == "navy" else "#344054")
    d.arrow(30, 22, 690, 22, "each step removes one kind of redundancy → fewer update, insert and delete anomalies",
            color=ACCENT, lsize=10, loff=(0, -10), lbg=None)
    d.text(360, 256, "In practice most OLTP designs aim for 3NF.", 9.8, 400, MUTED, italic=True)
    return d


@diagram
def star_schema():
    d = Diagram(720, 395)
    f = d.table(276, 128, 168, "fact_sales", [("sale_id", "PK"), ("date_key", "FK"), ("product_key", "FK"),
                                              ("customer_key", "FK"), ("store_key", "FK"), ("quantity", ""),
                                              ("amount", "")], kind="queue")
    dd = d.table(20, 18, 170, "dim_date", [("date_key", "PK"), ("full_date", ""), ("month", ""), ("quarter", ""),
                                           ("year", "")])
    dp = d.table(530, 18, 170, "dim_product", [("product_key", "PK"), ("product_name", ""), ("category", ""),
                                               ("brand", "")])
    dc = d.table(20, 268, 170, "dim_customer", [("customer_key", "PK"), ("customer_name", ""), ("city", ""),
                                                ("segment", "")])
    ds = d.table(530, 268, 170, "dim_store", [("store_key", "PK"), ("store_name", ""), ("city", ""), ("region", "")])
    d.parrow([(276, f["date_key"]), (233, f["date_key"]), (233, dd["date_key"]), (190, dd["date_key"])], head=6)
    d.parrow([(276, f["customer_key"]), (233, f["customer_key"]), (233, dc["customer_key"]), (190, dc["customer_key"])], head=6)
    d.parrow([(444, f["product_key"]), (487, f["product_key"]), (487, dp["product_key"]), (530, dp["product_key"])], head=6)
    d.parrow([(444, f["store_key"]), (487, f["store_key"]), (487, ds["store_key"]), (530, ds["store_key"])], head=6)
    d.text(360, 312, "FACT = numbers you measure", 10, 600, "#7A3608")
    d.text(360, 327, "(one row per sale line)", 9.4, 400, MUTED)
    d.text(360, 360, "DIMENSIONS = descriptive context: who, what, when, where", 10, 600, "#13294B")
    d.text(360, 376, "Each dimension joins to the fact table in ONE hop → simple, fast queries", 9.4, 400, MUTED)
    return d


@diagram
def snowflake_schema():
    d = Diagram(720, 405)
    f = d.table(276, 120, 168, "fact_sales", [("sale_id", "PK"), ("date_key", "FK"), ("product_key", "FK"),
                                              ("store_key", "FK"), ("quantity", ""), ("amount", "")], kind="queue")
    dd = d.table(18, 18, 172, "dim_date", [("date_key", "PK"), ("full_date", ""), ("month", ""), ("year", "")])
    dsx = d.table(18, 168, 172, "dim_store", [("store_key", "PK"), ("store_name", ""), ("city_key", "FK")])
    dci = d.table(18, 298, 172, "dim_city", [("city_key", "PK"), ("city_name", ""), ("region", "")])
    dp = d.table(530, 18, 172, "dim_product", [("product_key", "PK"), ("product_name", ""), ("category_key", "FK")])
    dca = d.table(530, 148, 172, "dim_category", [("category_key", "PK"), ("category_name", ""), ("dept_key", "FK")])
    dde = d.table(530, 278, 172, "dim_department", [("dept_key", "PK"), ("dept_name", "")])
    d.parrow([(276, f["date_key"]), (233, f["date_key"]), (233, dd["date_key"]), (190, dd["date_key"])], head=6)
    d.parrow([(276, f["store_key"]), (233, f["store_key"]), (233, dsx["store_key"]), (190, dsx["store_key"])], head=6)
    d.parrow([(444, f["product_key"]), (487, f["product_key"]), (487, dp["product_key"]), (530, dp["product_key"])], head=6)
    d.parrow([(18, dsx["city_key"]), (8, dsx["city_key"]), (8, dci["city_key"]), (18, dci["city_key"])], head=6, color=ACCENT)
    d.parrow([(702, dp["category_key"]), (712, dp["category_key"]), (712, dca["category_key"]), (702, dca["category_key"])],
             head=6, color=ACCENT)
    d.parrow([(702, dca["dept_key"]), (712, dca["dept_key"]), (712, dde["dept_key"]), (702, dde["dept_key"])],
             head=6, color=ACCENT)
    d.text(360, 300, "Dimensions are normalized into", 10, 600, "#7A3608")
    d.text(360, 315, "sub-dimensions (orange links)", 10, 600, "#7A3608")
    d.text(360, 340, "less duplication, but more joins", 9.4, 400, MUTED)
    d.text(360, 355, "(product → category → department)", 9.4, 400, MUTED)
    return d


@diagram
def dw_architecture():
    d = Diagram(720, 250)
    srcs = [("ERP (SAP)", "db"), ("CRM", "db"), ("App database", "db"), ("CSV / Excel files", "external")]
    for i, (t, k) in enumerate(srcs):
        d.box(8, 16 + i * 56, 128, 40, t, k, size=11)
        d.arrow(138, 36 + i * 56, 176, 122, head=6, color="#667085")
    d.box(178, 92, 96, 60, "ETL", "queue", "extract,\ntransform, load", sub_size=9)
    d.arrow(276, 122, 304, 122)
    d.db(306, 62, 146, 118, "Enterprise data\nwarehouse", "analytics", "integrated, historical,\nsubject-oriented", size=11.5,
         sub_size=9.2)
    d.box(494, 42, 104, 50, "Sales mart", "plain", "for sales team", size=11, sub_size=9)
    d.box(494, 150, 104, 50, "Finance mart", "plain", "for finance team", size=11, sub_size=9)
    d.arrow(454, 108, 492, 70, head=6)
    d.arrow(454, 136, 492, 172, head=6)
    d.box(626, 92, 88, 60, "BI tools", "user", "Power BI,\nTableau", size=11, sub_size=9)
    d.arrow(600, 70, 624, 112, head=6)
    d.arrow(600, 172, 624, 134, head=6)
    d.text(380, 236, "Schema-on-write: data is cleaned and modelled BEFORE it is loaded.", 9.8, 400, MUTED, italic=True)
    return d


# =============================================================== MODULE 3
def _venn_paths(cx, cy, r, off):
    h = math.sqrt(r * r - off * off)
    p1 = (cx, cy - h)
    p2 = (cx, cy + h)
    f = lambda p: f"{p[0]:.1f},{p[1]:.1f}"
    lens = f"M{f(p1)} A{r},{r} 0 0 1 {f(p2)} A{r},{r} 0 0 1 {f(p1)} Z"
    left = f"M{f(p1)} A{r},{r} 0 1 0 {f(p2)} A{r},{r} 0 0 1 {f(p1)} Z"
    right = f"M{f(p1)} A{r},{r} 0 1 1 {f(p2)} A{r},{r} 0 0 0 {f(p1)} Z"
    return lens, left, right


@diagram
def joins_venn():
    d = Diagram(720, 410)
    panels = [
        ("INNER JOIN", "only rows that match in both", {"lens"}),
        ("LEFT JOIN", "all of A + matching rows of B", {"lens", "left"}),
        ("RIGHT JOIN", "all of B + matching rows of A", {"lens", "right"}),
        ("FULL OUTER JOIN", "everything from A and B", {"lens", "left", "right"}),
        ("LEFT JOIN … WHERE B.key IS NULL", "rows of A with NO match (anti-join)", {"left"}),
        ("CROSS JOIN", "every A row × every B row (3 × 2 = 6)", None),
    ]
    r, off = 47, 27
    for i, (title, sub, regions) in enumerate(panels):
        px, py = (i % 3) * 240, (i // 3) * 205
        cx, cy = px + 120, py + 74
        if regions is not None:
            lens, left, right = _venn_paths(cx, cy, r, off)
            d.circle(cx - off, cy, r, "#FFFFFF", "none", 0)
            d.circle(cx + off, cy, r, "#FFFFFF", "none", 0)
            for name, p in (("lens", lens), ("left", left), ("right", right)):
                if name in regions:
                    d.path(p, fill=HL_FILL, stroke="none", lw=0)
            d.circle(cx - off, cy, r, "none", "#344054", 1.4)
            d.circle(cx + off, cy, r, "none", "#344054", 1.4)
            d.text(cx - off - 20, cy + 5, "A", 14, 700, "#13294B")
            d.text(cx + off + 20, cy + 5, "B", 14, 700, "#13294B")
        else:
            lefts = [cy - 42, cy - 7, cy + 28]
            rights = [cy - 26, cy + 12]
            for j, ly in enumerate(lefts):
                d.box(cx - 86, ly - 1, 40, 22, f"a{j + 1}", "highlight", size=10)
            for j, ry in enumerate(rights):
                d.box(cx + 46, ry - 1, 40, 22, f"b{j + 1}", "highlight", size=10)
            for ly in lefts:
                for ry in rights:
                    d.line(cx - 46, ly + 10, cx + 46, ry + 10, "#7A8699", 1)

        d.text(cx, py + 150, title, 12, 700, "#13294B")
        d.text(cx, py + 167, sub, 9.8, 400, MUTED)
    d.line(8, 198, 712, 198, "#E4E7EC", 1)
    return d


@diagram
def sql_order():
    d = Diagram(720, 362)
    d.text(125, 24, "How you WRITE it", 12.5, 700, "#13294B")
    d.text(415, 24, "How the database RUNS it", 12.5, 700, "#13294B")
    written = ["SELECT", "FROM / JOIN", "WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT / OFFSET"]
    run = [("FROM / JOIN", "collect rows from the tables"), ("WHERE", "drop rows that fail the condition"),
           ("GROUP BY", "make one group per key value"), ("HAVING", "drop groups that fail the condition"),
           ("SELECT", "compute columns, aliases, DISTINCT"), ("ORDER BY", "sort the result (can use aliases)"),
           ("LIMIT / OFFSET", "keep only the rows asked for")]
    y0, step, bh = 44, 44, 32
    for i, w in enumerate(written):
        d.box(40, y0 + i * step, 170, bh, w, "plain", size=11.5, weight=600)
    for i, (w, note) in enumerate(run):
        k = "highlight" if w == "SELECT" else "service"
        d.box(330, y0 + i * step, 170, bh, f"{i + 1}. {w}", k, size=11.5)
        d.text(512, y0 + i * step + bh / 2 + 4, note, 9.6, 400, MUTED, "start")
    mapping = {0: 4, 1: 0, 2: 1, 3: 2, 4: 3, 5: 5, 6: 6}
    for a, b in mapping.items():
        col = ACCENT if a == 0 else "#98A2B3"
        lw = 1.8 if a == 0 else 1.1
        d.arrow(212, y0 + a * step + bh / 2, 328, y0 + b * step + bh / 2, color=col, lw=lw, head=6)
    d.text(360, 352, "SELECT runs after WHERE — that is why a column alias from SELECT cannot be used in WHERE.",
           9.8, 600, ACCENT)
    return d


@diagram
def groupby_vs_window():
    d = Diagram(720, 262)
    rows = [("Eng", "120000"), ("Eng", "95000"), ("Eng", "80000"), ("Fin", "110000"), ("Fin", "70000")]
    d.text(170, 20, "GROUP BY → rows are collapsed", 12, 700, "#13294B")
    grid(d, 15, 44, [44, 58], ["dept", "salary"], rows)
    d.arrow(124, 100, 178, 100, "AVG()", lsize=9.4, head=6.5)
    grid(d, 186, 72, [44, 74], ["dept", "avg_sal"], [("Eng", "98333.33"), ("Fin", "90000.00")], hl_cols=(1,))
    d.text(250, 150, "5 rows in → 2 rows out", 9.6, 600, ACCENT)
    d.line(358, 14, 358, 236, "#E4E7EC", 1.2)
    d.text(540, 20, "Window function → rows are kept", 12, 700, "#13294B")
    grid(d, 372, 44, [44, 58], ["dept", "salary"], rows)
    d.arrow(480, 100, 530, 100, "OVER()", lsize=9.4, head=6.5)
    out = [(a, b, "98333.33" if a == "Eng" else "90000.00") for a, b in rows]
    grid(d, 536, 44, [42, 58, 76], ["dept", "salary", "dept_avg"], out, hl_cols=(2,))
    d.text(612, 172, "5 rows in → 5 rows out", 9.6, 600, ACCENT)
    d.text(360, 210, "AVG(salary) OVER (PARTITION BY dept) adds the department average to EVERY row,",
           9.8, 400, "#344054")
    d.text(360, 226, "so you can compare each employee with their department in the same query.", 9.8, 400, "#344054")
    return d


@diagram
def window_frame():
    d = Diagram(720, 250)
    vals = [12000, 15000, 11000, 18000, 21000, 17000, 23000]
    x0, cw, ch = 168, 76, 40
    rowsy = [30, 100, 170]
    labels = [("Running total", "UNBOUNDED PRECEDING\n→ CURRENT ROW"),
              ("3-row moving avg", "2 PRECEDING\n→ CURRENT ROW"),
              ("LAG / LEAD", "previous / next row")]
    frames = [range(0, 5), range(2, 5), None]
    results = ["= 77000 (sum of days 1–5)", "= 16666.67 (avg of days 3–5)", ""]
    for r, y in enumerate(rowsy):
        t, s = labels[r]
        d.text(10, y + 15, t, 11.5, 700, "#13294B", "start")
        d.mtext(10, y + 36, s, 8.8, 400, MUTED, "start", mono=True)
        for i, v in enumerate(vals):
            x = x0 + i * cw
            infr = frames[r] is not None and i in frames[r]
            fill = HL_FILL if infr else "#FFFFFF"
            stroke = HL_STROKE if i == 4 else "#C8D1DD"
            lw = 2 if i == 4 else 0.9
            d.rect(x, y, cw - 6, ch, fill, stroke, lw, 4)
            d.text(x + (cw - 6) / 2, y + 14, f"Mar {i + 1}", 8.6, 500, MUTED)
            d.text(x + (cw - 6) / 2, y + 31, f"{v}", 11, 600, TEXT, mono=True)
        if results[r]:
            d.text(x0 + 4 * cw + 35, y + ch + 13, results[r], 9.4, 600, ACCENT)
    y = rowsy[2]
    d.parrow([(x0 + 4 * cw + 35, y + ch + 2), (x0 + 4 * cw + 35, y + ch + 14), (x0 + 3 * cw + 35, y + ch + 14),
              (x0 + 3 * cw + 35, y + ch + 2)], color=ACCENT, head=6)
    d.parrow([(x0 + 4 * cw + 35, y + ch + 2), (x0 + 4 * cw + 35, y + ch + 14), (x0 + 5 * cw + 35, y + ch + 14),
              (x0 + 5 * cw + 35, y + ch + 2)], color="#0F766E", head=6)
    d.text(x0 + 3 * cw + 35, y + ch + 27, "LAG = 18000", 9.4, 600, ACCENT)
    d.text(x0 + 5 * cw + 35, y + ch + 27, "LEAD = 17000", 9.4, 600, "#0F766E")
    d.text(x0 + 1 * cw + 20, y + ch + 27, "current row = Mar 5 (thick border)", 9.2, 400, MUTED)
    return d


@diagram
def btree_index():
    d = Diagram(720, 270)
    def node(x, y, keys, w_key=50, hl=None):
        for i, k in enumerate(keys):
            fill = "#FFE7C7" if hl is not None and i == hl else "#FFFFFF"
            d.rect(x + i * w_key, y, w_key, 30, fill, "#1F5FA8", 1.2, 0)
            d.text(x + i * w_key + w_key / 2, y + 19.5, k, 10, 600, "#13294B", mono=True)
        return x, x + w_key * len(keys)
    d.text(14, 20, "Index on employees(salary)", 11.5, 700, "#13294B", "start")
    d.text(14, 36, "find salary = 95000", 9.6, 400, ACCENT, "start")
    node(335, 14, ["80000"], hl=0)
    node(165, 82, ["60000"])
    node(505, 82, ["110000"], hl=0)
    leaves = [(14, ["52000", "55000"]), (160, ["60000", "65000", "70000"]), (365, ["80000", "90000", "95000"]),
              (570, ["110000", "120000", "150000"])]
    for i, (x, keys) in enumerate(leaves):
        node(x, 150, keys, w_key=46, hl=2 if i == 2 else None)
        if i < 3:
            nx = leaves[i + 1][0]
            d.arrow(x + 46 * len(keys) + 2, 165, nx - 2, 165, head=5, color="#98A2B3", lw=1)
    d.arrow(345, 44, 215, 80, color="#98A2B3", head=6)
    d.arrow(375, 44, 545, 80, color=ACCENT, lw=2, head=7)
    d.arrow(180, 112, 60, 148, color="#98A2B3", head=6)
    d.arrow(200, 112, 230, 148, color="#98A2B3", head=6)
    d.arrow(530, 112, 440, 148, color=ACCENT, lw=2, head=7)
    d.arrow(560, 112, 630, 148, color="#98A2B3", head=6)
    d.label(505, 52, "95000 ≥ 80000 → right", 9.2, ACCENT, 600)
    d.label(470, 126, "95000 < 110000 → left", 9.2, ACCENT, 600, anchor="end")
    d.rect(14, 214, 692, 40, "#F7F9FB", "#C8D1DD", 1, 6)
    d.text(26, 238, "table rows:", 10, 600, "#344054", "start")
    d.text(110, 238, "… (3, 'Rahul Verma', 95000) … (4, 'Sneha Iyer', 95000) …", 10, 400, "#344054", "start", mono=True)
    d.arrow(480, 182, 300, 212, color=ACCENT, lw=2, head=7)
    d.text(590, 206, "a few page reads instead of a full table scan", 9.2, 500, MUTED)
    return d


@diagram
def org_chart():
    d = Diagram(720, 290)
    slot = lambda k: 110 + 80 * k
    W, H = 76, 38
    nodes = {
        1: ("Arjun", (slot(1) + slot(7)) / 2, 0), 2: ("Priya", slot(1), 1), 6: ("Ananya", (slot(3) + slot(4)) / 2, 1),
        9: ("Rohan", slot(5), 1), 11: ("Aditya", slot(6), 1), 13: ("Farhan", slot(7), 1),
        3: ("Rahul", slot(0), 2), 4: ("Sneha", slot(1), 2), 5: ("Vikram", slot(2), 2),
        7: ("Karan", slot(3), 2), 8: ("Meera", slot(4), 2), 10: ("Divya", slot(5), 2), 12: ("Neha", slot(6), 2),
        14: ("Pooja", slot(0), 3),
    }
    parent = {2: 1, 6: 1, 9: 1, 11: 1, 13: 1, 3: 2, 4: 2, 5: 2, 7: 6, 8: 6, 10: 9, 12: 11, 14: 3}
    ly = lambda lvl: 14 + lvl * 70
    for c, p in parent.items():
        cx, cl = nodes[c][1], nodes[c][2]
        px, pl = nodes[p][1], nodes[p][2]
        midy = ly(cl) - 16
        d.path(f"M{px},{ly(pl) + H} L{px},{midy} L{cx},{midy} L{cx},{ly(cl)}", stroke="#98A2B3", lw=1.2)
    for eid, (name, x, lvl) in nodes.items():
        kind = "navy" if lvl == 0 else ("service" if lvl == 1 else ("plain" if lvl == 2 else "amber"))
        d.box(x - W / 2, ly(lvl), W, H, name, kind, f"emp_id {eid}", size=11, sub_size=8.6)
    for lvl in range(4):
        d.text(8, ly(lvl) + 24, f"level {lvl + 1}", 9.4, 600, ACCENT, "start")
    return d


@diagram
def transaction_transfer():
    d = Diagram(720, 250)
    d.box(8, 42, 86, 50, "BEGIN", "navy", size=12)
    d.box(118, 28, 186, 78, "1. Debit Aarav", "service", "UPDATE accounts\nSET balance = balance - 5000\nWHERE account_id = 1",
          size=11.5, sub_size=8.6, mono_sub=True)
    d.box(328, 28, 186, 78, "2. Credit Isha", "service", "UPDATE accounts\nSET balance = balance + 5000\nWHERE account_id = 2",
          size=11.5, sub_size=8.6, mono_sub=True)
    d.box(540, 34, 172, 66, "COMMIT", "good", "both changes saved\npermanently, together", size=12.5, sub_size=9.4)
    d.arrow(96, 67, 116, 67, head=6)
    d.arrow(306, 67, 326, 67, head=6)
    d.arrow(516, 67, 538, 67, head=6)
    d.box(210, 170, 400, 60, "ROLLBACK", "bad", "every change since BEGIN is undone — no money is lost or created",
          size=12.5, sub_size=9.6)
    d.arrow(211, 108, 300, 168, "error / crash / CHECK fails", color="#B42318", dash="5 4", lsize=9.2,
            loff=(-58, -2), lcolor="#B42318")
    d.arrow(421, 108, 410, 168, color="#B42318", dash="5 4")
    d.text(360, 150, "", 9, 400, MUTED)
    return d
