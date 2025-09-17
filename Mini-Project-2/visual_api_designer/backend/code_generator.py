from rest_framework import serializers
from .models import APIProject, GeneratedProject


class APIProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIProject
        fields = ["id", "name", "description", "schema", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_schema(self, value):
        """Validate the visual design schema"""
        required_keys = ["models", "relationships"]

        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"Schema must contain '{key}' key")

        # Validate models structure
        if not isinstance(value["models"], list):
            raise serializers.ValidationError("Schema 'models' must be a list")

        for model in value["models"]:
            if "name" not in model or "fields" not in model:
                raise serializers.ValidationError(
                    "Each model must have 'name' and 'fields'"
                )

        return value


class GeneratedProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedProject
        fields = ["api_project", "zip_file", "generated_at"]
