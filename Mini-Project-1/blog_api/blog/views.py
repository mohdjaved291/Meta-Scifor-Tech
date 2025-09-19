from django.db.models import Q, Sum
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Post
from .serializers import PostSerializer, CategoryStatsSerializer, BlogStatsSerializer
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os


def frontend_view(request):
    """Serve the frontend HTML file"""
    try:
        static_path = os.path.join(
            settings.BASE_DIR, "static", "frontend", "index.html"
        )
        with open(static_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type="text/html")
    except FileNotFoundError:
        return HttpResponse(
            "<h1>Frontend not found</h1><p>Please ensure frontend files are in static/frontend/</p>"
        )


@method_decorator(csrf_exempt, name="dispatch")
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "content", "excerpt"]
    ordering_fields = ["created_at", "updated_at", "title", "view_count"]
    ordering = ["-created_at"]

    # Add parsers to handle both JSON and multipart form data (for images)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_context(self):
        """Add request context for image URL generation"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True)

        category = self.request.query_params.get("category", None)
        if category:
            queryset = queryset.filter(category=category)

        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(content__icontains=search)
                | Q(excerpt__icontains=search)
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=["view_count"])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("Create request data:", request.data)
        print("Create request files:", request.FILES)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            print(f"Post created successfully: {post.id}")

            response_serializer = PostSerializer(post, context={"request": request})
            return Response(
                {
                    "message": "Post created successfully!",
                    "post": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        print("Serializer errors:", serializer.errors)
        return Response(
            {"message": "Failed to create post", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        print("Update request data:", request.data)
        print("Update request files:", request.FILES)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            post = serializer.save()
            print(f"Post updated successfully: {post.id}")

            response_serializer = PostSerializer(post, context={"request": request})
            return Response(
                {
                    "message": "Post updated successfully!",
                    "post": response_serializer.data,
                }
            )

        print("Serializer errors:", serializer.errors)
        return Response(
            {"message": "Failed to update post", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Post deleted successfully!"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def categories(self, request):
        categories_data = []

        for category_code, category_name in Post.CATEGORY_CHOICES:
            count = Post.objects.filter(
                category=category_code, is_published=True
            ).count()

            categories_data.append(
                {
                    "category": category_code,
                    "category_display": category_name,
                    "count": count,
                }
            )

        categories_data.sort(key=lambda x: (-x["count"], x["category_display"]))

        serializer = CategoryStatsSerializer(categories_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        total_posts = Post.objects.filter(is_published=True).count()
        total_views = (
            Post.objects.filter(is_published=True).aggregate(total=Sum("view_count"))[
                "total"
            ]
            or 0
        )

        categories_data = []
        for category_code, category_name in Post.CATEGORY_CHOICES:
            count = Post.objects.filter(
                category=category_code, is_published=True
            ).count()
            if count > 0:
                categories_data.append(
                    {
                        "category": category_code,
                        "category_display": category_name,
                        "count": count,
                    }
                )

        stats_data = {
            "total_posts": total_posts,
            "total_views": total_views,
            "categories": categories_data,
        }

        serializer = BlogStatsSerializer(stats_data)
        return Response(serializer.data)
