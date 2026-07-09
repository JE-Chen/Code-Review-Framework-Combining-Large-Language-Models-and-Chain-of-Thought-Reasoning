# Security policy

## Executing pull-request code

Treat every pull request, generated test, build script, and dependency hook as
untrusted code. ``prthinker verify`` defaults to Docker and requires an
explicit image. For fork PRs, pin the image by digest, keep networking
disabled, mount no credentials, and use an ephemeral worker. Do not use
``--sandbox none --allow-unsandboxed`` for untrusted changes unless you
have reviewed every line of the change and explicitly accept that it
executes with your own privileges.

The sandbox is defense in depth, not a proof of isolation. Operators remain
responsible for runtime patching, host-kernel hardening, image contents, and
cleanup of compromised workers.

## Supported versions

Security fixes are applied to the latest release and `main` until the project
publishes a broader support table.

## Reporting a vulnerability

Do not open a public issue. Use GitHub's **Report a vulnerability** private
advisory for this repository. Include affected version/commit, impact,
reproduction steps, and any suggested mitigation. Maintainers should
acknowledge a complete report within seven days and coordinate disclosure after
a fix is available.

Treat pull-request diffs, repository rules, retrieved documents, model output,
and author replies as untrusted input. A prompt-injection bypass, secret leak,
unsafe suggestion execution, authentication bypass, or sandbox escape is a
security issue rather than an ordinary model-quality bug.
