from django.contrib.auth.models import Permission
from rest_framework import serializers

from .models import CustomUser, Pattern, Plotter, PlotterUserObjectPermission, PatternUserObjectPermission, \
    PlotterPattern


class RecursiveField(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class UserSerializerAdmin(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'groups', 'parent', 'children', 'administrator', 'dealer']


class UserSerializerDealer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'parent']


class PlotterSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = Plotter
        fields = '__all__'


class PlotterSerializerDealer(serializers.ModelSerializer):
    class Meta:
        model = Plotter
        fields = '__all__'


class PlotterSerializer(serializers.ModelSerializer):
    whole_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Plotter
        fields = ['id', 'title', 'whole_amount', 'pattern']


class PatternSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = '__all__'


class PatternSerializer(serializers.ModelSerializer):
    printed_num = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pattern
        fields = ['id', 'title', 'allowed_amount', 'printed_num']


class PlotterPatternStatSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = PlotterPattern
        fields = '__all__'


class PlotterPatternStatSerializer(serializers.ModelSerializer):
    plotter = serializers.PrimaryKeyRelatedField(read_only=True)
    pattern = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PlotterPattern
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class PlotterUserObjectPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlotterUserObjectPermission
        fields = '__all__'


class PatternUserObjectPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatternUserObjectPermission
        fields = '__all__'
