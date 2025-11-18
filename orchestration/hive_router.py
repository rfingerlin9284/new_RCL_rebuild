"""Rick→Hive routing interface.

This module defines the public interface that future work will use to
call out to external AI providers (GPT, Grok, etc.). In this pass it
provides a safe local stub implementation only.
"""

from __future__ import annotations

from typing import Optional, Dict, Any

from config.narration_logger import get_narration_logger


def get_best_trade_from_hive(request_text: str) -> Optional[Dict[str, Any]]:
    """Return a best‑effort trade idea or None.

    Current implementation is a stub that only logs the request and
    returns None. The signature and narration side‑effects are what
    matter for now so that higher‑level orchestration and the CLI can be
    wired without depending on external APIs.
    """

    logger = get_narration_logger()
    logger.log_event("HIVE_REQUEST", "Received hive trade request", request_text=request_text)
    # TODO: integrate real hive members (GPT, Grok, etc.) in a future pass.
    logger.log_event("HIVE_RESPONSE", "Hive stub returning no trade idea")
    return None
