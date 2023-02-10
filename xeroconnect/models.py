from django.db import models

"""
class XeroCredentials(models.Model):
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    redirect_uri = models.URLField()
    access_token = models.TextField()
    expires_in = models.IntegerField()
    expires_at = models.DateTimeField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save_token(self, token):
        self.access_token = token['access_token']
        self.expires_in = token['expires_in']
        expires_at = datetime.datetime.now() + timedelta(seconds=self.expires_in)
        self.expires_at = expires_at
        self.refresh_token = token.get('refresh_token', '')
        self.save()


class PLReport(models.Model):
    period = models.CharField(max_length=255)
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

"""


