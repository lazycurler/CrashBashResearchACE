# Arbitrary Code Execution (ACE) in Crash Bash NTSC-J

_Crash Bash_ is party video game released in 2000 for the Playstation 1. The game is comprised of a series of minigame challenges interleaved with boss fights. To this day, the game continues to be played by speedrunners who compete to beat the game as fast as possible as documented on [speedrun.com](https://www.speedrun.com/crashbash). Two main speedruning categories exist: `Any%` and `Any% No Memory Manipulation`. The main difference between these two categories is the allowance of a exploit that allows the runner to modify game code and/or data to complete the game faster than would otherwise be possible. This repo attempts to explain how this exploit works, investigates what code and data can be modified, and provides tools to further this endeavor.

The most interesting result of this research is a __human-feasible, hardware-verified, method for Arbitrary Code Execution (ACE)__ (see [Links](#links) section for video evidence). This technique relies on a series of roughly a couple hundred precise D-Pad inputs to modify the game's code allowing the player to skip to the final credits. This route does not rely on any pixel prefect setups nor time sensitive inputs. It does, however, require multiple buttons (up to all 4) on the D-Pad to be pressed simultaneously on the same frame. Implemented as a Tool Assisted Speedrun (TAS), the route takes roughly __35 seconds__ RTA to complete (from the player spawning in the Warp Room until the credits begin to roll).

It is my opinion that, with a few modifications to make the route more human-feasible, a speedrunner could use this technique to bring the `Any%` category down from roughly 1 hour and 50 minutes to just a handful of minutes. Community effort will be required to find the most feasible route and to determine if this technique qualifies for the `Any%` category. Given the human variant of this route will likely still require D-Pad combinations not possible on a standard Playstation controller (e.g. left, up, and right), a DDR pad may be required. Therefore, should the community choose to disallow this technique as part of `Any%` I would propose a new (meme) category be created; `DDR%`. This would have the player attempt to skip to the credits as fast as possible while only using a DDR pad.

## High-Level Overview

What follows is a high-level overview of this run/technique. For more technical details, please see the accompanying [writeup](./writeup/).

The run begins after the player has selected a new character and enters the Warp Room for the first time. The player heads straight to Save Station and enters the "Enter Name" Menu. From here, the cursor is navigated out of the intended menu space by pressing multiple directional buttons at once. This exploit was found by **BetaM** back in 2017 and is the foundation for the existing Memory Manipulation category and, indeed, this new route.

Once out of the intended menu, the cursor is precisely navigated to modify the game's code. The first part of code to be modified is used to increase the number of addresses in memory that can be changed. The cursor is then navigated to a new area that changes what happens when the "Enter Name" menu is accessed. The game's code is then further modified to allow a (practically) unlimited number of characters to be written. This change takes effect only _after_ the player exists and re-enters the menu.

When the menu is re-entered, the cursor is again navigated off the screen. Specific characters, not normally accessible from the menu, are selected to begin writing new code. This code is designed such that, when run, it will modify the existing game's code further. The target of this modification is the code responsible for preventing a player from warping to a new Warp Room without first collecting a specified number of collectables. Once this new code (or payload) has been written the game's code is again changed, this time modifying where new characters will be inserted.

Once characters can be written to a new region, the games memory is further changed. This change tricks the game into running the code that was written in the previous section; the payload. Once the payload has been run, the collectable check is removed and the player can safely exit the "Enter Name" menu. From there, the player can simply walk to the Warp Room selector and select Warp Room 5. The first time the player goes to Warp Room 5 the end credits are played. This marks the end of the run.

## Links

The rest of this repo contains the research and tools used to design and implement the aforementioned TAS
* [Writeup](./writeup/) - A rigorous, in-depth, explanation of the exploits and techniques used to achieve credit-skip ACE
* [Tools](./tools/) - The tools used to research this memory manipulation exploit and for generating the TAS
* [Annotated TAS Route (YouTube)](https://youtu.be/XHBzD3LvANY) - A video showing the TAS inputs and various memory regions
* [Hardware Verification (YouTube)](https://youtu.be/B50j4zk_VxI) - A video demonstrating the TAS working on an original PS1 using a modified controller
