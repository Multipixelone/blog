+++
title = "Typst & Nix backed resume generation"
date = 2026-06-26
slug = "resume-gen"
template = "page.html"
+++

One thing about me is I am obsessed with overengineering personal projects. Even when I am the singular consumer of a given project, I like to play pretend that I am leading a team of developers who are all following the trail of bread crumbs I left months ago.

<!-- more -->

I absolutely _hated_ resume writing and construction. It was one of my most dreaded tasks. Like any task that makes my soul recoil at the thought of doing it, I asked myself what I could do to make this most hated task one that I look forward to. Having spent my last four years in Musical Theatre school, I already had four disparate Google Docs that stared at me in my recents everytime I'd open. They'd drift, they didn't match, and everytime I did something actually _fun_, I'd have to add it to them, adding another barrier to me actually representing myself.

Here's a laundry list of things that make me despise resume construction:

- Maintaining an up-to-date list of things I've done
- Phrasing everything in a way that sounds impressive, but not _insane_
- Keeping theming consistant
- Maintaining multiple _genres_ of resumes for each of my realms of expertise

It all came to a head when I got a new job and wanted to add it to my resume. Four different files to open. Four different summaries to write. I sat on it and knew there had to be a better way. From my days of managing complex IaC systems, I instinctively wanted a single source of truth for everything. Change a fact about a previous gig, and I should just have to push that change to see it reflected on all my resumes.

I overengineered the _heck_ out of this. CI pipelines, testing solutions to check the PDFs all render in the expected number of pages, a nix flake to ensure no dependency drift. It works everywhere, and nothing hits my [resume website](https://multipixelone.github.io/resume/) before I am absolutely sure it's my best work

But that only solved my mechanical gripes with the process. The framing and phrasing were still my main sticking point because when I write, I write casual and personal, so I made a workflow for that too.

A whole skillset for my agentic coding assistant that automated the process: pulling the job listing, extracting key phrases, and mostly making sure the LLM structured things precisely how I wanted it. That's the part that interests me the most: making these complex and confusing systems _predictable_. Giving them enough context that anyone picking up my system in a year or two could get right back into writing resumes.

I know those breadcrumbs will save my ass in a year or two. By not assuming I will remember every little detail about a project, I build a clear system that holds up in the long term, for whenever I need to go back on the hunt for jobs.
