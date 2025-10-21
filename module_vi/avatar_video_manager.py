"""
Avatar Video Manager Module
Handles HeyGen video generation via Zapier integration
"""

import requests
import sqlite3
import os
from datetime import datetime
from typing import Dict, Optional, List
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AvatarVideoManager:
    """Manages avatar video generation and tracking"""
    
    def __init__(self, db_path='milton_publicist.db'):
        self.db_path = db_path
        self.zapier_webhook_url = os.getenv('ZAPIER_HEYGEN_WEBHOOK_URL')
        self.callback_base_url = os.getenv('DASHBOARD_BASE_URL', 'http://localhost:8080')
        self.heygen_avatar_id = os.getenv('HEYGEN_AVATAR_ID')
        self.heygen_voice_id = os.getenv('HEYGEN_VOICE_ID', '')
        
    def _get_connection(self):
        """Get thread-safe database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_video_record(
        self,
        user_id: str,
        script: str,
        scenario: str,
        voice_type: str,
        context: str = '',
        dimensions: str = 'square',
        post_id: Optional[int] = None,
        platform: str = 'linkedin'
    ) -> int:
        """Create a new avatar video record in database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO avatar_videos (
                    user_id, post_id, script, scenario, voice_type,
                    context, dimensions, avatar_id, voice_id, platform, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'generating')
            ''', (
                user_id, post_id, script, scenario, voice_type,
                context, dimensions, self.heygen_avatar_id,
                self.heygen_voice_id, platform
            ))

            video_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created avatar video record: {video_id}")
            return video_id

        except Exception as e:
            logger.error(f"Error creating video record: {e}")
            raise
        finally:
            conn.close()

    def trigger_zapier_workflow(
        self,
        video_id: int,
        script: str,
        scenario: str,
        voice_type: str,
        dimensions: str = 'square',
        platform: str = 'linkedin'
    ) -> Dict:
        """Trigger Zapier webhook to generate video via HeyGen"""
        if not self.zapier_webhook_url:
            raise ValueError("ZAPIER_HEYGEN_WEBHOOK_URL not configured")

        vibe_mapping = {
            'personal': 'warm and authentic',
            'professional': 'professional and authoritative'
        }

        dimension_mapping = {
            'square': 'square_1080x1080',
            'vertical': 'vertical_1080x1920',
            'horizontal': 'horizontal_1920x1080'
        }

        payload = {
            'video_record_id': video_id,
            'script': script,
            'topic': f"KSU Athletics - {scenario}",
            'vibe': vibe_mapping.get(voice_type, 'professional'),
            'targetAudience': 'College athletics fans, recruits, partners',
            'platform': platform,
            'avatar_id': self.heygen_avatar_id,
            'voice_id': self.heygen_voice_id,
            'dimensions': dimension_mapping.get(dimensions, 'square_1080x1080'),
            'callback_url': f"{self.callback_base_url}/api/avatar-video-complete"
        }

        try:
            logger.info(f"Triggering Zapier workflow for video {video_id}")
            response = requests.post(
                self.zapier_webhook_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Zapier workflow triggered successfully for video {video_id}")
            return response.json() if response.text else {'status': 'triggered'}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error triggering Zapier workflow: {e}")
            self.update_video_status(
                video_id=video_id,
                status='failed',
                error_message=f"Zapier trigger failed: {str(e)}"
            )
            raise

    def update_video_status(
        self,
        video_id: int,
        status: str,
        heygen_video_id: Optional[str] = None,
        heygen_job_id: Optional[str] = None,
        video_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Update video record status and metadata"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            updates = ['status = ?']
            params = [status]

            if heygen_video_id:
                updates.append('heygen_video_id = ?')
                params.append(heygen_video_id)
            if heygen_job_id:
                updates.append('heygen_job_id = ?')
                params.append(heygen_job_id)
            if video_url:
                updates.append('video_url = ?')
                params.append(video_url)
            if thumbnail_url:
                updates.append('thumbnail_url = ?')
                params.append(thumbnail_url)
            if duration_seconds:
                updates.append('duration_seconds = ?')
                params.append(duration_seconds)
            if error_message:
                updates.append('error_message = ?')
                params.append(error_message)

            if status == 'ready':
                updates.append('completed_at = ?')
                params.append(datetime.now().isoformat())

                cursor.execute('SELECT created_at FROM avatar_videos WHERE id = ?', (video_id,))
                result = cursor.fetchone()
                if result:
                    created_at = datetime.fromisoformat(result[0])
                    generation_time = int((datetime.now() - created_at).total_seconds())
                    updates.append('generation_time_seconds = ?')
                    params.append(generation_time)

            params.append(video_id)
            query = f"UPDATE avatar_videos SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            logger.info(f"Updated video {video_id} status to {status}")

        except Exception as e:
            logger.error(f"Error updating video status: {e}")
            raise
        finally:
            conn.close()

    def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        """Get video record by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM avatar_videos WHERE id = ?', (video_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_videos_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get all videos for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if status:
                cursor.execute('''
                    SELECT * FROM avatar_videos
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (user_id, status, limit))
            else:
                cursor.execute('''
                    SELECT * FROM avatar_videos
                    WHERE user_id = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (user_id, limit))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_video_statistics(self, user_id: str) -> Dict:
        """Get aggregate statistics for user's avatar videos"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT
                    COUNT(*) as total_videos,
                    SUM(CASE WHEN status = 'ready' THEN 1 ELSE 0 END) as completed_videos,
                    SUM(CASE WHEN status = 'generating' OR status = 'processing' THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_videos,
                    AVG(generation_time_seconds) as avg_generation_time,
                    SUM(views) as total_views,
                    AVG(engagement_rate) as avg_engagement_rate
                FROM avatar_videos
                WHERE user_id = ?
            ''', (user_id,))

            row = cursor.fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

# Singleton instance
avatar_video_manager = AvatarVideoManager()
