"""
Phase 1 Configuration
Minimal settings for manual-first blog publishing workflow
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
 """Phase 1 Settings - minimal configuration"""

 # AI/LLM
 anthropic_api_key: str
 claude_model: str = "claude-3-5-sonnet-20241022"

 # Paths
 content_dir: Path = Path("content")
 posts_dir: Path = Path("posts")
 prompts_dir: Path = Path("prompts")

 # Local repos for 1P research (add your repo paths)
 local_repos: list[str] = [
 "../semops-core",
 # Add other repos as needed
 ]

 model_config = SettingsConfigDict(
 env_file=".env",
 env_file_encoding="utf-8",
 extra="ignore"
 )


# Global settings instance
settings = Settings
