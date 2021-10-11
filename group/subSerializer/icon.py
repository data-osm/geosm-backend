from ..subModels.icon import Icon, TagsIcon
from rest_framework import serializers
import ast

class TagsIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagsIcon
        fields ="__all__"

class IconSerializer(serializers.ModelSerializer):
    """
        Icon serializer
    """
    tags = TagsIconSerializer(many=True, required=False)

    class Meta:
        model = Icon
        fields = "__all__"
        # fields = ['icon_id', 'name', 'tags', 'category']
    def to_representation(self, instance):
        representation = super(IconSerializer, self).to_representation(instance)
        full_path =  instance.path.url
        representation['path'] = full_path
        return representation
    
    def create(self, validate_data):
        if 'tags' in validate_data:
            list_tags =  ast.literal_eval(validate_data.pop('tags'))
            icon = Icon.objects.create(**validate_data)
            for api_tag in list_tags:
                tag = TagsIcon.objects.filter(name=api_tag)
                if tag.exists() == False:
                    icon.tags.create(name=api_tag)
                else:
                    icon.tags.add(tag.first().pk)
        else:
            icon = Icon.objects.create(**validate_data)
        
        return icon

    def update(self, instance, validate_data):
        icon = instance
        if 'tags' in validate_data:
            list_tags = ast.literal_eval(validate_data.pop('tags'))

            for existing_tag in icon.tags.all():
                icon.tags.remove(existing_tag)

            for api_tag in list_tags:
                tag = TagsIcon.objects.filter(name=api_tag)
                if tag.exists() == False:
                    icon.tags.create(name=api_tag)
                else:
                    icon.tags.add(tag.first().pk)

            return icon
        else:
            return icon
