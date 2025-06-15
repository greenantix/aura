#!/usr/bin/env python3
"""
Aura Async Processing Pipeline
==============================

High-performance async processing pipeline with intelligent task scheduling,
resource pooling, and concurrent execution optimization.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import weakref
import threading
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

try:
    from aura.security.audit_logger import get_audit_logger
except ImportError:
    try:
        from ..security.simple_validator import get_audit_logger
    except ImportError:
        # Fallback for standalone use
        def get_audit_logger():
            class DummyLogger:
                class SecurityEventType:
                    AUTHENTICATION_SUCCESS = "auth_success"
                    AUTHENTICATION_FAILURE = "auth_failure"
                    ACCESS_DENIED = "access_denied"
                    SUSPICIOUS_ACTIVITY = "suspicious_activity"
                
                def log_security_event(self, *args, **kwargs): pass
                def log_suspicious_activity(self, *args, **kwargs): pass
            return DummyLogger()


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineTask:
    """Represents a task in the processing pipeline"""
    id: str
    func: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None
    dependencies: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None


@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    peak_concurrent_tasks: int = 0
    throughput_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    queue_size: int = 0
    worker_utilization: float = 0.0


class AsyncPipeline:
    """High-performance async processing pipeline"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_workers = config.get('max_workers', min(32, (mp.cpu_count() or 1) + 4))
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 100)
        self.enable_thread_pool = config.get('enable_thread_pool', True)
        self.thread_pool_size = config.get('thread_pool_size', 4)
        
        # Task queues by priority
        self.task_queues = {
            TaskPriority.CRITICAL: deque(),
            TaskPriority.HIGH: deque(),
            TaskPriority.NORMAL: deque(),
            TaskPriority.LOW: deque()
        }
        
        # Active tasks and workers
        self.active_tasks: Dict[str, PipelineTask] = {}
        self.task_futures: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, PipelineTask] = {}
        
        # Pipeline state
        self.is_running = False
        self.worker_semaphore = asyncio.Semaphore(self.max_workers)
        self.task_completion_event = asyncio.Event()
        
        # Thread pool for CPU-bound tasks
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.thread_pool_size,
            thread_name_prefix="aura-pipeline"
        ) if self.enable_thread_pool else None
        
        # Metrics and monitoring
        self.metrics = PipelineMetrics()
        self.logger = logging.getLogger('aura.performance.pipeline')
        self.audit_logger = get_audit_logger()
        
        # Task dependency graph
        self.dependency_graph: Dict[str, List[str]] = {}
        self.reverse_dependencies: Dict[str, List[str]] = {}
        
        # Performance optimization
        self._last_metrics_update = time.time()
        self._execution_times = deque(maxlen=100)  # Rolling window
        
    async def start(self):
        """Start the pipeline"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info(f"Starting async pipeline with {self.max_workers} workers")
        
        # Start worker tasks
        self.worker_tasks = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        
        # Start metrics collection
        self.metrics_task = asyncio.create_task(self._collect_metrics())
        
        self.audit_logger.log_security_event(
            event_type=self.audit_logger.SecurityEventType.AUTHENTICATION_SUCCESS,
            service_id='async_pipeline',
            details={'action': 'pipeline_started', 'workers': self.max_workers}
        )

    async def stop(self):
        """Stop the pipeline gracefully"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping async pipeline...")
        self.is_running = False
        
        # Cancel all active tasks
        for task_id, future in self.task_futures.items():
            if not future.done():
                future.cancel()
                self.active_tasks[task_id].status = TaskStatus.CANCELLED
        
        # Wait for workers to finish
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Stop metrics collection
        if hasattr(self, 'metrics_task'):
            self.metrics_task.cancel()
        
        # Shutdown thread pool
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        
        self.logger.info("Pipeline stopped")

    async def submit_task(self, 
                         task_id: str,
                         func: Callable,
                         *args,
                         priority: TaskPriority = TaskPriority.NORMAL,
                         timeout: float = 30.0,
                         max_retries: int = 3,
                         dependencies: List[str] = None,
                         callback: Callable = None,
                         **kwargs) -> str:
        """Submit a task to the pipeline"""
        
        if not self.is_running:
            raise RuntimeError("Pipeline is not running")
        
        # Check for duplicate task IDs
        if task_id in self.active_tasks or task_id in self.completed_tasks:
            raise ValueError(f"Task with ID '{task_id}' already exists")
        
        # Create task
        task = PipelineTask(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            dependencies=dependencies or [],
            callback=callback
        )
        
        # Check dependencies
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id not in self.completed_tasks:
                    # Add to dependency graph
                    if dep_id not in self.reverse_dependencies:
                        self.reverse_dependencies[dep_id] = []
                    self.reverse_dependencies[dep_id].append(task_id)
                    
                    # Don't queue yet - wait for dependencies
                    self.dependency_graph[task_id] = task.dependencies.copy()
                    self.active_tasks[task_id] = task
                    return task_id
        
        # Queue task
        self._queue_task(task)
        self.metrics.total_tasks += 1
        
        self.logger.debug(f"Submitted task {task_id} with priority {priority.name}")
        return task_id

    def _queue_task(self, task: PipelineTask):
        """Add task to appropriate priority queue"""
        self.task_queues[task.priority].append(task)
        self.active_tasks[task.id] = task
        self.metrics.queue_size += 1

    async def _worker(self, worker_name: str):
        """Worker coroutine to process tasks"""
        while self.is_running:
            try:
                # Get next task
                task = await self._get_next_task()
                if not task:
                    await asyncio.sleep(0.1)  # Brief pause when no tasks
                    continue
                
                # Execute task
                await self._execute_task(task, worker_name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)  # Brief recovery pause

    async def _get_next_task(self) -> Optional[PipelineTask]:
        """Get the next task to execute based on priority"""
        # Check queues in priority order
        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, 
                        TaskPriority.NORMAL, TaskPriority.LOW]:
            queue = self.task_queues[priority]
            if queue:
                task = queue.popleft()
                self.metrics.queue_size -= 1
                return task
        
        return None

    async def _execute_task(self, task: PipelineTask, worker_name: str):
        """Execute a single task"""
        async with self.worker_semaphore:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            
            try:
                # Create task future
                if asyncio.iscoroutinefunction(task.func):
                    # Async function
                    future = asyncio.create_task(
                        asyncio.wait_for(
                            task.func(*task.args, **task.kwargs),
                            timeout=task.timeout
                        )
                    )
                else:
                    # Sync function - run in thread pool if available
                    if self.thread_pool:
                        future = asyncio.create_task(
                            asyncio.wait_for(
                                asyncio.get_event_loop().run_in_executor(
                                    self.thread_pool,
                                    lambda: task.func(*task.args, **task.kwargs)
                                ),
                                timeout=task.timeout
                            )
                        )
                    else:
                        # Run in current thread (blocking)
                        future = asyncio.create_task(
                            asyncio.wait_for(
                                asyncio.to_thread(task.func, *task.args, **task.kwargs),
                                timeout=task.timeout
                            )
                        )
                
                self.task_futures[task.id] = future
                
                # Execute with timeout
                result = await future
                
                # Task completed successfully
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                
                self._record_execution_time(task)
                self.metrics.completed_tasks += 1
                
                # Execute callback if provided
                if task.callback:
                    try:
                        if asyncio.iscoroutinefunction(task.callback):
                            await task.callback(task.result)
                        else:
                            task.callback(task.result)
                    except Exception as e:
                        self.logger.warning(f"Task callback failed for {task.id}: {e}")
                
                self.logger.debug(f"Task {task.id} completed by {worker_name}")
                
            except asyncio.TimeoutError:
                task.error = TimeoutError(f"Task {task.id} timed out after {task.timeout}s")
                await self._handle_task_failure(task)
                
            except Exception as e:
                task.error = e
                await self._handle_task_failure(task)
                
            finally:
                # Clean up
                if task.id in self.task_futures:
                    del self.task_futures[task.id]
                
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    # Move to completed tasks
                    self.completed_tasks[task.id] = task
                    if task.id in self.active_tasks:
                        del self.active_tasks[task.id]
                    
                    # Check for dependent tasks
                    await self._process_dependencies(task.id)
                
                # Update peak concurrent tasks
                active_count = len(self.active_tasks)
                if active_count > self.metrics.peak_concurrent_tasks:
                    self.metrics.peak_concurrent_tasks = active_count

    async def _handle_task_failure(self, task: PipelineTask):
        """Handle task failure with retry logic"""
        task.retry_count += 1
        
        if task.retry_count <= task.max_retries:
            # Retry task
            task.status = TaskStatus.PENDING
            task.started_at = None
            self._queue_task(task)
            
            self.logger.warning(f"Retrying task {task.id} (attempt {task.retry_count})")
        else:
            # Max retries exceeded
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            self.metrics.failed_tasks += 1
            
            self.logger.error(f"Task {task.id} failed after {task.max_retries} retries: {task.error}")
            
            self.audit_logger.log_suspicious_activity(
                'async_pipeline',
                f'task_failed: {task.id}',
                {'error': str(task.error), 'retries': task.retry_count}
            )

    async def _process_dependencies(self, completed_task_id: str):
        """Process tasks waiting for dependencies"""
        if completed_task_id not in self.reverse_dependencies:
            return
        
        # Check all tasks that depend on this one
        for dependent_task_id in self.reverse_dependencies[completed_task_id]:
            if dependent_task_id not in self.dependency_graph:
                continue
            
            # Remove completed dependency
            self.dependency_graph[dependent_task_id].remove(completed_task_id)
            
            # If all dependencies satisfied, queue the task
            if not self.dependency_graph[dependent_task_id]:
                del self.dependency_graph[dependent_task_id]
                
                if dependent_task_id in self.active_tasks:
                    task = self.active_tasks[dependent_task_id]
                    if task.status == TaskStatus.PENDING:
                        self._queue_task(task)

    def _record_execution_time(self, task: PipelineTask):
        """Record task execution time for metrics"""
        if task.started_at and task.completed_at:
            execution_time = task.completed_at - task.started_at
            self._execution_times.append(execution_time)

    async def _collect_metrics(self):
        """Collect performance metrics"""
        while self.is_running:
            try:
                import psutil
                
                # Calculate averages
                if self._execution_times:
                    self.metrics.average_execution_time = sum(self._execution_times) / len(self._execution_times)
                
                # Calculate throughput
                current_time = time.time()
                time_window = current_time - self._last_metrics_update
                if time_window > 0:
                    completed_in_window = self.metrics.completed_tasks
                    self.metrics.throughput_per_second = completed_in_window / time_window
                
                # System metrics
                try:
                    process = psutil.Process()
                    self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                    self.metrics.cpu_usage_percent = process.cpu_percent()
                except:
                    pass  # psutil not available
                
                # Worker utilization
                active_workers = len([t for t in self.task_futures.values() if not t.done()])
                self.metrics.worker_utilization = active_workers / self.max_workers * 100
                
                self._last_metrics_update = current_time
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)

    async def wait_for_task(self, task_id: str, timeout: float = None) -> Any:
        """Wait for a specific task to complete"""
        start_time = time.time()
        
        while True:
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                if task.status == TaskStatus.COMPLETED:
                    return task.result
                elif task.status == TaskStatus.FAILED:
                    raise task.error
                else:
                    raise RuntimeError(f"Task {task_id} in unexpected state: {task.status}")
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Timeout waiting for task {task_id}")
            
            await asyncio.sleep(0.1)

    async def wait_for_all(self, timeout: float = None) -> Dict[str, Any]:
        """Wait for all active tasks to complete"""
        start_time = time.time()
        
        while self.active_tasks or any(self.task_queues.values()):
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError("Timeout waiting for all tasks")
            
            await asyncio.sleep(0.5)
        
        # Return results
        results = {}
        for task_id, task in self.completed_tasks.items():
            if task.status == TaskStatus.COMPLETED:
                results[task_id] = task.result
        
        return results

    def get_metrics(self) -> PipelineMetrics:
        """Get current pipeline metrics"""
        # Update queue size
        total_queued = sum(len(queue) for queue in self.task_queues.values())
        self.metrics.queue_size = total_queued
        
        return self.metrics

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a specific task"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].status
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        return None

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task"""
        if task_id in self.task_futures:
            future = self.task_futures[task_id]
            if not future.done():
                future.cancel()
                
                if task_id in self.active_tasks:
                    self.active_tasks[task_id].status = TaskStatus.CANCELLED
                
                return True
        
        return False

    def clear_completed_tasks(self):
        """Clear completed tasks to free memory"""
        self.completed_tasks.clear()
        self.logger.info("Cleared completed tasks from memory")


# Utility functions for common pipeline patterns
async def process_batch(pipeline: AsyncPipeline, 
                       items: List[Any], 
                       processor_func: Callable,
                       batch_size: int = 10,
                       priority: TaskPriority = TaskPriority.NORMAL) -> List[Any]:
    """Process a batch of items through the pipeline"""
    task_ids = []
    
    # Submit tasks in batches
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        task_id = f"batch_{i // batch_size}"
        
        await pipeline.submit_task(
            task_id=task_id,
            func=processor_func,
            items=batch,
            priority=priority
        )
        task_ids.append(task_id)
    
    # Wait for all batches to complete
    results = []
    for task_id in task_ids:
        result = await pipeline.wait_for_task(task_id)
        results.extend(result if isinstance(result, list) else [result])
    
    return results


if __name__ == "__main__":
    # Test the async pipeline
    import asyncio
    
    async def test_pipeline():
        config = {
            'max_workers': 4,
            'max_concurrent_tasks': 10,
            'enable_thread_pool': True
        }
        
        pipeline = AsyncPipeline(config)
        await pipeline.start()
        
        # Test async function
        async def async_task(x):
            await asyncio.sleep(0.1)
            return x * 2
        
        # Test sync function
        def sync_task(x):
            time.sleep(0.05)
            return x + 10
        
        print("🚀 Testing Async Pipeline")
        print("=" * 40)
        
        # Submit various tasks
        tasks = []
        for i in range(10):
            if i % 2 == 0:
                task_id = await pipeline.submit_task(
                    f"async_task_{i}",
                    async_task,
                    i,
                    priority=TaskPriority.HIGH if i < 5 else TaskPriority.NORMAL
                )
            else:
                task_id = await pipeline.submit_task(
                    f"sync_task_{i}",
                    sync_task,
                    i,
                    priority=TaskPriority.NORMAL
                )
            tasks.append(task_id)
        
        # Wait for completion
        results = await pipeline.wait_for_all(timeout=30)
        
        print(f"✅ Completed {len(results)} tasks")
        
        # Show metrics
        metrics = pipeline.get_metrics()
        print(f"📊 Pipeline Metrics:")
        print(f"   Total tasks: {metrics.total_tasks}")
        print(f"   Completed: {metrics.completed_tasks}")
        print(f"   Failed: {metrics.failed_tasks}")
        print(f"   Avg execution time: {metrics.average_execution_time:.3f}s")
        print(f"   Peak concurrent: {metrics.peak_concurrent_tasks}")
        print(f"   Worker utilization: {metrics.worker_utilization:.1f}%")
        
        await pipeline.stop()
    
    asyncio.run(test_pipeline())