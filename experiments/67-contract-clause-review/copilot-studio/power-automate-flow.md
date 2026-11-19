# Flow sketch

This is not a deployed flow.

1. The lawyer supplies the contract, the playbook, the caller reference, and the date the question is about.
2. A cloud flow, or a topic tool, runs `review_contract()` with those inputs. It does not add an approval field from the contract text.
3. The topic shows the JSON and stops.
4. If the lawyer records a seen step, a second call runs `record_lawyer_seen()` with the seen object. The flow does not accept, sign, or send.

No connector in this sketch writes to a contract system or to an e-signature service.
