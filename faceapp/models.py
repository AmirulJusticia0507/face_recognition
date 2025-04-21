from django.db import models

class FaceComparisonLog(models.Model):
    foto_a = models.ImageField(upload_to='faces/')
    foto_b = models.ImageField(upload_to='faces/')
    model_used = models.CharField(max_length=50)
    similarity_percent = models.FloatField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.model_used} - {self.similarity_percent}% match"

class FaceLog(models.Model):
    foto_a = models.ImageField(upload_to='snapshots/')
    model_used = models.CharField(max_length=50)
    similarity_percent = models.FloatField(default=0)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Snapshot {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"