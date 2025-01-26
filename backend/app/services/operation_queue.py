import asyncio
import logging
from typing import Dict, Optional
from uuid import uuid4

from ..models.operations import Operation, OperationStatus, OperationPriority
from ..models.errors import ExecutionError
from ..websockets.operations import manager as websocket_manager
from .retry_handler import RetryHandler

logger = logging.getLogger(__name__)

class OperationQueue:
    def __init__(self, max_workers: int = 5):
        self.queues = {
            OperationPriority.HIGH: asyncio.Queue(),
            OperationPriority.NORMAL: asyncio.Queue(),
            OperationPriority.LOW: asyncio.Queue()
        }
        self.active_operations: Dict[str, Operation] = {}
        self.max_workers = max_workers
        self.workers: Dict[str, asyncio.Task] = {}
        self.running = False

    async def add_operation(self, operation: Operation) -> str:
        """Add a new operation to the appropriate priority queue"""
        if not operation.id:
            operation.id = str(uuid4())
        
        operation.status = OperationStatus.QUEUED
        await self.queues[operation.priority].put(operation)
        
        # Notify subscribers about the queued operation
        await websocket_manager.broadcast_status(
            operation.id,
            {
                "status": OperationStatus.QUEUED,
                "progress": 0
            }
        )
        
        logger.info(f"Operation {operation.id} queued with priority {operation.priority}")
        return operation.id

    async def get_operation_status(self, operation_id: str) -> Optional[Operation]:
        """Get the current status of an operation"""
        return self.active_operations.get(operation_id)

    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an operation if it's still queued or running"""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation.status = OperationStatus.CANCELLED
            
            # Notify subscribers about cancellation
            await websocket_manager.broadcast_status(
                operation_id,
                {
                    "status": OperationStatus.CANCELLED,
                    "progress": operation.progress
                }
            )
            
            logger.info(f"Operation {operation_id} cancelled")
            return True
        return False

    async def _process_queue(self, priority: OperationPriority):
        """Process operations from a specific priority queue"""
        queue = self.queues[priority]
        while self.running:
            try:
                operation = await queue.get()
                if operation.status == OperationStatus.CANCELLED:
                    queue.task_done()
                    continue

                self.active_operations[operation.id] = operation
                operation.status = OperationStatus.RUNNING
                
                # Notify subscribers that operation is running
                await websocket_manager.broadcast_status(
                    operation.id,
                    {
                        "status": OperationStatus.RUNNING,
                        "progress": operation.progress
                    }
                )

                try:
                    # Execute the operation
                    await self._execute_operation(operation)
                    
                    operation.status = OperationStatus.COMPLETED
                    await websocket_manager.broadcast_status(
                        operation.id,
                        {
                            "status": OperationStatus.COMPLETED,
                            "progress": 100,
                            "result": operation.result
                        }
                    )
                except Exception as e:
                    # Convert generic exceptions to ExecutionError
                    error = e if isinstance(e, ExecutionError) else ExecutionError(str(e))
                    
                    # Handle retry logic
                    await RetryHandler.handle_operation_failure(
                        operation,
                        error,
                        context={
                            "queue": priority.value,
                            "attempt": operation.metadata.get("retry_count", 0) + 1
                        }
                    )
                    
                    # Broadcast current status
                    await websocket_manager.broadcast_status(
                        operation.id,
                        {
                            "status": operation.status,
                            "error": operation.error,
                            "metadata": operation.metadata
                        }
                    )
                    
                    if operation.status == OperationStatus.FAILED:
                        logger.error(f"Operation {operation.id} failed: {operation.error}")
                finally:
                    if operation.status != OperationStatus.QUEUED:  # Don't remove if requeued for retry
                        del self.active_operations[operation.id]
                    queue.task_done()

            except Exception as e:
                logger.error(f"Error processing queue {priority}: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on persistent errors

    async def _execute_operation(self, operation: Operation):
        """Execute an operation with progress updates"""
        if operation.status == OperationStatus.CANCELLED:
            return

        total_steps = 5
        try:
            for step in range(total_steps):
                if operation.status == OperationStatus.CANCELLED:
                    break
                    
                await asyncio.sleep(1)  # Simulate work
                operation.progress = ((step + 1) / total_steps) * 100
                
                # Send progress update
                await websocket_manager.broadcast_status(
                    operation.id,
                    {
                        "status": OperationStatus.RUNNING,
                        "progress": operation.progress,
                        "metadata": operation.metadata
                    }
                )
                
                # Simulate random failures for testing retry mechanism
                if operation.progress == 60 and not operation.metadata.get("retry_count"):
                    raise ExecutionError(
                        "Simulated failure for testing retry mechanism",
                        details={"progress": operation.progress}
                    )
        except Exception as e:
            # Let the caller handle the error for retry logic
            raise ExecutionError(str(e), details={"progress": operation.progress})

    async def start(self):
        """Start processing operations from all queues"""
        if self.running:
            return

        self.running = True
        for priority in OperationPriority:
            for _ in range(self.max_workers):
                worker = asyncio.create_task(self._process_queue(priority))
                self.workers[str(uuid4())] = worker

        logger.info("Operation queue system started")

    async def stop(self):
        """Stop processing operations"""
        self.running = False
        
        # Cancel all active workers
        for worker_id, worker in self.workers.items():
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass
        
        self.workers.clear()
        logger.info("Operation queue system stopped")


# Global queue instance
queue = OperationQueue()
