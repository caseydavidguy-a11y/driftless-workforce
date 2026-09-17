# Driftless AI Agents + App Opportunity Hunter

## Purpose

Add four agents around the existing Driftless Workforce Command Center without replacing its current employer-intelligence pipeline:

1. **Scout** — discovers qualified employer prospects from existing hiring intelligence and approved external sources.
2. **Hunter** — enriches prospects with the most relevant business decision-maker and verified business contact information.
3. **Outreach** — drafts and sends controlled, personalized business outreach and follow-ups; stops on reply or suppression.
4. **Opportunity Hunter** — identifies mobile-app opportunities from demand, revenue, ranking, and review signals, then produces build-ready MVP briefs.

## Existing foundation

The current repository already provides La Crosse-area employer intelligence, normalization, scoring, evidence tracking, prospect profiles, change detection, and a browser recruiting workspace. The AI layer should consume these outputs rather than duplicate them.

## Driftless pipeline

```text
Existing employer intelligence
          |
        Scout
          |
   qualified prospect
          |
        Hunter
          |
 verified decision-maker
          |
       Outreach
          |
   reply / meeting / opt-out
          |
     Command Center
```

### Scout requirements

- Consume normalized employer opportunities and hiring-history signals already produced by the repository.
- Support target geography, industry, role-family, and minimum-opportunity-score filters.
- Preserve source URLs and evidence for every discovered prospect.
- Deduplicate against existing employers and prior prospects.
- Never contact a prospect itself.

### Hunter requirements

- Prefer role-relevant business contacts: HR/recruiting, talent acquisition, operations leadership, GM/owner where appropriate.
- Store contact source and verification timestamp.
- Do not infer or fabricate email addresses.
- Keep a suppression list and avoid contacts already marked do-not-contact.

### Outreach requirements

- Start in draft/approval mode.
- Generate individualized business outreach from verified company/job evidence.
- Maintain sequence state and next-action time.
- Stop the sequence on reply, explicit opt-out, bounce, or manual hold.
- Include an easy opt-out mechanism appropriate to the channel.
- Log message metadata and source evidence in the Command Center.
- Sending credentials/secrets must live server-side; never in GitHub Pages or client JavaScript.

## App Opportunity Hunter

The AriaCodez workflow uses Sensor Tower to inspect estimated app downloads/revenue, App Store listings and critical reviews, then Blink to build a native iOS app. Aria explicitly frames the method as competing in a category while rebuilding under a new brand and fixing recurring complaints, rather than copying protected names, logos, code, or content.

The automated version should rank opportunities using:

- demand / download evidence
- revenue evidence where available
- trend direction
- review volume and rating
- recurring negative-review themes
- competitor concentration
- monetization evidence
- MVP complexity
- dependence on external hardware, licensed catalogs, financial connections, or other high-friction dependencies

Output a build brief containing:

- problem statement
- evidence of demand
- competitor set
- recurring complaints
- differentiated solution
- MVP screens/features
- monetization hypothesis
- App Store positioning/keywords
- launch-content ideas
- validation checklist

The agent should recommend opportunities for human approval. It should not automatically clone or publish a third-party app.

## Initial implementation order

### Phase 1 — Scout

Connect the existing employer-opportunity data to an agent-facing prospect queue.

### Phase 2 — Hunter

Add contact-enrichment interfaces and evidence/verification fields.

### Phase 3 — Outreach

Add server-side email integration, draft mode, sequence state, suppression, and reply handling.

### Phase 4 — Opportunity Hunter

Start with public/accessible app-store and web signals. Treat Sensor Tower's deeper API/Connect capabilities as an optional paid integration; Sensor Tower currently markets API/data-feed access through its Connect offering.

### Phase 5 — App production

Use Blink/Expo for rapid MVP creation after an opportunity is approved. Blink's current iOS publishing flow builds in the cloud and uploads to TestFlight; App Store publishing requires Blink's Max tier and an Apple Developer account.

## Security boundary

The existing Pages deployment is not a secure CRM. Real client/contact records, email credentials, API keys, and candidate information must remain behind the authenticated server boundary. GitHub Pages should receive only sanitized/approved intelligence needed by the UI.

## First success criteria

- Scout can produce a deduplicated queue of qualified prospects from current Driftless intelligence.
- Hunter can attach a sourced business decision-maker to a prospect without fabricating contact data.
- Outreach can generate a personalized draft and record it without sending automatically.
- Opportunity Hunter can produce a ranked list of app opportunities with evidence and a build brief.

Only after those four paths are validated should autonomous sending or automatic app publishing be enabled.
