from sqlalchemy import String,JSON,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class RunSnapshot(Base):
 __tablename__='run_snapshots'
 run_id:Mapped[str]=mapped_column(ForeignKey('distribution_runs.id'),primary_key=True)
 snapshot:Mapped[dict]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String)
