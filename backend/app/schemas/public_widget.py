from uuid import UUID

from pydantic import BaseModel


class PublicWidgetSettingsResponse(
    BaseModel,
):
    welcome_message: str
    placeholder: str
    position: str

    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str

    assistant_bubble_color: str
    user_bubble_color: str

    font_family: str
    font_size: int

    avatar_url: str | None

    widget_width: int
    widget_height: int
    border_radius: int

    launcher_size: int
    launcher_icon: str | None

    theme: str

    show_copy: bool
    show_edit: bool
    show_regenerate: bool
    show_new_chat: bool
    show_timestamps: bool
    initially_open: bool


class PublicAssistantConfigResponse(
    BaseModel,
):
    assistant_id: UUID
    display_name: str

    widget: PublicWidgetSettingsResponse