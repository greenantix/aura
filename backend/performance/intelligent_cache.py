#!/usr/bin/env python3
"""
Aura Intelligent Caching System
================================

Advanced caching system with LRU eviction, TTL support, intelligent prefetching,
and performance optimization for code analysis results.

Author: Aura - Level 9 Autonomous AI Coding Assistant
"""

import asyncio
import time
import hashlib
import pickle
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict
import weakref
import logging
import os
from pathlib import Path

try:
    from aura.security.input_validator import SecurityValidator
except ImportError:
    try:
        from ..security.simple_validator import SimpleSecurityValidator as SecurityValidator
    except ImportError:
        # Fallback for standalone use
        class SecurityValidator:
            @staticmethod
            def validate_file_path(path, allowed_dirs=None):
                return str(path)
            @staticmethod
            def sanitize_filename(filename):
                return filename


class CacheStrategy(Enum):
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    TTL = "ttl"           # Time To Live
    ADAPTIVE = "adaptive"  # Intelligent adaptive strategy


class CacheLevel(Enum):
    MEMORY = "memory"     # In-memory cache
    DISK = "disk"        # Disk-based cache
    DISTRIBUTED = "distributed"  # Distributed cache (future)


@dataclass
class CacheEntry:
    """Represents a cache entry"""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update access time and count"""
        self.accessed_at = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    average_access_time: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0


class IntelligentCache:
    """High-performance intelligent caching system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_memory_mb = config.get('max_memory_mb', 512)
        self.max_entries = config.get('max_entries', 10000)
        self.default_ttl = config.get('default_ttl', 3600)  # 1 hour
        self.strategy = CacheStrategy(config.get('strategy', 'adaptive'))
        self.enable_disk_cache = config.get('enable_disk_cache', True)
        self.disk_cache_dir = config.get('disk_cache_dir', '.aura_cache')
        self.enable_compression = config.get('enable_compression', True)
        self.prefetch_enabled = config.get('prefetch_enabled', True)
        
        # Cache storage
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.access_times: Dict[str, List[float]] = {}
        self.access_patterns: Dict[str, int] = {}
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStats()
        self.logger = logging.getLogger('aura.performance.cache')
        
        # Disk cache setup
        if self.enable_disk_cache:
            self.disk_cache_path = Path(self.disk_cache_dir)
            self.disk_cache_path.mkdir(exist_ok=True)
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.prefetch_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Adaptive strategy parameters
        self.adaptive_weights = {
            'recency': 0.4,
            'frequency': 0.3,
            'size': 0.2,
            'ttl': 0.1
        }
        
        # Prefetching
        self.prefetch_queue: asyncio.Queue = asyncio.Queue()
        self.prefetch_callbacks: Dict[str, Callable] = {}

    async def start(self):
        """Start the cache system"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("Starting intelligent cache system")
        
        # Start background cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_worker())
        
        # Start prefetch worker if enabled
        if self.prefetch_enabled:
            self.prefetch_task = asyncio.create_task(self._prefetch_worker())
        
        # Load disk cache index
        if self.enable_disk_cache:
            await self._load_disk_cache_index()

    async def stop(self):
        """Stop the cache system"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping cache system")
        self.is_running = False
        
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        if self.prefetch_task:
            self.prefetch_task.cancel()
        
        # Save disk cache index
        if self.enable_disk_cache:
            await self._save_disk_cache_index()

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        start_time = time.time()
        
        try:
            # Validate key
            key = SecurityValidator.sanitize_filename(key)
            
            with self.lock:
                # Check memory cache first
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    
                    # Check if expired
                    if entry.is_expired():
                        del self.memory_cache[key]
                        self.stats.misses += 1
                        return default
                    
                    # Update access info
                    entry.touch()
                    
                    # Move to end for LRU
                    self.memory_cache.move_to_end(key)
                    
                    # Record access pattern
                    self._record_access_pattern(key)
                    
                    self.stats.hits += 1
                    self._update_hit_rate()
                    
                    access_time = time.time() - start_time
                    self._update_average_access_time(access_time)
                    
                    return entry.value
                
                # Check disk cache if enabled
                if self.enable_disk_cache:
                    disk_value = await self._get_from_disk(key)
                    if disk_value is not None:
                        # Promote to memory cache
                        await self._set_memory(key, disk_value, ttl=self.default_ttl)
                        
                        self.stats.hits += 1
                        self._update_hit_rate()
                        return disk_value
                
                # Cache miss
                self.stats.misses += 1
                self._update_hit_rate()
                
                # Schedule prefetch for related keys
                if self.prefetch_enabled:
                    await self._schedule_prefetch(key)
                
                return default
                
        except Exception as e:
            self.logger.error(f"Error getting cache entry {key}: {e}")
            return default

    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[float] = None,
                  level: CacheLevel = CacheLevel.MEMORY) -> bool:
        """Set value in cache"""
        try:
            # Validate key
            key = SecurityValidator.sanitize_filename(key)
            
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Set in appropriate cache level
            if level == CacheLevel.MEMORY or level == CacheLevel.DISTRIBUTED:
                return await self._set_memory(key, value, ttl)
            elif level == CacheLevel.DISK:
                return await self._set_disk(key, value, ttl)
            
        except Exception as e:
            self.logger.error(f"Error setting cache entry {key}: {e}")
            return False

    async def _set_memory(self, key: str, value: Any, ttl: Optional[float]) -> bool:
        """Set value in memory cache"""
        with self.lock:
            # Calculate entry size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Fallback estimate
            
            # Check memory limits
            if self._would_exceed_memory_limit(size_bytes):
                await self._evict_entries(size_bytes)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl,
                size_bytes=size_bytes,
                metadata={'level': 'memory'}
            )
            
            # Remove existing entry if present
            if key in self.memory_cache:
                old_entry = self.memory_cache[key]
                self.stats.size_bytes -= old_entry.size_bytes
            
            # Add new entry
            self.memory_cache[key] = entry
            self.stats.size_bytes += size_bytes
            self.stats.entry_count = len(self.memory_cache)
            
            # Record access pattern
            self._record_access_pattern(key)
            
            return True

    async def _set_disk(self, key: str, value: Any, ttl: Optional[float]) -> bool:
        """Set value in disk cache"""
        if not self.enable_disk_cache:
            return False
        
        try:
            # Create file path
            file_path = self.disk_cache_path / f"{key}.cache"
            
            # Prepare cache data
            cache_data = {
                'value': value,
                'created_at': time.time(),
                'ttl': ttl,
                'metadata': {'level': 'disk'}
            }
            
            # Write to disk
            if self.enable_compression:
                import gzip
                with gzip.open(file_path, 'wb') as f:
                    pickle.dump(cache_data, f)
            else:
                with open(file_path, 'wb') as f:
                    pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing to disk cache {key}: {e}")
            return False

    async def _get_from_disk(self, key: str) -> Any:
        """Get value from disk cache"""
        if not self.enable_disk_cache:
            return None
        
        try:
            file_path = self.disk_cache_path / f"{key}.cache"
            
            if not file_path.exists():
                return None
            
            # Read from disk
            if self.enable_compression:
                import gzip
                with gzip.open(file_path, 'rb') as f:
                    cache_data = pickle.load(f)
            else:
                with open(file_path, 'rb') as f:
                    cache_data = pickle.load(f)
            
            # Check expiration
            if cache_data['ttl'] is not None:
                age = time.time() - cache_data['created_at']
                if age > cache_data['ttl']:
                    # Expired, remove file
                    file_path.unlink()
                    return None
            
            return cache_data['value']
            
        except Exception as e:
            self.logger.error(f"Error reading from disk cache {key}: {e}")
            return None

    def _would_exceed_memory_limit(self, additional_bytes: int) -> bool:
        """Check if adding bytes would exceed memory limit"""
        max_bytes = self.max_memory_mb * 1024 * 1024
        return (self.stats.size_bytes + additional_bytes) > max_bytes

    async def _evict_entries(self, needed_bytes: int):
        """Evict entries based on strategy"""
        with self.lock:
            if self.strategy == CacheStrategy.LRU:
                await self._evict_lru(needed_bytes)
            elif self.strategy == CacheStrategy.LFU:
                await self._evict_lfu(needed_bytes)
            elif self.strategy == CacheStrategy.TTL:
                await self._evict_ttl(needed_bytes)
            elif self.strategy == CacheStrategy.ADAPTIVE:
                await self._evict_adaptive(needed_bytes)

    async def _evict_lru(self, needed_bytes: int):
        """Evict least recently used entries"""
        freed_bytes = 0
        keys_to_remove = []
        
        # LRU is at the beginning of OrderedDict
        for key, entry in self.memory_cache.items():
            keys_to_remove.append(key)
            freed_bytes += entry.size_bytes
            
            if freed_bytes >= needed_bytes:
                break
        
        # Remove entries
        for key in keys_to_remove:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                # Optionally save to disk
                if self.enable_disk_cache and entry.access_count > 1:
                    await self._set_disk(key, entry.value, entry.ttl)
                
                del self.memory_cache[key]
                self.stats.size_bytes -= entry.size_bytes
                self.stats.evictions += 1

    async def _evict_lfu(self, needed_bytes: int):
        """Evict least frequently used entries"""
        # Sort by access count
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].access_count
        )
        
        freed_bytes = 0
        for key, entry in sorted_entries:
            # Save to disk if valuable
            if self.enable_disk_cache and entry.access_count > 1:
                await self._set_disk(key, entry.value, entry.ttl)
            
            del self.memory_cache[key]
            self.stats.size_bytes -= entry.size_bytes
            self.stats.evictions += 1
            freed_bytes += entry.size_bytes
            
            if freed_bytes >= needed_bytes:
                break

    async def _evict_ttl(self, needed_bytes: int):
        """Evict entries closest to expiration"""
        current_time = time.time()
        
        # Sort by time to expiration
        entries_with_ttl = [
            (key, entry) for key, entry in self.memory_cache.items()
            if entry.ttl is not None
        ]
        
        sorted_entries = sorted(
            entries_with_ttl,
            key=lambda x: x[1].created_at + x[1].ttl - current_time
        )
        
        freed_bytes = 0
        for key, entry in sorted_entries:
            del self.memory_cache[key]
            self.stats.size_bytes -= entry.size_bytes
            self.stats.evictions += 1
            freed_bytes += entry.size_bytes
            
            if freed_bytes >= needed_bytes:
                break

    async def _evict_adaptive(self, needed_bytes: int):
        """Intelligent adaptive eviction strategy"""
        current_time = time.time()
        
        # Calculate composite scores for each entry
        scored_entries = []
        
        for key, entry in self.memory_cache.items():
            # Recency score (0-1, higher is more recent)
            recency = 1.0 / (1.0 + (current_time - entry.accessed_at) / 3600)
            
            # Frequency score (normalized by max access count)
            max_access = max((e.access_count for e in self.memory_cache.values()), default=1)
            frequency = entry.access_count / max_access
            
            # Size score (0-1, smaller is better)
            max_size = max((e.size_bytes for e in self.memory_cache.values()), default=1)
            size_score = 1.0 - (entry.size_bytes / max_size)
            
            # TTL score (0-1, longer TTL is better)
            if entry.ttl is not None:
                remaining_ttl = max(0, entry.ttl - (current_time - entry.created_at))
                ttl_score = min(1.0, remaining_ttl / entry.ttl)
            else:
                ttl_score = 1.0
            
            # Composite score
            score = (
                self.adaptive_weights['recency'] * recency +
                self.adaptive_weights['frequency'] * frequency +
                self.adaptive_weights['size'] * size_score +
                self.adaptive_weights['ttl'] * ttl_score
            )
            
            scored_entries.append((key, entry, score))
        
        # Sort by score (lower scores evicted first)
        scored_entries.sort(key=lambda x: x[2])
        
        freed_bytes = 0
        for key, entry, score in scored_entries:
            # Save valuable entries to disk
            if (self.enable_disk_cache and 
                entry.access_count > 2 and 
                score > 0.3):
                await self._set_disk(key, entry.value, entry.ttl)
            
            del self.memory_cache[key]
            self.stats.size_bytes -= entry.size_bytes
            self.stats.evictions += 1
            freed_bytes += entry.size_bytes
            
            if freed_bytes >= needed_bytes:
                break

    def _record_access_pattern(self, key: str):
        """Record access pattern for intelligent prefetching"""
        current_time = time.time()
        
        if key not in self.access_times:
            self.access_times[key] = []
        
        self.access_times[key].append(current_time)
        
        # Keep only recent access times (last hour)
        cutoff_time = current_time - 3600
        self.access_times[key] = [
            t for t in self.access_times[key] if t > cutoff_time
        ]
        
        # Update access pattern frequency
        self.access_patterns[key] = len(self.access_times[key])

    async def _schedule_prefetch(self, key: str):
        """Schedule prefetching of related keys"""
        if not self.prefetch_enabled:
            return
        
        # Find related keys based on patterns
        related_keys = self._find_related_keys(key)
        
        for related_key in related_keys[:3]:  # Limit prefetch
            if related_key not in self.memory_cache:
                await self.prefetch_queue.put(related_key)

    def _find_related_keys(self, key: str) -> List[str]:
        """Find keys related to the given key"""
        related = []
        
        # Simple heuristic: keys with similar prefixes or patterns
        for cache_key in list(self.memory_cache.keys()):
            if cache_key != key:
                # Check for common prefixes
                common_prefix_len = 0
                for i, (c1, c2) in enumerate(zip(key, cache_key)):
                    if c1 == c2:
                        common_prefix_len = i + 1
                    else:
                        break
                
                # If significant common prefix, consider related
                if common_prefix_len > len(key) * 0.5:
                    related.append(cache_key)
        
        return related

    async def _cleanup_worker(self):
        """Background worker for cache maintenance"""
        while self.is_running:
            try:
                await self._cleanup_expired_entries()
                await self._update_memory_usage()
                await asyncio.sleep(60)  # Run every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_expired_entries(self):
        """Remove expired entries from cache"""
        with self.lock:
            expired_keys = []
            
            for key, entry in self.memory_cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self.memory_cache[key]
                del self.memory_cache[key]
                self.stats.size_bytes -= entry.size_bytes
                self.stats.evictions += 1
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

    async def _update_memory_usage(self):
        """Update memory usage statistics"""
        try:
            import psutil
            process = psutil.Process()
            self.stats.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        except:
            pass  # psutil not available
        
        # Update disk usage
        if self.enable_disk_cache and self.disk_cache_path.exists():
            disk_usage = sum(
                f.stat().st_size for f in self.disk_cache_path.glob("*.cache")
                if f.is_file()
            )
            self.stats.disk_usage_mb = disk_usage / 1024 / 1024

    async def _prefetch_worker(self):
        """Background worker for prefetching"""
        while self.is_running:
            try:
                # Get next prefetch request
                key = await asyncio.wait_for(
                    self.prefetch_queue.get(), 
                    timeout=5.0
                )
                
                # Check if we have a prefetch callback for this key pattern
                for pattern, callback in self.prefetch_callbacks.items():
                    if pattern in key:
                        try:
                            value = await callback(key)
                            if value is not None:
                                await self.set(key, value)
                                self.logger.debug(f"Prefetched {key}")
                        except Exception as e:
                            self.logger.error(f"Prefetch error for {key}: {e}")
                        break
                
            except asyncio.TimeoutError:
                continue  # No prefetch requests
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Prefetch worker error: {e}")

    def register_prefetch_callback(self, pattern: str, callback: Callable):
        """Register a callback for prefetching keys matching pattern"""
        self.prefetch_callbacks[pattern] = callback

    async def _load_disk_cache_index(self):
        """Load disk cache index on startup"""
        if not self.enable_disk_cache:
            return
        
        try:
            index_file = self.disk_cache_path / "cache_index.json"
            if index_file.exists():
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                
                # Validate entries and remove expired ones
                current_time = time.time()
                valid_files = []
                
                for entry in index_data.get('entries', []):
                    file_path = self.disk_cache_path / entry['filename']
                    
                    # Check if file exists and is not expired
                    if (file_path.exists() and 
                        (entry['ttl'] is None or 
                         current_time - entry['created_at'] < entry['ttl'])):
                        valid_files.append(entry['filename'])
                    elif file_path.exists():
                        # Remove expired file
                        file_path.unlink()
                
                self.logger.info(f"Loaded disk cache with {len(valid_files)} valid entries")
                
        except Exception as e:
            self.logger.error(f"Error loading disk cache index: {e}")

    async def _save_disk_cache_index(self):
        """Save disk cache index on shutdown"""
        if not self.enable_disk_cache:
            return
        
        try:
            # Collect information about disk cache files
            entries = []
            for cache_file in self.disk_cache_path.glob("*.cache"):
                try:
                    # Read cache metadata without loading full value
                    if self.enable_compression:
                        import gzip
                        with gzip.open(cache_file, 'rb') as f:
                            cache_data = pickle.load(f)
                    else:
                        with open(cache_file, 'rb') as f:
                            cache_data = pickle.load(f)
                    
                    entries.append({
                        'filename': cache_file.name,
                        'created_at': cache_data['created_at'],
                        'ttl': cache_data['ttl']
                    })
                except:
                    continue  # Skip corrupted files
            
            # Save index
            index_file = self.disk_cache_path / "cache_index.json"
            index_data = {
                'entries': entries,
                'saved_at': time.time()
            }
            
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving disk cache index: {e}")

    def _update_hit_rate(self):
        """Update cache hit rate"""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.hit_rate = (self.stats.hits / total_requests) * 100

    def _update_average_access_time(self, access_time: float):
        """Update average access time"""
        # Simple moving average
        if self.stats.average_access_time == 0:
            self.stats.average_access_time = access_time
        else:
            self.stats.average_access_time = (
                self.stats.average_access_time * 0.9 + access_time * 0.1
            )

    async def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        try:
            key = SecurityValidator.sanitize_filename(key)
            
            with self.lock:
                # Remove from memory cache
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    del self.memory_cache[key]
                    self.stats.size_bytes -= entry.size_bytes
                    self.stats.entry_count = len(self.memory_cache)
                
                # Remove from disk cache
                if self.enable_disk_cache:
                    file_path = self.disk_cache_path / f"{key}.cache"
                    if file_path.exists():
                        file_path.unlink()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting cache entry {key}: {e}")
            return False

    async def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.memory_cache.clear()
            self.access_times.clear()
            self.access_patterns.clear()
            self.stats = CacheStats()
        
        # Clear disk cache
        if self.enable_disk_cache and self.disk_cache_path.exists():
            for cache_file in self.disk_cache_path.glob("*.cache"):
                cache_file.unlink()

    def get_stats(self) -> CacheStats:
        """Get current cache statistics"""
        with self.lock:
            self.stats.entry_count = len(self.memory_cache)
            return self.stats

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get detailed memory usage information"""
        with self.lock:
            entry_sizes = [entry.size_bytes for entry in self.memory_cache.values()]
            
            return {
                'total_entries': len(self.memory_cache),
                'total_size_bytes': self.stats.size_bytes,
                'total_size_mb': self.stats.size_bytes / 1024 / 1024,
                'average_entry_size': sum(entry_sizes) / len(entry_sizes) if entry_sizes else 0,
                'largest_entry_size': max(entry_sizes) if entry_sizes else 0,
                'smallest_entry_size': min(entry_sizes) if entry_sizes else 0,
                'memory_limit_mb': self.max_memory_mb,
                'memory_usage_percent': (self.stats.size_bytes / (self.max_memory_mb * 1024 * 1024)) * 100
            }


# Utility functions for common caching patterns
def cache_key_from_params(*args, **kwargs) -> str:
    """Generate cache key from function parameters"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_string = "|".join(key_parts)
    
    # Use hash for long keys
    if len(key_string) > 200:
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    return key_string


