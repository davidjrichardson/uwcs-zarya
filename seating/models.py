from django.db import models
from django.contrib.auth.models import User

from events.models import EventPage


class SeatingRoom(models.Model):
    name = models.CharField(max_length=50)
    max_rows = models.IntegerField()
    max_cols = models.IntegerField()


class RevisionManager(models.Manager):
    def for_event(self, event):
        pass


class SeatingRevision(models.Model):
    objects = RevisionManager()

    event = models.ForeignKey(EventPage)
    creator = models.ForeignKey(User)
    revision_number = models.IntegerField()
    comment = models.CharField(blank=True, max_length=1024)

    # TODO: Create util functions when necessary

    class Meta:
        unique_together = ("event", "revision_number")


class SeatManager(models.Manager):
    def for_event(self, event):
        pass

    def maximums(self, event):
        pass


class Seat(models.Model):
    objects = SeatManager()

    user = models.ForeignKey(User)
    revision = models.ForeignKey(SeatingRevision)
    col = models.IntegerField()
    row = models.IntegerField()

    def __str__(self):
        return "{user} at ({col},{row})".format(user=self.user, col=self.col, row=self.row)
