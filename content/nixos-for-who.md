---
title: Declarative systems are the future and I want more!
date: 2026-06-26
slug: nixos-for-who
template: page.html
taxonomies:
  tags:
    - technology
    - nix
    - declarative
    - project
---

I first tried NixOS way before I was ready to appreciate the concept. I tried it in my middle school days of taking my laptop to school and recklessly installing as many distros as possible alongside eachother and distro-hopping like my life depended on it (the day I learned I could have a separate partition for /home, everything changed). I didn't understand it, I thought it was clunky, I bounced off the concept __hard__. Fast forward to today, my [Multipixelone/infra](https://github.com/Multipixelone/infra) repo now sits at 3,773 commits. Who is this technology for?

<!-- more -->

Let me get one thing squared away first: I think NixOS is a massive overcomplication of the standard computing paradigm for, like, 90% of people. 

The standard way computers are set up is _imperative_. Your computer has what is called a _state_, a catch-all term for the configuration of everything that makes up your computer (apps, settings, files), and you, in using your computer, perform actions that manipulate that state. You install apps, you download files, you open System Preferences and change things. This is, genuinely, perfectly fine for your grandma's desktop, but scales terribly. Cruft building up over time, configuration drift, and forgetting changes you made years ago are just some of the things that make imperative computing bad once you start to move past 3+ computers.

The biggest problem at scale here is forgetting changes. If this computer dies, and, heaven forbid, you don't have a backup made, do you remember all the programs you had installed? Do you remember the intricate configuration files that connect them all together? How confident are you that you would be able to reproduce it again without doing the _same exact amount of work again_. NixOS solves this problem by giving you once place to define everything on your system: every single config key, installed app, _everything_ is in one place, where it will forever remain as the single source of truth for _your_ computer. 

This front loads the effort. When you want an app installed, instead of just `sudo apt install vlc`, you have to navigate to your configuration repository, add it to a key that holds installed packages, and rebuild your entire system from scratch. You are trading effort now for reliability in the long run. 

NixOS also has what I consider to be the most helpful feature: modules. Modules are a collection of code that contains an app and all of the configuration keys that app exposes. Take the 

