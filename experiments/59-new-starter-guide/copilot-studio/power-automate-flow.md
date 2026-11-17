# Power Automate

Do not add a flow that calls the service desk, the HR system, or mail.

If a tenant later wraps the Python, the flow returns the JSON and stops. It does not:

- create an equipment request
- create an account
- grant access
- enrol a course
- send the checklist
- write a personnel record

The line manager's approval is a step a person takes on the exact checklist id and item digest. It is not a condition inside the request text. After that step, a flow may store the in-memory receipt only if the organisation has decided, outside this starter, where that receipt lives. This repository does not include that connector.

Power Platform DLP should block mail and HR connectors if someone adds them later. This starter has none.
