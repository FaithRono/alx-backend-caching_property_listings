import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Property)
def invalidate_cache_on_property_save(sender, instance, created, **kwargs):
    """
    Signal handler to invalidate cache when a Property is created or updated.
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    # Invalidate the all_properties cache
    cache.delete('all_properties')
    
    # Also invalidate individual property cache if it exists
    cache.delete(f'property_{instance.id}')
    
    action = "created" if created else "updated"
    logger.info(f"Property {instance.id} {action}. Cache invalidated for 'all_properties' and 'property_{instance.id}'")


@receiver(post_delete, sender=Property)
def invalidate_cache_on_property_delete(sender, instance, **kwargs):
    """
    Signal handler to invalidate cache when a Property is deleted.
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments
    """
    # Invalidate the all_properties cache
    cache.delete('all_properties')
    
    # Also invalidate individual property cache
    cache.delete(f'property_{instance.id}')
    
    logger.info(f"Property {instance.id} deleted. Cache invalidated for 'all_properties' and 'property_{instance.id}'")
