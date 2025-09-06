from django.core.management.base import BaseCommand
from decimal import Decimal
from properties.models import Property


class Command(BaseCommand):
    help = 'Populate the database with sample property data'

    def handle(self, *args, **options):
        """
        Creates sample property data for testing caching functionality.
        """
        sample_properties = [
            {
                'title': 'Luxury Downtown Apartment',
                'description': 'Beautiful 2-bedroom apartment in the heart of downtown with stunning city views, modern amenities, and walking distance to all major attractions.',
                'price': Decimal('2500.00'),
                'location': 'Downtown, New York'
            },
            {
                'title': 'Suburban Family Home',
                'description': 'Spacious 4-bedroom family home with large backyard, garage, and quiet neighborhood. Perfect for families with children.',
                'price': Decimal('450000.00'),
                'location': 'Westchester, NY'
            },
            {
                'title': 'Cozy Studio Near University',
                'description': 'Perfect studio apartment for students, just 5 minutes walk from campus. Furnished and utilities included.',
                'price': Decimal('1200.00'),
                'location': 'Cambridge, MA'
            },
            {
                'title': 'Beachfront Condo',
                'description': 'Stunning oceanfront condominium with private beach access, 3 bedrooms, and panoramic ocean views.',
                'price': Decimal('750000.00'),
                'location': 'Miami Beach, FL'
            },
            {
                'title': 'Modern Loft in Arts District',
                'description': 'Industrial-style loft with exposed brick walls, high ceilings, and premium finishes. Located in trendy arts district.',
                'price': Decimal('3200.00'),
                'location': 'Los Angeles, CA'
            },
            {
                'title': 'Historic Brownstone',
                'description': 'Beautifully restored 19th-century brownstone with original details, 5 bedrooms, and private garden.',
                'price': Decimal('1250000.00'),
                'location': 'Brooklyn, NY'
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Peaceful cabin in the mountains with fireplace, deck, and hiking trails. Perfect weekend getaway.',
                'price': Decimal('320000.00'),
                'location': 'Aspen, CO'
            },
            {
                'title': 'Tech Hub Apartment',
                'description': 'Modern 1-bedroom apartment in the tech district with smart home features and rooftop amenities.',
                'price': Decimal('2800.00'),
                'location': 'Seattle, WA'
            },
            {
                'title': 'Victorian Mansion',
                'description': 'Grand Victorian mansion with original architecture, 8 bedrooms, and extensive grounds. Rich in history.',
                'price': Decimal('2200000.00'),
                'location': 'San Francisco, CA'
            },
            {
                'title': 'Waterfront Townhouse',
                'description': 'Contemporary townhouse with private dock, 3 levels, and panoramic water views. Move-in ready.',
                'price': Decimal('890000.00'),
                'location': 'Baltimore, MD'
            }
        ]

        # Clear existing properties
        Property.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared existing properties'))

        # Create new properties
        created_count = 0
        for prop_data in sample_properties:
            property_obj = Property.objects.create(**prop_data)
            created_count += 1
            self.stdout.write(f'Created: {property_obj.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample properties')
        )
