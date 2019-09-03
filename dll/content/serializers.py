import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from psycopg2._range import NumericRange
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField, CharField
from rest_framework.relations import RelatedField
from rest_framework.validators import UniqueValidator
from rest_polymorphic.serializers import PolymorphicSerializer

from dll.communication.models import CoAuthorshipInvitation
from dll.content.fields import RangeField
from dll.content.models import SchoolType, Competence, SubCompetence, Subject, OperatingSystem, ToolApplication, \
    HelpText, Review
from dll.general.utils import custom_slugify
from dll.user.models import DllUser
from .models import Content, Tool, Trend, TeachingModule, ContentLink, Review


logger = logging.getLogger('dll.communication.serializers')


class ContentListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # WARNING: can conflict with Content.image
    type = serializers.SerializerMethodField()
    type_verbose = serializers.SerializerMethodField()
    competences = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format="%d.%m.%Y")
    co_authors = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created',
                  'co_authors']

    def get_image(self, obj):
        return obj.get_image()

    def get_co_authors(self, obj):
        return [f'{author.username}' for author in obj.co_authors.all()]

    def get_type(self, obj):
        return obj.type

    def get_type_verbose(self, obj):
        return obj.type_verbose

    def get_competences(self, obj):
        competences = obj.competences.all()
        return [i.icon_class for i in competences]

    def get_url(self, obj):
        return obj.get_absolute_url()


class ContentListInternalSerializer(ContentListSerializer):
    author = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    edit_url = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_author(self, obj):
        return str(obj.author.username)

    def get_preview_url(self, obj):
        return obj.get_preview_url()

    def get_edit_url(self, obj):
        return obj.get_edit_url()

    def get_status(self, obj):
        status = _('Draft')
        if obj.publisher_linked:
            if obj.review:
                if obj.review.status == Review.DECLINED:
                    return _('Approved - Resubmission declined.')
                else:
                    return _('Approved - Resubmission pending.')
            return _('Approved')

        if obj.publisher_is_draft and obj.review and obj.review.status == Review.DECLINED:
            return _('Declined')

        if obj.publisher_is_draft and obj.reviews.count():
            return _('Submitted')

        return status

    class Meta(ContentListSerializer.Meta):
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created',
                  'co_authors', 'preview_url', 'edit_url', 'author', 'status']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DllUser
        fields = ['username', 'pk']


class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = ['name', 'pk']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name', 'pk']


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = ['name', 'pk']


class SubCompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCompetence
        fields = ['name', 'pk']


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLink
        fields = ['url', 'name', 'type']
        depth = 1


class DllM2MField(RelatedField):

    def to_representation(self, value):
        try:
            label = getattr(value, 'username')
        except AttributeError:
            label = getattr(value, 'name')
        return {'pk': value.pk, 'label': label}

    def to_internal_value(self, data):
        return data['pk']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['status', 'json_data']


