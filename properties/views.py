import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from django.core.paginator import Paginator
from .models import Property
from .utils import get_all_properties, get_redis_cache_metrics, get_property_by_id

logger = logging.getLogger(__name__)


@cache_page(60 * 15)  # Cache for 15 minutes
def property_list(request):
    """
    View to display all properties with view-level caching.
    Cached for 15 minutes using @cache_page decorator.
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: JSON response containing property data
    """
    logger.info("property_list view called")
    
    # Use low-level cached function to get properties
    properties = get_all_properties()
    
    # Convert to list of dictionaries for JSON response
    property_data = []
    for prop in properties:
        property_data.append({
            'id': prop.id,
            'title': prop.title,
            'description': prop.description,
            'price': float(prop.price),
            'location': prop.location,
            'created_at': prop.created_at.isoformat(),
        })
    
    response_data = {
        'properties': property_data,
        'count': len(property_data),
        'cached': True
    }
    
    return JsonResponse(response_data)


def property_list_html(request):
    """
    HTML view for property listings with pagination.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered HTML template
    """
    logger.info("property_list_html view called")
    
    # Use cached function to get properties
    properties = get_all_properties()
    
    # Implement pagination
    paginator = Paginator(properties, 10)  # Show 10 properties per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_properties': len(properties)
    }
    
    return render(request, 'properties/property_list.html', context)


def property_detail(request, property_id):
    """
    View to display a single property with caching.
    
    Args:
        request: HTTP request object
        property_id: ID of the property to display
        
    Returns:
        JsonResponse: JSON response containing property data
    """
    logger.info(f"property_detail view called for property ID: {property_id}")
    
    # Use cached function to get property
    property_obj = get_property_by_id(property_id)
    
    if not property_obj:
        return JsonResponse({'error': 'Property not found'}, status=404)
    
    property_data = {
        'id': property_obj.id,
        'title': property_obj.title,
        'description': property_obj.description,
        'price': float(property_obj.price),
        'location': property_obj.location,
        'created_at': property_obj.created_at.isoformat(),
    }
    
    return JsonResponse(property_data)


@require_http_methods(["GET"])
def cache_metrics(request):
    """
    View to display Redis cache metrics.
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: JSON response containing cache metrics
    """
    logger.info("cache_metrics view called")
    
    metrics = get_redis_cache_metrics()
    
    return JsonResponse({
        'cache_metrics': metrics,
        'message': 'Cache metrics retrieved successfully'
    })


def clear_cache(request):
    """
    View to manually clear the properties cache (for testing purposes).
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: JSON response confirming cache clearance
    """
    from django.core.cache import cache
    
    cache.delete('all_properties')
    logger.info("Cache manually cleared")
    
    return JsonResponse({
        'message': 'Cache cleared successfully'
    })
