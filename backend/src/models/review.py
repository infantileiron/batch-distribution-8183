from sqlalchemy import String,Integer,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ShiftReview(Base):
 __tablename__='shift_reviews'
 __table_args__=(UniqueConstraint('run_id','version',name='uq_shift_review_version'),)
 id:Mapped[str]=mapped_column(String,primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey('distribution_runs.id'))
 version:Mapped[int]=mapped_column(Integer)
 note:Mapped[str]=mapped_column(Text)
 decision:Mapped[str]=mapped_column(String)
 author:Mapped[str]=mapped_column(String)
 dataset_version:Mapped[int]=mapped_column(Integer,default=1,server_default='1')
 created_at:Mapped[str]=mapped_column(String)
