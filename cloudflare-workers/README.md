# Service Workers

API gateway and routing service.

## Setup

1. Install dependencies: `npm install`
2. Configure secrets (see TOKENS.md)
3. Deploy: `npm run deploy`

## Development

```bash
npm run dev
```

## Deployment

Automatic via GitHub Actions on push to main branch.

## API Endpoints

- `/api/health` - Health check
- `/api/usage` - Usage statistics
- `/api/catalog` - API catalog
- `/api/mcp/*` - MCP server routing

## Configuration

See TOKENS.md for required environment variables.
