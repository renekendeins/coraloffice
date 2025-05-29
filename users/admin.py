
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity, DivingSite, InventoryItem, DivingGroup, DivingGroupMember

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(Customer)
admin.site.register(DiveSchedule)
admin.site.register(DiveActivity)
admin.site.register(CustomerDiveActivity)
admin.site.register(DivingSite)
admin.site.register(InventoryItem)
admin.site.register(DivingGroup)
admin.site.register(DivingGroupMember)
