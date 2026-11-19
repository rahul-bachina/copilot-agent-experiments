# Power Automate

No flow in this starter writes a row or sends a message.

A later flow, if an organisation builds one, may show the JSON to the employee and wait. The wait is not `record_employee_decision()`. That function has to receive the separate object, the inventory hash, and the skill hash, and the approver has to be the employee on the directory.

A flow must not write the proposal into an HR system, a payroll system, or a performance form. The catalogue names Microsoft 365 because that is where a CV or a learning record might already sit. This file does not authorise a Graph call. A mailbox item is out of scope for a skill proposal.

The employee can reject or correct a skill after HR has validated it. A flow that locks the row against a later rejection would be outside this starter.
