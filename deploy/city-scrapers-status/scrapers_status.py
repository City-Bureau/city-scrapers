import os
import boto3
from datetime import datetime

PROJECT_SLUG = 'documenters_aggregator'
STATUS_BUCKET = os.getenv('STATUS_BUCKET')

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


def handler(event, context):
    client = boto3.client('s3')
    print(event)

    if 'detail-type' not in event or event['detail-type'] != 'ECS Task State Change':
        raise ValueError('ERROR: Event is not an ECS task state change event')

    if event['detail']['lastStatus'] != 'STOPPED':
        print('INFO: Last status was not STOPPED, exiting...')
        return

    if event['detail']['containers'][0]['exitCode'] == 0:
        status = 'running'
    else:
        status = 'failed'

    # Pull scraper name from ARN in documenters_aggregator-{SCRAPER}
    task_def = event['detail']['taskDefinitionArn'].split('/')[1]
    scraper = task_def.split(':')[0][len(PROJECT_SLUG) + 1:]
    
    if scraper == '':
        message = 'Could not extract scraper name from {}'.format(event['detail']['taskDefinitionArn'])
        raise ValueError(message)

    client.put_object(
        Bucket=STATUS_BUCKET,
        Key='{}.svg'.format(scraper),
        Body=STATUS_ICON.format(
            color=STATUS_COLOR_MAP[status],
            status=status,
            date=datetime.today().strftime('%Y-%m-%d')
        ),
        CacheControl='no-cache',
        ContentType='image/svg+xml',
    )
