---
name: explain-handbook-route
description: Explain a handbook route that is already on screen, including the named person and why the question was not answered as policy. Use when the employee or HR asks what the route means. Do not decide the case, contact anyone, or send the route.
---

# Explain a handbook route

Harness: Copilot Studio **Microsoft Copilot harness**, in the skills layout the common brief calls the GitHub Copilot harness. It is a Copilot Studio runtime. It is not the GitHub Copilot service. The page opened on 16 November 2026 names this runtime the Microsoft Copilot harness.

This skill reads JSON that `answer_handbook()` already returned. It does not classify the question again and it does not call Experiment 32 to confirm a category.

The `name` and `description` above are the skill fields. Generative orchestration, where the tenant uses it, selects a skill from that description. This file does not assign trigger phrases or routing weights.

## When to use this skill

Use it when someone asks what to do with a route, a withheld marking, or a gap that is already in the JSON. Answering a new handbook question is the other skill.

## Tool contract

There is no second tool. Read the JSON. Do not call `acknowledge`, `decide_entitlement`, `send_answer`, `write_record`, or `approve_source`. `callable_by_agent: false` on those names in `schema/tools.json` is the control.

## What to show

1. `human_route.named` and `human_route.reason`. Say a person is always available.
2. If the reason is distress or safeguarding, say it was not treated as a routine policy answer.
3. If a document was withheld, say the marking, the legal hold, and the retention labels. Do not invent the body.
4. `classification_confirmed` is false. Experiment 32 proposed a category. It did not confirm one.
5. `entitlement_decision` is null. Do not fill it in.

Do not decide the case. Do not contact the employee, a manager, or Acas. Do not send the route. Do not write to an HR system.
