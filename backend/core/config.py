"""
Enhanced Configuration Management for FileGuard
Uses pydantic-settings for type-safe environment variable handling
"""
import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All values can be overridden via .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ==========================================
    # Application Settings
    # ==========================================
    app_name: str = Field(default="FileGuard", description="Application name")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    app_version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # ==========================================
    # Security Settings
    # ==========================================
    secret_key: str = Field(
        default="CHANGE_THIS_SECRET_KEY_IN_PRODUCTION",
        description="Secret key for JWT tokens - MUST be changed in production"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")

    # Password Policy
    min_password_length: int = Field(default=12, description="Minimum password length")
    require_special_chars: bool = Field(default=True, description="Require special characters in password")
    require_numbers: bool = Field(default=True, description="Require numbers in password")
    require_uppercase: bool = Field(default=True, description="Require uppercase letters in password")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Max requests per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Max requests per hour")

    # ==========================================
    # Database Settings
    # ==========================================
    postgres_server: str = Field(default="localhost", description="PostgreSQL server host")
    postgres_port: int = Field(default=5432, description="PostgreSQL server port")
    postgres_user: str = Field(default="fileguard", description="PostgreSQL username")
    postgres_password: str = Field(default="password", description="PostgreSQL password")
    postgres_db: str = Field(default="fileguard_db", description="PostgreSQL database name")

    # Connection Pool
    db_pool_size: int = Field(default=20, description="Database connection pool size")
    db_max_overflow: int = Field(default=10, description="Max overflow connections")
    db_pool_pre_ping: bool = Field(default=True, description="Enable connection health checks")

    # SQLAlchemy
    sqlalchemy_echo: bool = Field(default=False, description="Echo SQL queries (debug)")

    @property
    def database_url(self) -> str:
        """Construct database URL from components"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    # ==========================================
    # Redis Settings
    # ==========================================
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")

    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Celery
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend URL")

    @property
    def get_celery_broker_url(self) -> str:
        """Get Celery broker URL (defaults to Redis)"""
        return self.celery_broker_url or self.redis_url

    @property
    def get_celery_result_backend(self) -> str:
        """Get Celery result backend URL (defaults to Redis)"""
        return self.celery_result_backend or self.redis_url

    # ==========================================
    # Object Storage Settings (S3/MinIO)
    # ==========================================
    storage_backend: str = Field(default="minio", description="Storage backend: s3 or minio")

    # MinIO
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str = Field(default="minioadmin", description="MinIO access key")
    minio_secret_key: str = Field(default="minioadmin", description="MinIO secret key")
    minio_secure: bool = Field(default=False, description="Use HTTPS for MinIO")
    minio_bucket: str = Field(default="fileguard-files", description="MinIO bucket name")

    # AWS S3
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    aws_region: str = Field(default="us-east-1", description="AWS region")
    s3_bucket: str = Field(default="fileguard-files", description="S3 bucket name")
    s3_endpoint_url: Optional[str] = Field(default=None, description="Custom S3 endpoint URL")

    # ==========================================
    # ClamAV Antivirus
    # ==========================================
    clamav_enabled: bool = Field(default=True, description="Enable ClamAV antivirus scanning")
    clamav_host: str = Field(default="localhost", description="ClamAV host")
    clamav_port: int = Field(default=3310, description="ClamAV port")
    clamav_timeout: int = Field(default=120, description="ClamAV scan timeout in seconds")

    # ==========================================
    # CORS Settings
    # ==========================================
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS,PATCH", description="Allowed HTTP methods")
    cors_allow_headers: str = Field(default="*", description="Allowed headers")

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_methods_list(self) -> List[str]:
        """Convert CORS methods string to list"""
        return [method.strip() for method in self.cors_allow_methods.split(",")]

    # ==========================================
    # File Upload Settings
    # ==========================================
    max_file_size_mb: int = Field(default=500, description="Maximum file size in MB")
    max_chunk_size_mb: int = Field(default=10, description="Maximum chunk size in MB")
    allowed_extensions: str = Field(default="*", description="Allowed file extensions (comma-separated or *)")
    storage_path: str = Field(default="/var/lib/fileguard/storage", description="Local storage path")

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes"""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def max_chunk_size_bytes(self) -> int:
        """Convert max chunk size to bytes"""
        return self.max_chunk_size_mb * 1024 * 1024

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get list of allowed extensions"""
        if self.allowed_extensions == "*":
            return []  # Empty list means all extensions allowed
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]

    # ==========================================
    # Email Settings
    # ==========================================
    smtp_enabled: bool = Field(default=False, description="Enable SMTP email")
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_from_email: str = Field(default="noreply@fileguard.com", description="From email address")
    smtp_from_name: str = Field(default="FileGuard", description="From name")

    # ==========================================
    # Logging Settings
    # ==========================================
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_max_size_mb: int = Field(default=100, description="Max log file size in MB")
    log_backup_count: int = Field(default=10, description="Number of log file backups")

    # ==========================================
    # Monitoring Settings
    # ==========================================
    sentry_enabled: bool = Field(default=False, description="Enable Sentry error tracking")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    sentry_environment: Optional[str] = Field(default=None, description="Sentry environment")

    prometheus_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics endpoint port")

    # ==========================================
    # Feature Flags
    # ==========================================
    feature_file_versioning: bool = Field(default=True, description="Enable file versioning")
    feature_file_sharing: bool = Field(default=True, description="Enable file sharing")
    feature_real_time_notifications: bool = Field(default=True, description="Enable real-time notifications")
    feature_advanced_search: bool = Field(default=True, description="Enable advanced search")
    feature_analytics_dashboard: bool = Field(default=True, description="Enable analytics dashboard")
    feature_two_factor_auth: bool = Field(default=True, description="Enable 2FA")
    feature_bulk_operations: bool = Field(default=True, description="Enable bulk operations")

    # ==========================================
    # API Documentation
    # ==========================================
    enable_docs: bool = Field(default=True, description="Enable API documentation")
    docs_url: str = Field(default="/docs", description="Swagger UI URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")

    # ==========================================
    # Server Settings
    # ==========================================
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=4, description="Number of worker processes")

    @field_validator("app_env")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values"""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v.lower()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.app_env == "production"

    def model_post_init(self, __context) -> None:
        """Validate critical settings after initialization"""
        if self.is_production:
            # Security checks for production
            if self.secret_key == "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION":
                raise ValueError(
                    "SECRET_KEY must be changed in production! "
                    "Generate a secure key with: openssl rand -hex 32"
                )

            if self.debug:
                raise ValueError("DEBUG must be False in production")

            if self.postgres_password == "password":
                raise ValueError("Default database password detected in production!")


# Create global settings instance
settings = Settings()


# Export for backwards compatibility
DATABASE_URL = settings.database_url
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
