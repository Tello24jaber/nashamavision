"""
Application Configuration Module
Handles all environment variables and application settings using Pydantic v2
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="Nashama Vision", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # Database - Support both connection URL and individual parameters
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    # Supabase / PostgreSQL individual connection parameters
    db_host: Optional[str] = Field(default=None, alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="postgres", alias="DB_NAME")
    db_user: Optional[str] = Field(default=None, alias="DB_USER")
    db_password: Optional[str] = Field(default=None, alias="DB_PASSWORD")
    
    # Supabase Configuration
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_bucket_name: str = Field(default="videos", alias="SUPABASE_BUCKET_NAME")
    
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    
    def get_database_url(self) -> str:
        """Build database URL from individual parameters if DATABASE_URL not provided"""
        if self.database_url:
            return self.database_url
        
        if not all([self.db_host, self.db_user, self.db_password]):
            return "postgresql://user:password@localhost:5432/nashama_vision"
        
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        alias="CELERY_RESULT_BACKEND"
    )
    
    # Object Storage
    storage_type: str = Field(default="local", alias="STORAGE_TYPE")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    s3_bucket_name: str = Field(default="nashama-vision-storage", alias="S3_BUCKET_NAME")
    s3_endpoint_url: Optional[str] = Field(default=None, alias="S3_ENDPOINT_URL")
    local_storage_path: str = Field(default="./storage", alias="LOCAL_STORAGE_PATH")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="ALLOWED_ORIGINS"
    )
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # File Upload
    max_upload_size: int = Field(default=5368709120, alias="MAX_UPLOAD_SIZE")  # 5GB
    allowed_video_extensions: List[str] = Field(
        default=[".mp4", ".avi", ".mov", ".mkv"],
        alias="ALLOWED_VIDEO_EXTENSIONS"
    )
    min_video_duration: int = Field(default=10, alias="MIN_VIDEO_DURATION")  # Lowered for testing
    max_video_duration: int = Field(default=7200, alias="MAX_VIDEO_DURATION")
    
    @field_validator("allowed_video_extensions", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    # Computer Vision
    yolo_model_path: str = Field(default="./models/yolov8x.pt", alias="YOLO_MODEL_PATH")
    yolo_confidence_threshold: float = Field(default=0.5, alias="YOLO_CONFIDENCE_THRESHOLD")
    yolo_iou_threshold: float = Field(default=0.45, alias="YOLO_IOU_THRESHOLD")
    tracking_method: str = Field(default="deepsort", alias="TRACKING_METHOD")
    deepsort_model_path: str = Field(default="./models/deepsort.pb", alias="DEEPSORT_MODEL_PATH")
    max_age: int = Field(default=30, alias="MAX_AGE")
    min_hits: int = Field(default=3, alias="MIN_HITS")
    
    # Video Processing
    frame_extraction_fps: int = Field(default=25, alias="FRAME_EXTRACTION_FPS")
    video_codec: str = Field(default="libx264", alias="VIDEO_CODEC")
    video_crf: int = Field(default=23, alias="VIDEO_CRF")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", alias="LOG_FILE")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
