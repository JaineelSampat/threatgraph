"""
Owns the single Neo4j driver instance used to talk to CognoDB.

CognoDB is a managed graph database that speaks openCypher over Bolt
5.0-5.4 and is compatible with the official Neo4j Python driver. We
never concatenate user input into Cypher strings - every query in this
project goes through the driver's parameter binding.
"""
import logging
from contextlib import contextmanager
from typing import Any, Iterator

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.config import get_settings

logger = logging.getLogger("threatgraph.db")

_driver: Driver | None = None


class DatabaseUnavailableError(RuntimeError):
    """Raised when CognoDB cannot be reached or a query fails.

    Routes catch this and translate it into a clean 503 response instead
    of letting a raw driver exception (and a stack trace with connection
    details) leak to the client.
    """


def init_driver() -> None:
    """Create the driver on application startup.

    Creating a driver does not open a network connection by itself -
    the neo4j driver lazily opens/pools connections per-session. This
    keeps startup fast and lets the app boot even if CognoDB happens to
    be briefly unreachable; individual requests will surface a clear
    error until connectivity is restored.
    """
    global _driver
    settings = get_settings()
    _driver = GraphDatabase.driver(
        settings.cognodb_uri,
        auth=(settings.cognodb_username, settings.cognodb_password),
    )
    logger.info("Neo4j driver initialized for %s", settings.cognodb_uri)


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        logger.info("Neo4j driver closed")


def verify_connectivity() -> bool:
    """Used by the /health endpoint. Never raises - returns False on failure."""
    if _driver is None:
        return False
    try:
        _driver.verify_connectivity()
        return True
    except (ServiceUnavailable, Neo4jError, OSError) as exc:
        logger.warning("CognoDB connectivity check failed: %s", exc)
        return False


@contextmanager
def get_session() -> Iterator[Any]:
    """Yield a database session, translating driver errors into DatabaseUnavailableError.

    Every repository method uses this context manager rather than
    touching the driver directly, so connection handling is defined in
    exactly one place.
    """
    if _driver is None:
        raise DatabaseUnavailableError("Database driver has not been initialized.")

    settings = get_settings()
    try:
        with _driver.session(database=settings.cognodb_database) as session:
            yield session
    except ServiceUnavailable as exc:
        logger.error("CognoDB is unreachable: %s", exc)
        raise DatabaseUnavailableError("CognoDB is unreachable right now. Please try again shortly.") from exc
    except Neo4jError as exc:
        logger.error("CognoDB query failed: %s", exc)
        raise DatabaseUnavailableError("A database error occurred while processing this request.") from exc


def run_query(query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run a single parameterized Cypher query and return records as plain dicts.

    `parameters` is always passed to the driver as bound parameters -
    never interpolated into the `query` string. This is the single
    choke point every repository calls through.
    """
    with get_session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]
