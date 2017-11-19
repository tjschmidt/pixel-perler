import os

from django.db import models


class Color(models.Model):
    """
    Abstract class that represents an RGBA color
    """
    red = models.PositiveSmallIntegerField()
    green = models.PositiveSmallIntegerField()
    blue = models.PositiveSmallIntegerField()
    alpha = models.PositiveSmallIntegerField(default=255)

    def __str__(self):
        return '({}, {}, {})'.format(self.red, self.green, self.blue)

    class Meta:
        abstract = True


class BeadBrand(models.Model):
    """
    Model containing an enumeration of various bead brands
    """
    name = models.TextField()


class BeadColor(Color):
    """
    Model that associates an RGB color with a specific bead
    """
    brand = models.ForeignKey(BeadBrand, on_delete=models.CASCADE)
    name = models.TextField()
    size_mm = models.FloatField(default=5)

    def __str__(self):
        return '{} ({})'.format(self.name, self.brand.name)


class PixelColor(Color):
    """
    Model that will map all possible RBG values to a specific bead
    """
    beads = models.ManyToManyField(BeadColor, through='BeadDistance', through_fields=('pixel_color', 'bead_color'))


class BeadDistance(models.Model):
    """
    Model that augments the many-to-many relationship between pixel values and the nearest bead color
    """
    id = models.BigAutoField(primary_key=True)
    pixel_color = models.ForeignKey(PixelColor, on_delete=models.CASCADE)
    bead_color = models.ForeignKey(BeadColor, on_delete=models.CASCADE)
    distance = models.FloatField()

    class Meta:
        ordering = ['pixel_color', 'distance']


class ImageSession(models.Model):
    session_key = models.TextField(primary_key=True)
    src_file = models.TextField()
    processed_file = models.TextField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        for fp in (self.src_file, self.processed_file):
            if fp is not None and os.path.isfile(fp):
                os.remove(fp)
        super().delete(*args, **kwargs)
