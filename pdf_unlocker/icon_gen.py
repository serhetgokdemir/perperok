from __future__ import annotations

from pathlib import Path

from PIL import Image


def _load_source_image() -> Image.Image | None:
    """Load the butterfly photo provided by the user.

    Beklenen dosya: paket içindeki assets klasöründe "butterfly_source.png".
    Bu dosya yoksa None döner ve çağıran taraf ikonsuz devam eder.
    """

    source_path = Path(__file__).resolve().parent / "assets" / "butterfly_source.png"
    if not source_path.exists():
        return None

    try:
        img = Image.open(source_path).convert("RGBA")
    except Exception:  # noqa: BLE001
        return None
    return img


def ensure_icon(path: str | Path | None = None, size: int = 32) -> str | None:
    """Ensure butterfly icon PNG exists by resizing the photo.

    Kullanıcıdan alınan kelebek fotoğrafını "butterfly_source.png" adıyla
    assets klasörüne koyduktan sonra, bu fonksiyon onu istenen boyuta
    ölçekleyip butterfly_icon.png olarak üretir.
    Fotoğraf yoksa None döner (uygulama ikonsuz çalışır).
    """

    src_img = _load_source_image()
    if src_img is None:
        return None

    if path is None:
        path = Path(__file__).resolve().parent / "assets" / "butterfly_icon.png"
    else:
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    # Always regenerate to yansıt any source change, boyutlandırmayı da burada yapıyoruz.
    img = src_img.copy()
    img.thumbnail((size, size), Image.LANCZOS)
    img.save(path, format="PNG")

    return str(path)
