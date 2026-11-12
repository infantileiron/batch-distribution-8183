from sqlalchemy import String,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DistributionRun(Base):
 __tablename__='distribution_runs'
 id:Mapped[str]=mapped_column(String,primary_key=True)
 study_id:Mapped[str]=mapped_column(ForeignKey('distribution_studies.id'))
 status:Mapped[str]=mapped_column(String)
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 error:Mapped[str]=mapped_column(Text,default='')
 dataset_version:Mapped[int]=mapped_column(Integer,default=1,server_default='1')
 created_at:Mapped[str]=mapped_column(String)
