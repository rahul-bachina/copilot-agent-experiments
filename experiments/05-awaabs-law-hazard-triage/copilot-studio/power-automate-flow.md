# Power Automate flow for the clock

One flow. It returns JSON. It does not send, and it does not write.

## Trigger

When Copilot Studio calls an agent flow, or an HTTP request from a locked-down identity. Prefer a solution-aware flow in a dedicated environment, not the default environment.

## Inputs

The same fields as [../schema/clock_tool.schema.json](../schema/clock_tool.schema.json). `additionalProperties` is false. Do not add a "send" or "create row" input.

Default `officer_approved_category`, `officer_approved_clock`, `social_home_in_england`, `part_6_complied`, and `caller_asserts_phase_2_instrument_in_force` to false in the flow. A blank must not become true.

## Steps

1. Validate that `aware_at` parses as a timezone-aware time. If it does not, return a 400 and stop.
2. Call the internal API that runs `calculate_statutory_clock`. Pass the fields through. Do not transform a date in the flow.
3. Return the JSON body to Copilot Studio.

No other actions. In particular:

- No "Send an email", "Send an SMS", or "Post a message" action.
- No Dataverse create or update.
- No connector to a housing management product.
- No approval action that approves itself. The officer ticks the flags in the topic. The flow only receives them.

## Identity

Use a managed identity or a service principal that can call only that API. If a secret has to be used, store it in Key Vault and reference it. Do not put it in the flow definition. The experiment does not provision the vault.

## DLP

Put the environment in a Power Platform data-loss-prevention policy that blocks mail connectors and any housing connector. The flow should still work, because it only calls the clock API. If the policy blocks that call, the triage stops. It does not fall back to a hand-written date.

## What this flow is not

It is not the regulation 9 summary, and it is not a reasonable-endeavours file. The endeavours draft is a separate skill on the GitHub Copilot harness, and it uses [../schema/endeavours_tool.schema.json](../schema/endeavours_tool.schema.json). That skill also does not file the record.
