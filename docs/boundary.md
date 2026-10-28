# What runs where

Kortix is open source, and this is the boundary of a self-hosted Kortix
instance, taken from the
documented install at https://kortix.com/docs/host and checked 2026-10-28.
It is the first thing a security reviewer asks about, so it is written down
here instead of being inferred from a diagram.

## On the machine you keep

- The Compose project `kortix-<instance>`: the web front end, `kortix-api`
  serving `/v1`, the standalone `llm-gateway`, a one-shot `kortix-migrate` job
  and a daily `kortix-updater`.
- Postgres, the storage buckets and the Supabase distribution images, each
  pinned by digest.
- The project repository: `kortix.yaml`, the agent files, skills, memory and
  the connector configuration. This is the grant file a reviewer reads.
- `~/.config/kortix/self-host/<instance>/` holding `docker-compose.yml`,
  `.env`, `Caddyfile` and `updater.sh`. `API_KEY_SECRET` in `.env` encrypts
  every stored credential, so back it up with the database.

## Off the machine

- **Sessions.** Every session runs on a Platinum sandbox that `kortix-api`
  creates with `PLATINUM_API_KEY`, and the sandbox calls back to the instance's
  public URL (`KORTIX_URL`). A loopback install runs the stack and starts no
  session, because no sandbox can reach an API bound to `127.0.0.1`.
- **Model calls.** The gateway calls the providers each project connects.
- **Images.** Pulled from Docker Hub; pulls need no credentials.

## Consequences a reviewer should write down

- If the rule is that no agent machine may connect out, a managed sandbox does
  not satisfy it. That rule picks the vendor list, not just the install.
- If the rule is that the grant and its history stay yours, they do on this
  install: they are files in your repository.
- The action log is a separate artifact from the grant. Every action is
  recorded; reading, exporting and streaming the audit log depend on the plan,
  and the per-session audit view is an Enterprise entitlement.

Two companion pages for a review: the grant and audit questions in more
detail at https://onpremaiguide.com/on-prem-ai-security-and-audit, and the
machine sizing that goes with this stack at
https://onpremaiguide.com/on-prem-ai-server-requirements.
