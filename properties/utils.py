import logging
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property

logger = logging.getLogger(__name__)


def get_all_properties():
    """
    Retrieves all properties from cache or database.
    Implements low-level caching with 1-hour TTL.
    
    Returns:
        QuerySet: All Property objects
    """
    cache_key = 'all_properties'
    
    # Try to get from cache first
    properties = cache.get(cache_key)
    
    if properties is not None:
        logger.info(f"Cache HIT for key: {cache_key}")
        return properties
    
    # Cache miss - fetch from database
    logger.info(f"Cache MISS for key: {cache_key}")
    properties = list(Property.objects.all().order_by('-created_at'))
    
    # Store in cache for 1 hour (3600 seconds)
    cache.set(cache_key, properties, 3600)
    logger.info(f"Cached {len(properties)} properties with key: {cache_key}")
    
    return properties


def get_redis_cache_metrics():
    """
    Retrieves and analyzes Redis cache hit/miss metrics.
    
    Returns:
        dict: Dictionary containing cache metrics and hit ratio
    """
    try:
        # Get Redis connection
        redis_conn = get_redis_connection("default")
        
        # Get cache statistics from Redis INFO
        info = redis_conn.info()
        
        # Extract keyspace statistics
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        
        # Calculate hit ratio
        total_requests = keyspace_hits + keyspace_misses
        hit_ratio = (keyspace_hits / total_requests * 100) if total_requests > 0 else 0
        
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': round(hit_ratio, 2),
            'miss_ratio': round(100 - hit_ratio, 2)
        }
        
        # Log the metrics
        logger.info(f"Redis Cache Metrics: {metrics}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {str(e)}")
        return {
            'error': str(e),
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0,
            'miss_ratio': 0
        }


def invalidate_property_cache():
    """
    Invalidates the all_properties cache.
    Used by signal handlers when properties are modified.
    """
    cache_key = 'all_properties'
    cache.delete(cache_key)
    logger.info(f"Cache invalidated for key: {cache_key}")


def get_property_by_id(property_id):
    """
    Retrieves a specific property by ID with caching.
    
    Args:
        property_id (int): The ID of the property to retrieve
        
    Returns:
        Property: The property object or None if not found
    """
    cache_key = f'property_{property_id}'
    
    # Try to get from cache first
    property_obj = cache.get(cache_key)
    
    if property_obj is not None:
        logger.info(f"Cache HIT for key: {cache_key}")
        return property_obj
    
    # Cache miss - fetch from database
    try:
        property_obj = Property.objects.get(id=property_id)
        logger.info(f"Cache MISS for key: {cache_key}")
        
        # Store in cache for 30 minutes
        cache.set(cache_key, property_obj, 1800)
        logger.info(f"Cached property {property_id} with key: {cache_key}")
        
        return property_obj
        
    except Property.DoesNotExist:
        logger.info(f"Property with ID {property_id} not found")
        return None
