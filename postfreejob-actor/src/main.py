"""
This module defines the `main()` coroutine for the Apify Actor, executed from the `__main__.py` file.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""
from .postjobfree_crawler import crawl


# Apify SDK - toolkit for building Apify Actors, read more at https://docs.apify.com/sdk/python
from apify import Actor


async def main() -> None:
    """
    The main coroutine is being executed using `asyncio.run()`, so do not attempt to make a normal function
    out of it, it will not work. Asynchronous execution is required for communication with Apify platform,
    and it also enhances performance in the field of web scraping significantly.
    """
    async with Actor:
        # Structure of input is defined in input_schema.json
        actor_input = await Actor.get_input() or {}
        keyword = actor_input.get('keyword')
        location = actor_input.get('location')
        radius = actor_input.get('radius')


        # Extract all headings from the page (tag name and text)
        headings = crawl(location=location, radius=radius, keyword=keyword)

        # Save headings to Dataset - a table-like storage
        await Actor.push_data(headings)
