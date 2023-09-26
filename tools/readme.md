# **DISCLAIMER!**

* All scripts were written to further the research and are not, themselves, intended to be the end product.
* They likely exist solely to solve one-off problems and were quickly (re)written in an attempt to better understand or explain observed in-game phenomenon.
* This code was written as a **hobby**, it is not up to professional standards; meaning it's almost assuredly **not**:
  * bug free
  * well tested
  * reuseable
  * maintainable
  * well documented
* That being said, please feel free to ask questions or open a PR ;)

# Requirements
The following are required to use this tool suite and can be installed with `pip`:
* `igraph`
* `matplotlib`

# Usage

Simply running `python ace.py` from inside the `tools` directory should result in the TAS string for the main route being printed. The **EXPERIMENTAL** `-w` option can be passed to generate weighted graphs which should, in theory, result in more human feasible graphs. Further route tuning and optimization will be needed to make these viable. Primitive debug options are exposed via the `--debug_index` and `--debug_table` options which can print out useful information about a given cursor index for a specific table. Unfortunately, while a lot of functionality is not yet exposed via the argument parser and requires code modification. If there is a feature you'd like to see implemented or exposed please reach out and I may be able to expose it or help you add it. Again, this was written over the span of almost a year and most of the work to this point has been focused on getting something to _work_, not really on creating a tool for the community to use. Only with _your_ help will this tool be modified from a novelty to a powerful community tool.

# Overview of Implementation

With the disclaimer out of the way, what follows is a brief overview of the majority of the files in this repo and their purpose. The majority of these tools are designed for use with the NTSC-J version of _Crash Bash_ but with a little effort could be modified to work for any/all versions.

At a high level, the input heavy portion of the TAS is generated using a series of Python modules which each (attempt) to abstract a given layer of complexity. The `ace.py` contains `main()` and is the primary point of entry for the end-user. It creates all needed graphs (of the state space) and uses them to create a `Navigator` object which will be used to navigate the state space. Each `Navigator` object contains a collection of methods for moving the cursor to and from points of interest including writing specific bytes (used for code generation). All movements and insertions are recorded inside the `Navigator` object using the `Tracker` object. This object can be queried at the end of a route to generate the resulting TAS inputs as well as corresponding debug information about the rote. Finally, the `Visualizer` object provides a way for a user to graph the state space used.

## Graph Generation

As alluded to previously, each `Navigator` object is comprised of one or more `Graph` objects which represent all possible cursor movement and locations for a given character table e.g. the "Hiragana" character table. This is a cyclic, directed, optionally-weighted graph where the nodes contain information about that memory address (e.g. what address(es) are NOP'd, what byte would be inserted if any if this index was selected, etc) and the edges are the D-Pad press required to move between nodes. These graphs are generated using memory dumps of the 2MB of RAM while the player is in "Enter Name" menu.

Starting from the lowest layer, `MemoryReader` provides an easy way for other modules to read values of a given size at a given memory address while abstracting away endianness and relevant memory mapping/mirroring. `CharTable` sits on top of `MemoryReader` and simulates the movement and insertion operations the player triggers while in the menu. This is the module that provides all the required data for the nodes and edges of the resulting graph. A depth-first search is done using starting at `curosrIndex` `0` and used to build up all the node and edge information about a specific graph. This is then converted into an `igraph` graph which is stored inside the `Graph` object. `Graph` provides all the functionality for generating these `igraphs` and some basic search functionality.

## Main Modules

* `ace.py` - Primary script for end-user interaction. Contains `main()` and argument parsing
* `bad-addresses.py` - An incomplete list of addresses that, if NOP'd, will cause adverse affects during a speedrun. Meant to be imported by other modules as it contains no real code, only data
* `charTable.py` - Wraps a `MemoryReader` object and simulates cursor movement and insertion for a given character table
* `graph.py` - Convert node and edge information into an `igraph` `graph` object and provides basic search functionality
* `memoryReader.py` - Provides an interface for querying the value of memory in a specific location for a given memory dump file abstracting away Playstation specific memory implementation details
* `menu_constants.py`- Data only module containing important, table specific, cursor indices
* `navigator.py` - High level interface for navigating the state space. Contains multiple graphs, provides an interface to search them for relevant bytes and locations, and tracks requested movements with an internal `Tracker` object
* `nodeInfo.py` - Simple dataclass used to encapsulate all information needed create a node for the graphs. (e.g. NOP'd address(es) cursor's index, byte inserted (if any), etc)
* `routing.py` - Specifies the different routes implemented to achieve ACE or other exploits. Describes what addresses need to be modified, what bytes need to be inserted, and in what order.
* `subgraphTools.py` - Used to trim terminal subgraphs
* `tracker.py` - Used in `Navigator` to track all player inputs. Generates _Bizhawk_ compliant TAS strings and debug information
* `visualizer.py` - Generate graphs and gifs for visualizing graph navigation

## Utilities
### Tools created to solve unexpected/intermittent challenges but not strictly needed in the TAS generation stack
* `addr_diff.py` - Hastily written utility tool for diffing Crash Bash memory dumps
* `asm.py` - Partially implemented PSX MIPS 3000 (dis)assembler. Primarily used for finding available opcodes/instructions
* `mips.py` - Data module containing dictionaries for assembly [en, de]coding