def cached(cache: IntelligentCache, ttl: Optional[float] = None, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}_{cache_key_from_params(*args, **kwargs)}"
            
            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache.set(cache_key, result, ttl=ttl)
            return result
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in event loop
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


if __name__ == "__main__":
    # Test the intelligent cache
    import asyncio
    
    async def test_cache():
        config = {
            'max_memory_mb': 10,
            'max_entries': 100,
            'strategy': 'adaptive',
            'enable_disk_cache': True,
            'disk_cache_dir': 'test_cache'
        }
        
        cache = IntelligentCache(config)
        await cache.start()
        
        print("🚀 Testing Intelligent Cache")
        print("=" * 40)
        
        # Test basic operations
        await cache.set("key1", {"data": "value1", "number": 42})
        await cache.set("key2", [1, 2, 3, 4, 5])
        await cache.set("key3", "simple string", ttl=5)  # 5 second TTL
        
        # Test retrieval
        result1 = await cache.get("key1")
        result2 = await cache.get("key2")
        result3 = await cache.get("key3")
        
        print(f"✅ Basic Operations:")
        print(f"   Key1: {result1}")
        print(f"   Key2: {result2}")
        print(f"   Key3: {result3}")
        
        # Test cache statistics
        stats = cache.get_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"   Hits: {stats.hits}")
        print(f"   Misses: {stats.misses}")
        print(f"   Hit Rate: {stats.hit_rate:.1f}%")
        print(f"   Entries: {stats.entry_count}")
        print(f"   Size: {stats.size_bytes} bytes")
        
        # Test memory usage
        memory_usage = cache.get_memory_usage()
        print(f"\n💾 Memory Usage:")
        print(f"   Total Entries: {memory_usage['total_entries']}")
        print(f"   Total Size: {memory_usage['total_size_mb']:.2f} MB")
        print(f"   Average Entry Size: {memory_usage['average_entry_size']:.0f} bytes")
        print(f"   Usage Percent: {memory_usage['memory_usage_percent']:.1f}%")
        
        # Test TTL expiration
        print(f"\n⏰ Testing TTL expiration...")
        await asyncio.sleep(6)  # Wait for TTL to expire
        
        expired_result = await cache.get("key3")
        print(f"   Expired key result: {expired_result}")
        
        # Test eviction by filling cache
        print(f"\n🗑️  Testing cache eviction...")
        for i in range(50):
            large_data = "x" * 1000  # 1KB per entry
            await cache.set(f"large_key_{i}", large_data)
        
        final_stats = cache.get_stats()
        print(f"   Final entries: {final_stats.entry_count}")
        print(f"   Evictions: {final_stats.evictions}")
        
        await cache.stop()
        
        # Clean up test cache directory
        import shutil
        if os.path.exists('test_cache'):
            shutil.rmtree('test_cache')
    
    asyncio.run(test_cache())