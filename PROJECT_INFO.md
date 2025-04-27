![Vera Banner](./vera-banner.svg)

# Sentient Chat Hacks 2025 Project

## Inspiration

We were inspired by what we believe is one of the greatest needs in today's society: trustworthy information.
In a world flooded with constant updates, conflicting opinions, and growing bias, finding a reliable stream of credible knowledge has become increasingly difficult.

When designing Vera, we focused not on reinventing the wheel, but on addressing a timeless need — the human desire for clarity, truth, and understanding. Rather than chase novelty for its own sake, we chose to iterate thoughtfully on a real-world problem that isn't going away anytime soon.

We believe Vera offers real value by helping users quickly access credible sources and providing clear, high-level explanations that are easy to digest — typically in just two to three concise paragraphs, readable in under a minute. Vera isn't just about fact-checking — it's about empowering users to feel confident in what they know.

## What It Does

Vera is a conversational fact-checking assistant designed to help users verify claims, clarify misunderstandings, and explore information with confidence.
Built by Cache Flow, Vera provides thoughtful, nuanced responses that encourage learning without confrontation.

When a user asks a question or shares a claim, Vera:

* Searches credible sources to determine if the information is true, false, or partially true.

* Delivers a warm, human-like explanation that reflects the complexity of the topic.

* Lists sources separately at the end of the response using clean, readable Markdown link formatting.

* Handles casual conversation gracefully, maintaining a professional assistant persona without revealing internal processes.

## How We Built It

We built Vera starting from Sentient AI’s example agent code and Hack UI interface, which gave us a strong foundation to jump-start development.
This framework allowed us to focus less on boilerplate setup and more on deeply understanding the codebase, how the agent operated, and how to tailor its behavior.

Throughout the hackathon, we spent our time studying the underlying systems, then iterating on the code to adapt it for our specific use case — transforming it into a tactful, conversational fact-checking assistant.
Our customizations focused on both the technical workflow and the user experience, ensuring Vera responds gracefully, delivers clear explanations, and supports users in navigating today's complex information landscape.

## Challenges We Ran into

* Getting the AI to intelligently design a search query for Tavily

* Setting up the system prompt so that the AI didn't go off the rails

* Properly hosting the front end

## What We Learned

* How to use Tavily for AI web searching

* How to use the Fireworks.ai api

* How to handle async functions in Python