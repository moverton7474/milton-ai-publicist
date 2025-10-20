"""
Executive Input API - Module I
Provides endpoints for Milton to submit insights via voice, text, or email
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
import asyncio
from datetime import datetime
import whisper
import io
import uuid
import asyncpg
import os
from pathlib import Path

# Models
class ExecutiveInsight(BaseModel):
    """Model for Milton's raw insights"""
    insight_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_type: str  # "voice", "text", "email"
    raw_content: str
    transcription: Optional[str] = None
    metadata: dict = {}
    processed: bool = False
    priority: str = "medium"  # "low", "medium", "high", "urgent"

class InsightSubmission(BaseModel):
    """Request model for text insight submission"""
    content: str
    priority: str = "medium"
    source: str = "manual"

class VoiceTranscriber:
    """Whisper-based transcription for Milton's voice notes"""

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model = whisper.load_model(model_size)

    async def transcribe_audio(self, audio_file: bytes) -> str:
        """
        Transcribe audio to text using OpenAI Whisper

        Args:
            audio_file: Audio file bytes

        Returns:
            Transcribed text

        Raises:
            HTTPException: If transcription fails
        """
        try:
            # Save temporarily
            temp_path = f"/tmp/audio_{uuid.uuid4().hex}.mp3"
            with open(temp_path, 'wb') as f:
                f.write(audio_file)

            # Transcribe
            result = self.model.transcribe(temp_path)

            # Cleanup
            os.remove(temp_path)

            return result["text"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

class ExecutiveInputAPI:
    """
    FastAPI application for capturing executive insights
    """

    def __init__(self, db_url: str, jwt_secret: str):
        """
        Initialize the Executive Input API

        Args:
            db_url: PostgreSQL connection URL
            jwt_secret: Secret for JWT token validation
        """
        self.app = FastAPI(title="Milton Overton Executive Input API", version="1.0.0")
        self.db_url = db_url
        self.jwt_secret = jwt_secret
        self.security = HTTPBearer()
        self.transcriber = VoiceTranscriber()
        self.db_pool = None

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Configure API routes"""

        @self.app.on_event("startup")
        async def startup():
            """Initialize database connection pool"""
            self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)

        @self.app.on_event("shutdown")
        async def shutdown():
            """Close database connection pool"""
            if self.db_pool:
                await self.db_pool.close()

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "executive_input_api",
                "timestamp": datetime.utcnow().isoformat()
            }

        @self.app.post("/api/v1/voice-note", response_model=ExecutiveInsight)
        async def submit_voice_note(
            audio: UploadFile = File(...),
            priority: str = "medium",
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """
            Submit a voice note from Milton

            Process:
            1. Authenticate request
            2. Transcribe audio
            3. Store raw insight
            4. Queue for processing
            """
            # Authenticate
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            # Read audio
            audio_bytes = await audio.read()

            # Transcribe
            transcription = await self.transcriber.transcribe_audio(audio_bytes)

            # Create insight record
            insight = ExecutiveInsight(
                insight_id=self._generate_insight_id(),
                input_type="voice",
                raw_content=transcription,
                transcription=transcription,
                priority=priority,
                metadata={
                    "filename": audio.filename,
                    "content_type": audio.content_type,
                    "size_bytes": len(audio_bytes)
                }
            )

            # Store in database
            await self._store_insight(insight)

            # Queue for async processing
            await self._queue_insight_processing(insight.insight_id)

            return insight

        @self.app.post("/api/v1/text-insight", response_model=ExecutiveInsight)
        async def submit_text_insight(
            submission: InsightSubmission,
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """
            Submit a text-based insight (Slack message, quick note, etc.)
            """
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            insight = ExecutiveInsight(
                insight_id=self._generate_insight_id(),
                input_type="text",
                raw_content=submission.content,
                priority=submission.priority,
                metadata={"source": submission.source}
            )

            await self._store_insight(insight)
            await self._queue_insight_processing(insight.insight_id)

            return insight

        @self.app.get("/api/v1/insights")
        async def list_insights(
            limit: int = 20,
            processed: Optional[bool] = None,
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """List recent insights with optional filtering"""
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT insight_id, timestamp, input_type, raw_content,
                           priority, processed, created_at
                    FROM executive_insights
                """
                params = []

                if processed is not None:
                    query += " WHERE processed = $1"
                    params.append(processed)

                query += " ORDER BY timestamp DESC LIMIT $" + str(len(params) + 1)
                params.append(limit)

                rows = await conn.fetch(query, *params)

                return [dict(row) for row in rows]

    # Helper methods
    async def _validate_token(self, token: str) -> bool:
        """
        Validate JWT token for Milton's authorized devices

        Args:
            token: JWT token

        Returns:
            True if valid, False otherwise
        """
        # TODO: Implement proper JWT validation
        # For now, accept any non-empty token
        return bool(token)

    def _generate_insight_id(self) -> str:
        """Generate unique insight ID"""
        return f"INS-{uuid.uuid4().hex[:12].upper()}"

    async def _store_insight(self, insight: ExecutiveInsight):
        """
        Store insight in PostgreSQL

        Args:
            insight: ExecutiveInsight object
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO executive_insights (
                    insight_id, timestamp, input_type, raw_content,
                    transcription, metadata, processed, priority
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                insight.insight_id,
                insight.timestamp,
                insight.input_type,
                insight.raw_content,
                insight.transcription,
                insight.metadata,
                insight.processed,
                insight.priority
            )

    async def _queue_insight_processing(self, insight_id: str):
        """
        Queue insight for async processing by Module II

        Args:
            insight_id: ID of insight to process
        """
        # TODO: Implement Redis queue or Celery task
        # For now, just mark as queued in metadata
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE executive_insights
                SET processing_started_at = NOW()
                WHERE insight_id = $1
            """, insight_id)

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the API server

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


# Standalone execution
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv

    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    jwt_secret = os.getenv("SECRET_KEY", "dev-secret-key")

    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    api = ExecutiveInputAPI(db_url=db_url, jwt_secret=jwt_secret)
    api.run()
