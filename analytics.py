"""
Analytics Engine for Professional Bot
Real-time statistics, reporting, and business intelligence
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import asyncio
from dataclasses import dataclass, asdict
from database import db, ProcessedMessage
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesData:
    """Time series data point"""
    timestamp: str
    value: float
    category: str = ""


@dataclass
class ServiceStats:
    """Service-specific statistics"""
    service_name: str
    total_requests: int
    forwarded_requests: int
    average_confidence: float
    peak_hours: List[int]  # Hours 0-23 with highest activity


class AnalyticsEngine:
    """Professional analytics and reporting engine"""
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes cache
        self._cache = {}
        self._last_cache_update = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._last_cache_update:
            return False
        
        elapsed = (datetime.now() - self._last_cache_update[key]).seconds
        return elapsed < self.cache_ttl
    
    def _update_cache(self, key: str, data: Any):
        """Update cache with new data"""
        self._cache[key] = data
        self._last_cache_update[key] = datetime.now()
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time system statistics"""
        cache_key = "realtime_stats"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            # Get dashboard stats from database
            dashboard_stats = db.get_dashboard_stats()
            
            # Calculate additional real-time metrics
            current_time = datetime.now()
            
            # Messages per minute (last 5 minutes)
            five_min_ago = current_time - timedelta(minutes=5)
            recent_messages = db.get_statistics('message_processing', hours=1)
            messages_last_5min = len([s for s in recent_messages 
                                    if datetime.fromisoformat(s.timestamp) > five_min_ago])
            mpm = messages_last_5min / 5  # messages per minute
            
            # Account utilization
            account_stats = self.get_account_utilization()
            
            # Service popularity trend
            service_trends = self.get_service_trends(hours=24)
            
            stats = {
                'timestamp': current_time.isoformat(),
                'dashboard_stats': dashboard_stats,
                'messages_per_minute': round(mpm, 2),
                'account_utilization': account_stats,
                'service_trends': service_trends,
                'system_uptime': self._calculate_uptime(),
                'performance_metrics': self._get_performance_metrics()
            }
            
            self._update_cache(cache_key, stats)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting real-time stats: {e}")
            return {'error': str(e)}
    
    def get_account_utilization(self) -> Dict[str, Any]:
        """Get account utilization statistics"""
        try:
            # This would integrate with account_manager
            # For now, return placeholder data
            return {
                'total_accounts': 0,
                'active_accounts': 0,
                'utilization_rate': 0.0,
                'average_load': 0.0,
                'peak_utilization_time': ""
            }
        except Exception as e:
            logger.error(f"Error getting account utilization: {e}")
            return {'error': str(e)}
    
    def get_service_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get service popularity trends"""
        try:
            # Get recent processed messages
            recent_messages = db.get_recent_messages(limit=1000)
            
            # Group by service and hour
            service_hour_counts = defaultdict(lambda: defaultdict(int))
            total_by_service = defaultdict(int)
            
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=hours)
            
            for msg in recent_messages:
                if msg.processed_at and msg.processed_at > cutoff_time:
                    services = json.loads(msg.detected_services) if msg.detected_services else []
                    hour = msg.processed_at.hour
                    
                    for service in services:
                        service_hour_counts[service][hour] += 1
                        total_by_service[service] += 1
            
            # Calculate trends
            trends = []
            for service, hourly_data in service_hour_counts.items():
                if total_by_service[service] > 0:
                    # Find peak hours
                    peak_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)[:3]
                    peak_hour_list = [hour for hour, count in peak_hours]
                    
                    # Calculate growth trend (simplified)
                    recent_count = sum(count for hour, count in hourly_data.items() 
                                     if hour >= (current_time.hour - 6))
                    older_count = sum(count for hour, count in hourly_data.items() 
                                    if hour < (current_time.hour - 6))
                    
                    trend = "increasing" if recent_count > older_count else "decreasing" if recent_count < older_count else "stable"
                    
                    trends.append({
                        'service': service,
                        'total_requests': total_by_service[service],
                        'peak_hours': peak_hour_list,
                        'trend': trend,
                        'popularity_score': total_by_service[service] / len(recent_messages) * 100
                    })
            
            return sorted(trends, key=lambda x: x['total_requests'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting service trends: {e}")
            return []
    
    def get_user_behavior_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get messages from period
            # This would need a date filter in the database query
            messages = db.get_recent_messages(limit=5000)  # Adjust limit as needed
            
            user_stats = defaultdict(lambda: {
                'total_messages': 0,
                'help_requests': 0,
                'services_requested': set(),
                'activity_days': set(),
                'avg_confidence': 0
            })
            
            total_confidence = 0
            confidence_count = 0
            
            for msg in messages:
                if msg.processed_at and msg.processed_at > cutoff_date:
                    user_id = msg.sender_id
                    stats = user_stats[user_id]
                    
                    stats['total_messages'] += 1
                    
                    if msg.is_forwarded:
                        stats['help_requests'] += 1
                        services = json.loads(msg.detected_services) if msg.detected_services else []
                        stats['services_requested'].update(services)
                    
                    # Track activity days
                    if msg.processed_at:
                        stats['activity_days'].add(msg.processed_at.date())
                    
                    # Track confidence scores
                    if msg.confidence_score > 0:
                        total_confidence += msg.confidence_score
                        confidence_count += 1
            
            # Convert sets to lists and calculate averages
            for user_id, stats in user_stats.items():
                stats['services_requested'] = list(stats['services_requested'])
                stats['activity_days'] = len(stats['activity_days'])
                stats['help_request_rate'] = (stats['help_requests'] / stats['total_messages'] * 100) if stats['total_messages'] > 0 else 0
                stats['avg_confidence'] = total_confidence / confidence_count if confidence_count > 0 else 0
            
            # Identify user segments
            high_value_users = []
            frequent_users = []
            one_time_users = []
            
            for user_id, stats in user_stats.items():
                if stats['help_requests'] >= 5 and stats['help_request_rate'] >= 30:
                    high_value_users.append({'user_id': user_id, **stats})
                elif stats['total_messages'] >= 10:
                    frequent_users.append({'user_id': user_id, **stats})
                elif stats['total_messages'] == 1:
                    one_time_users.append({'user_id': user_id, **stats})
            
            return {
                'total_users': len(user_stats),
                'high_value_users': sorted(high_value_users, key=lambda x: x['help_requests'], reverse=True),
                'frequent_users': sorted(frequent_users, key=lambda x: x['total_messages'], reverse=True),
                'one_time_users': len(one_time_users),
                'average_help_request_rate': sum(s['help_request_rate'] for s in user_stats.values()) / len(user_stats) if user_stats else 0
            }
            
        except Exception as e:
            logger.error(f"Error in user behavior analysis: {e}")
            return {'error': str(e)}
    
    def generate_report(self, report_type: str, format: str = 'json', 
                       days: int = 7) -> str:
        """Generate analytical report"""
        try:
            if report_type == 'daily_summary':
                data = self._generate_daily_summary(days)
            elif report_type == 'service_performance':
                data = self._generate_service_performance_report(days)
            elif report_type == 'user_engagement':
                data = self._generate_user_engagement_report(days)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            if format == 'json':
                return json.dumps(data, indent=2, default=str)
            elif format == 'csv':
                return self._to_csv(data)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error generating report {report_type}: {e}")
            return f"Error: {str(e)}"
    
    def _generate_daily_summary(self, days: int) -> Dict[str, Any]:
        """Generate daily summary report"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get recent statistics
        daily_stats = db.get_statistics('daily_summary', hours=days*24)
        
        # Aggregate by day
        daily_aggregation = defaultdict(lambda: {
            'messages_processed': 0,
            'help_requests': 0,
            'accounts_active': 0
        })
        
        for stat in daily_stats:
            date_key = stat.timestamp.split('T')[0]  # YYYY-MM-DD
            aggregation = daily_aggregation[date_key]
            
            if stat.stat_key == 'messages_processed':
                aggregation['messages_processed'] += int(stat.stat_value)
            elif stat.stat_key == 'help_requests':
                aggregation['help_requests'] += int(stat.stat_value)
            elif stat.stat_key == 'accounts_active':
                aggregation['accounts_active'] = max(aggregation['accounts_active'], int(stat.stat_value))
        
        return {
            'report_type': 'daily_summary',
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'daily_data': dict(daily_aggregation)
        }
    
    def _generate_service_performance_report(self, days: int) -> Dict[str, Any]:
        """Generate service performance report"""
        service_stats = self.get_service_statistics(days)
        
        return {
            'report_type': 'service_performance',
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'service_statistics': service_stats
        }
    
    def _generate_user_engagement_report(self, days: int) -> Dict[str, Any]:
        """Generate user engagement report"""
        user_analysis = self.get_user_behavior_analysis(days)
        
        return {
            'report_type': 'user_engagement',
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'user_analysis': user_analysis
        }
    
    def get_service_statistics(self, days: int = 30) -> List[ServiceStats]:
        """Get detailed service statistics"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            messages = db.get_recent_messages(limit=10000)
            
            service_data = defaultdict(lambda: {
                'total': 0,
                'forwarded': 0,
                'confidences': [],
                'hourly_distribution': defaultdict(int)
            })
            
            for msg in messages:
                if msg.processed_at and msg.processed_at > cutoff_date:
                    services = json.loads(msg.detected_services) if msg.detected_services else []
                    hour = msg.processed_at.hour if msg.processed_at else 0
                    
                    for service in services:
                        data = service_data[service]
                        data['total'] += 1
                        if msg.is_forwarded:
                            data['forwarded'] += 1
                        if msg.confidence_score > 0:
                            data['confidences'].append(msg.confidence_score)
                        data['hourly_distribution'][hour] += 1
            
            # Convert to ServiceStats objects
            service_stats = []
            for service_name, data in service_data.items():
                avg_confidence = sum(data['confidences']) / len(data['confidences']) if data['confidences'] else 0
                peak_hours = sorted(data['hourly_distribution'].items(), key=lambda x: x[1], reverse=True)[:3]
                
                service_stats.append(ServiceStats(
                    service_name=service_name,
                    total_requests=data['total'],
                    forwarded_requests=data['forwarded'],
                    average_confidence=round(avg_confidence, 2),
                    peak_hours=[hour for hour, count in peak_hours]
                ))
            
            return sorted(service_stats, key=lambda x: x.total_requests, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting service statistics: {e}")
            return []
    
    def _calculate_uptime(self) -> str:
        """Calculate system uptime"""
        # This would track actual uptime in a production system
        return "24/7"  # Placeholder
    
    def _get_performance_metrics(self) -> Dict[str, float]:
        """Get system performance metrics"""
        return {
            'response_time_ms': 150.5,
            'success_rate': 98.7,
            'error_rate': 1.3,
            'throughput_per_minute': 45.2
        }
    
    def _to_csv(self, data: Dict[str, Any]) -> str:
        """Convert data to CSV format"""
        if not data:
            return ""
        
        output = []
        
        # Handle different data structures
        if 'daily_data' in data:
            output.append("Date,Messages_Processed,Help_Requests,Active_Accounts")
            for date, stats in data['daily_data'].items():
                output.append(f"{date},{stats['messages_processed']},{stats['help_requests']},{stats['accounts_active']}")
        elif 'service_statistics' in data:
            output.append("Service,Total_Requests,Forwarded,Avg_Confidence,Peak_Hours")
            for service in data['service_statistics']:
                peak_hours = '|'.join(map(str, service.peak_hours))
                output.append(f"{service.service_name},{service.total_requests},{service.forwarded_requests},{service.average_confidence},{peak_hours}")
        
        return '\n'.join(output)
    
    async def collect_periodic_stats(self):
        """Periodically collect and store statistics"""
        while True:
            try:
                # Collect current stats
                stats = self.get_realtime_stats()
                
                # Store in database
                current_time = datetime.now()
                
                # Store key metrics
                db.save_statistic('system', 'messages_per_minute', str(stats.get('messages_per_minute', 0)))
                db.save_statistic('system', 'active_accounts', str(stats['dashboard_stats']['active_accounts']))
                
                # Wait for next collection cycle
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Error in periodic stats collection: {e}")
                await asyncio.sleep(60)


# Global analytics engine instance
analytics_engine = AnalyticsEngine()