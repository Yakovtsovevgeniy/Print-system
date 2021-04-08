from django.contrib.auth.models import Group, Permission
from django.db.models import Sum
from guardian.shortcuts import assign_perm, remove_perm
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import CustomUser, Plotter, Pattern, PlotterUserObjectPermission, PatternUserObjectPermission, \
    PlotterGroupObjectPermission, PlotterPattern
from .serializers import PlotterSerializer, PatternSerializer, UserSerializerDealer, PermissionSerializer, \
    PlotterUserObjectPermissionSerializer, PatternUserObjectPermissionSerializer, UserSerializerAdmin, \
    PlotterPatternStatSerializer, PlotterPatternStatSerializerAdmin, PlotterSerializerAdmin, PatternSerializerAdmin, \
    PlotterSerializerDealer


class UserModelView(viewsets.ModelViewSet):
    serializer_class = UserSerializerDealer
    queryset = CustomUser.objects
    permission_classes = [IsAuthenticated]
    permission_required = ['view_customuser', 'add_customuser']

    def get_queryset(self):
        if self.request.user in Group.objects.get(name='dealer').user_set.all():
            queryset = self.request.user.children.all()
            return queryset
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            queryset = self.queryset
            return queryset

    def get_serializer(self, *args, **kwargs):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            serializer_class = UserSerializerAdmin
        else:
            serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        administrator_group, created = Group.objects.get_or_create(name='administrator')
        dealer_group, created = Group.objects.get_or_create(name='dealer')
        if self.request.user in dealer_group.user_set.all() or \
                self.request.user in administrator_group.user_set.all() or self.request.user.is_superuser:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        administrator_group, created = Group.objects.get_or_create(name='administrator')
        dealer_group, created = Group.objects.get_or_create(name='dealer')
        if self.request.user in administrator_group.user_set.all() and administrator_group.permissions.filter(
                codename='add_customuser') or self.request.user.is_superuser or self.request.user in dealer_group.user_set.all():
            serializer = self.get_serializer(data=request.data)
            if self.request.user.id == request.data['parent']:
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                customuser = CustomUser.objects.get(username=serializer.data['username'])

                if self.request.user in administrator_group.user_set.all() and administrator_group.permissions.filter(
                        codename='add_customuser') or self.request.user.is_superuser:
                    if request.data['administrator']:
                        administrator_group.permissions.set(Permission.objects.all())
                        administrator_group.user_set.add(customuser)
                    if request.data['dealer']:
                        customuser.groups.add(dealer_group)
                if self.request.user in dealer_group.user_set.all():
                    assign_perm('view_customuser', self.request.user, customuser)
                    assign_perm('change_customuser', self.request.user, customuser)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return Response(f'parent must be {self.request.user}, but not other, your id is {self.request.user.id}',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)


class PlotterModelView(viewsets.ModelViewSet):
    serializer_class = PlotterSerializer
    queryset = Plotter.objects
    permission_classes = [IsAuthenticated]
    permission_required = ['view_plotter', 'change_plotter']

    def get_queryset(self):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            queryset = self.queryset
            return queryset
        if Plotter.objects.filter(creator_id=self.request.user.id):
            queryset = self.request.user.plotter_creator
            return queryset
        if self.request.user:
            queryset = self.request.user.plotters_users
            return queryset

    def get_serializer(self, *args, **kwargs):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            serializer_class = PlotterSerializerAdmin
        elif self.request.user in Group.objects.get(name='dealer').user_set.all() and self.request.user.plotter_creator:
            serializer_class = PlotterSerializerDealer
        else:
            serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        admin_group = Group.objects.get(name='administrator')
        perm = Permission.objects.filter(codename=self.permission_required[0])
        if self.request.user in admin_group.user_set.all() and PlotterGroupObjectPermission.objects.filter(
                group=admin_group.id).filter(permission_id=perm.values_list('id', flat=True)[0]):
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        dealer_group = Group.objects.get(name='dealer')
        administrator_group = Group.objects.get(name='administrator')
        if self.request.user in dealer_group.user_set.all() or \
                self.request.user in administrator_group.user_set.all() or self.request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            if self.request.user.id == request.data['creator']:
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                plot_subq = Plotter.objects.filter(title=serializer.data['title'])
                if self.request.user in dealer_group.user_set.all():
                    assign_perm('add_plotter', self.request.user, plot_subq)
                    assign_perm('view_plotter', self.request.user, plot_subq)
                    assign_perm('change_plotter', self.request.user, plot_subq)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return Response(f'creator must be {self.request.user}, but not other, your id is {self.request.user.id}',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        dealer_group = Group.objects.get(name='dealer')
        administrator_group = Group.objects.get(name='administrator')
        if self.request.user in dealer_group.user_set.all() or \
                self.request.user in administrator_group.user_set.all() or self.request.user.is_superuser:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)


