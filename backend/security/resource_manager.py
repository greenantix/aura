import asyncio
import time
import logging
from collections import defaultdict
from typing import Dict, Optional
import psutil

logger = logging.getLogger(__name__)

class ResourceError(Exception):
    """Resource-related error"""
    pass

class ResourceManager:
    """Manage and limit resource usage across Aura services"""

    def __init__(self, config: Dict):
        self.max_memory_mb = config.get('max_memory_mb', 2048)
        self.max_cpu_percent = config.get('max_cpu_percent', 80)
        self.max_concurrent_analysis = config.get('max_concurrent_analysis', 10)
        self.rate_limits = config.get('rate_limits', {})

        self._active_analyses = 0
        self._rate_limit_counters = defaultdict(list)
        self._memory_monitor_task = None

    async def start_monitoring(self):
        """Start resource monitoring"""
        self._memory_monitor_task = asyncio.create_task(self._monitor_resources())

    async def stop_monitoring(self):
        """Stop resource monitoring"""
        if self._memory_monitor_task:
            self._memory_monitor_task.cancel()

    async def acquire_analysis_slot(self, client_id: str) -> bool:
        """Acquire a slot for code analysis with rate limiting"""
        # Check concurrent analysis limit
        if self._active_analyses >= self.max_concurrent_analysis:
            raise ResourceError("Maximum concurrent analyses exceeded")

        # Check rate limits
        if not self._check_rate_limit(client_id, 'analysis'):
            raise ResourceError("Rate limit exceeded for analysis requests")

        # Check system resources
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)

        if memory_percent > self.max_memory_mb:
            raise ResourceError("System memory usage too high")

        if cpu_percent > self.max_cpu_percent:
            raise ResourceError("System CPU usage too high")

        self._active_analyses += 1
        return True

    def release_analysis_slot(self):
        """Release an analysis slot"""
        self._active_analyses = max(0, self._active_analyses - 1)

    def _check_rate_limit(self, client_id: str, operation: str) -> bool:
        """Check if operation is within rate limits"""
        limit_key = f"{client_id}:{operation}"
        current_time = time.time()

        # Clean old entries
        self._rate_limit_counters[limit_key] = [
            timestamp for timestamp in self._rate_limit_counters[limit_key]
            if current_time - timestamp < 60  # 1-minute window
        ]

        # Check limit
        limit = self.rate_limits.get(operation, 100)  # Default 100 per minute
        if len(self._rate_limit_counters[limit_key]) >= limit:
            return False

        # Record this request
        self._rate_limit_counters[limit_key].append(current_time)
        return True

    async def _monitor_resources(self):
        """Continuously monitor system resources"""
        while True:
            try:
                memory_percent = psutil.virtual_memory().percent
                cpu_percent = psutil.cpu_percent(interval=1)

                # Log warnings for high usage
                if memory_percent > 90:
                    logger.warning(f"High memory usage: {memory_percent}%")

                if cpu_percent > 95:
                    logger.warning(f"High CPU usage: {cpu_percent}%")

                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")