from django.contrib import admin
from .models import Member, StudyMaterial  # StudyMaterial ko import karo

class MemberAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "phone", "joined_date")

class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "class_name", "created_at")
    list_filter = ("subject", "class_name") # Side mein filter aayega

admin.site.register(Member, MemberAdmin)
admin.site.register(StudyMaterial, StudyMaterialAdmin) # Ise register karo