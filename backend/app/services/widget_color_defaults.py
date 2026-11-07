from app.models.assistant_widget_settings import (
    AssistantWidgetSettings,
)


LIGHT_BACKGROUND_TEXT = "#1e293b"
DARK_BACKGROUND_TEXT = "#f8fafc"


def readable_text_color(
    background_color: str,
) -> str:
    red = int(background_color[1:3], 16) / 255
    green = int(background_color[3:5], 16) / 255
    blue = int(background_color[5:7], 16) / 255

    def linearize(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92

        return ((channel + 0.055) / 1.055) ** 2.4

    luminance = (
        0.2126 * linearize(red)
        + 0.7152 * linearize(green)
        + 0.0722 * linearize(blue)
    )

    return (
        LIGHT_BACKGROUND_TEXT
        if luminance > 0.179
        else DARK_BACKGROUND_TEXT
    )


def resolved_widget_control_colors(
    widget: AssistantWidgetSettings,
) -> dict[str, str]:
    readable_text = readable_text_color(
        widget.background_color,
    )

    return {
        "message_input_text_color": (
            widget.message_input_text_color
            or readable_text
        ),
        "new_chat_button_text_color": (
            widget.new_chat_button_text_color
            or readable_text
        ),
        "new_chat_button_background_color": (
            widget.new_chat_button_background_color
            or widget.background_color
        ),
    }
