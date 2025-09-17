from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    reading_time = serializers.ReadOnlyField()
    category_display = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "excerpt",
            "category",
            "category_display",
            "image",
            "image_url",
            "is_published",
            "view_count",
            "reading_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "view_count"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long."
            )
        return value.strip()

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Content must be at least 10 characters long."
            )
        return value.strip()


class CategoryStatsSerializer(serializers.Serializer):
    category = serializers.CharField()
    category_display = serializers.CharField()
    count = serializers.IntegerField()


class BlogStatsSerializer(serializers.Serializer):
    total_posts = serializers.IntegerField()
    total_views = serializers.IntegerField()
    categories = CategoryStatsSerializer(many=True)
