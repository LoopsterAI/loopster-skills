# Loopster

Run real go-to-market plays with Loopster from Claude: build prospect lists, find work emails and phones, enrich lists, watch buying signals and job changes, route inbound leads, clean your CRM and launch outbound campaigns. The plugin bundles 15 plays, 20 single-step skills and the Loopster connector.

## Install

In Claude Code: `/plugin install loopster --marketplace LoopsterAI/loopster-skills`. On claude.ai: Customize, Plugins, Add, then Add marketplace with `https://github.com/LoopsterAI/loopster-skills`.

## Use it

Connect Loopster from the plugin's Connectors tab and sign in with your Loopster account. Then say "Set up Loopster", or ask for what you need, for example "Build a list of VPs of Sales at US fintechs and find their work emails". Every play tries free Loopster data first, shows the price of any paid step and asks before it spends, and asks again before anything leaves Loopster, such as a CRM update, a campaign push or a Slack message.

## Data

The skills send your requests and the records you work with (companies, people, list rows) to your Loopster workspace through the Loopster connector at https://app.loopster.ai/api/mcp. Paid steps are charged to your Loopster wallet. The plugin stores nothing itself. CRM, sequencer and Slack actions run through the accounts you connect in Loopster, only after you approve them.

Help: https://help.loopster.ai
