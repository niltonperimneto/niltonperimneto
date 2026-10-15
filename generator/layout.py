"""Layout coordinates live here so spacing changes do not touch data fetching."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Layout:
    width: int
    height: int
    portrait: bool
    header_bottom: int
    languages_y: int
    platforms_y: int
    focus_y: int
    activity_y: int
    projects_y: int
    margin: int = 28

    @property
    def right(self):
        return self.width - self.margin

    @property
    def content_width(self):
        return self.width - 2 * self.margin


WIDE = Layout(800, 560, False, 142, 166, 230, 230, 318, 444)
PORTRAIT = Layout(400, 780, True, 166, 190, 280, 354, 434, 564)
