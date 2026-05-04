# Security

## Authentication model

Access policy is enforced by client origin:

| Origin | Dashboard (`/`) | API (`/api/*`) |
|--------|-----------------|----------------|
| Localhost / LAN (RFC1918) | Open | Open |
| External / public IP | HTTP Basic Auth | API key required |

Configure credentials in `.env` (see [configuration.md](configuration.md)):

```bash
cp .env.example .env
./generate-api-key.sh   # prints a secure random API_KEY
nano .env
```

External API calls require the key via header:

```bash
curl -H "X-API-Key: <your-key>" http://<host>:8080/api/health
# or
curl -H "Authorization: Bearer <your-key>" http://<host>:8080/api/health
```

---

## SSL certificates

Self-signed certificates are generated automatically on first startup in `./certs/`, with the server's detected public IP included in the SAN.

To use your own certificates (e.g. Let's Encrypt):

```bash
cp /etc/letsencrypt/live/your.domain/fullchain.pem certs/server.crt
cp /etc/letsencrypt/live/your.domain/privkey.pem   certs/server.key
docker compose restart electrumx
```

Certificates are mounted read-only into the container and never rebuilt if they already exist.

---

## Firewall

```bash
sudo ufw allow 13496/tcp   # BitcoinPurple P2P
sudo ufw allow 50001/tcp   # ElectrumX TCP
sudo ufw allow 50002/tcp   # ElectrumX SSL
# open 8080 only after configuring auth in .env
sudo ufw enable
```

RPC (13495) and ZMQ (28332–28335) must **not** be opened — they are internal-only.
