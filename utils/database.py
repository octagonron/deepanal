import os
import datetime
import json
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Get the database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create engine and base
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class AnalysisResult(Base):
    """Model for storing analysis results."""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50))
    entropy_value = Column(Float)
    meta_data = Column(Text)  # JSON string - renamed from 'metadata' which is reserved
    analysis_date = Column(DateTime, default=datetime.datetime.utcnow)
    thumbnail = Column(LargeBinary, nullable=True)  # For image files
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, filename='{self.filename}')>"

# Create tables
Base.metadata.create_all(engine)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Get a database session."""
    session = SessionLocal()
    try:
        return session
    except:
        session.close()
        raise

def save_analysis(filename, file_size, file_type, entropy_value, metadata, thumbnail=None):
    """Save analysis results to database."""
    try:
        session = get_db_session()
        analysis = AnalysisResult(
            filename=filename,
            file_size=file_size,
            file_type=file_type,
            entropy_value=entropy_value,
            meta_data=metadata,
            thumbnail=thumbnail
        )
        session.add(analysis)
        session.commit()
        return analysis.id
    except Exception as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()

def get_recent_analyses(limit=10):
    """Get recent analysis records."""
    session = get_db_session()
    try:
        results = session.query(AnalysisResult).order_by(
            AnalysisResult.analysis_date.desc()
        ).limit(limit).all()
        return results
    finally:
        session.close()

def get_analysis_by_id(analysis_id):
    """Get analysis by ID."""
    session = get_db_session()
    try:
        result = session.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        return result
    finally:
        session.close()