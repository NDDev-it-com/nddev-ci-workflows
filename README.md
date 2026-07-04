# nddev-ci-workflows

Reusable GitHub Actions CI/CD and supply-chain workflows for the NDDev estate.

Two tiers, by repository billing reality:

- **Public tier** — the full free OSS security suite (code scanning, Scorecard,
  dependency review, egress hardening, SBOM/attestations).
- **Private free tier** — only zero-cost capabilities, because CodeQL, native
  secret scanning, dependency review, and harden-runner are paid on private
  repositories. Dual-tier workflows expose `enable_harden_runner` /
  `upload_sarif` toggles; set them `false` on private repos.

## Capability tiers

| Capability | Workflow | Public (free) | Private (free) |
| --- | --- | --- | --- |
| CodeQL code scanning | `public-codeql.yml` | ✅ | ❌ paid (GHAS) |
| OSSF Scorecard | `public-scorecard.yml` | ✅ | ❌ public-oriented |
| Dependency Review | `public-dependency-review.yml` | ✅ | ❌ paid (GHAS) |
| Gitleaks secret scan | `secret-scan.yml` | ✅ | ✅ (`enable_harden_runner: false`) |
| actionlint | `actionlint.yml` | ✅ | ✅ (`enable_harden_runner: false`) |
| zizmor workflow security | `zizmor.yml` | ✅ | ✅ (`enable_harden_runner: false`, `upload_sarif: false`) |
| Cross-platform smoke | `cross-platform-smoke.yml` | ✅ | ✅ |
| Release supply chain (SBOM/attest) | `release-supply-chain.yml` | ✅ | ✅ |
| Lightweight static validation | `private-static.yml` | ✅ | ✅ |

## Usage

Always pin by full commit SHA (tags are mutable). Dependabot bumps the SHA.

### Public repository (full suite)

```yaml
# .github/workflows/security.yml
name: security
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
  schedule: [{ cron: "31 2 * * 1" }]
permissions: {}
jobs:
  codeql:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/public-codeql.yml@<sha>
    with:
      languages: '["python","actions"]'
  scorecard:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/public-scorecard.yml@<sha>
  secret-scan:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/secret-scan.yml@<sha>
  actionlint:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/actionlint.yml@<sha>
  zizmor:
    permissions: { contents: read, security-events: write }
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/zizmor.yml@<sha>
```

```yaml
# .github/workflows/dependency-review.yml
name: dependency-review
on: { pull_request: { branches: [main] } }
permissions: {}
jobs:
  dependency-review:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/public-dependency-review.yml@<sha>
```

### Private repository (free-minimal)

```yaml
# .github/workflows/security.yml
name: security
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
permissions: {}
jobs:
  secret-scan:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/secret-scan.yml@<sha>
    with:
      enable_harden_runner: false
  actionlint:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/actionlint.yml@<sha>
    with:
      enable_harden_runner: false
  zizmor:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/zizmor.yml@<sha>
    with:
      enable_harden_runner: false
      upload_sarif: false
  validate:
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/private-static.yml@<sha>
    with:
      command: "python3 scripts/validate_all.py"
```

### Release (either tier)

```yaml
# .github/workflows/release.yml
name: release
on: { push: { tags: ["[0-9]+.[0-9]+.[0-9]+"] } }
permissions: {}
jobs:
  publish:
    permissions: { contents: write, id-token: write, attestations: write }
    uses: NDDev-it-com/nddev-ci-workflows/.github/workflows/release-supply-chain.yml@<sha>
    with:
      version: ${{ github.ref_name }}
      package_name: my-repo
      archive_paths: "README.md LICENSE VERSION CHANGELOG.md src"
```

## Inputs

Each workflow documents its inputs in its header comment. Common inputs:

- `runner` — runner label (default `ubuntu-latest`).
- `enable_harden_runner` — dual-tier hardening toggle (default `true`; `false`
  on private repos where harden-runner is paid).
- `upload_sarif` — upload results to code scanning (default `true`; `false` on
  private repos where code scanning is paid).
- `egress_policy` — `audit` (default) or `block` for harden-runner.

## Conventions

- Third-party actions pinned to full commit SHAs with version comments.
- Least-privilege `permissions`, `concurrency`, and `timeout-minutes` everywhere.
- Digest-pinned container images (gitleaks) and checksum-verified downloads
  (actionlint).

## License

[AGPL-3.0-or-later](LICENSE). Author: Danil Silantyev (github:rldyourmnd), CEO NDDev.

- Security policy: [SECURITY.md](SECURITY.md)
- Releases: https://github.com/NDDev-it-com/nddev-ci-workflows/releases
