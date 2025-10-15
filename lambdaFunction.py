# handler.py (minimal example)
import boto3, gzip, csv, io, json
s3 = boto3.client('s3')

def lambda_handler(event, context):
    rec = event['Records'][0]['s3']
    bucket = rec['bucket']['name']
    key = rec['object']['key']
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj['Body'].read()
    # CUR is gzipped CSV
    with gzip.GzipFile(fileobj=io.BytesIO(body)) as gf:
        reader = csv.DictReader(io.TextIOWrapper(gf, 'utf-8'))
        total = 0.0
        by_service = {}
        for row in reader:
            cost = float(row.get('lineItem/UnblendedCost', row.get('UnblendedCost', '0')) or 0)
            svc = row.get('product/ProductName', 'Unknown')
            by_service[svc] = by_service.get(svc, 0.0) + cost
            total += cost
    summary = {"total_cost": total, "by_service": by_service}
    # write to dashboard bucket
    out_bucket = 'my-billing-dashboard-aj'
    s3.put_object(Bucket=out_bucket, Key='dashboard/summary.json',
                  Body=json.dumps(summary).encode('utf-8'),
                  ContentType='application/json')
    return {"status": "ok"}
