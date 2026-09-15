import os
import pandas as pd
from sqlalchemy import Column, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./complaints.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ComplaintDB(Base):
  __tablename__ = "complaints"

  id = Column(Integer, primary_key=True, index=True)
  description = Column(Text, nullable=True)
  category = Column(String, index=True)
  severity_score = Column(Float, default=5.0)
  severity_level = Column(String, default="Medium")
  image_path = Column(String, nullable=True)


def init_db():
  # Automatically delete old database to keep data fresh and multi-category
  if os.path.exists("./complaints.db"):
    os.remove("./complaints.db")

  Base.metadata.create_all(bind=engine)
  db = SessionLocal()

  csv_file = "civic_issues_with_severity-1 - Copy.csv"
  if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)

    # Sample across all categories evenly for a balanced chart
    df_sample = (
        df.groupby("category", group_keys=False)
        .apply(lambda x: x.sample(min(len(x), 40), random_state=42))
        .reset_index(drop=True)
    )

    for _, row in df_sample.iterrows():
      db_item = ComplaintDB(
          description="Preloaded dataset record for civic issue.",
          category=str(row["category"]),
          severity_score=float(row["severity_score"]),
          severity_level=str(row["severity_level"]),
          image_path=str(row.get("image_path", "")),
      )
      db.add(db_item)
    db.commit()
  db.close()


if __name__ == "__main__":
  init_db()
  print(
      "Database initialized successfully with diverse dataset categories!"
  )