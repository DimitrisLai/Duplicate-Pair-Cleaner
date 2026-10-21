# Code signing policy

**Current status (October 2026):** Duplicate Pair Cleaner v3.0.0 is **unsigned**. Windows Defender SmartScreen may display **"Windows protected your PC"** and **"Unknown publisher"** for the downloadable ZIP's `DuplicatePairCleaner.exe`. The software has **not** yet been accepted by SignPath Foundation, and its GitHub release must not be advertised as signed.

## Purpose

We intend to provide authenticated public releases, preferably using a no-cost open-source signing program such as [SignPath Foundation](https://signpath.org/). Signing establishes a verifiable publisher and protects signed executables from undetected modification, but **does not guarantee an immediate SmartScreen warning-free experience**. [Microsoft's SmartScreen guidance](https://learn.microsoft.com/windows/apps/package-and-deploy/smartscreen-reputation) explains that new signed binaries can still require reputation.

## Proposed open-source signing service (not active)

If this project is approved, future signing would use **“Free code signing provided by SignPath.io, certificate by SignPath Foundation”**. This statement is **conditional** and is not a claim that the current releases have been signed or endorsed.

## Team roles

The public repository is maintained by [DimitrisLai](https://github.com/DimitrisLai).

- **Authors / code maintainers:** DimitrisLai.
- **Reviewers:** DimitrisLai reviews incoming pull requests. Changes by external contributors are not merged without maintainer review.
- **Release signing approver:** DimitrisLai. Each release signing request will require explicit review and approval.
- **Additional contributors:** May be appointed only after their access and review responsibilities are documented.

All people with release or signing permissions must enable multi-factor authentication for GitHub and any signing service.

## Privacy policy

**This program will not transfer any information to other networked systems unless specifically requested by the user or the person installing or operating it.**

Duplicate Pair Cleaner processes file names and moves or renames selected local files only after user approval. It neither uploads user files nor collects telemetry. Third-party components used to build the portable executable are included to provide Python runtime support.

## Release security commitments

1. Keep all application sources, build scripts and workflows public.
2. Run automated tests and use GitHub-hosted Windows build runners for published EXEs.
3. Ensure signing requests reference the original GitHub Actions build artifact, so signed bytes can be traced to a source revision.
4. Require explicit manual approval of every signing request; no automatic signing of unreviewed contributions.
5. Set consistent product and version metadata on signed binaries; timestamp verified signatures and check them with `Get-AuthenticodeSignature`.
6. Upload **only** verified signed binaries to future releases advertised as signed; never change signed files after signing.
7. Publish SHA-256 digests to help users check downloaded files and keep the signing status accurate on the release page.
8. Retain older unsigned releases clearly labeled; a future signed release does not retroactively sign existing binaries.

## SignPath Foundation preparation checklist

- [x] Public MIT-licensed project, documented application, reproducible GitHub Actions workflow, published portable EXE.
- [ ] Confirm project eligibility and reputation with SignPath Foundation (approval is discretionary).
- [ ] Confirm GitHub account has 2FA and configure any required SignPath account 2FA.
- [ ] Submit application at https://signpath.org/apply.html.
- [ ] After approval: configure SignPath organization, certificate, trusted GitHub builder, signing policy, artifact configuration, GitHub App access, and required secrets.
- [ ] Add signing stage between building and publishing the next release; independently verify the resulting Authenticode signature.
- [ ] Conduct a download-and-run test on a clean Windows PC and document SmartScreen behavior truthfully.

**Do not add an active signing workflow requiring secrets or claim verified-publisher status until the signing provider has approved the project.**
