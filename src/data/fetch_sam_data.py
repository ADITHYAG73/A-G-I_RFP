"""Fetch RFP data from SAM.gov API."""

import argparse
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests
from tqdm import tqdm

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings, ensure_directories

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class SAMDataFetcher:
    """Fetch RFP/contract opportunity data from SAM.gov."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize fetcher with API key."""
        self.api_key = api_key or settings.sam_api_key
        self.base_url = settings.sam_api_base_url

        if not self.api_key:
            logger.warning(
                "No SAM.gov API key found. "
                "Register at https://sam.gov/ and add to .env file"
            )

    def search_opportunities(
        self,
        limit: int = 10,
        days_back: int = 30,
        notice_type: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Search for contract opportunities.

        Args:
            limit: Maximum number of results to return
            days_back: Search for opportunities posted in last N days
            notice_type: Filter by notice type (e.g., 'Solicitation', 'Combined Synopsis/Solicitation')
            **kwargs: Additional query parameters

        Returns:
            List of opportunity dictionaries
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Build query parameters
        params = {
            "api_key": self.api_key,
            "limit": limit,
            "postedFrom": start_date.strftime("%m/%d/%Y"),
            "postedTo": end_date.strftime("%m/%d/%Y"),
            **kwargs
        }

        if notice_type:
            params["noticeType"] = notice_type

        logger.info(f"Searching SAM.gov for opportunities from {start_date.date()} to {end_date.date()}")

        try:
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            opportunities = data.get("opportunitiesData", [])

            logger.info(f"Found {len(opportunities)} opportunities")
            return opportunities

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from SAM.gov: {e}")
            return []

    def get_opportunity_details(self, notice_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific opportunity.

        Args:
            notice_id: The unique opportunity ID

        Returns:
            Opportunity details dictionary or None if error
        """
        params = {"api_key": self.api_key}

        try:
            response = requests.get(
                f"{self.base_url}/{notice_id}",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching opportunity {notice_id}: {e}")
            return None

    def download_attachments(self, notice_id: str, save_dir: Path) -> List[Path]:
        """
        Download attachments for an opportunity.

        Args:
            notice_id: The unique opportunity ID
            save_dir: Directory to save attachments

        Returns:
            List of paths to downloaded files
        """
        save_dir.mkdir(parents=True, exist_ok=True)

        # Note: The actual attachment download endpoint may vary
        # This is a placeholder - actual implementation depends on SAM.gov API docs
        logger.warning(
            f"Attachment download for {notice_id} - "
            "Implementation depends on SAM.gov API attachment endpoint"
        )

        # TODO: Implement actual attachment download when API endpoint is confirmed
        # Typical endpoint: /opportunities/{noticeId}/resources/download
        return []

    def save_opportunities(
        self,
        opportunities: List[Dict],
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Save opportunities to JSON file.

        Args:
            opportunities: List of opportunity dictionaries
            output_file: Path to output file (default: data/raw/sam_opportunities_{timestamp}.json)

        Returns:
            Path to saved file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = settings.raw_data_dir / f"sam_opportunities_{timestamp}.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(opportunities)} opportunities to {output_file}")
        return output_file


def main():
    """CLI interface for fetching SAM.gov data."""
    parser = argparse.ArgumentParser(description="Fetch RFP data from SAM.gov")
    parser.add_argument(
        "--limit",
        type=int,
        default=settings.max_documents_fetch,
        help="Number of opportunities to fetch"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=30,
        help="Search for opportunities from last N days"
    )
    parser.add_argument(
        "--notice-type",
        type=str,
        help="Filter by notice type (e.g., 'Solicitation')"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path"
    )

    args = parser.parse_args()

    # Ensure directories exist
    ensure_directories()

    # Fetch data
    fetcher = SAMDataFetcher()
    opportunities = fetcher.search_opportunities(
        limit=args.limit,
        days_back=args.days_back,
        notice_type=args.notice_type
    )

    if opportunities:
        output_path = fetcher.save_opportunities(opportunities, args.output)
        print(f"\n✓ Successfully fetched and saved {len(opportunities)} opportunities")
        print(f"  File: {output_path}")

        # Print sample
        if opportunities:
            sample = opportunities[0]
            print(f"\n  Sample opportunity:")
            print(f"    Title: {sample.get('title', 'N/A')}")
            print(f"    Notice ID: {sample.get('noticeId', 'N/A')}")
            print(f"    Type: {sample.get('type', 'N/A')}")
    else:
        print("\n⚠ No opportunities found or error occurred")
        print("  Check your SAM.gov API key in .env file")


if __name__ == "__main__":
    main()
