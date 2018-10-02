from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_conversations import forms
from ej_conversations.models import Conversation
from ej_conversations.routes import conversation_detail_context, moderate_context, edit_context
from .forms import BoardForm
from .models import Board

app_name = 'ej_boards'

#
# Board management
#
urlpatterns = Router(
    template=['ej_boards/{name}.jinja2', 'generic.jinja2'],
    models={
        'board': Board,
        'conversation': Conversation,
    },
    object='conversation',
    lookup_field='slug',
    lookup_type='slug',
)


@urlpatterns.route('profile/boards/', template='ej_boards/list.jinja2', login=True)
def list(request):
    user = request.user
    boards = user.boards.all()
    can_add_board = user.has_perm('ej_boards.can_add_board')

    if not can_add_board and user.boards.count() == 1:
        return redirect(f'{boards[0].get_absolute_url()}conversations/')

    return {
        'boards': boards,
        'can_add_board': can_add_board,
    }


@urlpatterns.route('profile/boards/add/', login=True)
def create(request):
    user = request.user
    if not user.has_perm('ej_boards.can_add_board'):
        raise Http404

    form_class = BoardForm
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = user
            board.save()

            return redirect(board.get_absolute_url())
    else:
        form = form_class()

    return {
        'form': form,
    }


#
# Conversation and boards management
#
@urlpatterns.route('<model:board>/edit/')
def edit(request, board):
    if request.user != board.owner:
        raise Http404
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.instance.save()
            return redirect(board.get_absolute_url())
    else:
        form = BoardForm(instance=board)
    return {
        'form': form,
    }


@urlpatterns.route('<model:board>/conversations/', template='ej_conversations/list.jinja2')
def conversation_list(request, board):
    user = request.user
    conversations = board.conversations.all()
    board_user = board.owner
    boards = []
    boards_count = 0
    if user == board_user:
        boards = board_user.boards.all()
        boards_count = boards.count()
        user_is_owner = True
    else:
        user_is_owner = False
    return {
        'can_add_conversation': user_is_owner,
        'create_url': reverse('boards:create-conversation', kwargs={'board': board}),
        'conversations': conversations,
        'boards_count': boards_count,
        'boards': boards,
        'current_board': board,
        'is_a_board': True,
        'title': _("%s' conversations") % board.title,
        'subtitle': _("These are %s's conversations. Contribute to them too") % board.title,
    }


@urlpatterns.route('<model:board>/conversations/add/', perms=['ej_boards.can_add_conversation'])
def create_conversation(request, board):
    user = request.user
    form = forms.ConversationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            conversation = form.save_all(
                author=user,
                board=board,
            )
        return redirect(f'/{board.slug}/conversations/{conversation.slug}')

    return {'form': form}


@urlpatterns.route('<model:board>/conversations/<model:conversation>/')
def conversation_detail(request, board, conversation):
    if conversation not in board.conversations.all():
        raise Http404
    return conversation_detail_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/edit/', perms=['ej.can_edit_conversation'])
def edit_conversation(request, board, conversation):
    if conversation not in board.conversations.all():
        raise Http404
    return edit_context(request, conversation)


@urlpatterns.route('<model:board>/conversations/<model:conversation>/moderate/', perms=['ej.can_edit_conversation'])
def moderate_conversation(request, board, conversation):
    if conversation not in board.conversations.all():
        raise Http404
    return moderate_context(request, conversation, board)
