import uuid
import time
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Optional, Dict, Any, List


def get_utc_now():
    return datetime.now(timezone.utc)


class SimpleTracer:
    """
    A lightweight tracer to capture telemetry spans and traces.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.trace_id = str(uuid.uuid4())
        self.session_id = session_id
        self.query: Optional[str] = None
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.spans: List[Dict[str, Any]] = []
        self.total_tokens = 0
        self.metadata: Dict[str, Any] = {}

    def set_query(self, query: str):
        self.query = query

    def add_tokens(self, tokens: int):
        self.total_tokens += tokens

    @contextmanager
    def span(self, name: str, inputs: Optional[Dict[str, Any]] = None):
        span_id = str(uuid.uuid4())
        span_start = get_utc_now()

        span_data = {
            "id": span_id,
            "name": name,
            "start_time": span_start,
            "end_time": None,
            "inputs": inputs,
            "outputs": None,
        }

        self.spans.append(span_data)
        try:
            yield span_data
        finally:
            span_data["end_time"] = get_utc_now()

    def finish(self):
        self.end_time = time.time()

    def get_latency_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000.0
        return (time.time() - self.start_time) * 1000.0

    def persist(self, db_session):
        """
        Save the trace and its spans to the database.
        """
        from .models import Trace, TraceSpan

        self.finish()

        trace = Trace(
            id=self.trace_id,
            session_id=self.session_id,
            query=self.query or "unknown",
            total_tokens=self.total_tokens,
            latency_ms=self.get_latency_ms(),
            metadata_=self.metadata,
        )

        db_session.add(trace)

        for span_data in self.spans:
            span = TraceSpan(
                id=span_data["id"],
                trace_id=self.trace_id,
                name=span_data["name"],
                start_time=span_data["start_time"],
                end_time=span_data["end_time"],
                inputs=span_data.get("inputs"),
                outputs=span_data.get("outputs"),
            )
            db_session.add(span)

        db_session.commit()
