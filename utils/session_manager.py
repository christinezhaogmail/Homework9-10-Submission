"""
Session Management Module
Handles session tracking, conversation history, and context management
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger


class SessionManager:
    """
    Manages research assistant sessions with conversation history and context.
    Each session has a unique ID and maintains dialogue history for follow-up questions.
    """

    def __init__(self, max_history: int = 10):
        """
        Initialize the session manager.

        Args:
            max_history: Maximum number of conversation turns to keep in history
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.max_history = max_history
        logger.info(f"SessionManager initialized (max_history={max_history})")

    def create_session(self) -> str:
        """
        Create a new session with unique ID.

        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "history": [],
            "query_count": 0,
            "metadata": {}
        }
        logger.info(f"Created new session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session dictionary or None if not found
        """
        return self.sessions.get(session_id)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to session history.

        Args:
            session_id: Session identifier
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata (function_call info, etc.)

        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        session["history"].append(message)
        session["updated_at"] = datetime.now().isoformat()

        if role == "user":
            session["query_count"] += 1

        # Trim history if it exceeds max_history
        if len(session["history"]) > self.max_history * 2:  # *2 for user+assistant pairs
            session["history"] = session["history"][-self.max_history * 2:]

        logger.debug(f"Added {role} message to session {session_id}")
        return True

    def get_conversation_history(
        self,
        session_id: str,
        last_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            last_n: Return only last N messages (None = all)

        Returns:
            List of message dictionaries
        """
        session = self.get_session(session_id)
        if not session:
            return []

        history = session["history"]
        if last_n:
            return history[-last_n:]
        return history

    def get_conversation_text(
        self,
        session_id: str,
        include_metadata: bool = False
    ) -> str:
        """
        Get conversation history as formatted text.

        Args:
            session_id: Session identifier
            include_metadata: Include message metadata in output

        Returns:
            Formatted conversation text
        """
        history = self.get_conversation_history(session_id)
        if not history:
            return ""

        lines = []
        for msg in history:
            role = msg["role"].title()
            content = msg["content"]
            timestamp = msg.get("timestamp", "")

            if include_metadata:
                lines.append(f"[{timestamp}] {role}: {content}")
                if msg.get("metadata"):
                    lines.append(f"  Metadata: {msg['metadata']}")
            else:
                lines.append(f"{role}: {content}")

        return "\n\n".join(lines)

    def update_metadata(
        self,
        session_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update session metadata.

        Args:
            session_id: Session identifier
            metadata: Metadata dictionary to merge

        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session["metadata"].update(metadata)
        session["updated_at"] = datetime.now().isoformat()
        return True

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def get_all_sessions(self) -> List[str]:
        """
        Get list of all session IDs.

        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary information for a session.

        Args:
            session_id: Session identifier

        Returns:
            Summary dictionary or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session["id"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "query_count": session["query_count"],
            "message_count": len(session["history"]),
            "metadata": session["metadata"]
        }


if __name__ == "__main__":
    # Test the session manager
    print("SessionManager Test")
    print("-" * 50)

    manager = SessionManager(max_history=5)

    # Create session
    session_id = manager.create_session()
    print(f"Created session: {session_id}")

    # Add messages
    manager.add_message(session_id, "user", "What is quantum entanglement?")
    manager.add_message(
        session_id,
        "assistant",
        "Quantum entanglement is a phenomenon...",
        metadata={"function_called": "search_arxiv"}
    )
    manager.add_message(session_id, "user", "Tell me more about the second paper")
    manager.add_message(session_id, "assistant", "The second paper discusses...")

    # Get history
    print("\nConversation History:")
    print("=" * 50)
    print(manager.get_conversation_text(session_id))

    # Get summary
    print("\nSession Summary:")
    print("=" * 50)
    summary = manager.get_session_summary(session_id)
    for key, value in summary.items():
        print(f"{key}: {value}")
