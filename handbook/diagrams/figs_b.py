"""Diagrams for Modules 4-7 and the final section."""
from __future__ import annotations

from svglib import ARROW, MUTED, PAL, TEXT, Diagram, text_width

REGISTRY = {}
ACCENT = "#B5520C"


def diagram(fn):
    REGISTRY[fn.__name__] = fn
    return fn


def seq_lifelines(d: Diagram, names, xs, top=14, bottom=300, w=150, kinds=None):
    for i, (n, x) in enumerate(zip(names, xs)):
        k = kinds[i] if kinds else "service"
        d.box(x - w / 2, top, w, 36, n, k, size=11.5)
        d.line(x, top + 38, x, bottom, "#98A2B3", 1.1, "4 4")


# =============================================================== MODULE 4
@diagram
def cloud_responsibility():
    d = Diagram(720, 300)
    cols = ["On-premises", "DB on a cloud VM", "Managed DB\n(RDS / Cloud SQL)", "Serverless DB"]
    rows = ["Hardware, power, data centre", "Operating system install & patches", "Database install, patches, upgrades",
            "Backups, replication, failover", "Capacity planning & scaling", "Schema, queries, indexes, access"]
    Y, U, S, P = "You", "Shared", "Provider", "Provider"
    m = [[Y, P, P, P], [Y, Y, P, P], [Y, Y, P, P], [Y, Y, P, P], [Y, Y, S, P], [Y, Y, Y, Y]]
    colors = {"You": ("#FFE9D6", "#B5520C"), "Shared": ("#EFE7FB", "#6941C6"), "Provider": ("#DDF2EE", "#0F766E")}
    x0, cw, rh, y0 = 230, 120, 33, 52
    for j, c in enumerate(cols):
        d.mtext(x0 + j * cw + cw / 2, 28, c, 10.5, 700, "#13294B")
    for i, r in enumerate(rows):
        y = y0 + i * rh
        d.text(10, y + rh / 2 + 4, r, 10, 500, "#344054", "start")
        for j in range(4):
            v = m[i][j]
            fill, col = colors[v]
            d.rect(x0 + j * cw + 2, y + 2, cw - 4, rh - 4, fill, "none", 0, 4)
            d.text(x0 + j * cw + cw / 2, y + rh / 2 + 4, v, 10, 600, col)
    ly = y0 + 6 * rh + 22
    d.text(10, ly, "Moving right = you manage less infrastructure and focus more on data and queries.", 9.8, 400,
           MUTED, "start", italic=True)
    return d


@diagram
def replication_failover():
    d = Diagram(720, 290)
    d.frame(6, 14, 344, 268, "Normal operation", "#1F5FA8")
    d.box(110, 34, 130, 40, "Application", "user", size=11.5)
    d.db(30, 120, 130, 70, "Primary", "db", "reads + writes", size=11.5)
    d.db(200, 120, 130, 70, "Read replica", "db", "read-only copy", size=11.5)
    d.db(115, 214, 130, 62, "Standby", "neutral", "zone B (hot spare)", size=11)
    d.arrow(150, 76, 100, 118, "writes", lsize=9, loff=(-18, -2))
    d.arrow(200, 76, 262, 118, "reports", lsize=9, loff=(22, -2))
    d.arrow(162, 150, 198, 150, head=6, dash="4 3")
    d.text(180, 140, "async", 8.6, 500, MUTED)
    d.arrow(95, 192, 140, 214, head=6)
    d.text(80, 210, "sync", 8.6, 500, MUTED)
    d.frame(370, 14, 344, 268, "After the primary fails (failover)", "#B42318")
    d.box(476, 34, 130, 40, "Application", "user", size=11.5)
    d.db(394, 120, 130, 70, "Old primary", "bad", "crashed", size=11.5)
    d.line(404, 128, 514, 186, "#B42318", 2.5)
    d.line(514, 128, 404, 186, "#B42318", 2.5)
    d.db(560, 120, 130, 70, "New primary", "good", "standby promoted", size=11.5)
    d.arrow(566, 76, 610, 118, "same endpoint,\nnew server", lsize=9, loff=(46, 0))
    d.text(542, 232, "Automatic failover takes seconds to a", 9.4, 400, MUTED)
    d.text(542, 247, "minute or two; the app should retry", 9.4, 400, MUTED)
    d.text(542, 262, "its connection.", 9.4, 400, MUTED)
    return d


@diagram
def scaling():
    d = Diagram(720, 270)
    d.frame(6, 14, 300, 248, "Vertical scaling (scale UP)", "#1F5FA8")
    d.box(30, 92, 76, 70, "DB", "db", "2 vCPU\n8 GB", size=11, sub_size=9)
    d.arrow(110, 127, 150, 127, head=7)
    d.box(156, 54, 130, 146, "DB", "db", "16 vCPU\n128 GB RAM\nfaster disk", size=13, sub_size=9.6)
    d.text(156, 226, "simple · no code change", 9.6, 600, "#2F7A4D")
    d.text(156, 242, "hardware ceiling · often a restart", 9.6, 600, "#B42318")
    d.frame(326, 14, 388, 248, "Horizontal scaling (scale OUT)", "#0F766E")
    d.box(450, 40, 140, 38, "Router / load balancer", "navy", size=10.5)
    shards = [("Shard 1", "customers 1–1M"), ("Shard 2", "customers 1M–2M"), ("Shard 3", "customers 2M–3M")]
    for i, (t, s) in enumerate(shards):
        x = 342 + i * 124
        d.db(x, 112, 112, 74, t, "db", s, size=11, sub_size=8.8)
        d.arrow(520, 80, x + 56, 110, head=6, color="#667085")
    d.text(520, 216, "near-limitless growth · fault isolation", 9.6, 600, "#2F7A4D")
    d.text(520, 232, "harder: shard key, cross-shard joins, consistency", 9.6, 600, "#B42318")
    return d


@diagram
def cap_triangle():
    d = Diagram(600, 380)
    C, A, P = (300, 58), (92, 300), (508, 300)
    d.path(f"M{C[0]},{C[1]} L{A[0]},{A[1]} L{P[0]},{P[1]} Z", fill="#F7F9FB", stroke="#98A2B3", lw=1.5)
    for (x, y), letter in ((C, "C"), (A, "A"), (P, "P")):
        d.circle(x, y, 24, "#13294B", "#13294B", 1)
        d.text(x, y + 7, letter, 18, 700, "#FFFFFF")
    d.text(300, 22, "Consistency", 12, 700, "#13294B")
    d.text(300, 98, "every read sees the latest write", 9.2, 400, MUTED)
    d.text(92, 342, "Availability", 12, 700, "#13294B")
    d.text(92, 357, "every request gets a response", 9.2, 400, MUTED)
    d.text(508, 342, "Partition tolerance", 12, 700, "#13294B")
    d.text(508, 357, "keeps working if the network splits", 9.2, 400, MUTED)
    d.label(158, 176, "CA\nsingle-node RDBMS\n(no network partition\nto tolerate)", 9.6, "#344054", 500)
    d.label(446, 176, "CP\nMongoDB*, HBase,\netcd, ZooKeeper\n(may refuse requests)", 9.6, "#344054", 500)
    d.label(300, 300, "AP — Cassandra, DynamoDB*, CouchDB (may return stale data)", 9.6, "#344054", 500)
    d.text(300, 376, "* default settings — most modern databases let you tune consistency per query.", 9, 400, MUTED,
           italic=True)
    return d


