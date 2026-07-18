from pathlib import Path
from io import StringIO
import pandas as pd
import yfinance as yf
import requests
from config import load_config
config = load_config()

DATA_PATH = Path(config["paths"]["raw_data"])
START_DATE = config["data"]["start_date"]
END_DATE = config["data"]["end_date"]

def download_sp500_constituents(output_path: Path) -> pd.DataFrame:
    """
    Download the current S&P 500 constituent list from Wikipedia.

    Parameters
    ----------
    output_path : Path
        Location where the constituent data will be saved.

    Returns
    -------
    pd.DataFrame
        Table containing the current S&P 500 constituents.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    print("Downloading S&P 500 constituent list...")

    headers = {

    "User-Agent": (

        "Mozilla/5.0 "

        "(Macintosh; Intel Mac OS X 10_15_7) "

        "AppleWebKit/537.36 "

        "(KHTML, like Gecko) "

        "Chrome/137.0 Safari/537.36"

    )}
    response = requests.get(url, headers=headers, timeout=30)

    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))
    constituents = tables[0].copy()

    constituents["Symbol"] = constituents["Symbol"].str.replace(
        ".", "-", regex=False
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    constituents.to_csv(output_path, index=False)

    print(f"Saved constituent list to: {output_path}")
    print(f"Number of constituents: {len(constituents)}")

    return constituents

def download_benchmark(
    ticker: str,
    start_date: str,
    end_date: str,
    output_path: Path,
) -> pd.DataFrame:
    """
    Download benchmark price data from Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Yahoo Finance ticker symbol.
    start_date : str
        Start date in YYYY-MM-DD format.
    end_date : str
        End date in YYYY-MM-DD format.
    output_path : Path
        Location where the benchmark data will be saved.

    Returns
    -------
    pd.DataFrame
        Historical benchmark price data.

    Raises
    ------
    ValueError
        If no data are downloaded.
    """
    print(f"Downloading benchmark data for {ticker}...")

    benchmark = yf.download(
        
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
    )
    if isinstance(benchmark.columns, pd.MultiIndex):
            benchmark.columns = benchmark.columns.get_level_values(0)
    benchmark.index.name = "Date"
    if benchmark.empty:
        raise ValueError(f"No benchmark data downloaded for {ticker}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(output_path)

    print(f"Saved benchmark data to: {output_path}")
    print(f"Number of observations: {len(benchmark)}")

    return benchmark

if __name__ == "__main__":
    constituent_path = DATA_PATH / "sp500_constituents.csv"
    benchmark_path = DATA_PATH / "sp500_benchmark.csv"

    download_sp500_constituents(constituent_path)

    download_benchmark(
        ticker="^GSPC",
        start_date=START_DATE,
        end_date=END_DATE,
        output_path=benchmark_path,
    )