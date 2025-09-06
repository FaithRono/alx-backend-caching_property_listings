from django.db import models


class Property(models.Model):
    """
    Property model for storing real estate listings.
    """
    title = models.CharField(max_length=200, help_text="Property title")
    description = models.TextField(help_text="Detailed property description")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Property price in USD"
    )
    location = models.CharField(max_length=100, help_text="Property location")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} - ${self.price}"
