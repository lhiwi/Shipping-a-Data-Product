from dagster import op, get_dagster_logger
from ultralytics import YOLO
from pathlib import Path
from PIL import Image
import re, os, psycopg2, gc, torch
from dotenv import load_dotenv

@op
def run_yolo_enrichment():
    """CPU-safe YOLO on images for CheMed123 & lobelia4cosmetics; insert rows into raw.image_detections."""
    log = get_dagster_logger()
    load_dotenv(".env")

    BASE = Path(".")
    IMAGES_ROOT = BASE / "data" / "raw" / "images"
    date_dirs = sorted([p for p in IMAGES_ROOT.glob("*") if p.is_dir()])
    if not date_dirs:
        log.warning("No image date folders found.")
        return {"inserted": 0}
    date_dir = date_dirs[-1]
    CHANNELS_TO_INCLUDE = {"CheMed123", "lobelia4cosmetics"}

    MAX_PER_CHANNEL = None
    MAX_DIM = 1600
    IMGSZ = 512
    CONF_THRES = 0.25
    CPU_THREADS = 1
    torch.set_num_threads(CPU_THREADS)

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db   = os.getenv("POSTGRES_DB", "telegram_dw")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd  = os.getenv("POSTGRES_PASSWORD", "postgres")

    conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd)
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

    model = YOLO("yolov8n.pt")
    msg_id_re = re.compile(r"(\d+)(?:\.[A-Za-z0-9]+)?$")

    insert_sql = """
    insert into raw.image_detections (message_id, class_name, confidence, image_path)
    values (%s, %s, %s, %s)
    """

    def load_downscale(p: Path):
        im = Image.open(p).convert("RGB")
        w, h = im.size
        if max(w, h) > MAX_DIM:
            im.thumbnail((MAX_DIM, MAX_DIM), Image.Resampling.LANCZOS)
        return im

    total_rows = 0
    for ch_dir in sorted([p for p in date_dir.glob("*") if p.is_dir()]):
        ch_name = ch_dir.name
        if ch_name not in CHANNELS_TO_INCLUDE:
            continue
        images = [p for p in ch_dir.iterdir() if p.is_file()]
        if MAX_PER_CHANNEL:
            images = images[:MAX_PER_CHANNEL]
        log.info(f"YOLO: {ch_name} ({len(images)} images)")

        for idx, img_path in enumerate(images, 1):
            m = msg_id_re.search(img_path.name)
            if not m:
                continue
            message_id = int(m.group(1))
            try:
                im = load_downscale(img_path)
                res_list = model.predict(im, device="cpu", imgsz=IMGSZ, conf=CONF_THRES, verbose=False)
                if not res_list:
                    continue
                res = res_list[0]
                if not res or res.boxes is None or len(res.boxes) == 0:
                    continue
                names = res.names
                for b in res.boxes:
                    cls_idx = int(b.cls.item())
                    conf = float(b.conf.item())
                    class_name = names.get(cls_idx, str(cls_idx))
                    cur.execute(insert_sql, (message_id, class_name, conf, str(img_path).replace("\\", "/")))
                    total_rows += 1
                if idx % 50 == 0:
                    conn.commit()
                    log.info(f"{ch_name}: {idx}/{len(images)} images processed, rows={total_rows}")
            except Exception as e:
                log.warning(f"skip {img_path.name}: {e}")
            finally:
                if "m" in locals():
                    del m
                gc.collect()

    conn.commit()
    cur.close(); conn.close()
    log.info(f"YOLO inserted rows: {total_rows}")
    return {"inserted": total_rows, "date": date_dir.name}