class BaseContentSubclassSerializer(serializers.ModelSerializer):
    name = CharField(required=True, validators=[
        UniqueValidator(
            queryset=Content.objects.all(),
            message=_('A content with this name already exists.')
        )
    ])
    image = SerializerMethodField()
    author = AuthorSerializer(read_only=True, allow_null=True, required=False)
    contentlink_set = LinkSerializer(many=True, allow_null=True, required=False)
    co_authors = DllM2MField(allow_null=True, many=True, required=False, queryset=DllUser.objects.all())
    competences = DllM2MField(allow_null=True, many=True, queryset=Competence.objects.all())
    sub_competences = DllM2MField(allow_null=True, many=True, queryset=SubCompetence.objects.all())
    related_content = DllM2MField(allow_null=True, many=True, queryset=Content.objects.all())
    tools = SerializerMethodField(allow_null=True)
    trends = SerializerMethodField(allow_null=True)
    teaching_modules = SerializerMethodField(allow_null=True)
    review = ReviewSerializer(read_only=True)
    help_texts = SerializerMethodField(allow_null=True)
    preview_url = SerializerMethodField(allow_null=True)
    submitted = SerializerMethodField(allow_null=True)
    pending_co_authors = SerializerMethodField(allow_null=True)


    def validate_name(self, data):
        """Make sure the slug of this name will be unique too."""
        expected_slug = custom_slugify(data)
        if Content.objects.drafts().filter(slug=expected_slug).count() > 1 or \
                Content.objects.published().filter(slug=expected_slug).count() > 1:
            raise ValidationError(_('A content with this name already exists.'))
        return data

    def validate_related_content(self, data):
        res = []
        for x in data:
            obj = Content.objects.get(pk=x)
            if obj.is_public:
                res.append(x)
        return res

    def get_pending_co_authors(self, obj):
        return [invite.to.username for invite in obj.invitations.filter(accepted__isnull=True)]

    def get_submitted(self, obj):
        return obj.review and (obj.review.status == Review.IN_PROGRESS or obj.review.status == Review.NEW)

    def get_help_texts(self, obj):
        result = {}
        try:
            help_text = HelpText.objects.get(content_type=ContentType.objects.get_for_model(obj))
            for field in help_text.help_text_fields.all():
                result[field.name.split('.')[-1]] = field.text
        except HelpText.DoesNotExist:
            pass
        return result

    def get_preview_url(self, obj):
        return obj.get_preview_url()

    def get_image(self, obj):
        if obj.image:
            return {'name': str(obj.image), 'url': obj.image.url}
        return None

    def get_tools(self, obj):
        return [{'pk': content.pk, 'label': content.name} for content in obj.related_content.instance_of(Tool)]

    def get_trends(self, obj):
        return [{'pk': content.pk, 'label': content.name} for content in obj.related_content.instance_of(Trend)]

    def get_teaching_modules(self, obj):
        return [{'pk': content.pk, 'label': content.name} for content in obj.related_content.instance_of(TeachingModule)]

    def get_m2m_fields(self):
        return [
            'competences',
            'sub_competences',
            'related_content'
        ]

    def get_array_fields(self):
        return [
            'learning_goals',
        ]

    def create(self, validated_data):
        links_data = validated_data.pop('contentlink_set', [])
        co_authors = validated_data.pop('co_authors', [])
        content = super(BaseContentSubclassSerializer, self).create(validated_data)
        self._update_content_links(content, links_data)
        self._update_co_authors(content, co_authors)
        return content

    def _update_content_links(self, content, data):
        """
        delete all previous links first, because we can't distinguish whether it is a new link, or an old one with
        updated href AND name AND ...
        """
        content.contentlink_set.all().delete()
        for link in data:
            ContentLink.objects.create(content=content, **dict(link))

    def _update_co_authors(self, content, co_authors):
        invited_co_authors = set(DllUser.objects.filter(pk__in=content.invitations.values_list('to', flat=True)))
        current_co_authors = set(content.co_authors.all())
        updated_list = set(DllUser.objects.filter(pk__in=co_authors))
        new_co_authors = updated_list - current_co_authors - invited_co_authors
        removed_co_authors = current_co_authors - updated_list
        content.co_authors.remove(*removed_co_authors)
        for user in new_co_authors:
            invitation = CoAuthorshipInvitation.objects.create(
                by=self.context['request'].user,
                to=user,
                content=content,
                site_id=settings.SITE_ID
            )
            invitation.send_invitation_mail()

    def _update_m2m_fields(self, instance, field, values):
        for pk in values:
            getattr(instance, field).add(pk)
        for pk in getattr(instance, field).values_list('pk', flat=True):
            if pk not in values:
                getattr(instance, field).remove(pk)

    def _update_array_fields(self, instance, field, values):
        setattr(instance, field, values)

    def update(self, instance, validated_data):
        """
        `update_methods` provides a mapping of keys present in the serialized data that need further
        processing, and
        maps it to the corresponding processing method
        """
        update_methods = {
            'contentlink_set': '_update_content_links',
            'co_authors': '_update_co_authors'
        }
        for update_key, update_method in update_methods.items():
            try:
                data = validated_data.pop(update_key, [])
                method = getattr(self, update_method)
            except AttributeError:
                logger.warning("No update method for {}".format(update_key))
                pass
            except KeyError:
                # this key was not present in the serialized data, so it doesn't have to be updated
                pass
            else:
                method(instance, data)

        for field in self.get_m2m_fields():
            try:
                values = validated_data.pop(field)
            except KeyError:
                pass
            else:
                self._update_m2m_fields(instance, field, values)

        for field in self.get_array_fields():
            try:
                values = validated_data.pop(field)
            except KeyError:
                pass
            else:
                self._update_array_fields(instance, field, values)

        instance = super().update(instance, validated_data)
        return instance


class ToolSerializer(BaseContentSubclassSerializer):
    operating_systems = DllM2MField(allow_null=True, many=True, queryset=OperatingSystem.objects.all(), required=False)
    applications = DllM2MField(allow_null=True, many=True, queryset=ToolApplication.objects.all(), required=False)

    def get_array_fields(self):
        fields = super(ToolSerializer, self).get_array_fields()
        fields.extend([
            'pro',
            'contra'
        ])
        return fields

    def get_m2m_fields(self):
        fields = super(ToolSerializer, self).get_m2m_fields()
        fields.extend([
            'operating_systems',
            'applications'
        ])
        return fields

    class Meta:
        model = Tool
        fields = '__all__'


class TrendSerializer(BaseContentSubclassSerializer):

    def get_array_fields(self):
        fields = super(TrendSerializer, self).get_array_fields()
        fields.extend([
            'target_group',
            'publisher'
        ])
        return fields

    class Meta:
        model = Trend
        fields = '__all__'


class TeachingModuleSerializer(BaseContentSubclassSerializer):
    subjects = DllM2MField(allow_null=True, many=True, queryset=Subject.objects.all())
    school_types = DllM2MField(allow_null=True, many=True, queryset=Subject.objects.all())
    school_class = RangeField(NumericRange, child=IntegerField(), required=False, allow_null=True)

    def get_array_fields(self):
        fields = super(TeachingModuleSerializer, self).get_array_fields()
        fields.extend([
            'expertise',
            'equipment',
            'estimated_time',
            'subject_of_tuition',
        ])
        return fields

    class Meta:
        model = TeachingModule
        fields = '__all__'

    def get_m2m_fields(self):
        fields = super(TeachingModuleSerializer, self).get_m2m_fields()
        fields.extend([
            'subjects',
            'school_types',
        ])
        return fields


class ContentPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Tool: ToolSerializer,
        Trend: TrendSerializer,
        TeachingModule: TeachingModuleSerializer
    }


class FileSerializer(serializers.Serializer):
    image = serializers.FileField()
