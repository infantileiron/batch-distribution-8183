from sqlalchemy import String,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DatasetRevision(Base):
 __tablename__='dataset_revisions'
 __table_args__=(UniqueConstraint('dataset_id','version',name='uq_dataset_revision_version'),)
 id:Mapped[str]=mapped_column(String,primary_key=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey('color_batch_datasets.id'))
 version:Mapped[int]=mapped_column(Integer)
 note:Mapped[str]=mapped_column(Text)
 author:Mapped[str]=mapped_column(String)
 changes:Mapped[list]=mapped_column(JSON,default=list)
 batch_a:Mapped[list]=mapped_column(JSON)
 batch_b:Mapped[list]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String)
