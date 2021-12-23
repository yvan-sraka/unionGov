from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.views.generic.list import ListView
from django_filters.rest_framework import DjangoFilterBackend
from PIL import Image
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import Candidate, Config, ConfigRef, Position, User
from .serializers import (
    CandidateSerializer,
    ConfigRefSerializer,
    ConfigSerializer,
    PositionSerializer,
    RichConfigSerializer,
    UserSerializer,
    XConfigSerializer,
)


class CandidateAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CandidateSerializer
    queryset = Candidate.objects.all()


class ConfigAPIView(viewsets.ModelViewSet):
    # Do not enable: delete, neither partial update.
    http_method_names = [
        m
        for m in viewsets.ModelViewSet.http_method_names
        if m not in ("delete", "patch")
    ]
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["config_ref"]

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]

            if isinstance(data, list):
                kwargs["many"] = True
        return super(ConfigAPIView, self).get_serializer(*args, **kwargs)


class RichConfigAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Config.objects.all()
    serializer_class = RichConfigSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["config_ref"]


class XConfigAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Config.objects.all()
    serializer_class = XConfigSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["config_ref__config_ref"]


class ConfigRefAPIView(viewsets.ModelViewSet):
    # Get only a reference
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m in ("get", "post")
    ]
    serializer_class = ConfigRefSerializer
    queryset = ConfigRef.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["config_ref"]


class PositionAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = PositionSerializer
    queryset = Position.objects.all().order_by("id")


class UserAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class PositionListView(ListView):
    model = Position
    paginate_by = 20

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class CandidateListView(ListView):
    model = Candidate
    paginate_by = 20

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


def candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    return render(request, "gov/candidate.html", {"candidate": candidate})


# Turn a given color in image into RGBA transparency
def color2alpha(image, color=(7, 115, 125)):
    data = image.getdata()
    new_data = []
    for pixel in data:
        if pixel[0] == color[0] and pixel[1] == color[1] and pixel[2] == color[2]:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(pixel)
    alpha_image = Image.new("RGBA", image.size)
    alpha_image.putdata(new_data)
    return alpha_image


# Resize and crop an image to make it fill a square
# TODO: resize at right dimensions
def square(image, size=256, fill_color=(0, 0, 0, 255)):
    x, y = image.size
    max_size = max(size, x, y)
    squared_image = Image.new("RGBA", (max_size, max_size), fill_color)
    squared_image.paste(image, (int((max_size - x) / 2), int((max_size - y) / 2)))
    return squared_image.resize((size, size), Image.ANTIALIAS)


# Given a candidate ID return a profile picture thumbnail path
def get_candidate_thumbnail_path(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    # TODO: get thumbnail_path in MEDIA_ROOT from hash(candidate.image_file + version)
    if True:  # TODO: if path not found load image_file
        background = square(Image.open(f"{settings.MEDIA_ROOT}/{candidate.image_file}"))
        # TODO: if fail load image from candidate.image_url?
        foreground = square(Image.open(f"{settings.STATIC_ROOT}/thumbnail.png"))
        background.paste(foreground, (0, 0), foreground)
        image = color2alpha(background)
        response = HttpResponse(content_type="image/png")
        image.save(response, "PNG")  # TODO: save image in thumbnail_path
    return response  # TODO: return thumbnail_path


# Given a government ID return an image shareable on social media
def generate_gov_thumbnail(request, gov_id):
    pos = [
        (360, 190),
        (560, 190),
        (60, 360),
        (260, 360),
        (460, 360),
        (660, 360),
        (860, 360),
        (160, 530),
        (360, 530),
        (560, 530),
        (760, 530),
        (60, 600),
        (260, 600),
        (460, 600),
        (660, 600),
        (860, 600),
    ]
    # TODO: big green empty layer
    for i, gov_member in enumerate(Config.objects.filter(config_ref=gov_id)):
        # TODO: sort gov_member by gov_member.position?
        print(gov_member)
        # TODO: paste get_candidate_thumbnail_path(gov_member.candidate.id) at pos[i]
        # TODO: write text gov_member.position at pos[i]?
    image = Image.open(f"{settings.STATIC_ROOT}/governement.png")
    # TODO: paste last layer
    response = HttpResponse(content_type="image/png")
    image.save(response, "PNG")
    # TODO: cache image?
    return response
