from django.db import models

class Policy(models.Model):   
    title = models.CharField(max_length=100)     
    description = models.TextField() 
    effective_date = models.DateTimeField()  
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.title} Policy ({self.id})"

