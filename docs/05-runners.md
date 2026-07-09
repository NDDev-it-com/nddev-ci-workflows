# Runners

GitHub-hosted and self-hosted runners execute jobs. This doc covers the runner
types, the cost model across the three tiers, egress hardening, and self-hosted
considerations.

## GitHub-hosted runner types

| Type | Labels | Notes |
| --- | --- | --- |
| Standard Linux | `ubuntu-latest`, `ubuntu-24.04` | cheapest; the library default |
| Standard Windows | `windows-latest` | higher minute multiplier |
| Standard macOS | `macos-latest` | highest standard multiplier |
| ARM64 (Linux/Windows) | `ubuntu-24.04-arm`, `windows-11-arm` | native ARM builds |
| Larger runners | custom labels | more vCPU/RAM; billable |
| GPU runners | custom labels | ML/graphics; billable |
| macOS-XL | custom labels | Apple-silicon XL; **billable even for public** |

The library defaults reusables to `ubuntu-latest` and exposes a `runner` (or
`os_list`) input to select alternatives.

<a id="cost-model"></a>
## Cost model by tier

| Scenario | Cost |
| --- | --- |
| Public repo + standard hosted runner | **Free, unlimited minutes** |
| Public repo + larger / GPU / macOS-XL runner | **Billable** (even on public) |
| Private repo + standard runner | Free monthly minutes, then billed per-minute |
| Private repo + Windows / macOS | Same, at higher minute **multipliers** |
| Any repo + self-hosted runner | No GitHub minute billing; your infra cost |

Key points:

- **Standard hosted runners are free with unlimited minutes on public repos.**
- **Larger, GPU, and macOS-XL runners are always billable**, including on public
  repositories — do not assume "public = free" for them.
- On private repos, non-Linux runners consume the included-minutes budget faster
  because of platform multipliers. The private-free tier keeps matrices to Linux
  where possible (see [02 Private free](02-private-free.md)).

## July 2026 runner governance updates

GitHub added more hosted-runner governance controls on 2026-06-25:

- admins can disable standard hosted-runner labels such as `ubuntu-latest`;
- macOS runners can be placed in runner groups with repository/workflow access
  controls;
- runner groups can enforce concurrency and routing policy.

RHEL 9 and RHEL 10 images for Linux x64 larger runners are also in public
preview. They are useful for enterprise compatibility testing, but they remain
larger-runner capacity and therefore metered. The catalog entries are
`hosted-runner-governance-controls` and `rhel-larger-runner-images`.

## harden-runner egress control

`step-security/harden-runner` monitors and optionally restricts network egress
from a job, catching exfiltration and unexpected outbound calls.

- **`egress-policy: audit`** — observe and report outbound connections; nothing
  is blocked. Start here.
- **`egress-policy: block`** — deny everything except an explicit
  `allowed-endpoints` list. Use once the audit run has revealed the real egress
  set.

```yaml
- name: Harden runner
  uses: step-security/harden-runner@<full-sha>  # pinned in the library
  with:
    egress-policy: block
    allowed-endpoints: >
      agent.api.stepsecurity.io:443
      github.com:443
      api.github.com:443
```

Harden-Runner is **free on public repos and paid on private repos**. The library
therefore references it only from explicit public/GHAS workflows. Cross-tier
and private-free workflows contain no action reference at all. A step-level
boolean is not a valid off switch because JavaScript actions can have `pre` and
`post` hooks whose lifecycle is independent of the main-step condition.

Recommended progression: `audit` → review the observed endpoints → `block`
with an explicit allow-list.

<a id="self-hosted"></a>
## Self-hosted runners and ARC

Self-hosted runners run on your own machines and skip GitHub minute billing, but
you own patching, isolation, and security.

- **Never** attach self-hosted runners to a **public** repository or any repo
  that accepts forked pull requests — an attacker's PR could execute code on
  your infrastructure. Use ephemeral, isolated runners if you must.
- **Actions Runner Controller (ARC)** runs runners as ephemeral Kubernetes pods
  that auto-scale and are destroyed after each job, which is the recommended
  pattern for private-fleet CI.
- Apply egress controls at the network layer; harden-runner's hosted-runner
  features do not all apply to self-hosted.

---
Last verified: 2026-07-10
