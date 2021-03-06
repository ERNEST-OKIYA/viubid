from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from simple_history.admin import SimpleHistoryAdmin
from users.models import User,Profile


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'
    fk_name = 'user'

# class UserProfileAdmin(admin.ModelAdmin):

#     fields = ('first_name','last_name','id_number','email','alternative_phone_number','date_of_birth','created_by','date_created',)

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'groups',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()


    class Meta:
        model = User
        fields = ('phone_number', 'password', 'is_active',)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin, SimpleHistoryAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    inlines =(ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('pk','phone_number', 'get_first_name','get_last_name', 'is_active',)
    list_filter = ('is_active',)
    list_select_related = ('profile', )

    fieldsets = (
        (None, {'fields': ('phone_number', 'password',)}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'groups',)}),

    )

    def get_first_name(self, instance):
        return instance.profile.first_name

    def get_last_name(self, instance):
        return instance.profile.last_name

    def get_id_number(self, instance):
        return instance.profile.id_number

    get_first_name.short_description = 'First Name'
    get_last_name.short_description = 'Last Name'
    

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number',

                       'password1', 'password2',)}
         ),
    )
    search_fields = ('phone_number',)
    ordering = ('phone_number',)
    #filter_horizontal = ()


admin.site.register(User, UserAdmin)


