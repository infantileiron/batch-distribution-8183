from fastapi import APIRouter,Depends,HTTPException,Response
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import ShiftReview,ReviewInvalidation
from src.schemas.review import ReviewInput
from src.services import reviews as service
from src.utils.serialization import serialize
router=APIRouter(prefix='/reviews')
@router.get('')
def listing(db=Depends(db_session),user=Depends(current_user)):
 invalidations={row.review_id:serialize(row) for row in db.scalars(select(ReviewInvalidation))}
 result=[]
 for row in db.scalars(select(ShiftReview).order_by(ShiftReview.created_at.desc())):
  item=serialize(row);item['invalidated']=invalidations.get(row.id);result.append(item)
 return result
@router.post('')
def create(payload:ReviewInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload,user)