@diagram
def nosql_types():
    d = Diagram(720, 300)
    panels = [("Key-value", "Redis, DynamoDB"), ("Document", "MongoDB, Couchbase"),
              ("Wide-column", "Cassandra, HBase"), ("Graph", "Neo4j, Neptune")]
    for i, (t, ex) in enumerate(panels):
        x = 8 + i * 178
        d.rect(x, 12, 170, 276, "#FBFCFD", "#C8D1DD", 1, 8)
        d.text(x + 85, 36, t, 13, 700, "#13294B")
        d.text(x + 85, 278, ex, 9.4, 500, MUTED)
    # key-value
    x = 8
    for j, (k, v) in enumerate([("session:42", "{cart: [...]}"), ("user:7:name", "\"Asha\""), ("otp:98450", "\"381204\"")]):
        y = 64 + j * 52
        d.rect(x + 10, y, 70, 30, "#FFE9D6", "#B5520C", 1, 4)
        d.text(x + 45, y + 19, k, 8.4, 600, "#7A3608", mono=True)
        d.arrow(x + 82, y + 15, x + 96, y + 15, head=5)
        d.rect(x + 98, y, 64, 30, "#FFFFFF", "#C8D1DD", 1, 4)
        d.text(x + 130, y + 19, v, 7.8, 400, TEXT, mono=True)
    d.text(x + 85, 236, "lookup by key only", 9.4, 600, "#344054")
    d.text(x + 85, 251, "super fast (cache, sessions)", 9.2, 400, MUTED)
    # document
    x = 186
    d.rect(x + 12, 56, 146, 160, "#FFFFFF", "#2F855A", 1.2, 6)
    doc = ['{', '  "_id": 101,', '  "name": "Asha",', '  "city": "Pune",', '  "orders": [', '    {"id": 1,',
           '     "total": 799}', '  ]', '}']
    for j, ln in enumerate(doc):
        d.text(x + 22, 74 + j * 15.5, ln, 8.6, 400, TEXT, "start", mono=True)
    d.text(x + 85, 236, "JSON-like documents", 9.4, 600, "#344054")
    d.text(x + 85, 251, "flexible fields, nested data", 9.2, 400, MUTED)
    # wide column
    x = 364
    d.text(x + 14, 66, "row key", 8.6, 600, MUTED, "start")
    rowsw = [("user#1", ["name", "city", "plan"]), ("user#2", ["name", "phone"]), ("user#3", ["name", "email", "tier"])]
    for j, (rk, cols) in enumerate(rowsw):
        y = 76 + j * 50
        d.rect(x + 10, y, 50, 34, "#FFE9D6", "#B5520C", 1, 3)
        d.text(x + 35, y + 21, rk, 8, 600, "#7A3608", mono=True)
        for c, cn in enumerate(cols):
            d.rect(x + 64 + c * 32, y, 30, 34, "#EAF2FB", "#1F5FA8", 0.8, 2)
            d.text(x + 79 + c * 32, y + 21, cn, 6.6, 500, "#13294B", mono=True)
    d.text(x + 85, 236, "rows can have different", 9.4, 600, "#344054")
    d.text(x + 85, 251, "columns; huge write volume", 9.2, 400, MUTED)
    # graph
    x = 542
    pts = {"Asha": (x + 44, 84), "Ravi": (x + 128, 90), "Neha": (x + 52, 176), "Pune": (x + 130, 182)}
    edges = [("Asha", "Ravi", "FRIEND"), ("Asha", "Neha", "FRIEND"), ("Ravi", "Pune", "LIVES_IN"), ("Neha", "Pune", "LIVES_IN")]
    for a, b, lbl in edges:
        (x1, y1), (x2, y2) = pts[a], pts[b]
        d.line(x1, y1, x2, y2, "#7A8699", 1.2)
        d.text((x1 + x2) / 2 + (8 if lbl == "LIVES_IN" else 0), (y1 + y2) / 2 - 3, lbl, 6.6, 600, ACCENT)
    for n, (px, py) in pts.items():
        d.circle(px, py, 20, "#F2EDFC" if n != "Pune" else "#E7F6F3", "#6941C6" if n != "Pune" else "#0F766E", 1.2)
        d.text(px, py + 3.5, n, 8.8, 600, "#3E1F8C" if n != "Pune" else "#0B4F4A")
    d.text(x + 85, 236, "nodes + relationships", 9.4, 600, "#344054")
    d.text(x + 85, 251, "friends-of-friends, fraud rings", 9.2, 400, MUTED)
    return d


@diagram
def mongo_structure():
    d = Diagram(720, 290)
    d.frame(6, 14, 708, 268, "MongoDB server", "#2F855A")
    d.box(20, 40, 150, 60, "Database: shop", "good", "like a SQL database", size=11.5, sub_size=9.2)
    colls = [("customers", 112), ("orders", 172), ("products", 232)]
    d.line(34, 100, 34, 252, "#98A2B3", 1.2)
    for name, y in colls:
        d.box(48, y, 140, 40, f"collection: {name}", "plain", size=10)
        d.arrow(34, y + 20, 46, y + 20, head=5, color="#98A2B3")
    d.text(270, 52, "collection = like a table   ·   document = like a row   ·   field = like a column", 9.6, 600,
           "#344054", "start")
    docs = [
        ['{', '  "_id": ObjectId("6650…a1"),', '  "name": "Aarav Patel",', '  "email": "aarav@mail.com",',
         '  "city": "Mumbai",', '  "tags": ["prime", "early"]', '}'],
        ['{', '  "_id": ObjectId("6650…a2"),', '  "name": "Isha Kulkarni",', '  "city": "Pune",',
         '  "phone": "+91-98xxxxxx10"', '}'],
    ]
    for i, lines in enumerate(docs):
        x = 270 + i * 222
        d.rect(x, 74, 206, 170, "#FFFFFF", "#2F855A", 1.2, 6)
        d.text(x + 10, 92, f"document {i + 1}", 8.6, 700, "#2F855A", "start")
        for j, ln in enumerate(lines):
            d.text(x + 10, 110 + j * 15.5, ln, 8.6, 400, TEXT, "start", mono=True)
    d.arrow(190, 132, 266, 150, head=6, color="#2F855A")
    d.text(490, 266, "Two documents in the SAME collection can have different fields (phone vs tags).",
           9.4, 400, MUTED, italic=True)
    return d


@diagram
def embedding_vs_referencing():
    d = Diagram(720, 310)
    d.frame(6, 14, 344, 288, "Embedding — data that is read together lives together", "#2F855A")
    emb = ['{', '  "_id": 101,', '  "customer": "Aarav Patel",', '  "order_date": "2024-01-05",',
           '  "items": [', '    {"product": "Wireless Mouse",', '     "qty": 2, "price": 799},',
           '    {"product": "Notebook Pack",', '     "qty": 5, "price": 249}', '  ],',
           '  "ship_to": {"city": "Mumbai",', '              "pin": "400001"}', '}']
    d.rect(24, 38, 308, 236, "#FFFFFF", "#2F855A", 1.2, 6)
    for j, ln in enumerate(emb):
        d.text(36, 58 + j * 16.5, ln, 9, 400, TEXT, "start", mono=True)
    d.text(178, 292, "one read returns the whole order", 9.6, 600, "#2F7A4D")
    d.frame(370, 14, 344, 288, "Referencing — store an id, look it up", "#1F5FA8")
    c = ['// customers', '{', '  "_id": 1,', '  "name": "Aarav Patel",', '  "email": "aarav@mail.com"', '}']
    o = ['// orders', '{', '  "_id": 101,', '  "customer_id": 1,', '  "total": 2843', '}']
    d.rect(388, 38, 150, 112, "#FFFFFF", "#1F5FA8", 1.2, 6)
    for j, ln in enumerate(c):
        d.text(396, 56 + j * 16, ln, 8.6, 400, "#6B7280" if j == 0 else TEXT, "start", mono=True)
    d.rect(548, 150, 150, 112, "#FFFFFF", "#1F5FA8", 1.2, 6)
    for j, ln in enumerate(o):
        d.text(556, 168 + j * 16, ln, 8.6, 400, "#6B7280" if j == 0 else TEXT, "start", mono=True)
    d.parrow([(548, 216), (378, 216), (378, 88), (386, 88)], color=ACCENT, head=6, lw=1.6)
    d.text(384, 232, "customer_id points to _id", 8.8, 600, ACCENT, "start")
    d.text(520, 292, "no duplication; needs a 2nd query or $lookup", 9.6, 600, "#1F5FA8")
    return d


