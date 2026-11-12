from fastapi import APIRouter,Depends
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer
from src.models import ColorBatchDataset
from src.schemas.dataset import DatasetInput,DatasetRevisionInput
from src.services import datasets as service
from src.utils.serialization import rows
router=APIRouter(prefix='/datasets')
@router.get('')
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(ColorBatchDataset).order_by(ColorBatchDataset.created_at.desc())))
@router.post('')
def create(payload:DatasetInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
@router.get('/{id}/revisions')
def history(id:str,db=Depends(db_session),user=Depends(current_user)):return service.history(db,id)
@router.post('/{id}/revisions')
def correct(id:str,payload:DatasetRevisionInput,db=Depends(db_session),user=Depends(writer)):return service.correct(db,id,payload,user)
