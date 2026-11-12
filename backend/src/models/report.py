from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Report(Base):
 __tablename__='reports'
 id:Mapped[str]=mapped_column(String,primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey('distribution_runs.id'))
 review_id:Mapped[str]=mapped_column(ForeignKey('shift_reviews.id'),unique=True)
 title:Mapped[str]=mapped_column(String)
 published_by:Mapped[str]=mapped_column(String)
 dataset_version:Mapped[int]=mapped_column(Integer,default=1,server_default='1')
 created_at:Mapped[str]=mapped_column(String)
