from pathlib import Path
from PIL import Image
from ultralytics import YOLO
import re, os, psycopg2, torch, gc
from src.utils.config import DBConfig

def ensure_detection_table(cfg: DBConfig):
    conn = psycopg2.connect(host=cfg.host, port=cfg.port, dbname=cfg.db, user=cfg.user, password=cfg.pwd)
    cur = conn.cursor()
    cur.execute("create schema if not exists raw;")
    cur.execute("""
    create table if not exists raw.image_detections (
      id bigserial primary key,
      message_id bigint not null,
      class_name text not null,
      confidence double precision not null,
      image_path text not null,
      detected_at timestamp default now()
    );
    """)
    conn.commit()
    cur.close(); conn.close()

def enrich_latest_images(base_dir: str | Path = ".", include_channels=("CheMed123","lobelia4cosmetics"),
                         max_per_channel=None, imgsz=512, max_dim=1600, conf_thres=0.25) -> dict:
    cfg = DBConfig()
    ensure_detection_table(cfg)
    conn = psycopg2.connect(host=cfg.host, port=cfg.port, dbname=cfg.db, user=cfg.user, password=cfg.pwd)
    cur = conn.cursor()

    torch.set_num_threads(1)
    base = Path(base_dir)
    img_root = base / "data" / "raw" / "images"
    date_dirs = sorted([p for p in img_root.glob("*") if p.is_dir()])
    if not date_dirs:
        cur.close(); conn.close()
        return {"inserted": 0, "date": None}

    date_dir = date_dirs[-1]
    model = YOLO("yolov8n.pt")
    msg_id_re = re.compile(r"(\d+)(?:\.[A-Za-z0-9]+)?$")
    insert_sql = """
      insert into raw.image_detections (message_id, class_name, confidence, image_path)
      values (%s, %s, %s, %s)
    """

    def load_downscale(p: Path):
        im = Image.open(p).convert("RGB")
        w, h = im.size
        if max(w, h) > max_dim:
            im.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        return im

    total_rows = 0
    for ch_dir in sorted([p for p in date_dir.glob("*") if p.is_dir()]):
        ch = ch_dir.name
        if ch not in include_channels:
            continue
        imgs = [p for p in ch_dir.iterdir() if p.is_file()]
        if max_per_channel:
            imgs = imgs[:max_per_channel]
        for idx, img in enumerate(imgs, 1):
            m = msg_id_re.search(img.name)
            if not m:
                continue
            mid = int(m.group(1))
            try:
                im = load_downscale(img)
                res_list = model.predict(im, device="cpu", imgsz=imgsz, conf=conf_thres, verbose=False)
                if not res_list or not res_list[0].boxes or len(res_list[0].boxes) == 0:
                    continue
                names = res_list[0].names
                for b in res_list[0].boxes:
                    cls_idx = int(b.cls.item()); conf = float(b.conf.item())
                    cur.execute(insert_sql, (mid, names.get(cls_idx, str(cls_idx)), conf, str(img).replace("\\","/")))
                    total_rows += 1
                if idx % 50 == 0:
                    conn.commit()
            except Exception:
                pass
            finally:
                if "m" in locals(): del m
                gc.collect()

    conn.commit()
    cur.close(); conn.close()
    return {"inserted": total_rows, "date": date_dir.name}
