from sqlalchemy import String,Integer,JSON
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ColorBatchDataset(Base):
 __tablename__='color_batch_datasets'
 id:Mapped[str]=mapped_column(String,primary_key=True)
 name:Mapped[str]=mapped_column(String,unique=True)
 source:Mapped[str]=mapped_column(String)
 batch_a:Mapped[list]=mapped_column(JSON)
 batch_b:Mapped[list]=mapped_column(JSON)
 current_version:Mapped[int]=mapped_column(Integer,default=1,server_default='1')
 created_at:Mapped[str]=mapped_column(String)
