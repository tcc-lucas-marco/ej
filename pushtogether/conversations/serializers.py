from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import routers, serializers, viewsets
from .models import Conversation, Comment, Vote


User = get_user_model()

class AuthorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class VoteSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ('id', 'author','comment', 'value')


class CommentReportSerializer(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()
    agree_votes = serializers.SerializerMethodField()
    disagree_votes = serializers.SerializerMethodField()
    pass_votes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'total_votes', 'agree_votes',
            'disagree_votes', 'pass_votes')

    def get_agree_votes(self, obj):
        return Vote.objects.filter(comment_id=obj.id, value=Vote.AGREE).count()

    def get_disagree_votes(self, obj):
        return Vote.objects.filter(comment_id=obj.id, value=Vote.DISAGREE).count()

    def get_pass_votes(self, obj):
        return Vote.objects.filter(comment_id=obj.id, value=Vote.PASS).count()

    def get_total_votes(self, obj):
        return obj.votes.count()


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'conversation', 'author', 'content', 'approval', 'votes')


class ConversationReportSerializer(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()
    agree_votes = serializers.SerializerMethodField()
    disagree_votes = serializers.SerializerMethodField()
    pass_votes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    approved_comments = serializers.SerializerMethodField()
    rejected_comments = serializers.SerializerMethodField()
    unmoderated_comments = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'total_votes', 'agree_votes', 'disagree_votes',
            'pass_votes', 'total_comments', 'approved_comments',
            'rejected_comments', 'unmoderated_comments')

    def get_agree_votes(self, obj):
        return Vote.objects.filter(comment__conversation_id=obj.id,
            value=Vote.AGREE).count()

    def get_disagree_votes(self, obj):
        return Vote.objects.filter(comment__conversation_id=obj.id,
            value=Vote.DISAGREE).count()

    def get_pass_votes(self, obj):
        return Vote.objects.filter(comment__conversation_id=obj.id,
            value=Vote.PASS).count()

    def get_total_votes(self, obj):
        return Vote.objects.filter(comment__conversation_id=obj.id).count()

    def get_approved_comments(self, obj):
        return Comment.objects.filter(conversation_id=obj.id,
            approval=Comment.APPROVED).count()

    def get_rejected_comments(self, obj):
        return Comment.objects.filter(conversation_id=obj.id,
            approval=Comment.REJECTED).count()

    def get_unmoderated_comments(self, obj):
        return Comment.objects.filter(conversation_id=obj.id,
            approval=Comment.UNMODERATED).count()

    def get_total_comments(self, obj):
        return obj.comments.count()


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'description', 'author', 'comments')