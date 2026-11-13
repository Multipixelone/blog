---
title: "Exploring my Library: Album Graph"
date: 2026-10-06
description: "I mapped my whole music library into a graph you can fly around and search with plain-language questions."
slug: album-graph
template: page.html
taxonomies:
  tags:
    - technology
    - nix
    - flakes
    - music
    - llm
    - project
---

Finally got around to mapping my whole music library into a visualizer.

<!-- more -->

Find it at [albums.finnrut.is](https://albums.finnrut.is).

I maintain a somewhat sizable [beets](https://beets.io/) library that's grown over the years to be 2 terabytes. Beets is basically my favorite program ever. It's a command-line only tool that takes album folders as input and then tags them from [MusicBrainz](https://musicbrainz.org/) and moves them so every album is exactly where I want it. It's tremendous. 2 terabytes might sound like a **lot**, but really it's only about 6.5k albums stored losslessly. I got _really_ anal about lossless storage of music some years back and I never really lost the excitement that comes from the endless search of where I can get the music I love in FLAC.

Sidenote: if you're an artist reading this, please make sure I can purchase your album from Bandcamp or something. There's been an uncomfortable number of friends who send me music that I truly cannot find without ripping it off of a streaming site and I hate that :( I want to pay you!

Spotify has a number of proprietary models that tag every song that gets uploaded with thousands of numbers. Spotify then uses these numbers to categorize songs together, recommend adjacent songs to users, and any number of playlist generating shenanigans. In my search of if there was a way to roll this kind of setup at home, I stumbled on [Essentia](https://essentia.upf.edu/index.html). It's an open source library for audio analysis and I ran it on my whole. music library.

It took multiple nights but now every song in my music library has a number of high level attributes that I can use for analysis and querying. I ran 20 threads of this and it truly pegged every core of my CPU at 100% for multiple nights straight. I'd wake up every morning and look at the progress and see a couple hundred more albums show up in the visualizer. It was a hoot.

In my love for creating visualizations for things, I made this into a web app that renders every album in my collection as a connected point between albums that the numbers determine sound similar. It averages the sound of all the tracks on each album, so it can kinda get shoddy for albums that are all over the place (a lot of my library). I also have the engine tag the albums with arbitrary words for what the analysis fits into so it has buckets of genre around each cloud of albums :-)

I added a timeline with important events in my life, and you can see what my library looked at any point in time.

hmu if anything breaks. She's trying her best with a pretty large music library <3
