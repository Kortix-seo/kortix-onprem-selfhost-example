# Kortix on-prem starter: a manifest, a boundary, and a grant audit

Kortix is the open-source AI Operating System, and this repository is a
starting point for the on-premises half of a deployment: the governance files
that decide what each agent may touch, a written boundary of what the stack
puts on your machine and what it does not, and a script that turns the
manifest's grants into a table a security reviewer can read.

It is built from Kortix's documented self-host flow
(https://kortix.com/docs/host) and the shape of the starter manifest
(https://github.com/kortix-ai/suna/blob/dev/packages/starter/templates/base/kortix.yaml),
both checked 2026-10-28. It is a starting point, not an official artifact.

## Why the manifest is the first file to read

A Kortix project splits governance from behavior. The `agents:` map in
`kortix.yaml` is governance only: `connectors`, `secrets`, `kortix_permissions`,
`skills`, `workspace` and `enabled`. What an agent does lives in
`agents/<name>.md`, in that file's frontmatter and body.

The map is deny-by-default. An omitted `connectors`, `secrets`,
`kortix_permissions` or `skills` line resolves to `none`, so an agent declared
without a grant reaches nothing. That is why the field that matters to a
reviewer is not how many tools exist, but which agents carry `all`.

## What the audit prints

```console
$ python3 scripts/audit_grants.py kortix.yaml
agent                 connectors   secrets  permissions  skills
-----------------------------------------------------------------
ops                   all          all      all          all
ledger-reader         none         none     all          all
transcript-auditor    none         none     all          all

1 of 3 agents reach every connector and every secret: ops. Each one is a grant a reviewer reads first.
```

The script reads only the `agents:` map, defaults every missing grant to
`none`, and exits `3` when at least one agent holds both `connectors: all` and
`secrets: all`, so CI can fail on a grant nobody meant to widen. It needs no
dependencies: `python3 scripts/audit_grants.py`.

## Layout

| Path | What it holds |
|---|---|
| `kortix.yaml` | the manifest: three agents, one of them the general worker |
| `agents/` | one markdown file per agent, behavior only |
| `docs/boundary.md` | what runs on your machine, what runs off it, and why |
| `scripts/audit_grants.py` | the grant table and the exit code above |
| `.env.example` | the values the stack reads, with the docs' names |

## Standing up the stack

The install is one bootstrap command on the server, documented in full at
https://kortix.com/docs/host. Point `A`/`AAAA` records for the domain and
`api.<domain>` at the machine, add the wildcard for previews, open 80 and 443,
then:

```sh
# the bootstrap one-liner is on https://kortix.com/docs/host, step 2
kortix self-host configure
kortix self-host start
kortix self-host doctor
```

`kortix self-host init` writes `docker-compose.yml`, `.env`, a `Caddyfile` and
`updater.sh` into `~/.config/kortix/self-host/<instance>/`. `doctor` runs seven
checks; `open-sign-up` is the one to fix first, because until you set `EMAIL_URL`
or `DISABLE_SIGNUP=true`, anyone who reaches the instance can create a confirmed
account for any address, the admin address included.

## The two records a reviewer asks for

They are not the same artifact, and the difference decides what you can answer
after the contract ends.

- **The grant**, and the commit history behind it, are files in your
  repository. They cost nothing to read. A manifest edit takes effect when it
  reaches the default branch, and a dashboard, API or SDK edit commits there at
  once, so the commit is what records who changed a grant and when.
- **The action log** is the platform's. Every action is recorded. Reading,
  exporting and streaming the audit log depend on the plan, and the per-session
  audit view is an Enterprise entitlement.

## Where the layers are argued in prose

The companion guide at https://onpremaiguide.com/what-is-on-prem-ai works
through the four layers a buyer is choosing between, and
https://onpremaiguide.com/self-hosted-ai-agent-platform is the platform
checklist for the runtime layer.

Three more pages answer what a reviewer asks next.
https://onpremaiguide.com/on-prem-ai-server-requirements covers the inference
layer underneath: what the model server needs before an agent runtime has
anything to call. https://onpremaiguide.com/on-prem-llm-vs-api decides where
the model should sit, on your own cards or behind a provider's API, because
that choice is what makes this stack the right shape at all. And
https://onpremaiguide.com/on-prem-ai-security-and-audit is the record: the six
questions that survive a security review, asked of this manifest, onprem.ai and
ibl.ai side by side.

This repository is the artifact; those are the argument.

## What this repository is not

It is not an inference stack. A self-hosted Kortix instance runs the platform,
the database and the files on your machine, while sessions run on Platinum
sandboxes and model calls go to the provider each project connects. Read
`docs/boundary.md` before a review, and do not describe the deployment as
fully air-gapped unless your own install is.
