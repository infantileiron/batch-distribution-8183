from sqlalchemy import String,Integer,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ReviewInvalidation(Base):
 __tablename__='review_invalidations'
 review_id:Mapped[str]=mapped_column(ForeignKey('shift_reviews.id'),primary_key=True)
 dataset_version:Mapped[int]=mapped_column(Integer)
 reason:Mapped[str]=mapped_column(Text)
 created_at:Mapped[str]=mapped_column(String)
