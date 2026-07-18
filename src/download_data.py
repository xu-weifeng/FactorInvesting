from pathlib import Path

import pandas as pd
import yfinance as yf
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def load_config() -> dict:
    """Load project configuration from YAML."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def download_sp500_constituents(output_path: Path) -> pd.DataFrame:
    """
    Download the current S&P 500 constituent list from Wikipedia.

    Note:
        Using current constituents for historical analysis introduces
        survivorship bias. This limitation will be documented in the report.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)

    constituents = tables[0].copy()
    constituents["Symbol"] = constituents["Symbol"].str.replace(".", "-", regex=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    constituents.to_csv(output_path, index=False)

    return constituents


def download_benchmark(
    ticker: str,
    start_date: str,
    end_date: str,
    output_path: Path,
) -> pd.DataFrame:
    """Download benchmark market data from Yahoo Finance."""
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise RuntimeError(f"No benchmark data were downloaded for {ticker}.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path)

    return data


def main() -> None:
    """Run the initial data collection pipeline."""
    config = load_config()

    raw_data_dir = PROJECT_ROOT / config["paths"]["raw_data"]

    constituents_path = raw_data_dir / "sp500_constituents.csv"
    benchmark_path = raw_data_dir / "sp500_benchmark.csv"

    constituents = download_sp500_constituents(constituents_path)

    benchmark = download_benchmark(
        ticker=config["data"]["benchmark"],
        start_date=config["data"]["start_date"],
        end_date=config["data"]["end_date"],
        output_path=benchmark_path,
    )

    print(f"Downloaded {len(constituents)} S&P 500 constituents.")
    print(f"Downloaded {len(benchmark)} benchmark observations.")
    print(f"Constituent data saved to: {constituents_path}")
    print(f"Benchmark data saved to: {benchmark_path}")


if __name__ == "__main__":
    main()