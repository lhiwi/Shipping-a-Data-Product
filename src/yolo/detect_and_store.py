import os
from pathlib import Path
from loguru import logger
from ultralytics import YOLO
from sqlalchemy import text
from api.database import engine

RAW_SCHEMA = os.getenv("DBT_RAW_SCHEMA", "raw")
IMAGES_DIR = Path("data/raw/images")

DDL = f"""create table if not exists {RAW_SCHEMA}.image_detections (
  id bigserial primary key,
  message_id bigint,
  detected_object_class text,
  confidence_score double precision
);
"""

INSERT = text(
    f"""    insert into {RAW_SCHEMA}.image_detections
    (message_id, detected_object_class, confidence_score)
    values (:message_id, :cls, :conf)
    """
)

def run_yolo():
    with engine.begin() as conn:
        conn.exec_driver_sql(DDL)
    if not IMAGES_DIR.exists():
        logger.warning(f"No images dir {IMAGES_DIR}")
        return

    model = YOLO("yolov8n.pt")
    for img in IMAGES_DIR.rglob("*.jpg"):
        res = model(img)
        for r in res:
            boxes = r.boxes
            for b in boxes:
                cls_id = int(b.cls[0].item())
                conf = float(b.conf[0].item())
                # TODO: map filename to message_id via image_path in raw table
                with engine.begin() as conn:
                    conn.execute(INSERT, {
                        "message_id": None,
                        "cls": str(cls_id),
                        "conf": conf
                    })
        logger.info(f"Processed {img}")

if __name__ == "__main__":
    run_yolo()