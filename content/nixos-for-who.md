---
title: Declarative systems are the future of systems administration
date: 2026-06-26
description: "Why declarative systems like NixOS are the future: one source of truth for an entire fleet, modules, and composition that imperative sysadmin can't match."
slug: nixos-for-who
template: page.html
taxonomies:
  tags:
    - technology
    - nix
    - declarative
    - project
extra:
  cover_alt: "Social card for 'Declarative systems are the future and I want more!'"
---

I first tried NixOS way before I was ready to appreciate the concept. I didn't understand it, I thought it was clunky, I bounced off the concept __hard__. Fast forward to today, my [Multipixelone/infra](https://github.com/Multipixelone/infra) repo now sits at 3,773 commits. Who is this technology for?

<!-- more -->

My first experince was in my middle school days of taking my laptop to school and recklessly installing as many distros as possible alongside each other and distro-hopping like crazy (the day I learned I could have a separate partition for /home, everything changed). So let me get one thing squared away first: NixOS is a massive overcomplication of the standard computing paradigm for, like, 90% of people. 

The standard way computers are set up is _imperative_. Your computer has what is called a _state_, a catch-all term for the configuration of everything that makes up your computer (apps, settings, files), and you perform actions that manipulate that state. You install apps, you download files, you open System Preferences and change things. This is, genuinely, perfectly fine for your grandma's desktop, but scales terribly. 

The biggest problem at scale here is forgetting changes. If this computer dies, and, heaven forbid, you don't have a backup made, do you remember all the programs you had installed? Do you remember the intricate configuration files that connect them all together? How confident are you that you would be able to reproduce it without doing the _same exact amount of work over again_? NixOS solves this problem by giving you one place to define everything on your system: every config key and installed app is in one place, where it is the single source of truth for your computer. 

Here's what that looks like in practice. My entire fleet and homelab: desktop, laptop, IoT server, media server are defined by four files, each one a list of concerns pulled from a shared vocabulary. My desktop pulls in gaming related concerns:

```nix
{ config, ... }:
{
  configurations.nixos.link.module = {
    imports = with config.flake.modules.nixos; [
      efi
      pc
      gaming
      cloudflared
    ];
  };
}
```
While my laptop pulls in a different profile called `laptop` that completely changes how a device with the profile manages power and performance. Note here that `laptop` depends on `pc`: 
```nix
{ config, ... }:
{
  configurations.nixos.zelda.module = {
    imports = with config.flake.modules.nixos; [
      efi
      wifi
      laptop
      gaming
    ];
  };
}
```
My music server, `marin`, pulls in no profiles with GUI:
```nix
{ config, ... }:
{
  configurations.nixos.marin.module = {
    imports = with config.flake.modules.nixos; [
      efi
      wifi
      base
      media
    ];
  };
}
```

No machines are configured: they're described. Adding a new server is writing one 11-line file.

And it's not just machines. My identity is defined once, and everything else derives from it:

```nix
{ config, ... }:
{
  flake = {
    meta.owner = {
      email = "me@finnrut.is";
      name = "Finn Rutis";
      username = "tunnel";
    };

    modules = {
      nixos.base = {
        users.users.${config.flake.meta.owner.username} = {
          isNormalUser = true;
          linger = true;
          extraGroups = [ "input" ];
        };

        systemd.tmpfiles.rules = [
          "L /var/lib/AccountsService/icons/${config.flake.meta.owner.username} - - - - ${./Finn.jpg}"
        ];
      };
    };
  };
}
```

Change my name in one place, and it changes everywhere — the user account, the `nix` trusted-users list, the login screen avatar. The person is the root of the configuration tree.

This, however, front-loads the effort. When you want an app installed, instead of just `sudo apt install vlc`, you have to navigate to your configuration repository, add it to a key that holds installed packages, and rebuild your system. You are trading effort now for reliability in the long run. 

NixOS also has what I consider to be the most helpful feature: modules. Modules are a collection of code that contains an app and all of the configuration keys that app exposes. Take the 

<!-- NOTE (review): The modules paragraph should illustrate COMPOSITION or REUSE — the thing imperative systems structurally cannot do. Don't make it "here's what a module looks like" (e.g. "here's an nginx module" doesn't advance the argument). Make it "here's how I use the same module across three machines" or "here's how I imported someone else's module and got their entire setup in one line" — that's the "future" argument moving forward. Also: "Modules are a collection of code that contains an app and all of the configuration keys that app exposes" — "a collection of code" is vague; "a module bundles an application with its configuration options" is tighter. "exposes" is correct Nix terminology but may lose a general audience; consider whether context defines it enough. STRATEGIC: this paragraph is the last natural place to plant the seed for the title's "I want more" promise — frame modules as "here's what's possible, and I'm already pushing against the limits" to set up the ending. If modules are just "here's what I have," the "I want more" turn later will feel unearned. -->

<!-- NOTE (review): OVERALL PACING — diagnosis section (lines 18-22) is now longer than discovery (lines 22-26). Risk of the post becoming a complaint rather than an argument. The modules paragraph needs to do heavy lifting to rebalance: shift from "here's the fix" to "here's why this is the future." The title's second promise ("I want more") is still entirely absent — fine for now (~40% mark), but it belongs near the end and should be foreshadowed in the modules paragraph above. -->
