# Changelog

## [Unreleased]

## [0.1.0] - 2026-07-04

### Added

- Initial reusable GitHub Actions CI/CD + supply-chain workflow library for the
  NDDev estate, split into two tiers.
- Public-only reusables (free on public repos): `public-codeql.yml`,
  `public-scorecard.yml`, `public-dependency-review.yml`.
- Dual-tier reusables (free on both; `enable_harden_runner`/`upload_sarif`
  toggles for the private free tier): `secret-scan.yml` (digest-pinned
  gitleaks), `actionlint.yml` (checksum-verified), `zizmor.yml`,
  `cross-platform-smoke.yml`, `release-supply-chain.yml`.
- Private free-minimal reusable: `private-static.yml`.
- Self-CI (`ci.yml`) dogfoods `actionlint` and `zizmor` on this repository and
  enforces a reusable-workflow contract; tag-driven `release.yml` publishes an
  attested SBOM/checksum bundle via `release-supply-chain.yml`.
- All third-party actions pinned to full commit SHAs; least-privilege
  `permissions`; concurrency and timeouts on every workflow.
