# Assuming your NewsArticle model looks something like this:
from django.db import models


class NewsArticle(models.Model):
    symbol = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    url = models.URLField()
    url_to_image = models.URLField(null=True, blank=True)  # Ensure this is present
    source_name = models.CharField(max_length=255, null=True,
                                   blank=True)  # If you're storing the source name separately
    published_at = models.DateTimeField()
    summary = models.TextField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)  # For tracking when it was fetched

    def __str__(self):
        return self.title
