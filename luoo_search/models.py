from django.db import models


# Create your models here.
class QQ(models.Model):
    song_id = models.CharField(max_length=100)
    song_url = models.CharField(max_length=1000)

    def __str__(self):
        return "qq %s: %s" % (self.song_id, self.song_url)


class Netease(models.Model):
    song_id = models.CharField(max_length=100)
    song_url = models.CharField(max_length=1000)

    def __str__(self):
        return "netease %s: %s" % (self.song_id, self.song_url)
