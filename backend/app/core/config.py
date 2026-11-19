import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "FIXORA"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"

    # Optional Production Admin Bootstrap (Option A)
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None

    # Security & JWT Auth
    JWT_SECRET: str = "fixora_super_secret_jwt_key_2026_dev_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./fixora.db"

    # Cache & Queues (Redis - Optional)
    REDIS_URL: Optional[str] = None

    # Vector Knowledge Base (Qdrant - Optional remote, falls back to in-memory)
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # Graph Database (Neo4j - Optional)
    NEO4J_URI: Optional[str] = None
    NEO4J_USER: Optional[str] = None
    NEO4J_PASSWORD: Optional[str] = None

    # Sandbox Remote Worker (Optional isolated container worker provider)
    SANDBOX_WORKER_URL: Optional[str] = None
    SANDBOX_WORKER_TOKEN: Optional[str] = None

    # GitHub Integration
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: str = "fixora_default_github_webhook_secret"

    # AI & Reasoning Providers
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-latest"
    ANTHROPIC_API_KEY: Optional[str] = None

    # Sandbox
    DOCKER_MEMORY_LIMIT: str = "2048 MB"
    SANDBOX_TIMEOUT_SECONDS: int = 15

    # Deployment & Network
    PORT: int = int(os.getenv("PORT", "8000"))
    FRONTEND_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return ["*"]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production":
            # 1. JWT Secret Security Check
            if not self.JWT_SECRET or len(self.JWT_SECRET) < 32 or self.JWT_SECRET == "fixora_super_secret_jwt_key_2026_dev_prod":
                raise ValueError(
                    "Insecure or missing JWT_SECRET in production. Set a secure 32+ character random secret."
                )

            # 2. CORS Origins Security Check: restrict to explicit origins in production
            filtered_origins: List[str] = []
            for origin in self.CORS_ORIGINS:
                clean = origin.strip().rstrip("/")
                if clean == "*" or "localhost" in clean or "127.0.0.1" in clean:
                    continue
                if clean and clean not in filtered_origins:
                    filtered_origins.append(clean)

            if self.FRONTEND_URL:
                fe = self.FRONTEND_URL.strip().rstrip("/")
                if fe and fe not in filtered_origins:
                    filtered_origins.append(fe)

            if not filtered_origins:
                filtered_origins = ["https://fixora-ui.onrender.com"]

            self.CORS_ORIGINS = filtered_origins

            # 3. External Services localhost sanitization in production:
            # Prevent silent local fallback attempts to localhost on production Render hosts
            if self.QDRANT_URL and ("localhost" in self.QDRANT_URL or "127.0.0.1" in self.QDRANT_URL):
                self.QDRANT_URL = None

            if self.REDIS_URL and ("localhost" in self.REDIS_URL or "127.0.0.1" in self.REDIS_URL):
                self.REDIS_URL = None

            if self.NEO4J_URI and ("localhost" in self.NEO4J_URI or "127.0.0.1" in self.NEO4J_URI):
                self.NEO4J_URI = None

        return self

    model_config = SettingsConfigDict(
        env_file=(
            str(BACKEND_DIR / ".env"),
            str(ROOT_DIR / ".env"),
            ".env",
        ),
        extra="allow",
    )

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Returns non-sensitive configuration diagnostics."""
        has_env = (ROOT_DIR / ".env").exists() or (BACKEND_DIR / ".env").exists()
        from app.orchestrator.sandbox.runner import sandbox_runner
        sandbox_info = sandbox_runner.get_runtime_status()

        return {
            "envFileFound": has_env,
            "environment": self.ENVIRONMENT,
            "jwtSecretConfigured": bool(self.JWT_SECRET and len(self.JWT_SECRET) >= 32 and self.JWT_SECRET != "fixora_super_secret_jwt_key_2026_dev_prod"),
            "databaseType": "SQLite" if "sqlite" in self.DATABASE_URL.lower() else "PostgreSQL",
            "githubTokenConfigured": bool(self.GITHUB_TOKEN and len(self.GITHUB_TOKEN) > 5),
            "geminiConfigured": bool(self.GEMINI_API_KEY and len(self.GEMINI_API_KEY) > 5),
            "openaiConfigured": bool(self.OPENAI_API_KEY and len(self.OPENAI_API_KEY) > 5),
            "qdrantUrl": self.QDRANT_URL or "in-memory (fallback)",
            "redisUrl": self.REDIS_URL or "disabled (optional)",
            "neo4jUri": self.NEO4J_URI or "in-memory (fallback)",
            "sandboxMode": sandbox_info["mode"],
            "sandboxStatus": sandbox_info["status"],
            "sandboxTimeout": self.SANDBOX_TIMEOUT_SECONDS,
            "dockerMemoryLimit": self.DOCKER_MEMORY_LIMIT,
        }

    async def run_live_connectivity_checks(self) -> Dict[str, Any]:
        """Safely verifies live service connectivity without exposing secrets."""
        results: Dict[str, Any] = {}

        # 1. Environment file check
        env_root = (ROOT_DIR / ".env").exists()
        env_backend = (BACKEND_DIR / ".env").exists()
        results["environmentFile"] = {
            "status": "Configured and loaded" if (env_root or env_backend) else "Missing .env file",
            "rootLocation": str(ROOT_DIR / ".env") if env_root else None,
            "backendLocation": str(BACKEND_DIR / ".env") if env_backend else None,
        }

        # 2. JWT Cryptographic Security
        is_jwt_strong = bool(self.JWT_SECRET and len(self.JWT_SECRET) >= 32 and self.JWT_SECRET != "fixora_super_secret_jwt_key_2026_dev_prod")
        results["jwtAuthentication"] = {
            "status": "Configured and verified" if is_jwt_strong else "Using default development key (rotate for production)",
            "algorithm": self.ALGORITHM,
            "tokenExpiryMinutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "keyLengthChars": len(self.JWT_SECRET) if self.JWT_SECRET else 0,
        }

        # 3. Database connection
        try:
            from sqlalchemy import text
            from app.db.session import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            results["database"] = {
                "status": "Configured and connectivity tested",
                "dialect": "sqlite" if "sqlite" in self.DATABASE_URL.lower() else "postgresql",
                "connected": True,
            }
        except Exception as e:
            results["database"] = {
                "status": "Service unavailable",
                "error": str(e),
                "connected": False,
            }

        # 4. GitHub API Integration
        if self.GITHUB_TOKEN:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=5.0) as client:
                    gh_res = await client.get(
                        "https://api.github.com/user",
                        headers={"Authorization": f"Bearer {self.GITHUB_TOKEN}", "User-Agent": "FIXORA"}
                    )
                    if gh_res.status_code == 200:
                        login = gh_res.json().get("login")
                        results["github"] = {
                            "status": "Configured and connectivity tested",
                            "authenticatedAs": login,
                            "rateLimit": gh_res.headers.get("x-ratelimit-remaining"),
                        }
                    else:
                        results["github"] = {
                            "status": f"Invalid configuration: HTTP {gh_res.status_code}",
                            "detail": "Token was rejected by GitHub API",
                        }
            except Exception as e:
                results["github"] = {
                    "status": "Service unavailable",
                    "error": str(e),
                }
        else:
            results["github"] = {
                "status": "Missing user-provided credential",
                "variable": "GITHUB_TOKEN",
                "instructions": "Generate a GitHub Personal Access Token at https://github.com/settings/tokens (scopes: repo, read:org) and set GITHUB_TOKEN in .env",
            }

        # 5. AI Providers
        results["aiProviders"] = {}
        if self.GEMINI_API_KEY:
            results["aiProviders"]["gemini"] = {
                "status": "Configured (API key present)",
                "model": self.GEMINI_MODEL,
            }
        else:
            results["aiProviders"]["gemini"] = {
                "status": "Missing user-provided credential",
                "variable": "GEMINI_API_KEY",
                "instructions": "Obtain from https://aistudio.google.com/app/apikey",
            }

        if self.OPENAI_API_KEY:
            results["aiProviders"]["openai"] = {
                "status": "Configured (API key present)",
                "model": self.OPENAI_MODEL,
            }
        else:
            results["aiProviders"]["openai"] = {
                "status": "Missing user-provided credential",
                "variable": "OPENAI_API_KEY",
                "instructions": "Obtain from https://platform.openai.com/api-keys",
            }

        # 6. Qdrant Vector DB
        if self.QDRANT_URL and str(self.QDRANT_URL).strip():
            try:
                import httpx
                async with httpx.AsyncClient(timeout=1.5) as client:
                    q_res = await client.get(f"{self.QDRANT_URL}/collections")
                    if q_res.status_code == 200:
                        results["qdrant"] = {
                            "status": "Configured and connectivity tested",
                            "mode": "remote",
                            "url": self.QDRANT_URL,
                            "persistent": True,
                        }
                    else:
                        results["qdrant"] = {
                            "status": "Configured with in-memory fallback",
                            "mode": "in-memory (fallback active)",
                            "persistent": False,
                            "note": f"Remote Qdrant returned HTTP {q_res.status_code}; running in-memory fallback.",
                        }
            except Exception as e:
                results["qdrant"] = {
                    "status": "Configured with in-memory fallback",
                    "mode": "in-memory (fallback active)",
                    "persistent": False,
                    "note": f"Remote Qdrant unavailable ({str(e)}); in-memory vector store running smoothly.",
                }
        else:
            results["qdrant"] = {
                "status": "In-memory vector store active (fallback)",
                "mode": "in-memory (fallback active)",
                "persistent": False,
                "note": "QDRANT_URL not set; running ephemeral in-memory vector store.",
            }

        # 7. Redis Cache
        if self.REDIS_URL and str(self.REDIS_URL).strip():
            results["redis"] = {
                "status": "Configured",
                "url": self.REDIS_URL,
                "note": "Used for background job queuing.",
            }
        else:
            results["redis"] = {
                "status": "Not configured (optional background worker)",
                "url": None,
                "note": "Redis is optional; background tasks run in-process.",
            }

        # 8. Neo4j Graph DB
        if self.NEO4J_URI and str(self.NEO4J_URI).strip():
            try:
                from app.rag.graph_rag import graph_rag_service
                if graph_rag_service.is_remote:
                    results["neo4j"] = {
                        "status": "Configured and connectivity tested",
                        "mode": "remote",
                        "uri": self.NEO4J_URI,
                        "persistent": True,
                    }
                else:
                    results["neo4j"] = {
                        "status": "Configured with in-memory fallback",
                        "mode": "in-memory (fallback active)",
                        "persistent": False,
                        "note": "Remote Neo4j unreachable; running in-memory dependency topology.",
                    }
            except Exception as e:
                results["neo4j"] = {
                    "status": "Configured with in-memory fallback",
                    "mode": "in-memory (fallback active)",
                    "persistent": False,
                    "note": f"Neo4j connection error: {str(e)}",
                }
        else:
            results["neo4j"] = {
                "status": "In-memory topology active (fallback)",
                "mode": "in-memory (fallback active)",
                "persistent": False,
                "note": "NEO4J_URI not set; running in-memory dependency topology.",
            }

        # 9. Isolated Sandbox Runtime
        from app.orchestrator.sandbox.runner import sandbox_runner
        sandbox_info = sandbox_runner.get_runtime_status()
        results["dockerSandbox"] = {
            "status": sandbox_info["status"],
            "mode": sandbox_info["mode"],
            "runtime": sandbox_info["description"],
            "canExecuteUntrusted": sandbox_info["can_execute_untrusted_tests"],
            "isolated": sandbox_info["isolated"],
            "memoryLimit": self.DOCKER_MEMORY_LIMIT,
            "timeoutSeconds": self.SANDBOX_TIMEOUT_SECONDS,
        }

        return results

settings = Settings()
