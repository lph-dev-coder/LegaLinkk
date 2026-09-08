"""Run PaddleOCR in a subprocess so native crashes cannot kill the API worker."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from app.core.logging import get_logger
from app.ocr import OcrDocumentResult, OcrError, OcrPageResult

logger = get_logger(__name__)

# PaddleOCR language codes are plain identifiers ("en", "french", "ch_tra").
# Anything else is rejected rather than forwarded to the child process.
_LANG_PATTERN = re.compile(r"\A[A-Za-z][A-Za-z0-9_]{0,31}\Z")

# The OCR worker only needs to find Python, write to its cache/temp dirs and
# obey the single-thread math limits. Everything else — database password, LLM
# and Langfuse API keys — is withheld, so the child process cannot leak them
# through a crash dump, its own subprocesses, or /proc/<pid>/environ.
_ENV_ALLOWLIST = frozenset(
    {
        "PATH",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TZ",
        "TMPDIR",
        "TMP",
        "TEMP",
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONUNBUFFERED",
        "PYTHONDONTWRITEBYTECODE",
        "XDG_CACHE_HOME",
        "HF_HOME",
        "NUMEXPR_NUM_THREADS",
        # Windows needs these for the interpreter and DLL loader to start.
        "SYSTEMROOT",
        "SYSTEMDRIVE",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "USERPROFILE",
        "LOCALAPPDATA",
        "APPDATA",
        "PROCESSOR_ARCHITECTURE",
        "NUMBER_OF_PROCESSORS",
        # The first OCR run downloads Paddle models.
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "no_proxy",
    }
)

# Paddle reads its own tuning knobs from FLAGS_* and PADDLE_* variables.
_ENV_ALLOWED_PREFIXES = ("FLAGS_", "PADDLE_")


def _build_worker_env() -> dict[str, str]:
    """Return a minimal environment for the OCR child process."""
    env = {
        key: value
        for key, value in os.environ.items()
        if key in _ENV_ALLOWLIST or key.startswith(_ENV_ALLOWED_PREFIXES)
    }
    # Single-threaded math keeps peak RAM bounded on small hosts.
    env.update(
        {
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "FLAGS_use_mkldnn": "0",
        }
    )
    return env


def _resolve_input_path(file_path: str) -> Path:
    """Validate ``file_path`` before it becomes a command-line argument."""
    try:
        resolved = Path(file_path).resolve(strict=True)
    except OSError as exc:
        raise OcrError(f"OCR input file is not readable: {file_path}") from exc
    if not resolved.is_file():
        raise OcrError(f"OCR input path is not a regular file: {file_path}")
    return resolved


def _parse_worker_stdout(stdout: str) -> dict:
    """Parse worker JSON even when PaddleOCR polluted stdout with progress bars."""
    raw = (stdout or "").strip()
    if not raw:
        raise OcrError("OCR subprocess produced no output")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    for line in reversed(raw.splitlines()):
        candidate = line.strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    start = raw.rfind("{")
    end = raw.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            pass

    raise OcrError("OCR subprocess returned invalid JSON")


def _load_payload(*, output_json: Path, stdout: str) -> dict:
    """Prefer the dedicated JSON file; fall back to parsing stdout."""
    if output_json.is_file():
        try:
            return json.loads(output_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to read OCR result file %s: %s", output_json, exc)

    return _parse_worker_stdout(stdout)


def run_paddle_ocr_subprocess(
    file_path: str,
    *,
    lang: str = "en",
    scale: float = 1.0,
    timeout_seconds: int = 1800,
    use_angle_cls: bool = False,
    max_image_side: int = 1280,
) -> OcrDocumentResult:
    """Execute OCR in a child process and return structured results."""
    if not _LANG_PATTERN.match(lang):
        raise OcrError(f"Unsupported OCR language code: {lang!r}")
    resolved_path = _resolve_input_path(file_path)

    with tempfile.TemporaryDirectory(prefix="legallink-ocr-") as tmp_dir:
        output_json = Path(tmp_dir) / "result.json"
        # Fixed argv (no shell), an interpreter path we own, and validated
        # numeric/enum options. The positional input path goes after "--" so a
        # filename beginning with "-" can never be parsed as an option.
        cmd = [
            sys.executable,
            "-m",
            "app.ocr.paddle_ocr_worker",
            "--lang",
            lang,
            "--scale",
            str(float(scale)),
            "--max-image-side",
            str(int(max_image_side)),
            "--use-angle-cls" if use_angle_cls else "--no-use-angle-cls",
            "--output-json",
            str(output_json),
            "--",
            str(resolved_path),
        ]
        logger.info(
            "Starting isolated OCR subprocess for %s "
            "(timeout=%ss scale=%s lang=%s angle_cls=%s max_side=%s)",
            file_path,
            timeout_seconds,
            scale,
            lang,
            use_angle_cls,
            max_image_side,
        )

        try:
            completed = subprocess.run(  # noqa: S603  # fixed argv, shell=False, validated args
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                shell=False,
                env=_build_worker_env(),
            )
        except subprocess.TimeoutExpired as exc:
            logger.error(
                "OCR subprocess timed out after %ss for %s",
                timeout_seconds,
                file_path,
            )
            raise OcrError(
                f"OCR subprocess timed out after {timeout_seconds}s for {file_path}"
            ) from exc

        if completed.returncode < 0:
            signal_num = -completed.returncode
            logger.error(
                "OCR subprocess killed by signal %s for %s (API worker preserved)",
                signal_num,
                file_path,
            )
            raise OcrError(
                f"OCR process crashed (signal {signal_num}). The API remains available."
            )

        try:
            payload = _load_payload(
                output_json=output_json,
                stdout=completed.stdout or "",
            )
        except OcrError:
            logger.error(
                "OCR subprocess produced no usable JSON (code=%s): %s",
                completed.returncode,
                (completed.stderr or "")[-500:],
            )
            raise

        if not payload.get("ok"):
            raise OcrError(payload.get("error") or "OCR subprocess failed")

        pages_raw = payload.get("pages") or []
        pages: list[OcrPageResult] = []
        if isinstance(pages_raw, list):
            for item in pages_raw:
                if not isinstance(item, dict):
                    continue
                try:
                    pages.append(
                        OcrPageResult(
                            page_number=int(item.get("page_number") or 0),
                            text=str(item.get("text") or ""),
                        )
                    )
                except (TypeError, ValueError):
                    continue

        return OcrDocumentResult(
            text=str(payload.get("text") or ""),
            page_count=int(payload.get("page_count") or 0),
            pages=tuple(pages),
        )
