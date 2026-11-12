import uuid
from fastapi import HTTPException
from sqlalchemy import select,func
from src.models import ShiftReview,DistributionRun,DistributionStudy,ColorBatchDataset
from src.utils.serialization import serialize
from src.utils.time import now

def create(db,payload,user):
 run=db.get(DistributionRun,payload.run_id)
 if not run:raise HTTPException(404,'运行不存在')
 study=db.get(DistributionStudy,run.study_id)
 # Serialize with corrections and approvals on the source dataset row, then re-read state.
 db.scalar(select(ColorBatchDataset).where(ColorBatchDataset.id==study.dataset_id).with_for_update())
 db.expire_all()
 run=db.get(DistributionRun,payload.run_id);study=db.get(DistributionStudy,run.study_id);dataset=db.get(ColorBatchDataset,study.dataset_id)
 if run.status!='completed':raise HTTPException(409,'运行尚未成功完成，不能提审')
 if (run.dataset_version or 1)!=study.dataset_version or study.dataset_version!=(dataset.current_version or 1):
  raise HTTPException(409,'运行基于更正前的读数，已失效；请复核最新重算结果')
 version=(db.scalar(select(func.max(ShiftReview.version)).where(ShiftReview.run_id==payload.run_id)) or 0)+1
 item=ShiftReview(id=str(uuid.uuid4()),version=version,author=user['email'],dataset_version=run.dataset_version or 1,created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
