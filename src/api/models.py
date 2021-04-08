from django.contrib.auth import password_validation
from django.contrib.auth.models import AbstractUser
from django.db import models

from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase


class CustomUser(AbstractUser):
    administrator = models.BooleanField(default=False)
    dealer = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                               blank=True, related_name='children')

    def save(self, *args, **kwargs):
        if self.password is not None:
            password_validation.password_changed(self.password, self)
            if not self.is_superuser:
                self.set_password(self.password)
            super().save(*args, **kwargs)


class Plotter(models.Model):
    title = models.CharField(max_length=50)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='plotter_creator')
    pattern = models.ManyToManyField('Pattern', through='api.PlotterPattern', related_name='plotter_through_pattern')
    users = models.ManyToManyField(CustomUser, blank=True, related_name='plotters_users')
    whole_amount = models.PositiveIntegerField(default=0)

    class Meta:
        default_permissions = ('add', 'change', 'delete')
        permissions = (
            ('view_plotter', 'Can view plotter'),
        )

    def __str__(self):
        return self.title


class Pattern(models.Model):
    title = models.CharField(max_length=50)
    allowed_amount = models.PositiveIntegerField(default=0)
    printed_num = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True,
                             blank=True, related_name='pattern_user')

    def __str__(self):
        return self.title


class PlotterPattern(models.Model):
    plotter = models.ForeignKey(Plotter, on_delete=models.CASCADE, related_name='plotterpattern_plotter')
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name='plotterpattern_pattern')
    stats = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        unique_together = ('plotter', 'pattern')


class ParentUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='child_perms')


class PlotterUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Plotter, on_delete=models.CASCADE)


class PlotterGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Plotter, on_delete=models.CASCADE)


class PatternUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Pattern, on_delete=models.CASCADE)


class PatternGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Pattern, on_delete=models.CASCADE)
