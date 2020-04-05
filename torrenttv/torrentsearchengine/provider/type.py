from enum import Enum


class ProviderType(Enum):
    HTML_V1 = "html/v1"

    @staticmethod
    def from_str(s: str):
        s = s.lower()
        if s in ["html/v1", "html/1", "html"]:
            return ProviderType.HTML_V1
        else:
            # default
            return ProviderType.HTML_V1
