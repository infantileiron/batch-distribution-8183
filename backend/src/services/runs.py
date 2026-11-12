import uuid,redis
from fastapi import HTTPException
from sqlalchemy import select
from src.models import DistributionRun,DistributionStudy,RunSnapshot,Report
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize

def create(db,study_id):
 study=db.get(DistributionStudy,study_id)
 if not study:raise HTTPException(404,"分布研究不存在")
 if archived(db,study_id):raise HTTPException(409,'研究已归档，冻结快照与CSV不再重跑；请新建研究应用新读数')
 item=DistributionRun(id=str(uuid.uuid4()),study_id=study_id,status='queued',result={},error='',dataset_version=study.dataset_version or 1,created_at=now());db.add(item);db.add(RunSnapshot(run_id=item.id,snapshot=study.snapshot,created_at=now()));db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush('batch-distribution:jobs',item.id)
 except redis.RedisError:
  item.status='failed';item.error='队列不可用，请重试';db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def archived(db,study_id):return db.scalar(select(Report.id).join(DistributionRun,DistributionRun.id==Report.run_id).where(DistributionRun.study_id==study_id)) is not None
def require_completed(db,id):
 item=db.get(DistributionRun,id)
 if not item:raise HTTPException(404,'运行不存在')
 if item.status=='superseded':raise HTTPException(409,'运行基于更正前的读数，已被重算替代')
 if item.status!='completed':raise HTTPException(409,'运行尚未成功完成')
 return item
def snapshot_for(db,run):
 stored=db.get(RunSnapshot,run.id)
 if stored:return stored.snapshot
 return db.get(DistributionStudy,run.study_id).snapshot
