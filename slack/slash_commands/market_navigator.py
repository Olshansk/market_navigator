import requests

API_URL = 'http://localhost:8000'

def _prepare_mm_body_with_data(data: dict, ticker: str):
    return {
            "response_type": "in_channel",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": data["message"]}},
                {"type": "divider"},
                {
                    "type": "image",
                    "block_id": "image",
                    "image_url": data['img'],
                    "alt_text": f"Mayer Multiple Histogram for {ticker}",
                },
            ],
        }


def _prepare_mm_body_without_data(ticker: str):
    return {
            "response_type": "in_channel",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": f'"{ticker}" is either an invalid ticker or no data is available.'}},
            ],
        }

def prepare_mm_body(ticker: str) -> dict:
    res = requests.get(f"{API_URL}/charts/mayer_multiple/png/{ticker}")
    data = res.json()
    if data.get('img', None):
        return _prepare_mm_body_with_data(data, ticker)
    return _prepare_mm_body_without_data(ticker)
