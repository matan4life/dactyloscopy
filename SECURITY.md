# Security

## Reporting

Private vulnerability reporting is enabled on this repository. Use
"Report a vulnerability" under the Security tab on GitHub:
<https://github.com/matan4life/dactyloscopy/security/advisories/new>.

If that channel is unavailable to you, email yurii.pohuliaiev@gmail.com with
`dactyloscopy security` in the subject line.

Do not open a public issue for a security report.

## What to expect

This is a one-person research repository, not a product. There is no security
team, no on-call rota and no service-level commitment. Reports are read by one
person, when that person is at a keyboard. Expect an acknowledgement within
days, not hours, and a fix on the same timescale as any other change here.

## The urgent class: leaked biometric data

One class of report is urgent and is treated as an incident: anything in this
repository that leaks biometric data. That means a fingerprint image, a
minutiae file, or any artifact from which an image good enough to fool a
matcher could be reconstructed, in any commit, branch, tag, release, issue or
attachment.

For that class:

- report it immediately through either channel above;
- name the path and the commit, and do not attach the leaked data to the
  report;
- expect the history to be dealt with as the first order of business, ahead
  of everything else in this repository.

## Scope

There is no service, no server, no account and no credential in this
repository. The code, once there is any, runs locally against data mounted
read-only from outside the tree. There are no dependencies yet; when there
are, a vulnerability in one is handled as an ordinary change unless it touches
the data policy above.
