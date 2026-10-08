import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import logger
from app.db.neo4j_client import neo4j_client


def bootstrap():
    logger.info("Bootstrapping Neo4j constraints and indexes...")
    neo4j_client.bootstrap_constraints()
    logger.info("Neo4j bootstrap completed successfully.")


if __name__ == "__main__":
    bootstrap()
