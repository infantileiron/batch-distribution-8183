from sqlalchemy import String,Integer,JSON,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DistributionStudy(Base):
 __tablename__='distribution_studies'
 id:Mapped[str]=mapped_column(String,primary_key=True)
 name:Mapped[str]=mapped_column(String,unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey('color_batch_datasets.id'))
 policy_id:Mapped[str]=mapped_column(ForeignKey('kernel_policies.id'))
 snapshot:Mapped[dict]=mapped_column(JSON)
 dataset_version:Mapped[int]=mapped_column(Integer,default=1,server_default='1')
 created_at:Mapped[str]=mapped_column(String)
