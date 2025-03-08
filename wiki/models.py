from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class Writeup(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Gunakan Markdown untuk formatting")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True, help_text="Toggle visibilitas writeup")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        # Jika update, simpan versi sebelumnya
        if self.pk:
            orig = Writeup.objects.get(pk=self.pk)
            if orig.content != self.content or orig.title != self.title:
                WriteupVersion.objects.create(
                    writeup=self,
                    title=orig.title,
                    content=orig.content,
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class WriteupVersion(models.Model):
    writeup = models.ForeignKey(Writeup, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Versi {self.pk} dari {self.writeup.title}"