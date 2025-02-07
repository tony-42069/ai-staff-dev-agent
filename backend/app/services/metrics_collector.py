"""Service for collecting and managing system metrics."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from collections import defaultdict
import json
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import async_session_maker
from ..models.agent_operations import AgentMetric

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and manages system metrics."""

    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.retention_days = 30
        self.history_file = Path("data/metrics_history.json")
        self.load_history()
        self._db_session: Optional[AsyncSession] = None

    async def get_db(self) -> AsyncSession:
        """Get database session."""
        if not self._db_session:
            self._db_session = async_session_maker()
        return self._db_session

    async def close_db(self) -> None:
        """Close database session."""
        if self._db_session:
            await self._db_session.close()
            self._db_session = None

    async def stop(self) -> None:
        """Stop metrics collection and cleanup."""
        # Save final metrics to history file
        self.save_history()
        # Close database connection
        await self.close_db()

    def load_history(self) -> None:
        """Load metrics history from file."""
        try:
            if self.history_file.exists():
                with self.history_file.open() as f:
                    data = json.load(f)
                    # Convert stored data to defaultdict
                    self.history = defaultdict(list, data)
                logger.info("Loaded metrics history from %s", self.history_file)
        except Exception as e:
            logger.error("Failed to load metrics history: %s", e)

    def save_history(self) -> None:
        """Save metrics history to file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with self.history_file.open('w') as f:
                json.dump(dict(self.history), f, indent=2)
            logger.info("Saved metrics history to %s", self.history_file)
        except Exception as e:
            logger.error("Failed to save metrics history: %s", e)

    async def record_metric(
        self,
        category: str,
        name: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a metric value."""
        timestamp = datetime.utcnow()
        
        # Store current value
        self.metrics[category][name] = {
            'value': value,
            'timestamp': timestamp.isoformat(),
            'metadata': metadata or {}
        }
        
        # Add to history
        self.history[f"{category}.{name}"].append({
            'value': value,
            'timestamp': timestamp.isoformat(),
            'metadata': metadata or {}
        })
        
        # Prune old history
        self._prune_history()

        # Store in database if it's an agent metric
        if category.startswith("agent."):
            agent_id = category.split(".")[1]
            await self._store_agent_metric(agent_id, name, value, metadata)

    async def _store_agent_metric(
        self,
        agent_id: str,
        metric_type: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store metric in the database."""
        try:
            db = await self.get_db()
            metric = AgentMetric(
                agent_id=agent_id,
                timestamp=datetime.utcnow(),
                metric_type=metric_type,
                value=value,
                metadata=metadata or {}
            )
            db.add(metric)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to store metric in database: {e}")
            await db.rollback()

    def get_metric(
        self,
        category: str,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """Get current value of a metric."""
        return self.metrics.get(category, {}).get(name)

    def get_metric_history(
        self,
        category: str,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get historical values for a metric."""
        history = self.history.get(f"{category}.{name}", [])
        
        if not (start_time or end_time):
            return history
            
        filtered = []
        for entry in history:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if start_time and entry_time < start_time:
                continue
            if end_time and entry_time > end_time:
                continue
            filtered.append(entry)
            
        return filtered

    def get_metrics_summary(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get summary of current metrics."""
        if category:
            return {
                'category': category,
                'metrics': self.metrics.get(category, {}),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        return {
            'categories': list(self.metrics.keys()),
            'metrics': dict(self.metrics),
            'timestamp': datetime.utcnow().isoformat()
        }

    def calculate_statistics(
        self,
        category: str,
        name: str,
        window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Calculate statistics for a metric over a time window."""
        end_time = datetime.utcnow()
        start_time = end_time - window
        
        history = self.get_metric_history(category, name, start_time, end_time)
        if not history:
            return {}
            
        values = [entry['value'] for entry in history if isinstance(entry['value'], (int, float))]
        if not values:
            return {}
            
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }

    def _prune_history(self) -> None:
        """Remove metrics older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        
        for key in self.history:
            self.history[key] = [
                entry for entry in self.history[key]
                if datetime.fromisoformat(entry['timestamp']) > cutoff
            ]

    async def start(self) -> None:
        """Start metrics collection."""
        # Start collection task
        asyncio.create_task(self._collect_metrics())

    async def _collect_metrics(self) -> None:
        """Periodic metrics collection task."""
        while True:
            try:
                # Collect system metrics
                await self.record_metric('system', 'memory_usage', self._get_memory_usage())
                await self.record_metric('system', 'cpu_usage', self._get_cpu_usage())
                await self.record_metric('system', 'disk_usage', self._get_disk_usage())
                
                # Save history periodically
                self.save_history()
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error("Error collecting metrics: %s", e)
                await asyncio.sleep(5)  # Wait before retrying
            finally:
                # Ensure DB connection is cleaned up after each iteration
                await self.close_db()

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage metrics."""
        try:
            import psutil
            vm = psutil.virtual_memory()
            return {
                'total': vm.total / (1024 * 1024 * 1024),  # GB
                'available': vm.available / (1024 * 1024 * 1024),  # GB
                'percent': vm.percent
            }
        except ImportError:
            logger.warning("psutil not available for memory metrics")
            return {}

    def _get_cpu_usage(self) -> Dict[str, float]:
        """Get CPU usage metrics."""
        try:
            import psutil
            return {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count()
            }
        except ImportError:
            logger.warning("psutil not available for CPU metrics")
            return {}

    def _get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage metrics."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                'total': disk.total / (1024 * 1024 * 1024),  # GB
                'used': disk.used / (1024 * 1024 * 1024),  # GB
                'free': disk.free / (1024 * 1024 * 1024),  # GB
                'percent': disk.percent
            }
        except ImportError:
            logger.warning("psutil not available for disk metrics")
            return {}

# Global metrics collector instance
collector = MetricsCollector()
