from django.db import models

TARGETS = (
    ('ACA', 'Academic'),
    ('GAM', 'Gaming'),
    ('SCL', 'Social'),
    ('SCT', 'Society'),
)


class EventType(models.Model):
    name = models.CharField(max_length=50)
    target = models.CharField(max_length=3, choices=TARGETS)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']