@diagram
def data_lake():
    d = Diagram(720, 280)
    srcs = [("Structured", "DB tables, CSV", "db"), ("Semi-structured", "JSON, logs, XML", "amber"),
            ("Unstructured", "images, PDFs, audio", "purple")]
    for i, (t, s, k) in enumerate(srcs):
        d.box(6, 22 + i * 82, 142, 60, t, k, s, size=11.5, sub_size=9.2)
        d.arrow(150, 52 + i * 82, 212, 140, head=6, color="#667085")
    d.frame(196, 14, 352, 252, "Data lake on object storage (S3 / ADLS / GCS)", "#0F766E")
    zones = [("Raw", "bronze", "exact copy,\nas it arrived"), ("Cleaned", "silver", "validated,\ndeduplicated,\nstandard types"),
             ("Curated", "gold", "business-ready\ntables and\naggregates")]
    for i, (t, tag, s) in enumerate(zones):
        x = 212 + i * 112
        d.box(x, 44, 100, 206, "", "teal")
        d.text(x + 50, 76, t, 12.5, 700, "#0B4F4A")
        d.text(x + 50, 94, f"({tag})", 9.4, 500, ACCENT)
        d.mtext(x + 50, 150, s, 9.4, 400, "#344054")
        if i < 2:
            d.arrow(x + 101, 147, x + 111, 147, head=5)
    cons = [("Data science / ML", 30), ("BI & SQL analytics", 112), ("Data apps / APIs", 194)]
    for t, y in cons:
        d.box(578, y, 136, 50, t, "analytics", size=10.5)
        d.arrow(550, 147, 576, y + 25, head=6, color="#667085")
    d.text(372, 278, "Schema-on-read: store first in open formats (Parquet), decide the structure when reading.",
           9.4, 400, MUTED, italic=True)
    return d


@diagram
def lakehouse():
    d = Diagram(700, 300)
    for i, t in enumerate(["BI dashboards", "Data science / ML", "Streaming & apps"]):
        d.box(14 + i * 228, 12, 216, 42, t, "analytics", size=11.5)
    d.box(14, 82, 672, 44, "Compute engines: SQL warehouse engine · Spark · Trino", "service", size=11.5)
    d.box(14, 154, 672, 60, "Open table format: Delta Lake / Apache Iceberg / Apache Hudi", "navy",
          "ACID transactions · schema enforcement · time travel · upserts · metadata for fast queries", size=12,
          sub_size=9.6)
    d.box(14, 242, 672, 46, "Cheap object storage (S3 / ADLS / GCS) holding open files (Parquet)", "teal", size=11.5)
    for y in (56, 128, 216):
        for x in (130, 350, 570):
            d.arrow(x, y + 24, x, y + 2, head=6, color="#667085")
    return d


