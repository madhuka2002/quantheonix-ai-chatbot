from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


WidgetPosition = Literal[
    "bottom-right",
    "bottom-left",
]

WidgetTheme = Literal[
    "light",
    "dark",
]


class AssistantWidgetUpdate(BaseModel):
    welcome_message: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    placeholder: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    position: WidgetPosition | None = None

    primary_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    secondary_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    background_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    text_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    assistant_bubble_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    user_bubble_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    font_family: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    font_size: int | None = Field(
        default=None,
        ge=10,
        le=24,
    )

    avatar_url: str | None = Field(
        default=None,
        max_length=1000,
    )

    widget_width: int | None = Field(
        default=None,
        ge=280,
        le=800,
    )

    widget_height: int | None = Field(
        default=None,
        ge=350,
        le=1000,
    )

    border_radius: int | None = Field(
        default=None,
        ge=0,
        le=50,
    )

    launcher_size: int | None = Field(
        default=None,
        ge=40,
        le=100,
    )

    launcher_icon: str | None = Field(
        default=None,
        max_length=1000,
    )

    theme: WidgetTheme | None = None

    show_copy: bool | None = None
    show_edit: bool | None = None
    show_regenerate: bool | None = None
    show_new_chat: bool | None = None
    show_timestamps: bool | None = None
    initially_open: bool | None = None


class AssistantWidgetResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    assistant_id: UUID

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

    created_at: datetime
    updated_at: datetime