import asyncio
import os
from typing import Dict, Optional

# Dictionary to store active tasks by user_id
active_tasks: Dict[int, asyncio.Task] = {}

def add_task(user_id: int, task: asyncio.Task) -> None:
    """Add a task to tracking"""
    # Cancel existing task if any
    if user_id in active_tasks:
        old_task = active_tasks[user_id]
        if not old_task.done():
            old_task.cancel()
    
    active_tasks[user_id] = task

def cancel_task(user_id: int) -> bool:
    """Cancel task for user. Returns True if task was found and cancelled"""
    if user_id in active_tasks:
        task = active_tasks[user_id]
        if not task.done():
            task.cancel()
        del active_tasks[user_id]
        return True
    return False

def remove_task(user_id: int) -> None:
    """Remove completed task from tracking"""
    if user_id in active_tasks:
        del active_tasks[user_id]

def cleanup_temp_file(file_path: Optional[str]) -> None:
    """Clean up temporary file if exists"""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing temp file {file_path}: {e}")