@diagram
def data_shapes():
    d = Diagram(720, 230)
    titles = [("Structured", "fixed rows & columns", "db"), ("Semi-structured", "self-describing tags/keys", "amber"),
              ("Unstructured", "no predefined model", "purple")]
    for i, (t, s, k) in enumerate(titles):
        x = 8 + i * 240
        fill, stroke, tcol = PAL[k]
        d.rect(x, 12, 228, 206, "#FFFFFF", stroke, 1.2, 8)
        d.text(x + 114, 36, t, 13, 700, tcol)
        d.text(x + 114, 53, s, 9.4, 400, MUTED)
    # structured grid
    hdr = ["id", "name", "salary"]
    rows = [["1", "Asha", "65000"], ["2", "Ravi", "72000"], ["3", "Neha", "58000"]]
    x0, y0, cw = 30, 72, 60
    for j, h in enumerate(hdr):
        d.rect(x0 + j * cw, y0, cw, 24, "#E9EEF5", "#C8D1DD", 0.8, 0)
        d.text(x0 + j * cw + cw / 2, y0 + 16, h, 9.4, 600, "#13294B", mono=True)
    for r, row in enumerate(rows):
        for j, v in enumerate(row):
            d.rect(x0 + j * cw, y0 + 24 * (r + 1), cw, 24, "#FFFFFF", "#D9DFE7", 0.8, 0)
            d.text(x0 + j * cw + cw / 2, y0 + 24 * (r + 1) + 16, v, 9.4, 400, TEXT, mono=True)
    d.text(122, 200, "SQL tables, spreadsheets", 9.4, 600, "#344054")
    # semi structured
    js = ['{ "id": 7,', '  "name": "Asha",', '  "skills": ["SQL",', '             "Python"],', '  "address": {', '    "city": "Pune" } }']
    for j, ln in enumerate(js):
        d.text(268, 84 + j * 17, ln, 9, 400, TEXT, "start", mono=True)
    d.text(362, 200, "JSON, XML, logs, emails", 9.4, 600, "#344054")
    # unstructured icons
    icons = [("IMG", "photo.jpg"), ("PDF", "invoice.pdf"), ("MP3", "call.mp3"), ("TXT", "review.txt")]
    for j, (ic, nm) in enumerate(icons):
        x = 500 + (j % 2) * 104
        y = 70 + (j // 2) * 64
        d.rect(x, y, 44, 50, "#F2EDFC", "#6941C6", 1, 4)
        d.text(x + 22, y + 30, ic, 10, 700, "#3E1F8C")
        d.text(x + 50, y + 30, nm, 8.4, 400, MUTED, "start", mono=True)
    d.text(602, 200, "images, video, audio, PDFs", 9.4, 600, "#344054")
    return d


# =============================================================== MODULE 5
@diagram
def client_server():
    d = Diagram(720, 282)
    clients = [("Browser", "React web app"), ("Mobile app", "Android / iOS"), ("Another server", "partner system")]
    for i, (t, s) in enumerate(clients):
        d.box(10, 20 + i * 72, 150, 52, t, "client", s, size=11.5, sub_size=9.2)
        d.arrow(162, 46 + i * 72, 286, 120, head=6, color="#667085", both=True)
    d.box(290, 82, 160, 76, "Server", "navy", "REST API (Spring Boot,\nNode.js, Django)", size=13, sub_size=9.2)
    d.db(560, 78, 150, 86, "Database", "db", "PostgreSQL", size=12)
    d.arrow(452, 120, 558, 120, both=True)
    d.text(505, 110, "SQL", 9.6, 600, "#344054")
    d.text(360, 252, "Clients send requests; the server does the work and sends responses.", 9.8, 400, MUTED)
    d.text(360, 270, "The client never talks to the database directly.", 9.8, 600, ACCENT)
    return d


@diagram
def api_request_flow():
    d = Diagram(720, 350)
    xs = [110, 360, 610]
    seq_lifelines(d, ["Frontend", "Backend (API)", "Database"], xs, bottom=340, kinds=["client", "navy", "db"])
    def msg(y, a, b, text, dash=None, color=ARROW, mono=True):
        d.arrow(xs[a], y, xs[b], y, dash=dash, color=color, head=7)
        d.label((xs[a] + xs[b]) / 2, y - 11, text, 9.2, "#13294B" if not dash else "#344054", 500)
    msg(84, 0, 1, "GET /api/users?page=1   (Authorization: Bearer <token>)")
    d.rect(xs[1] + 6, 104, 210, 34, "#FFF8E6", "#C27803", 1, 4)
    d.mtext(xs[1] + 111, 121, "check token → allowed?\nvalidate query parameters", 9, 500, "#7A4B02")
    msg(166, 1, 2, "SELECT id, name, email FROM users ORDER BY id LIMIT 20 OFFSET 0;")
    msg(204, 2, 1, "20 rows", dash="5 4")
    d.rect(xs[1] + 6, 224, 210, 34, "#FFF8E6", "#C27803", 1, 4)
    d.mtext(xs[1] + 111, 241, "convert rows → JSON\nadd paging info", 9, 500, "#7A4B02")
    msg(292, 1, 0, "200 OK  [{\"id\":1,\"name\":\"Asha\",…}]", dash="5 4")
    return d


@diagram
def http_anatomy():
    d = Diagram(720, 260)
    req = [("POST /api/v1/orders HTTP/1.1", "request line: method + path"),
           ("Host: shop.example.com", "headers"),
           ("Authorization: Bearer eyJhbGciOi…", ""),
           ("Content-Type: application/json", ""),
           ("", ""),
           ('{"productId": 2, "quantity": 1}', "body (JSON)")]
    res = [("HTTP/1.1 201 Created", "status line"),
           ("Content-Type: application/json", "headers"),
           ("Location: /api/v1/orders/9001", ""),
           ("", ""),
           ('{"orderId": 9001,', "body (JSON)"),
           (' "status": "PENDING"}', "")]
    def panel(x, title, lines, color):
        d.rect(x, 14, 340, 232, "#FFFFFF", color, 1.3, 7)
        d.rect(x, 14, 340, 28, color, color, 1, 7)
        d.rect(x, 34, 340, 8, color, color, 1, 0)
        d.text(x + 170, 33, title, 11.5, 700, "#FFFFFF")
        for i, (ln, note) in enumerate(lines):
            y = 70 + i * 28
            d.text(x + 12, y, ln, 9.4, 600 if i == 0 else 400, TEXT, "start", mono=True)
            if note:
                d.text(x + 330, y + 13, note, 8.4, 600, ACCENT, "end", italic=True)
    panel(8, "HTTP REQUEST (client → server)", req, "#1F5FA8")
    panel(372, "HTTP RESPONSE (server → client)", res, "#0F766E")
    return d


@diagram
def authn_authz():
    d = Diagram(720, 240)
    d.text(10, 24, "1. Authentication — WHO are you?", 12, 700, "#13294B", "start")
    d.box(10, 40, 128, 50, "User", "user", "email + password\nor OTP / Google", size=11, sub_size=8.8)
    d.arrow(140, 65, 214, 65, "login", lsize=9)
    d.box(216, 40, 168, 50, "Auth server / API", "navy", "verifies identity", size=11, sub_size=9)
    d.arrow(386, 65, 470, 65, "issues", lsize=9)
    d.box(472, 40, 236, 50, "Token (JWT)", "amber", "user_id=7, role=customer, exp=1h", size=11, sub_size=9)
    d.text(10, 134, "2. Authorization — WHAT are you allowed to do?", 12, 700, "#13294B", "start")
    d.box(10, 150, 178, 54, "DELETE /api/products/5", "client", "Authorization: Bearer <JWT>", size=10, sub_size=8.4)
    d.arrow(190, 177, 254, 177)
    d.box(256, 150, 168, 54, "Permission check", "service", "does role allow this?", size=11, sub_size=9)
    d.box(474, 140, 234, 34, "role = admin  →  204 No Content", "good", size=10.2)
    d.box(474, 182, 234, 34, "role = customer  →  403 Forbidden", "bad", size=10.2)
    d.arrow(426, 168, 472, 157, head=6)
    d.arrow(426, 186, 472, 199, head=6)
    d.text(360, 232, "No / invalid token → 401 Unauthorized (really means 'unauthenticated').", 9.6, 600, ACCENT)
    return d


@diagram
def idempotency_flow():
    d = Diagram(720, 330)
    xs = [110, 360, 610]
    seq_lifelines(d, ["Client (checkout)", "Payment API", "Payments DB"], xs, bottom=322, kinds=["client", "navy", "db"])
    def msg(y, a, b, text, dash=None, color=ARROW):
        d.arrow(xs[a], y, xs[b], y, dash=dash, color=color, head=7)
        d.label((xs[a] + xs[b]) / 2, y - 11, text, 9.2, "#344054", 500)
    msg(80, 0, 1, "POST /payments  Idempotency-Key: 7f3a9c")
    msg(112, 1, 2, "save key 7f3a9c + charge ₹500 → pay_881")
    d.arrow(xs[1], 146, xs[0] + 90, 146, dash="5 4", color="#B42318")
    d.line(xs[0] + 70, 136, xs[0] + 90, 156, "#B42318", 2.2)
    d.line(xs[0] + 90, 136, xs[0] + 70, 156, "#B42318", 2.2)
    d.label((xs[0] + xs[1]) / 2 + 40, 134, "201 response lost (network timeout)", 9.2, "#B42318", 600)
    msg(194, 0, 1, "retry: POST /payments  Idempotency-Key: 7f3a9c")
    msg(226, 1, 2, "key 7f3a9c already exists → return stored result")
    msg(262, 1, 0, "201 Created  {payment_id: pay_881}  (same result, charged once)", dash="5 4")
    d.text(360, 304, "Same key = same operation. The server does the work at most once.", 9.8, 600, ACCENT)
    return d


@diagram
def retry_backoff():
    d = Diagram(720, 170)
    d.line(20, 80, 700, 80, "#C8D1DD", 2)
    events = [(30, "try 1", "bad"), (110, "wait 1s", None), (180, "try 2", "bad"), (280, "wait 2s", None),
              (380, "try 3", "bad"), (520, "wait 4s", None), (640, "try 4", "good")]
    for x, t, k in events:
        if k:
            d.box(x - 30, 58, 68, 44, t, k, "503 error" if k == "bad" else "200 OK", size=11, sub_size=9)
        else:
            d.text(x + 4, 74, t, 10, 600, ACCENT)
    for x1, x2 in ((40, 175), (190, 375), (390, 635)):
        d.path(f"M{x1 + 30},{106} Q{(x1 + x2) / 2},{150} {x2 - 30},{106}", stroke="#98A2B3", lw=1.1, dash="4 3")
    d.text(360, 32, "Exponential backoff: wait 1s, 2s, 4s … (+ random jitter) and give up after a few tries.",
           10, 600, "#13294B")
    d.text(360, 164, "Only retry safe/idempotent operations, or use an idempotency key.", 9.6, 400, MUTED, italic=True)
    return d


@diagram
def sync_vs_async():
    d = Diagram(720, 320)
    d.frame(6, 14, 344, 298, "Synchronous — caller waits", "#1F5FA8")
    xs = [80, 270]
    for n, x in zip(["Checkout", "Payment"], xs):
        d.box(x - 55, 34, 110, 32, n, "service", size=11)
        d.line(x, 66, x, 300, "#98A2B3", 1.1, "4 4")
    d.rect(74, 92, 12, 150, "#FFE7C7", "#B5520C", 1, 2)
    d.arrow(86, 96, 264, 96, "request", lsize=9.2)
    d.rect(264, 102, 12, 120, "#DCEBFB", "#1F5FA8", 1, 2)
    d.arrow(264, 236, 86, 236, "response", dash="5 4", lsize=9.2)
    d.text(178, 166, "caller is BLOCKED", 9.6, 600, ACCENT)
    d.text(178, 180, "until the reply comes", 9.2, 400, MUTED)
    d.text(178, 288, "simple; but slow/failing callee = slow caller", 9.2, 500, "#344054")
    d.frame(370, 14, 344, 298, "Asynchronous — caller moves on", "#0F766E")
    xs = [430, 560, 670]
    for n, x in zip(["Checkout", "Queue", "Email"], xs):
        d.box(x - 45, 34, 90, 32, n, "queue" if n == "Queue" else "service", size=10.5)
        d.line(x, 66, x, 300, "#98A2B3", 1.1, "4 4")
    d.arrow(xs[0], 98, xs[1], 98, "message", lsize=9)
    d.rect(xs[0] - 6, 92, 12, 30, "#FFE7C7", "#B5520C", 1, 2)
    d.text(xs[0] + 6, 142, "continues", 9.2, 600, "#2F7A4D", "start")
    d.text(xs[0] + 6, 156, "immediately", 9.2, 600, "#2F7A4D", "start")
    d.arrow(xs[1], 196, xs[2], 196, "delivered later", lsize=9)
    d.rect(xs[2] - 6, 202, 12, 46, "#DCEBFB", "#1F5FA8", 1, 2)
    d.text(542, 288, "resilient & scalable; result arrives later", 9.2, 500, "#344054")
    return d


@diagram
def webhook_vs_polling():
    d = Diagram(720, 260)
    d.text(10, 22, "Polling — client keeps asking", 12, 700, "#13294B", "start")
    d.box(10, 36, 120, 76, "Your app", "client", size=11.5)
    d.box(590, 36, 120, 76, "Payment\nprovider", "navy", size=11.5)
    for i, (q, a) in enumerate([("done?", "no"), ("done?", "no"), ("done?", "yes")]):
        y = 46 + i * 22
        d.arrow(132, y, 588, y, q, lsize=8.6, loff=(-150, -1), head=5.5, color="#667085")
        d.text(500, y - 3, a, 8.8, 600, "#B42318" if a == "no" else "#2F7A4D")
    d.text(360, 128, "wasteful requests · delay up to one polling interval", 9.4, 400, MUTED, italic=True)
    d.text(10, 160, "Webhook — server calls you when something happens", 12, 700, "#13294B", "start")
    d.box(10, 174, 120, 66, "Your app", "client", "POST /webhooks/payment", size=11.5, sub_size=8.2)
    d.box(590, 174, 120, 66, "Payment\nprovider", "navy", size=11.5)
    d.arrow(132, 190, 588, 190, "1. register URL once", lsize=8.8, head=6)
    d.arrow(588, 222, 132, 222, "2. event happened → POST {\"status\":\"captured\"} (signed)", lsize=8.8, head=6,
            color="#0F766E")
    return d


@diagram
def data_integration_overview():
    d = Diagram(720, 290)
    srcs = [("ERP (SAP)", "db"), ("CRM (Salesforce)", "db"), ("E-commerce DB", "db"), ("SaaS APIs", "external"),
            ("CSV / Excel files", "external")]
    for i, (t, k) in enumerate(srcs):
        d.box(8, 14 + i * 54, 140, 40, t, k, size=10.8)
        d.arrow(150, 34 + i * 54, 226, 34 + i * 54 if i in (1, 2, 3) else 34 + (1 if i == 0 else 3) * 54, head=6,
                color="#667085")
    d.frame(228, 20, 258, 236, "Integration layer", "#B5520C")
    methods = [("APIs (REST / SOAP)", "real-time request / response"), ("ETL / ELT jobs", "scheduled bulk copies"),
               ("CDC", "stream every DB change"), ("Messaging / events", "queues, pub/sub topics")]
    for i, (t, s) in enumerate(methods):
        d.box(244, 40 + i * 52, 226, 44, t, "queue", s, size=10.8, sub_size=8.8)
    tg = [("Data warehouse", "analytics"), ("Other applications", "service"), ("Search / cache", "db"),
          ("Dashboards & ML", "analytics")]
    for i, (t, k) in enumerate(tg):
        d.box(560, 30 + i * 58, 152, 42, t, k, size=10.8)
        d.arrow(488, 138, 558, 51 + i * 58, head=6, color="#667085")
    d.text(360, 280, "Same goal every time: get the right data to the right place, in the right shape, on time.",
           9.6, 400, MUTED, italic=True)
    return d


@diagram
def cdc_flow():
    d = Diagram(720, 200)
    d.db(8, 52, 130, 90, "Orders DB", "db", "INSERT / UPDATE /\nDELETE", size=11.5, sub_size=8.8)
    d.box(170, 66, 120, 62, "Transaction log", "neutral", "WAL / binlog", size=10.8, sub_size=9)
    d.arrow(140, 97, 168, 97, head=6)
    d.box(322, 66, 120, 62, "CDC tool", "queue", "e.g. Debezium", size=11.5, sub_size=9)
    d.arrow(292, 97, 320, 97, head=6)
    d.box(474, 66, 90, 62, "Kafka", "queue", "change events", size=11.5, sub_size=8.8)
    d.arrow(444, 97, 472, 97, head=6)
    for i, t in enumerate(["Warehouse", "Search index", "Cache"]):
        d.box(600, 26 + i * 52, 112, 40, t, "analytics" if i == 0 else "service", size=10.8)
        d.arrow(566, 97, 598, 46 + i * 52, head=6, color="#667085")
    d.text(360, 182, "Reads changes from the log, so the source database does almost no extra work.",
           9.6, 400, MUTED, italic=True)
    return d


# =============================================================== MODULE 6
@diagram
def p2p_vs_hub():
    d = Diagram(720, 290)
    import math
    d.frame(6, 14, 344, 268, "Point-to-point: 5 systems → 10 links", "#B42318")
    names = ["CRM", "ERP", "Billing", "Website", "HRMS"]
    pts = []
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        pts.append((178 + 100 * math.cos(a), 152 + 100 * math.sin(a)))
    for i in range(5):
        for j in range(i + 1, 5):
            d.line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], "#E4A9A3", 1.4)
    for (x, y), n in zip(pts, names):
        d.box(x - 38, y - 16, 76, 32, n, "service", size=10.5)
    d.frame(370, 14, 344, 268, "Hub / integration platform: 5 links", "#2F7A4D")
    hub = (542, 152)
    pts2 = []
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        pts2.append((hub[0] + 104 * math.cos(a), hub[1] + 104 * math.sin(a)))
    for (x, y) in pts2:
        d.line(hub[0], hub[1], x, y, "#8CC5A2", 1.8)
    d.box(hub[0] - 52, hub[1] - 22, 104, 44, "Integration hub", "good", "ESB / iPaaS", size=10, sub_size=8.6)
    for (x, y), n in zip(pts2, names):
        d.box(x - 38, y - 16, 76, 32, n, "service", size=10.5)
    return d


