import logging

logging.basicConfig(level=logging.DEBUG)

import os

from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
# TODO: Remove this
import sys
sys.path.append("..")

from slash_commands.market_navigator import prepare_mm_body

app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
app_handler = AsyncSlackRequestHandler(app)


async def _market_navigator_ack(ack, body):
    text = body.get("text")
    if text is None or len(text) == 0:
        await ack(f":x: Usage: /market_navigator (ticker)")
    else:
        # TODO: Validate ticker here.
        await ack(f"Crunching data for {body['text']}")

async def _market_navigator_compute(body, logger, respond):
    ticker = body["text"]
    logger.info(f'Slack command for {ticker}')
    body = prepare_mm_body(ticker)
    await respond(body)

app.command("/market_navigator")(
    ack=_market_navigator_ack,
    lazy=[_market_navigator_compute]
)

api = FastAPI()

@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)