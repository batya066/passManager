"""Kişiye özel gelişmiş şifre yöneticisi."""

from importlib import metadata as _metadata
from typing import Optional, Sequence

__all__ = ["main", "__version__"]


def main(argv: Optional[Sequence[str]] = None) -> None:
    """CLI giriş noktası, import'u geciktirir."""
    from .cli import main as _cli_main  # yerel import, GUI kullanımında rich gerektirmez

    _cli_main(argv)


try:
    __version__ = _metadata.version("pass-manager-tanjiro")
except _metadata.PackageNotFoundError:  # paket kurulmamışsa geliştirme sürümü
    __version__ = "0.1.0"

