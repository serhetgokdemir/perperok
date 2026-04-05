from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple

from PyPDF2 import PdfReader, PdfWriter


@dataclass
class PdfJob:
    path: str
    password: str

    @property
    def name(self) -> str:
        return Path(self.path).name


ProgressCallback = Callable[[int, int, str], None]


def unlock_pdfs(
    jobs: Iterable[PdfJob],
    target_dir: str,
    progress_callback: Optional[ProgressCallback] = None,
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """Unlock a list of PDF files.

    Returns (success_paths, failed_items) where failed_items is
    a list of (file_name, reason).
    """

    job_list = list(jobs)
    total = len(job_list)
    successes: List[str] = []
    failures: List[Tuple[str, str]] = []

    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    for index, job in enumerate(job_list, start=1):
        if progress_callback:
            progress_callback(index, total, job.name)

        try:
            reader = PdfReader(job.path)

            if reader.is_encrypted:
                try:
                    result = reader.decrypt(job.password)
                except TypeError:
                    # Backwards-compat signature
                    result = reader.decrypt(password=job.password)

                if not result:
                    failures.append((job.name, "Şifre hatalı veya dosya açılamadı"))
                    continue

            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            original_stem = Path(job.path).stem
            output_path = target_path / f"{original_stem}_unlocked.pdf"

            with output_path.open("wb") as f_out:
                writer.write(f_out)

            successes.append(str(output_path))

        except Exception as exc:  # noqa: BLE001
            failures.append((job.name, str(exc)))

    return successes, failures
