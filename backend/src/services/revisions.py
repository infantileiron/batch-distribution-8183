import uuid,redis
from fastapi import HTTPException
from sqlalchemy import select,func
from src.models import ColorBatchDataset,DistributionStudy,DatasetRevision,DistributionRun,ShiftReview,Report,ReviewInvalidation,RunSnapshot
from src.services.validation import validate_dataset
from src.services.runs import archived as study_is_archived
from src.utils.serialization import serialize
from src.utils.time import now
from src.config.settings import REDIS_URL

def revisions(db,dataset_id=None):
 query=select(DatasetRevision)
 if dataset_id is not None:query=query.where(DatasetRevision.dataset_id==dataset_id)
 result=[]
 for row in db.scalars(query.order_by(DatasetRevision.version.desc())):
  item=serialize(row);item.pop('batch_a',None);item.pop('batch_b',None);result.append(item)
 return result

def baseline(db,dataset):
 if db.scalar(select(DatasetRevision).where(DatasetRevision.dataset_id==dataset.id)):return
 db.add(DatasetRevision(id=str(uuid.uuid4()),dataset_id=dataset.id,version=1,note='批次导入基线',author='system',changes=[],batch_a=dataset.batch_a,batch_b=dataset.batch_b,created_at=dataset.created_at or now()))

def _log_reviews(db,runs,version):
 invalidated=[]
 if not runs:return invalidated
 run_ids=[run.id for run in runs]
 reviewed=db.scalars(select(ShiftReview).where(ShiftReview.run_id.in_(run_ids))).all()
 known=set(db.scalars(select(ReviewInvalidation.review_id).where(ReviewInvalidation.review_id.in_([review.id for review in reviewed])))) if reviewed else set()
 for review in reviewed:
  if review.id in known:continue
  db.add(ReviewInvalidation(review_id=review.id,dataset_version=version,reason='源读数更正至v'+str(version)+'，基于旧读数的复核失效；未归档研究已重算',created_at=now()))
  invalidated.append(review.id)
 return invalidated

def apply_correction(db,dataset_id,payload,user):
 # Lock the dataset row first so a concurrent approval serializes against this correction.
 dataset=db.scalar(select(ColorBatchDataset).where(ColorBatchDataset.id==dataset_id).with_for_update())
 if not dataset:raise HTTPException(404,'批次对照不存在')
 a=[dict(row) for row in dataset.batch_a];b=[dict(row) for row in dataset.batch_b]
 if len({change.sample_id for change in payload.changes})!=len(payload.changes):raise HTTPException(422,'同一次更正内的样本ID不可重复')
 locations={}
 for label,rows in (('A',a),('B',b)):
  for index,row in enumerate(rows):locations[row['sample_id']]=(label,index)
 changes=[]
 for change in payload.changes:
  location=locations.get(change.sample_id)
  if location is None:raise HTTPException(422,'样本ID '+change.sample_id+' 不在该批次对照中')
  label,index=location;target=a if label=='A' else b;row=target[index]
  before={key:row[key] for key in ('l','a','b')};after={'l':change.l,'a':change.a,'b':change.b}
  if before==after:continue
  target[index]={**row,**after}
  changes.append({'sample_id':change.sample_id,'batch':label,'before':before,'after':after})
 if not changes:raise HTTPException(422,'未检测到实际读数变化，未创建新版本')
 try:validate_dataset(a,b)
 except ValueError as error:raise HTTPException(422,str(error))
 baseline(db,dataset)
 latest=db.scalar(select(func.max(DatasetRevision.version)).where(DatasetRevision.dataset_id==dataset.id))
 version=latest+1
 dataset.batch_a=a;dataset.batch_b=b;dataset.current_version=version
 revision=DatasetRevision(id=str(uuid.uuid4()),dataset_id=dataset.id,version=version,note=payload.note,author=user['email'],changes=changes,batch_a=a,batch_b=b,created_at=now())
 db.add(revision)
 studies=db.scalars(select(DistributionStudy).where(DistributionStudy.dataset_id==dataset.id)).all()
 dataset_snapshot={key:getattr(dataset,key) for key in ('id','name','source','batch_a','batch_b','current_version','created_at')}
 invalidated=[];superseded=[];recalculated=[];archived_skipped=[];new_runs=[]
 for study in studies:
  if study_is_archived(db,study.id):
   # Approved studies keep their frozen readings, run and CSV untouched.
   archived_skipped.append(study.id);continue
  snapshot=dict(study.snapshot or {});snapshot['dataset']=dataset_snapshot;study.snapshot=snapshot;study.dataset_version=version
  runs=db.scalars(select(DistributionRun).where(DistributionRun.study_id==study.id)).all()
  for run in runs:
   if run.status in ('queued','running','completed'):
    run.status='superseded';superseded.append(run.id)
  invalidated.extend(_log_reviews(db,runs,version))
  run=DistributionRun(id=str(uuid.uuid4()),study_id=study.id,status='queued',result={},error='',dataset_version=version,created_at=now())
  db.add(run);db.add(RunSnapshot(run_id=run.id,snapshot=snapshot,created_at=now()));new_runs.append(run)
  recalculated.append({'study_id':study.id,'run_id':run.id,'dataset_version':version})
 db.commit()
 outcome={'recalculated':recalculated,'archived_studies_skipped':archived_skipped,'invalidated_reviews':invalidated,'superseded_runs':superseded}
 if new_runs:
  try:
   client=redis.Redis.from_url(REDIS_URL)
   for run in new_runs:client.lpush('batch-distribution:jobs',run.id)
  except redis.RedisError:
   for run in new_runs:
    stored=db.get(DistributionRun,run.id)
    if stored:stored.status='failed';stored.error='队列不可用，请重新运行该研究'
   db.commit()
   outcome['queue_error']='队列不可用，重算运行已标记失败，可在研究页重新运行'
 return {'revision':serialize(revision),'recompute':outcome}
