"""
Approval Dashboard - FastAPI Backend with WebSocket
Real-time content approval interface for Milton
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Set
import asyncpg
import json
from datetime import datetime
import os
from pathlib import Path


# Models
class ContentApproval(BaseModel):
    """Content approval/rejection model"""
    content_id: int
    action: str  # "approve", "reject", "edit"
    rejection_reason: Optional[str] = None
    edited_content: Optional[str] = None
    notes: Optional[str] = None


class ContentItem(BaseModel):
    """Content item for approval queue"""
    content_id: int
    platform: str
    content_type: str
    content: str
    opportunity_type: str
    urgency: str
    pillar_alignment: List[str]

    # QA scores
    overall_qa_score: float
    voice_authenticity_score: float
    brand_alignment_score: float
    engagement_prediction_score: float

    # Metadata
    hashtags: List[str]
    visual_suggestions: Dict
    optimal_post_time: str
    created_at: str

    # Context
    original_insight: Optional[str]
    related_article_title: Optional[str]
    related_article_url: Optional[str]


class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[Dashboard] WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        print(f"[Dashboard] WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[Dashboard] Error broadcasting to client: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


class ApprovalDashboard:
    """
    FastAPI application for content approval dashboard

    Features:
    - Real-time content queue via WebSocket
    - Quick approve/reject/edit actions
    - Content preview with QA scores
    - Mobile-responsive UI
    """

    def __init__(self, db_url: str, jwt_secret: str, host: str = "0.0.0.0", port: int = 8080):
        """
        Initialize Approval Dashboard

        Args:
            db_url: PostgreSQL connection URL
            jwt_secret: Secret for JWT validation
            host: Host to bind to
            port: Port to bind to
        """
        self.app = FastAPI(
            title="Milton Overton AI Publicist - Approval Dashboard",
            version="1.0.0"
        )
        self.db_url = db_url
        self.jwt_secret = jwt_secret
        self.host = host
        self.port = port
        self.db_pool = None
        self.security = HTTPBearer()
        self.ws_manager = WebSocketManager()

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Configure API routes"""

        @self.app.on_event("startup")
        async def startup():
            """Initialize database connection pool"""
            self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)
            print(f"[Dashboard] Started on http://{self.host}:{self.port}")

        @self.app.on_event("shutdown")
        async def shutdown():
            """Close database connection pool"""
            if self.db_pool:
                await self.db_pool.close()

        @self.app.get("/")
        async def root():
            """Serve dashboard UI"""
            return FileResponse(str(Path(__file__).parent / "dashboard.html"))

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "approval_dashboard",
                "timestamp": datetime.utcnow().isoformat()
            }

        @self.app.get("/api/approval-queue", response_model=List[ContentItem])
        async def get_approval_queue(
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """
            Get all pending content for approval

            Returns items sorted by:
            1. Urgency (immediate > today > this_week > standard)
            2. QA score (highest first)
            3. Created date (oldest first)
            """
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        gc.content_id,
                        gc.platform,
                        gc.content_type,
                        gc.content,
                        gc.overall_qa_score,
                        gc.voice_authenticity_score,
                        gc.brand_alignment_score,
                        gc.engagement_prediction_score,
                        gc.hashtags,
                        gc.visual_suggestions,
                        gc.optimal_post_time,
                        gc.created_at,
                        co.type AS opportunity_type,
                        co.urgency,
                        co.pillar_alignment,
                        ei.raw_content AS original_insight,
                        na.title AS related_article_title,
                        na.url AS related_article_url
                    FROM generated_content gc
                    LEFT JOIN content_opportunities co ON gc.opportunity_id = co.opportunity_id
                    LEFT JOIN executive_insights ei ON co.insight_id = ei.insight_id
                    LEFT JOIN news_articles na ON co.article_id = na.article_id
                    WHERE gc.status = 'pending_approval'
                    ORDER BY
                        CASE co.urgency
                            WHEN 'immediate' THEN 1
                            WHEN 'today' THEN 2
                            WHEN 'this_week' THEN 3
                            ELSE 4
                        END,
                        gc.overall_qa_score DESC,
                        gc.created_at ASC
                """)

                items = []
                for row in rows:
                    items.append(ContentItem(
                        content_id=row['content_id'],
                        platform=row['platform'],
                        content_type=row['content_type'],
                        content=row['content'],
                        opportunity_type=row['opportunity_type'] or 'general',
                        urgency=row['urgency'] or 'standard',
                        pillar_alignment=row['pillar_alignment'] or [],
                        overall_qa_score=float(row['overall_qa_score'] or 0.0),
                        voice_authenticity_score=float(row['voice_authenticity_score'] or 0.0),
                        brand_alignment_score=float(row['brand_alignment_score'] or 0.0),
                        engagement_prediction_score=float(row['engagement_prediction_score'] or 0.0),
                        hashtags=row['hashtags'] or [],
                        visual_suggestions=json.loads(row['visual_suggestions']) if row['visual_suggestions'] else {},
                        optimal_post_time=row['optimal_post_time'].isoformat() if row['optimal_post_time'] else '',
                        created_at=row['created_at'].isoformat(),
                        original_insight=row['original_insight'],
                        related_article_title=row['related_article_title'],
                        related_article_url=row['related_article_url']
                    ))

                return items

        @self.app.post("/api/approve/{content_id}")
        async def approve_content(
            content_id: int,
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """Approve content for publishing"""
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            async with self.db_pool.acquire() as conn:
                # Update status
                updated = await conn.execute("""
                    UPDATE generated_content
                    SET status = 'approved',
                        updated_at = NOW()
                    WHERE content_id = $1
                    AND status = 'pending_approval'
                """, content_id)

                if updated == "UPDATE 0":
                    raise HTTPException(status_code=404, detail="Content not found or already processed")

                print(f"[Dashboard] Content {content_id} APPROVED")

                # Broadcast update to connected clients
                await self.ws_manager.broadcast({
                    "type": "content_approved",
                    "content_id": content_id,
                    "timestamp": datetime.utcnow().isoformat()
                })

                return {"status": "approved", "content_id": content_id}

        @self.app.post("/api/reject/{content_id}")
        async def reject_content(
            content_id: int,
            approval: ContentApproval,
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """Reject content with reason"""
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            if not approval.rejection_reason:
                raise HTTPException(status_code=400, detail="Rejection reason required")

            async with self.db_pool.acquire() as conn:
                updated = await conn.execute("""
                    UPDATE generated_content
                    SET status = 'rejected',
                        rejection_reason = $2,
                        updated_at = NOW()
                    WHERE content_id = $1
                    AND status = 'pending_approval'
                """, content_id, approval.rejection_reason)

                if updated == "UPDATE 0":
                    raise HTTPException(status_code=404, detail="Content not found or already processed")

                print(f"[Dashboard] Content {content_id} REJECTED: {approval.rejection_reason}")

                # Broadcast update
                await self.ws_manager.broadcast({
                    "type": "content_rejected",
                    "content_id": content_id,
                    "reason": approval.rejection_reason,
                    "timestamp": datetime.utcnow().isoformat()
                })

                return {"status": "rejected", "content_id": content_id, "reason": approval.rejection_reason}

        @self.app.post("/api/edit/{content_id}")
        async def edit_content(
            content_id: int,
            approval: ContentApproval,
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """Edit content and auto-approve"""
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            if not approval.edited_content:
                raise HTTPException(status_code=400, detail="Edited content required")

            async with self.db_pool.acquire() as conn:
                updated = await conn.execute("""
                    UPDATE generated_content
                    SET content = $2,
                        status = 'approved',
                        updated_at = NOW()
                    WHERE content_id = $1
                    AND status = 'pending_approval'
                """, content_id, approval.edited_content)

                if updated == "UPDATE 0":
                    raise HTTPException(status_code=404, detail="Content not found or already processed")

                print(f"[Dashboard] Content {content_id} EDITED and APPROVED")

                # Broadcast update
                await self.ws_manager.broadcast({
                    "type": "content_edited",
                    "content_id": content_id,
                    "timestamp": datetime.utcnow().isoformat()
                })

                return {"status": "edited_and_approved", "content_id": content_id}

        @self.app.get("/api/stats")
        async def get_dashboard_stats(
            credentials: HTTPAuthorizationCredentials = Security(self.security)
        ):
            """Get dashboard statistics"""
            if not await self._validate_token(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid authentication")

            async with self.db_pool.acquire() as conn:
                stats = await conn.fetchrow("""
                    SELECT
                        COUNT(*) FILTER (WHERE status = 'pending_approval') as pending,
                        COUNT(*) FILTER (WHERE status = 'approved') as approved,
                        COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
                        AVG(overall_qa_score) FILTER (WHERE status = 'pending_approval') as avg_qa_score
                    FROM generated_content
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                """)

                return {
                    "pending": stats['pending'] or 0,
                    "approved_this_week": stats['approved'] or 0,
                    "rejected_this_week": stats['rejected'] or 0,
                    "avg_qa_score": round(float(stats['avg_qa_score'] or 0.0), 2)
                }

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self.ws_manager.connect(websocket)

            try:
                while True:
                    # Keep connection alive and listen for client messages
                    data = await websocket.receive_text()

                    # Echo back (for heartbeat)
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            except WebSocketDisconnect:
                self.ws_manager.disconnect(websocket)
            except Exception as e:
                print(f"[Dashboard] WebSocket error: {e}")
                self.ws_manager.disconnect(websocket)

    async def _validate_token(self, token: str) -> bool:
        """Validate JWT token"""
        # TODO: Implement proper JWT validation
        # For now, accept any non-empty token
        return bool(token)

    def run(self):
        """Run the dashboard server"""
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)


# Standalone execution
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    jwt_secret = os.getenv("SECRET_KEY", "dev-secret-key")
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    port = int(os.getenv("DASHBOARD_PORT", "8080"))

    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        exit(1)

    dashboard = ApprovalDashboard(
        db_url=db_url,
        jwt_secret=jwt_secret,
        host=host,
        port=port
    )

    dashboard.run()
