from django.db import models
from django.contrib import auth

# Create your models here.
class Snippet(models.Model):
    #user = models.ForeignKey(auth.user)
    code = models.TextField()
    prefix = models.CharField(max_length=256)
    last_updated = models.DateTimeField()
    
    def __unicode__(self):
        return "snippet<name="+self.prefix+", last_edited="+str(self.last_updated)+">"

# db of recently saved/evaluated snippets on website - across users
class RecentSnippets(models.Model):
    LIMIT = 5000 #show last 40 on website, and delete entries older than 5000
    prefix = models.CharField(max_length=256)
    search_date = models.DateTimeField('date searched')
    was_saved = models.BooleanField(default=False)
    
    # clear one half of LRU words.
    @staticmethod
    def cleanup_table_cache():
        deleted = 0
        if RecentSnippets.objects.count() > (RecentSnippets.LIMIT-5):
            objs = RecentSnippets.objects.all().order_by("-search_date")
            C = RecentSnippets.objects.count()
            for itr in range(C-1,RecentSnippets.LIMIT/2,-1):
                objs[itr].delete()
                deleted += 1
        return deleted

    def __unicode__(self):
        return self.prefix
