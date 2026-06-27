---
title: What a resume generator taught me about making LLM output reliable
date: 2026-06-26
slug: resume-gen
template: page.html
taxonomies:
  tags:
    - technology
    - llm
    - project
---

One thing about me is I am obsessed with overengineering personal projects. Even when I am the singular consumer of a given project, I like to play pretend that I am leading a team of developers who are all following the trail of bread crumbs I left months ago.

<!-- more -->

I absolutely _hated_ resume writing and construction. So I did what I always do with a task I hate: I tried to engineer around it. Having spent my last four years in Musical Theatre school, I already had four disparate Google Docs that stared at me in my recents every time I'd open. They'd drift, they didn't match, and every time I did something actually _fun_, I'd have to add it to them, adding another barrier to me actually representing myself.

Here's a laundry list of things that make me despise resume construction:

- Maintaining an up-to-date list of things I've done
- Phrasing everything in a way that sounds impressive, but not _insane_
- Keeping theming consistent
- Maintaining multiple _genres_ of resumes for each of my realms of expertise

It all came to a head when I got a new job and wanted to add it to my resume. Four different files to open. Four different summaries to write. I sat on it and knew there had to be a better way. From years of managing infrastructure-as-code, I instinctively wanted a single source of truth for everything. Change a fact about a previous gig, and I should just have to push that change to see it reflected on all my resumes.

I overengineered the _heck_ out of this. I set up CI so every commit rebuilds all my resumes. Page-count checks catch any layout that spills over. A Nix flake pins every dependency so it builds the same way on any machine. It works everywhere, and nothing hits my [resume website](https://resume.finnrut.is/) before I am absolutely sure it's my best work.

That one metadata file now feeds around thirty variants covering acting, tech, work, nanny, and a bunch of theatre and startup spins, so a single date change rebuilds all of them.

But that only solved my mechanical gripes with the process. The framing and phrasing were still my main sticking point because when I write, I write casual and personal, so I made a workflow for that too.

I wrote a skill for my agentic coding assistant that automated the process: pulling the job listing, extracting key phrases, but mostly making sure the LLM structured things precisely how I wanted it. But the real trick wasn't the prompt itself. It was my [AGENTS.md](https://github.com/Multipixelone/resume/blob/main/AGENTS.md) file that lives in the resume repo, committed with the templates. It's about 325 lines of system prompt that governs how the model writes copy.

The section I kept revising was "What to Avoid (AI Tells)." Instead of telling the model to sound friendly or confident, it lists things it _can't_ write. No "leveraged." No "spearheaded." No "orchestrated." **No em dashes, ever.** I tried telling it what voice to use, and it kept sounding like a LinkedIn post. As soon as I told it explicitly what _not_ to do, it finally sounded normal. It wrote far better when I told it what to skip.

The other piece that keeps it from drifting is the output shape. The model doesn't get to spit out prose. It fills in TOML metadata against a schema I defined. If it hallucinates a field, the build fails. Same basic idea as writing a test for an API: the model is the function, and the schema is the test.

That's the part that actually matters. Generating text that _looks right_ is easy. Building a system where the generated output has to be correct is the hard part. Making these systems _predictable_. Giving them enough context that anyone picking up my system in a year or two could get right back into writing resumes.

I know those breadcrumbs will save my ass in a year or two.

The scale is obviously different from a production platform, but the problem is the same shape: the output has to be reliable enough that you don't have to rewrite it from scratch.
