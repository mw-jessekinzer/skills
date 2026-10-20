# Wireframes and Prototypes

Prototypes bridge ideas and implementation so the team tests concepts before costly development.

## Fidelity

| Level | Use for | Detail |
| --- | --- | --- |
| Low (sketch) | Brainstorming, flow options | Layout only, no color or type |
| Medium | Team alignment, early feedback | Layout, real content, basic interaction |
| High (HTML prototype on MW Platform Design System v4) | Developer handoff, user testing | Real components, states, worst-case toggle, interactions that work |

For platform handoff, build high fidelity in HTML: it proves interactions and states that static frames can't.

## Do

- Start from the flow, then the screens. Write entry points, steps, decisions and exits first.
- Use real Midwestern content (clients, projects, hours, people), never lorem ipsum.
- Include edge cases from the start: empty, error, worst-case data.
- Design mobile and desktop together; the platform must work at 390px.
- Define every interaction: trigger, result, feedback, keyboard path.
- Share early; collect comments on the prototype itself.
- Keep a dev toolbar (data, state, fixes on and off) so reviewers see each state without code.

## Don't

- Jump to polish before the flow is validated.
- Leave interactions undefined or test only with the team.
- Ignore accessibility or responsive behavior.
- Lock decisions before they've been tried with real data.

## Flow template

```
Screen: Daily Log
Entry: Sidebar, Dashboard Today card, Report a Blocker
Steps: Log time on the track -> write what got done per project -> add blockers -> tick to dos -> Post Day
Decisions: Earlier day unposted? -> Review and post it first (logging stays open)
Exits: Posted (toast), Keep Editing, navigate away (draft saved)
Refresh: Draft restored as saved
```

## Testing a prototype

Five representative users, task-based, unmoderated or moderated. Measure completion, time on task, errors and satisfaction. Report the top three friction points with quotes and recommended changes.
