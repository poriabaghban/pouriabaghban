from django.urls import path

from .views import delete_group_message, group_members_presence, mark_group_messages_read, message_view, send_group_message

urlpatterns = [
    path('_admin-chat/groups/<int:group_id>/send/', send_group_message, name='send_group_message'),
    path('_admin-chat/groups/<int:group_id>/read/', mark_group_messages_read, name='mark_group_messages_read'),
    path('_admin-chat/groups/<int:group_id>/messages/<int:message_id>/delete/', delete_group_message, name='delete_group_message'),
    path('_admin-chat/groups/<int:group_id>/presence/', group_members_presence, name='group_members_presence'),
    path('', message_view.as_view(), name='message'),
]
