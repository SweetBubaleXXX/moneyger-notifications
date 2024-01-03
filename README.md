## Configuration

You can create `.env` file in project root directory.

#### Following env variables are required:

- `DATABASE_URL`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `CACHE_URL`
- `MQ_URL`
- `MAIL_HOST`
- `MAIL_USER`
- `MAIL_PASSWORD`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

#### Optional variables:

- `LOG_LEVEL`
- `XFF_TRUSTED_PROXY_DEPTH` _number_
- `DEFAULT_DATABASE`
- `MAIL_PORT` _number_
- `MESSAGE_STORAGE_MAX_SIZE` _number_

## Docker

These variables must be present in your `.env` file:

- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `REDIS_PASSWORD`
- `MQ_URL`
- `MAIL_HOST`
- `MAIL_USER`
- `MAIL_PASSWORD`

Optional variables:

- `SERVICE_NETWORK`
- `SERVICE_NETWORK_EXTERNAL` _boolean_

### Development

To run development containers:

```bash
docker compose -f ./docker-compose.dev.yml up -d --build
```

### Production

To run production containers:

```bash
docker compose up -d
```
