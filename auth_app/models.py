from django.db import models

class AccessLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    endpoint = models.CharField(max_length=255)
    parameters = models.TextField()
    status = models.CharField(max_length=50)

class VerificationCode(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)


class DynamicDataModel(models.Model):
    some_field = models.CharField(max_length=100)

    class Meta:
        managed = False


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
