-- Stage raw.image_detections as typed columns
with src as (
  select * from raw.image_detections
)
select
  id                              as detection_id,
  message_id::bigint              as message_id,
  class_name::text                as class_name,
  confidence::double precision    as confidence,
  image_path::text                as image_path,
  detected_at::timestamp          as detected_at
from src
