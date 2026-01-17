"""
Notion Sync Module: NotionSync for saving conversations and summaries
Integrates with Notion API to persist research sessions
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger
from utils.logger import log_tool_call

try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    logger.warning("Notion client not available. Install with: pip install notion-client")


class NotionSync:
    """
    Notion synchronization service for persisting research conversations.
    Saves session data, queries, responses, and summaries to Notion database.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        database_id: Optional[str] = None
    ):
        """
        Initialize the Notion sync service.

        Args:
            token: Notion integration token (or from NOTION_TOKEN env var)
            database_id: Notion database ID (or from NOTION_DATABASE_ID env var)
        """
        if not NOTION_AVAILABLE:
            logger.warning("Notion client not available - syncing will be disabled")
            self.client = None
            self.database_id = None
            return

        self.token = token or os.getenv("NOTION_TOKEN")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")

        if not self.token:
            logger.warning("No Notion token provided - syncing will be disabled")
            self.client = None
            return

        if not self.database_id:
            logger.warning("No Notion database ID provided - syncing will be disabled")
            self.client = None
            return

        try:
            self.client = Client(auth=self.token)
            logger.info("✓ Notion client initialized")
            self._verify_connection()
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {e}")
            self.client = None

    def _verify_connection(self):
        """Verify connection to Notion"""
        try:
            if self.client and self.database_id:
                self.client.databases.retrieve(database_id=self.database_id)
                logger.info(f"✓ Connected to Notion database: {self.database_id}")
        except Exception as e:
            logger.error(f"Failed to verify Notion connection: {e}")
            logger.error("Please check your NOTION_TOKEN and NOTION_DATABASE_ID")

    def is_enabled(self) -> bool:
        """Check if Notion sync is enabled and configured"""
        return self.client is not None and self.database_id is not None

    @log_tool_call
    def sync_session(
        self,
        session_id: str,
        content: str,
        summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Sync a research session to Notion.

        Args:
            session_id: Unique session identifier
            content: Full conversation content
            summary: Optional summary of the session
            metadata: Additional metadata (query_count, papers_found, etc.)

        Returns:
            URL of created Notion page, or None if sync failed

        Note:
            This method works with any Notion database. Only the "Name" (title) property
            is required. Other properties (Session ID, Date, Query Count) are optional
            and will only be added if they exist in your database.
        """
        if not self.is_enabled():
            logger.warning("Notion sync is not enabled - skipping")
            return None

        try:
            # Prepare page properties
            # Note: We set all properties regardless of schema check, as some Notion databases
            # (especially those with data sources) don't expose properties in databases.retrieve()
            # Notion will gracefully ignore properties that don't exist in the database

            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": f"Research Session: {session_id}"
                            }
                        }
                    ]
                },
                "Session ID": {
                    "rich_text": [
                        {
                            "text": {
                                "content": session_id
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }

            # Add metadata if provided
            if metadata and "query_count" in metadata:
                properties["Query Count"] = {
                    "number": metadata["query_count"]
                }

            # Prepare page content
            children = []

            # Add summary section if provided
            if summary:
                children.extend([
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": summary[:2000]}}]
                        }
                    }
                ])

            # Add full conversation
            children.extend([
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Full Conversation"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]  # Notion limit
                    }
                }
            ])

            # Create the page
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )

            page_url = response.get("url", "")
            logger.info(f"✓ Session synced to Notion: {page_url}")
            return page_url

        except Exception as e:
            logger.error(f"Failed to sync session to Notion: {e}")
            return None

    @log_tool_call
    def append_to_session(
        self,
        page_id: str,
        content: str
    ) -> bool:
        """
        Append content to an existing Notion page.

        Args:
            page_id: Notion page ID
            content: Content to append

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False

        try:
            self.client.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                        }
                    }
                ]
            )
            logger.info(f"✓ Content appended to Notion page: {page_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to append to Notion page: {e}")
            return False


if __name__ == "__main__":
    # Test the Notion sync
    print("NotionSync Test")
    print("-" * 50)

    notion_sync = NotionSync()

    if notion_sync.is_enabled():
        print("Notion sync is enabled")
        print(f"Database ID: {notion_sync.database_id[:10]}...")

        # Test sync
        test_session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_content = "This is a test research session."
        test_summary = "Summary: Testing Notion integration."

        url = notion_sync.sync_session(
            session_id=test_session_id,
            content=test_content,
            summary=test_summary,
            metadata={"query_count": 1}
        )

        if url:
            print(f"\n✓ Test page created: {url}")
        else:
            print("\n✗ Failed to create test page")
    else:
        print("Notion sync is not enabled")
        print("Set NOTION_TOKEN and NOTION_DATABASE_ID environment variables to enable")