class PatternModelView(viewsets.ModelViewSet):
    serializer_class = PatternSerializer
    queryset = Pattern.objects
    permission_classes = [IsAuthenticated]
    permission_required = ['view_pattern']

    def get_queryset(self):
        perm = Permission.objects.filter(codename=self.permission_required[0])
        if self.request.user.patternuserobjectpermission_set.filter(permission=perm.values('id')[0]['id']):
            queryset = self.request.user.pattern_user.all()
            return queryset
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() and Group.objects.get(
            name='administrator').permissions.filter(codename='view_pattern') or self.request.user.is_superuser:
            queryset = self.queryset
            return queryset

    def get_serializer(self, *args, **kwargs):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() and Group.objects.get(
            name='administrator').permissions.filter(codename='view_pattern') or self.request.user.is_superuser:
            serializer_class = PatternSerializerAdmin
        else:
            serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        if self.request.user not in Group.objects.get(name='dealer').user_set.all():
            administrator_group = Group.objects.get(name='administrator')
            if self.request.user in administrator_group.user_set.all() or self.request.user.is_superuser:
                queryset = self.filter_queryset(self.get_queryset())
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            else:
                queryset = self.filter_queryset(self.get_queryset())
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        admin_group = Group.objects.get(name='administrator')
        if self.request.user in admin_group.user_set.all() and admin_group.permissions.filter(
                codename='add_pattern') or self.request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            patt_subq = Pattern.objects.get(title=serializer.data['title'])
            if not serializer.data['user'] == None:
                assign_perm('view_pattern', CustomUser.objects.get(id=request.data['user']), patt_subq)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        admin_group = Group.objects.get(name='administrator')
        if self.request.user in admin_group.user_set.all() and admin_group.permissions.filter(
                codename='change_pattern') or self.request.user.is_superuser:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            if request.data.get("user") and not instance.user == request.data['user']:
                if instance.user:
                    remove_perm('view_pattern', instance.user, instance)
                assign_perm('view_pattern', CustomUser.objects.get(id=request.data['user']), instance)
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)


class PlotterPatternModelView(viewsets.ModelViewSet):
    serializer_class = PlotterPatternStatSerializer
    queryset = PlotterPattern.objects
    permission_classes = [IsAuthenticated]
    permission_required = ['view_plotterpattern', 'add_plotterpattern', 'change_plotterpattern',
                           'delete_plotterpattern']

    def get_queryset(self):
        if self.request.user in Group.objects.get(
                name='administrator').user_set.all() or self.request.user.is_superuser:
            queryset = self.queryset
            return queryset
        if self.request.user.pattern_user and self.request.user.patternuserobjectpermission_set:
            queryset = PlotterPattern.objects.filter(pattern__in=self.request.user.pattern_user.values('id'))
            return queryset

    def get_serializer(self, *args, **kwargs):
        admin_group = Group.objects.get(name='administrator')
        if self.request.user in admin_group.user_set.all() and admin_group.permissions.filter(
                codename=self.permission_required[0]) or self.request.user.is_superuser:
            serializer_class = PlotterPatternStatSerializerAdmin
        else:
            serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        if self.request.user not in Group.objects.get(name='dealer').user_set.all():
            admin_group = Group.objects.get(name='administrator')
            if self.request.user in admin_group.user_set.all() and admin_group.permissions.filter(
                    codename=self.permission_required[0]) or self.request.user.is_superuser or \
                    self.request.user.pattern_user and self.request.user.patternuserobjectpermission_set:
                queryset = self.filter_queryset(self.get_queryset())

                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        admin_group = Group.objects.get(name='administrator')
        if self.request.user in admin_group.user_set.all() and admin_group.permissions.filter(
                codename=self.permission_required[1]) or self.request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        admin_group = Group.objects.get(name='administrator')
        if self.request.user in admin_group.user_set.all() and admin_group.permissions.filter(
                codename=self.permission_required[
                    2]) or self.request.user.is_superuser or self.request.user.pattern_user and self.request.user.patternuserobjectpermission_set:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            allowed_amount = Pattern.objects.filter(id=instance.pattern.id).values_list('allowed_amount', flat=True)[0]
            if int(request.data['stats']) >= 0:
                left_amount = allowed_amount - int(request.data['stats'])
                printed_num = Pattern.objects.filter(id=instance.pattern.id).values_list('printed_num', flat=True)[0]
                new_printed_num = printed_num + int(request.data['stats'])

                if left_amount < 0:
                    return Response(
                        f"overprinted, trying to print {request.data['stats']},but {allowed_amount} prints left ",
                        status=status.HTTP_403_FORBIDDEN)
                else:
                    Pattern.objects.filter(id=instance.pattern.id).update(allowed_amount=left_amount)
                    serializer.validated_data['stats'] += instance.stats
                    Pattern.objects.filter(id=instance.pattern.id).update(printed_num=new_printed_num)

                whole_amount = Plotter.objects.filter(id=instance.plotter.id).aggregate(
                    whole_amount=Sum('plotterpattern_plotter__stats'))['whole_amount']
                Plotter.objects.filter(id=instance.plotter.id).update(whole_amount=whole_amount)

                self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response('The number must be positive', status=status.HTTP_403_FORBIDDEN)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        admin_group = Group.objects.get(name='administrator')
        if self.request.user in admin_group.user_set.all() and admin_group.permissions.filter(
                codename=self.permission_required[3]) or self.request.user.is_superuser:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response("forbidden", status=status.HTTP_403_FORBIDDEN)


class PermissionsModelView(viewsets.ModelViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects
    permission_classes = [IsAuthenticated, IsAdminUser]


class PlotterUserObjectPermissionModelView(viewsets.ModelViewSet):
    serializer_class = PlotterUserObjectPermissionSerializer
    queryset = PlotterUserObjectPermission.objects
    permission_classes = [IsAuthenticated, IsAdminUser]


class PatternUserObjectPermissionModelView(viewsets.ModelViewSet):
    serializer_class = PatternUserObjectPermissionSerializer
    queryset = PatternUserObjectPermission.objects
    permission_classes = [IsAuthenticated, IsAdminUser]
