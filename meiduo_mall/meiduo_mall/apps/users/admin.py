from django.contrib import admin

# Register your models here.
from users.models import User, Address


class UserAdmin(admin.ModelAdmin):
    list_display = ['mobile', 'email_active', 'default_address']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'province', 'city', 'district', 'title', 'mobile', 'place', 'tel', 'email', 'is_deleted']


admin.site.register(User,UserAdmin)
admin.site.register(Address,AddressAdmin)
