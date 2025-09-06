from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from decimal import Decimal
from unittest.mock import patch
import json

from .models import Property
from .utils import get_all_properties, get_redis_cache_metrics, get_property_by_id


class PropertyModelTest(TestCase):
    """Test cases for Property model"""
    
    def setUp(self):
        self.property_data = {
            'title': 'Test Property',
            'description': 'A test property description',
            'price': Decimal('100000.00'),
            'location': 'Test City'
        }
    
    def test_property_creation(self):
        """Test property creation"""
        property_obj = Property.objects.create(**self.property_data)
        self.assertEqual(property_obj.title, 'Test Property')
        self.assertEqual(property_obj.price, Decimal('100000.00'))
        self.assertTrue(property_obj.created_at)
    
    def test_property_str(self):
        """Test property string representation"""
        property_obj = Property.objects.create(**self.property_data)
        expected = f"{property_obj.title} - ${property_obj.price}"
        self.assertEqual(str(property_obj), expected)


class CachingUtilsTest(TestCase):
    """Test cases for caching utilities"""
    
    def setUp(self):
        cache.clear()
        self.property1 = Property.objects.create(
            title='Property 1',
            description='Description 1',
            price=Decimal('100000.00'),
            location='Location 1'
        )
        self.property2 = Property.objects.create(
            title='Property 2',
            description='Description 2',
            price=Decimal('200000.00'),
            location='Location 2'
        )
    
    def test_get_all_properties_cache_miss(self):
        """Test get_all_properties when cache is empty"""
        # Ensure cache is empty
        cache.delete('all_properties')
        
        properties = get_all_properties()
        self.assertEqual(len(properties), 2)
        
        # Check if data is now cached
        cached_properties = cache.get('all_properties')
        self.assertIsNotNone(cached_properties)
        self.assertEqual(len(cached_properties), 2)
    
    def test_get_all_properties_cache_hit(self):
        """Test get_all_properties when cache contains data"""
        # First call to populate cache
        get_all_properties()
        
        # Mock the database query to ensure it's not called
        with patch('properties.models.Property.objects.all') as mock_query:
            properties = get_all_properties()
            self.assertEqual(len(properties), 2)
            # Database query should not be called
            mock_query.assert_not_called()
    
    def test_get_property_by_id(self):
        """Test individual property caching"""
        # Cache miss
        property_obj = get_property_by_id(self.property1.id)
        self.assertEqual(property_obj.title, 'Property 1')
        
        # Check if cached
        cached_property = cache.get(f'property_{self.property1.id}')
        self.assertIsNotNone(cached_property)
        
        # Cache hit
        with patch('properties.models.Property.objects.get') as mock_get:
            property_obj = get_property_by_id(self.property1.id)
            self.assertEqual(property_obj.title, 'Property 1')
            mock_get.assert_not_called()


class ViewsTest(TestCase):
    """Test cases for views"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
        self.property1 = Property.objects.create(
            title='Test Property 1',
            description='Test Description 1',
            price=Decimal('150000.00'),
            location='Test Location 1'
        )
        self.property2 = Property.objects.create(
            title='Test Property 2',
            description='Test Description 2',
            price=Decimal('250000.00'),
            location='Test Location 2'
        )
    
    def test_property_list_view(self):
        """Test property list API view"""
        url = reverse('properties:property_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('properties', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 2)
        self.assertTrue(data['cached'])
    
    def test_property_detail_view(self):
        """Test property detail view"""
        url = reverse('properties:property_detail', args=[self.property1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['title'], 'Test Property 1')
        self.assertEqual(data['id'], self.property1.id)
    
    def test_property_detail_not_found(self):
        """Test property detail view with non-existent ID"""
        url = reverse('properties:property_detail', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_cache_metrics_view(self):
        """Test cache metrics view"""
        url = reverse('properties:cache_metrics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('cache_metrics', data)
        self.assertIn('message', data)
    
    def test_clear_cache_view(self):
        """Test cache clearing view"""
        # First populate cache
        get_all_properties()
        self.assertIsNotNone(cache.get('all_properties'))
        
        # Clear cache via view
        url = reverse('properties:clear_cache')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('message', data)
        
        # Check that cache is cleared
        self.assertIsNone(cache.get('all_properties'))


class SignalsTest(TestCase):
    """Test cases for cache invalidation signals"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_invalidation_on_create(self):
        """Test cache invalidation when property is created"""
        # Populate cache
        get_all_properties()
        self.assertIsNotNone(cache.get('all_properties'))
        
        # Create new property (should trigger signal)
        Property.objects.create(
            title='New Property',
            description='New Description',
            price=Decimal('300000.00'),
            location='New Location'
        )
        
        # Cache should be invalidated
        self.assertIsNone(cache.get('all_properties'))
    
    def test_cache_invalidation_on_update(self):
        """Test cache invalidation when property is updated"""
        property_obj = Property.objects.create(
            title='Original Property',
            description='Original Description',
            price=Decimal('300000.00'),
            location='Original Location'
        )
        
        # Populate cache
        get_all_properties()
        get_property_by_id(property_obj.id)
        
        self.assertIsNotNone(cache.get('all_properties'))
        self.assertIsNotNone(cache.get(f'property_{property_obj.id}'))
        
        # Update property (should trigger signal)
        property_obj.title = 'Updated Property'
        property_obj.save()
        
        # Cache should be invalidated
        self.assertIsNone(cache.get('all_properties'))
        self.assertIsNone(cache.get(f'property_{property_obj.id}'))
    
    def test_cache_invalidation_on_delete(self):
        """Test cache invalidation when property is deleted"""
        property_obj = Property.objects.create(
            title='Property to Delete',
            description='Description',
            price=Decimal('300000.00'),
            location='Location'
        )
        
        # Populate cache
        get_all_properties()
        get_property_by_id(property_obj.id)
        
        self.assertIsNotNone(cache.get('all_properties'))
        self.assertIsNotNone(cache.get(f'property_{property_obj.id}'))
        
        # Delete property (should trigger signal)
        property_obj.delete()
        
        # Cache should be invalidated
        self.assertIsNone(cache.get('all_properties'))
        self.assertIsNone(cache.get(f'property_{property_obj.id}'))
