from pathlib import Path
import redis,traceback
from sqlalchemy import select,update
from src.config.settings import REDIS_URL
from src.config.database import Session
from src.models import DistributionRun
from src.services.analysis import analyze
from src.services.runs import snapshot_for
client=redis.Redis.from_url(REDIS_URL);heartbeat=Path('/artifacts/worker-heartbeat')
def execute(id):
 with Session() as db:
  # Conditional claim: a correction may already have superseded this run.
  claimed=db.execute(update(DistributionRun).where(DistributionRun.id==id,DistributionRun.status.in_(['queued','running'])).values(status='running')).rowcount
  db.commit()
  if not claimed:return
  run=db.get(DistributionRun,id)
  try:
   result=analyze(snapshot_for(db,run))
   # Conditional completion: never overwrite superseded/failed with a stale result.
   finished=db.execute(update(DistributionRun).where(DistributionRun.id==id,DistributionRun.status=='running').values(result=result,status='completed',error='')).rowcount
   db.commit()
   if not finished:return
  except Exception as e:
   db.rollback()
   db.execute(update(DistributionRun).where(DistributionRun.id==id,DistributionRun.status=='running').values(status='failed',error=str(e)))
   db.commit();traceback.print_exc()
with Session() as db:
 for id in db.scalars(select(DistributionRun.id).where(DistributionRun.status.in_(['queued','running']))):client.lpush('batch-distribution:jobs',id)
while True:
 heartbeat.touch();job=client.brpop('batch-distribution:jobs',timeout=1)
 if job:execute(job[1].decode())
