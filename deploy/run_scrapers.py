import os
import subprocess
from datetime import datetime, timedelta
from azure.storage.blob import BlockBlobService, ContentSettings
import rediswq


STATUS_CONTAINER = os.getenv('AZURE_STATUS_CONTAINER', 'city-scrapers-status')
STATUS_COLOR_MAP = {
    'running': '#44cc11',
    'failing': '#cb2431',
    'unclear': '#dfb317'
}
STATUS_ICON = '''
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="144" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="a">
        <rect width="144" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h67v20H0z"/>
        <path fill="{color}" d="M67 0h77v20H67z"/>
        <path fill="url(#b)" d="M0 0h144v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
        <text x="345" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{status}</text>
        <text x="345" y="140" transform="scale(.1)">{status}</text>
        <text x="1045" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{date}</text>
        <text x="1045" y="140" transform="scale(.1)">{date}</text>
    </g>
</svg>
'''


def upload_status_svg(scraper_name, status):
    blob_service = BlockBlobService(
        account_name=os.getenv('AZURE_ACCOUNT_NAME'),
        account_key=os.getenv('AZURE_ACCOUNT_KEY'),
    )
    blob_service.create_blob_from_text(
        STATUS_CONTAINER,
        '{}.svg'.format(scraper_name),
        STATUS_ICON.format(
            color=STATUS_COLOR_MAP[status],
            status=status,
            date=(datetime.utcnow() - timedelta(hours=6)).strftime('%Y-%m-%d'),
        ),
        content_settings=ContentSettings(
            content_type='image/svg+xml', cache_control='no-cache'
        ),
    )


if __name__ == '__main__':
    q = rediswq.RedisWQ(
        name=os.getenv('SCRAPER_QUEUE_NAME'),
        host=os.getenv('REDIS_HOST'),
    )

    while not q.empty():
        item = q.lease(block=True, timeout=2)
        if item is not None:
            scraper_name = item.decode('utf-8')
            try:
                subprocess.check_call(
                    ['scrapy', 'crawl', scraper_name], env=os.environ
                )
                status = 'running'
            except subprocess.CalledProcessError:
                status = 'failing'
            upload_status_svg(scraper_name, status)
            q.complete(item)
        else:
            print('Waiting for work')
    print('Queue empty, exiting')
