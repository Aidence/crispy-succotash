from django.db import models


class Comment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    entry = models.ForeignKey('feed.Entry', related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Comment')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date', )


class Bookmark(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    feed = models.ForeignKey('feed.Feed', related_name='bookmarks', db_index=True, on_delete=models.CASCADE)

    @staticmethod
    def get_bookmark(user, feed):
        return Bookmark.objects.filter(user=user, feed=feed).first()

    @staticmethod
    def user_has_bookmark(user, feed):
        return bool(Bookmark.get_bookmark(user, feed))
