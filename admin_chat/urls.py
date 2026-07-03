from django.urls import path

from . import views


app_name = "admin_chat"

urlpatterns = [
    path("chat/", views.chat_dashboard, name="dashboard"),
    path("chat/<int:room_id>/", views.chat_dashboard, name="dashboard_room"),
    path("api/rooms/", views.room_list, name="room_list"),
    path("api/rooms/<int:room_id>/messages/", views.message_list, name="message_list"),
    path("api/upload-chunk/", views.upload_chunk, name="upload_chunk"),
    path("attachments/<int:pk>/", views.attachment_file, name="attachment_file"),
]
