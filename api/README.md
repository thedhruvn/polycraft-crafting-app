# Polycraft Crafting Planner
Polycraft Crafting Planner builds a weighted crafting network across major inventories available in PolycraftWorld.
Using Dijkstra, the shortest weighted path from the queried item to it's base (naturally occurring) components is formed

This package takes advantage of NetworkX and Mermaid to build/traverse the network and to visually display the result

This module can be extended for AI purposes and will return either a NetworkX representation or a Mermaid markdown string with the result

### Usage
<code>
ps = Processor()<br>
ps.query_network("Item") //returns NetworkX object
ps.query_mermaid("Item") //returns Mermaid string
</code> 

### Limitations
* Does not compute total cost of items - cost displayed only valued for each step in the process
* Does not take into account inventory restrictions. i.e., solution for a Chemical Processor requires the use of a Chemical Processor
* Does not demonstrate how to craft base minecraft items. I.e., sticks are represented as "Sticks" and are not explained further