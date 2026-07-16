import logging
import sys

from src.pipeline import Pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _summary(result):
    print("\n" + "=" * 60)
    print("  NEBULA — PROCESSING SUMMARY")
    print("=" * 60)
    print(f"  Leads processed:     {len(result.daily)} days")
    print(f"  Agents evaluated:    {len(result.agents)}")
    print(f"  Conversion rate:     {result.conversion_rate:.2f}%")
    print(f"  Alerts generated:    {len(result.report['alerts'])}")
    print("=" * 60)


def main() -> int:
    logger.info("═══ Processing started ═══")
    try:
        result = Pipeline().run()
        _summary(result)
        return 0
    except Exception:
        logger.exception("Processing failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