@diagram
def integration_styles():
    d = Diagram(720, 320)
    cells = [("1. File transfer", "export a file, the other side imports it", "nightly · simple · stale data"),
             ("2. Shared database", "both apps read/write the same tables", "easy start · tight coupling"),
             ("3. Remote call (API)", "app A calls app B and waits for a reply", "real time · both must be up"),
             ("4. Messaging", "app A sends a message to a queue/topic", "decoupled · reliable · async")]
    for i, (t, s, n) in enumerate(cells):
        x = 8 + (i % 2) * 356
        y = 10 + (i // 2) * 156
        d.rect(x, y, 348, 148, "#FBFCFD", "#C8D1DD", 1, 8)
        d.text(x + 12, y + 22, t, 12, 700, "#13294B", "start")
        d.text(x + 12, y + 38, s, 9.2, 400, MUTED, "start")
        d.text(x + 12, y + 138, n, 9.2, 600, ACCENT, "start")
        ay = y + 84
        d.box(x + 16, ay - 22, 80, 44, "App A", "service", size=11)
        d.box(x + 252, ay - 22, 80, 44, "App B", "service", size=11)
        if i == 0:
            d.rect(x + 140, ay - 20, 68, 40, "#FFFFFF", "#98A2B3", 1, 3)
            d.text(x + 174, ay + 4, "orders.csv", 8.6, 500, "#344054", mono=True)
            d.arrow(x + 98, ay, x + 138, ay, head=6)
            d.arrow(x + 210, ay, x + 250, ay, head=6)
        elif i == 1:
            d.db(x + 138, ay - 30, 72, 60, "DB", "db", size=11)
            d.arrow(x + 98, ay, x + 136, ay, head=6, both=True)
            d.arrow(x + 212, ay, x + 250, ay, head=6, both=True)
        elif i == 2:
            d.arrow(x + 98, ay - 8, x + 250, ay - 8, "request", lsize=8.8, head=6)
            d.arrow(x + 250, ay + 10, x + 98, ay + 10, "reply", lsize=8.8, head=6, dash="4 3", loff=(0, 10))
        else:
            d.rect(x + 132, ay - 16, 84, 32, "#FFF4E6", "#B5520C", 1.2, 4)
            for k in range(4):
                d.rect(x + 138 + k * 19, ay - 10, 15, 20, "#F2B37A", "#B5520C", 0.8, 2)
            d.arrow(x + 98, ay, x + 130, ay, head=6)
            d.arrow(x + 218, ay, x + 250, ay, head=6)
    return d


@diagram
def message_queue():
    d = Diagram(720, 270)
    for i, t in enumerate(["Checkout service", "Admin portal"]):
        d.box(8, 44 + i * 80, 140, 46, t, "service", "producer", size=11, sub_size=9)
        d.arrow(150, 67 + i * 80, 222, 107, head=6)
    d.rect(224, 80, 236, 56, "#FFF4E6", "#B5520C", 1.4, 6)
    d.text(342, 72, "queue: order-processing", 10.5, 700, "#7A3608")
    for k in range(6):
        d.rect(236 + k * 37, 90, 31, 36, "#F2B37A", "#B5520C", 0.9, 3)
        d.text(251.5 + k * 37, 113, f"m{6 - k}", 9, 600, "#7A3608")
    d.text(342, 154, "messages wait here until a consumer takes them (FIFO-ish)", 9, 400, MUTED)
    workers = ["Worker 1", "Worker 2", "Worker 3"]
    for i, t in enumerate(workers):
        d.box(560, 20 + i * 62, 150, 44, t, "good", "consumer", size=11, sub_size=9)
        d.arrow(462, 108, 558, 42 + i * 62, head=6)
    d.text(635, 214, "each message goes to", 9.4, 600, "#2F7A4D")
    d.text(635, 228, "exactly ONE worker", 9.4, 600, "#2F7A4D")
    d.box(250, 196, 184, 54, "Dead-letter queue", "bad", "messages that failed 3 times", size=11, sub_size=9)
    d.arrow(342, 138, 342, 194, dash="4 3", color="#B42318", head=6)
    return d


@diagram
def pub_sub():
    d = Diagram(720, 270)
    d.box(8, 104, 150, 60, "Order service", "service", "publisher", size=11.5, sub_size=9)
    d.arrow(160, 134, 236, 134, "OrderPlaced", lsize=9)
    d.rect(238, 96, 170, 76, "#FFF4E6", "#B5520C", 1.4, 8)
    d.text(323, 126, "topic", 9.4, 500, "#7A3608")
    d.text(323, 146, "order-placed", 12, 700, "#7A3608", mono=True)
    subs = [("Inventory", "reserve stock"), ("Email", "send confirmation"), ("Analytics", "update dashboard"),
            ("Loyalty", "add reward points")]
    for i, (t, s) in enumerate(subs):
        y = 12 + i * 64
        d.box(520, y, 190, 50, t, "good", s, size=11, sub_size=9)
        d.arrow(410, 134, 518, y + 25, head=6)
    d.text(323, 204, "every subscriber gets", 9.6, 600, "#2F7A4D")
    d.text(323, 219, "its OWN copy", 9.6, 600, "#2F7A4D")
    d.text(323, 246, "publisher does not know who listens", 9.2, 400, MUTED, italic=True)
    return d


@diagram
def event_driven():
    d = Diagram(720, 300)
    d.rect(8, 132, 704, 40, "#FFF4E6", "#B5520C", 1.4, 8)
    d.text(360, 157, "Event broker / bus (Kafka, RabbitMQ, EventBridge, Azure Service Bus)", 11, 700, "#7A3608")
    top = [("Order service", "emits OrderPlaced", 30), ("Payment service", "emits PaymentSucceeded", 270),
           ("Inventory service", "emits StockReserved", 510)]
    for t, s, x in top:
        d.box(x, 26, 180, 54, t, "service", s, size=11, sub_size=9)
        d.arrow(x + 70, 82, x + 70, 130, head=6)
        d.arrow(x + 120, 130, x + 120, 82, head=6, dash="4 3", color="#667085")
    bottom = [("Shipping service", "creates shipment on PaymentSucceeded", 30),
              ("Notification service", "SMS/email on every event", 270), ("Analytics", "stores all events", 510)]
    for t, s, x in bottom:
        d.box(x, 222, 180, 54, t, "good", s, size=11, sub_size=8.6)
        d.arrow(x + 90, 174, x + 90, 220, head=6, dash="4 3", color="#667085")
    d.text(130, 112, "publish", 8.6, 600, ACCENT, "end")
    d.text(156, 112, "subscribe", 8.6, 600, MUTED, "start")
    d.text(360, 296, "Services react to events instead of calling each other directly.", 9.6, 400, MUTED, italic=True)
    return d


@diagram
def etl_vs_elt():
    d = Diagram(720, 290)
    d.box(6, 30, 66, 52, "ETL", "navy", size=14)
    d.db(84, 24, 92, 66, "Sources", "db", size=10.5)
    d.box(196, 30, 112, 52, "Extract", "plain", "pull data", size=11, sub_size=8.8)
    d.box(328, 22, 152, 68, "Transform", "queue", "on a separate ETL server\n(Informatica, SSIS, Talend)", size=11.5,
          sub_size=8.6)
    d.box(500, 30, 74, 52, "Load", "plain", size=11)
    d.db(594, 18, 120, 78, "Warehouse", "analytics", "clean data only", size=10.8, sub_size=8.6)
    for x1, x2 in ((178, 194), (310, 326), (482, 498), (576, 592)):
        d.arrow(x1, 56, x2, 56, head=6)
    d.text(360, 120, "Transform BEFORE loading · good for strict rules, sensitive data, older on-prem warehouses",
           9.4, 400, MUTED, italic=True)
    d.box(6, 168, 66, 52, "ELT", "navy", size=14)
    d.db(84, 162, 92, 66, "Sources", "db", size=10.5)
    d.box(196, 168, 112, 52, "Extract", "plain", "pull data", size=11, sub_size=8.8)
    d.box(328, 168, 100, 52, "Load", "plain", "raw, as-is", size=11, sub_size=8.8)
    d.frame(448, 150, 266, 92, "Cloud warehouse / lakehouse", "#6941C6")
    d.box(462, 168, 108, 54, "raw tables", "neutral", size=10.5)
    d.box(594, 162, 108, 66, "Transform", "queue", "SQL / dbt inside\nthe warehouse", size=11, sub_size=8.6)
    d.arrow(572, 195, 592, 195, head=6)
    for x1, x2 in ((178, 194), (310, 326), (430, 460)):
        d.arrow(x1, 194, x2, 194, head=6)
    d.text(360, 268, "Load FIRST, transform later with the warehouse's own compute · flexible, keeps raw history",
           9.4, 400, MUTED, italic=True)
    return d


@diagram
def data_pipeline():
    d = Diagram(720, 270)
    d.rect(8, 10, 704, 34, "#13294B", "#13294B", 1, 6)
    d.text(360, 32, "Orchestration (Airflow / Azure Data Factory): schedule · order · retry · alert", 11, 600, "#FFFFFF")
    steps = [("Sources", "apps, APIs,\nfiles, DBs", "user"), ("Ingest", "batch pulls or\nstreaming", "queue"),
             ("Raw zone", "store as-is\n(replayable)", "teal"), ("Transform", "clean, join,\naggregate", "service"),
             ("Curated", "modelled tables\n(star schema)", "analytics"), ("Serve", "BI, ML,\nAPIs, exports", "good")]
    for i, (t, s, k) in enumerate(steps):
        x = 8 + i * 120
        d.box(x, 76, 104, 84, t, k, s, size=11.5, sub_size=9)
        if i < 5:
            d.arrow(x + 106, 118, x + 118, 118, head=5.5)
        d.line(x + 52, 46, x + 52, 74, "#98A2B3", 1, "3 3")
    d.rect(8, 186, 704, 34, "#F2F4F7", "#98A2B3", 1, 6)
    d.text(360, 208, "Quality checks (nulls, duplicates, row counts) · monitoring · lineage · access control", 10.5, 500,
           "#344054")
    for i in range(6):
        d.line(8 + i * 120 + 52, 162, 8 + i * 120 + 52, 184, "#98A2B3", 1, "3 3")
    d.text(360, 252, "A pipeline is a repeatable, automated path from raw data to trusted, useful data.", 9.6, 400,
           MUTED, italic=True)
    return d


@diagram
def kafka_partitions():
    d = Diagram(720, 280)
    d.box(8, 108, 116, 60, "Producer", "service", "order service", size=11.5, sub_size=9)
    d.frame(150, 24, 380, 238, "topic: orders (3 partitions)", "#B5520C")
    for p in range(3):
        y = 56 + p * 70
        d.text(166, y + 23, f"P{p}", 11, 700, "#7A3608", "start")
        n = [6, 4, 5][p]
        for k in range(n):
            d.rect(196 + k * 44, y, 40, 34, "#FFF4E6", "#B5520C", 1, 3)
            d.text(216 + k * 44, y + 22, str(k), 10, 600, "#7A3608", mono=True)
        d.arrow(126, 138, 192, y + 17, head=5.5, color="#667085")
        d.text(196 + n * 44 + 6, y + 22, "← new", 8.6, 500, MUTED, "start")
    d.frame(556, 24, 158, 238, "consumer group: billing", "#2F7A4D")
    for p in range(3):
        y = 56 + p * 70
        d.box(574, y - 2, 124, 38, f"Consumer {'ABC'[p]}", "good", f"reads P{p}", size=10.5, sub_size=8.6)
        d.arrow(532, y + 17, 572, y + 17, head=5.5, dash="4 3", color="#2F7A4D")
    d.text(340, 276, "Numbers = offsets. Order is guaranteed only within a partition (key = customer_id keeps a "
           "customer's events in order).", 8.8, 400, MUTED, italic=True)
    return d


@diagram
def salesforce_warehouse():
    d = Diagram(720, 330)
    d.box(8, 110, 136, 92, "Salesforce", "client", "CRM: Accounts,\nContacts,\nOpportunities", size=12.5, sub_size=9)
    opts = [("REST / Bulk API", "scheduled extracts"), ("Change Data Capture", "near real-time events"),
            ("ELT tool", "Fivetran, MuleSoft,\nInformatica, ADF")]
    for i, (t, s) in enumerate(opts):
        y = 26 + i * 92
        d.box(186, y, 150, 70, t, "queue", s, size=11, sub_size=8.8)
        d.arrow(146, 156, 184, y + 35, head=6, color="#667085")
        d.arrow(338, y + 35, 380, 156, head=6, color="#667085")
    d.frame(382, 30, 210, 252, "Cloud data warehouse", "#6941C6")
    d.box(398, 56, 178, 46, "Staging (raw copy)", "neutral", "sf_account, sf_opportunity", size=10.5, sub_size=8.4)
    d.box(398, 128, 178, 46, "Transform (SQL / dbt)", "queue", "clean · dedupe · join", size=10.5, sub_size=8.6)
    d.box(398, 200, 178, 54, "Analytics models", "analytics", "fact_opportunity,\ndim_account", size=10.5, sub_size=8.6)
    d.arrow(487, 104, 487, 126, head=6)
    d.arrow(487, 176, 487, 198, head=6)
    d.box(614, 120, 98, 70, "BI", "user", "pipeline,\nwin-rate\ndashboards", size=11.5, sub_size=8.6)
    d.arrow(578, 227, 612, 170, head=6)
    d.parrow([(487, 284), (487, 316), (76, 316), (76, 204)], label="reverse ETL: push scores back into Salesforce",
             dash="5 4", color=ACCENT, head=6, lsize=9, lat=1, loff=(0, -2))
    return d


@diagram
def api_led():
    d = Diagram(720, 300)
    layers = [("Experience APIs", "shaped for each channel", ["Mobile app API", "Partner portal API", "Web API"], "client"),
              ("Process APIs", "business processes", ["Order fulfilment", "Customer 360"], "queue"),
              ("System APIs", "unlock core systems", ["SAP ERP", "Salesforce", "Orders DB"], "db")]
    for i, (t, s, items, k) in enumerate(layers):
        y = 14 + i * 96
        d.text(10, y + 30, t, 12, 700, "#13294B", "start")
        d.text(10, y + 46, s, 9.2, 400, MUTED, "start")
        n = len(items)
        w = (530 - (n - 1) * 14) / n
        for j, it in enumerate(items):
            d.box(176 + j * (w + 14), y + 10, w, 50, it, k, size=11)
        if i < 2:
            d.arrow(441, y + 62, 441, y + 104, head=6, both=True, color="#667085")
    d.text(441, 296, "Reusable layers: change SAP once in its System API; every consumer above keeps working.",
           9.4, 400, MUTED, italic=True)
    return d


# =============================================================== MODULE 7
@diagram
def centralized_vs_mesh():
    d = Diagram(720, 290)
    d.frame(6, 14, 344, 268, "Centralized: one data team for everyone", "#B42318")
    for i, t in enumerate(["Sales", "Orders", "Payments", "Marketing"]):
        d.box(22 + i * 80, 40, 72, 34, t, "service", size=10)
        d.arrow(58 + i * 80, 76, 178, 128, head=5.5, color="#667085")
    d.box(108, 130, 140, 54, "Central data team", "bad", "queue of requests", size=11, sub_size=9)
    d.arrow(178, 186, 178, 216, head=6)
    d.box(98, 218, 160, 40, "Consumers wait…", "user", size=10.5)
    d.text(296, 160, "bottleneck", 9.6, 700, "#B42318")
    d.frame(370, 14, 344, 268, "Data mesh: domains own data products", "#2F7A4D")
    doms = [("Orders", "orders_daily"), ("Payments", "settlements"), ("Marketing", "campaign_kpis")]
    for i, (t, p) in enumerate(doms):
        x = 384 + i * 108
        d.box(x, 40, 100, 34, t, "service", size=10.5)
        d.box(x, 92, 100, 46, "data product", "good", p, size=9.6, sub_size=8.6)
        d.arrow(x + 50, 76, x + 50, 90, head=5)
        d.arrow(x + 50, 140, x + 50, 168, head=5)
    d.box(384, 170, 316, 36, "Consumers use products directly (self-service)", "user", size=10)
    d.box(384, 222, 316, 40, "Self-serve platform + federated governance", "navy", size=10.5)
    return d


@diagram
def data_mesh():
    d = Diagram(720, 340)
    d.rect(8, 10, 704, 44, "#13294B", "#13294B", 1, 6)
    d.text(360, 30, "Federated computational governance", 12, 700, "#FFFFFF")
    d.text(360, 46, "shared rules for security, privacy, quality, naming — enforced automatically by the platform",
           9.2, 400, "#C9D5E8")
    doms = [("Orders domain", "team: order engineering", "orders_daily", "SLA: by 6 AM, 99.9% complete"),
            ("Payments domain", "team: payments", "settlements", "PII masked, reconciled"),
            ("Marketing domain", "team: growth", "campaign_kpis", "refreshed hourly")]
    for i, (t, team, prod, sla) in enumerate(doms):
        x = 8 + i * 238
        d.rect(x, 72, 228, 168, "#FBFCFD", "#1F5FA8", 1.2, 8)
        d.text(x + 114, 94, t, 12, 700, "#13294B")
        d.text(x + 114, 110, team, 9, 400, MUTED)
        d.box(x + 14, 124, 200, 66, f"data product: {prod}", "good",
              "discoverable · addressable ·\ntrustworthy · self-describing", size=10, sub_size=8.6)
        d.text(x + 114, 212, sla, 9, 600, ACCENT)
        d.arrow(x + 114, 242, x + 114, 268, head=6, both=True, color="#667085")
    d.rect(8, 270, 704, 50, "#E7F6F3", "#0F766E", 1.2, 6)
    d.text(360, 291, "Self-serve data platform", 12, 700, "#0B4F4A")
    d.text(360, 308, "storage · pipelines · catalog · access control · monitoring — offered as easy, shared tools",
           9.2, 400, "#344054")
    d.text(360, 336, "The four principles: domain ownership · data as a product · self-serve platform · federated governance",
           9.2, 600, "#13294B")
    return d


@diagram
def serverless_flow():
    d = Diagram(720, 280)
    events = [("HTTP request", "via API gateway"), ("File uploaded", "to object storage"), ("Message arrives", "in a queue"),
              ("Schedule", "every day 1 AM")]
    for i, (t, s) in enumerate(events):
        d.box(8, 14 + i * 62, 150, 48, t, "user", s, size=10.8, sub_size=8.6)
        d.arrow(160, 38 + i * 62, 252, 128, head=6, color="#667085")
    d.rect(256, 60, 210, 140, "#FFF8E6", "#C27803", 1.4, 10)
    d.text(361, 86, "Function (FaaS)", 13, 700, "#7A4B02")
    d.text(361, 104, "AWS Lambda · Azure Functions", 9.2, 400, MUTED)
    d.text(361, 118, "Google Cloud Functions", 9.2, 400, MUTED)
    for k in range(4):
        d.rect(286 + k * 40, 134, 32, 30, "#FFE7B8", "#C27803", 1, 4)
        d.text(302 + k * 40, 154, "λ", 13, 700, "#7A4B02")
    d.text(361, 188, "0 → many copies, automatically", 9.2, 600, "#7A4B02")
    outs = [("Serverless database", "DynamoDB, Aurora Serverless"), ("Object storage", "thumbnails, reports"),
            ("Notifications", "email / SMS / queue")]
    for i, (t, s) in enumerate(outs):
        d.box(530, 34 + i * 70, 182, 52, t, "db" if i < 2 else "service", s, size=10.8, sub_size=8.6)
        d.arrow(468, 130, 528, 60 + i * 70, head=6, color="#667085")
    d.text(360, 262, "You write the function; the cloud runs, scales and bills it per request (no servers to manage).",
           9.6, 400, MUTED, italic=True)
    return d


@diagram
def ai_data_pipeline():
    d = Diagram(720, 300)
    steps = [("Collect", "apps, docs,\nlogs, sensors", "user"), ("Clean & validate", "dedupe, fix types,\nhandle nulls", "service"),
             ("Label / enrich", "add metadata,\nlabels, lineage", "amber"), ("Features /\nembeddings", "feature store,\nvector DB", "teal"),
             ("Train or\nretrieve (RAG)", "model training,\nLLM grounding", "analytics"), ("AI application", "predictions,\nanswers", "good")]
    for i, (t, s, k) in enumerate(steps):
        x = 8 + i * 120
        d.box(x, 40, 104, 104, t, k, s, size=11, sub_size=8.8)
        if i < 5:
            d.arrow(x + 106, 92, x + 118, 92, head=5.5)
    d.parrow([(668, 146), (668, 196), (52, 196), (52, 146)], label="monitor quality & drift → fix data → retrain",
             color=ACCENT, dash="5 4", head=6, lsize=9.6, lat=1, loff=(0, -1))
    d.rect(8, 226, 704, 52, "#F2F4F7", "#98A2B3", 1, 6)
    d.text(360, 247, "Foundation: data governance · metadata catalog · privacy (PII masking) · access control",
           10.5, 600, "#344054")
    d.text(360, 265, "\"Garbage in, garbage out\": model quality can never beat data quality.", 9.6, 400, MUTED,
           italic=True)
    return d


@diagram
def modern_data_stack():
    d = Diagram(720, 240)
    steps = [("Sources", "SaaS, DBs,\nevents", "user"), ("Ingestion", "Fivetran,\nAirbyte, Kafka", "queue"),
             ("Cloud warehouse\n/ lakehouse", "Snowflake, BigQuery,\nDatabricks", "analytics"),
             ("Transformation", "dbt (SQL\nmodels + tests)", "service"), ("BI & activation", "Power BI, Looker,\nreverse ETL", "good")]
    for i, (t, s, k) in enumerate(steps):
        x = 8 + i * 144
        d.box(x, 26, 128, 104, t, k, s, size=11, sub_size=8.8)
        if i < 4:
            d.arrow(x + 130, 78, x + 142, 78, head=5.5)
    d.rect(8, 152, 704, 34, "#13294B", "#13294B", 1, 6)
    d.text(360, 174, "Orchestration (Airflow / Dagster) · catalog & lineage · data observability · access control",
           10, 500, "#FFFFFF")
    d.text(360, 216, "Cloud-native, managed, pay-as-you-go pieces that each do one job well.", 9.6, 400, MUTED,
           italic=True)
    return d


# =============================================================== FINAL
@diagram
def project_architecture():
    d = Diagram(720, 420)
    d.box(10, 20, 170, 58, "React frontend", "client", "forms, tables, login page", size=11.5, sub_size=9)
    d.arrow(182, 49, 248, 49, "HTTPS + JSON\nBearer JWT", lsize=8.8, loff=(0, -16))
    d.frame(250, 14, 290, 252, "Spring Boot REST API", "#1F5FA8")
    layers = [("Controller", "REST endpoints, validation, status codes"), ("Service", "business rules, @Transactional"),
              ("Repository", "JPA / SQL queries")]
    for i, (t, s) in enumerate(layers):
        d.box(266, 38 + i * 74, 258, 56, t, "service", s, size=11.5, sub_size=9)
        if i < 2:
            d.arrow(395, 96 + i * 74, 395, 110 + i * 74, head=5.5)
    d.db(276, 300, 180, 92, "PostgreSQL", "db", "normalized tables, FKs,\nindexes, transactions", size=12, sub_size=9)
    d.arrow(395, 244, 366, 298, head=6)
    d.box(590, 30, 122, 56, "Redis cache", "queue", "hot product list", size=11, sub_size=9)
    d.arrow(526, 140, 588, 66, head=6, both=True, color="#667085")
    d.box(590, 120, 122, 64, "Payment API", "external", "timeouts, retries,\nidempotency key", size=11, sub_size=8.6)
    d.arrow(526, 150, 588, 152, head=6, both=True, color="#667085")
    d.box(590, 214, 122, 56, "Queue → email", "good", "async notifications", size=11, sub_size=9)
    d.arrow(526, 166, 588, 238, head=6, color="#667085")
    d.box(520, 330, 192, 62, "Nightly export / ETL", "analytics", "to a warehouse for reports", size=11, sub_size=9)
    d.arrow(458, 346, 518, 360, head=6, color="#667085")
    d.box(10, 120, 210, 112, "", "neutral")
    notes = ["Where each concept lives:", "SQL & joins → Repository", "Transactions → Service layer",
             "Indexes → PostgreSQL", "REST / JSON / status → Controller", "AuthN/AuthZ → JWT filter",
             "Integration → Payment API"]
    for i, n in enumerate(notes):
        d.text(22, 140 + i * 14.5, n, 9.4, 700 if i == 0 else 400, "#13294B" if i == 0 else "#344054", "start")
    return d


@diagram
def answer_framework():
    d = Diagram(720, 150)
    steps = [("1. Define", "one simple\nsentence", "navy"), ("2. Why", "problem it\nsolves", "service"),
             ("3. How", "how it works\n(briefly)", "service"), ("4. Example", "real or project\nexample", "good"),
             ("5. Trade-off", "limits / when\nnot to use", "amber")]
    for i, (t, s, k) in enumerate(steps):
        x = 8 + i * 144
        d.box(x, 20, 128, 84, t, k, s, size=12.5, sub_size=9.4)
        if i < 4:
            d.arrow(x + 130, 62, x + 142, 62, head=5.5)
    d.text(360, 134, "30–60 seconds. Stop after the trade-off and let the interviewer pick the next direction.", 9.8,
           400, MUTED, italic=True)
    return d
